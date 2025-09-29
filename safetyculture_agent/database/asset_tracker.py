# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor


@dataclass
class AssetInspectionRecord:
    """Represents an asset inspection record in the database."""
    asset_id: str
    asset_name: str
    asset_type: str
    location: str
    inspection_id: str
    template_id: str
    template_name: str
    inspection_date: str
    completion_date: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    inspector: str
    month_year: str  # Format: "2024-01"
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


class AssetTracker:
    """Database manager for tracking asset inspections and preventing duplicates."""
    
    def __init__(self, db_path: str = "safetyculture_assets.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1)
    
    def _execute_sync(self, func, *args, **kwargs):
        """Execute a synchronous database operation."""
        with self._lock:
            return func(*args, **kwargs)
    
    async def _execute_async(self, func, *args, **kwargs):
        """Execute a database operation asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._execute_sync, func, *args, **kwargs)
    
    def _initialize_database_sync(self):
        """Initialize the database with required tables (sync version)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS asset_inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT NOT NULL,
                    asset_name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    location TEXT NOT NULL,
                    inspection_id TEXT UNIQUE,
                    template_id TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    inspection_date TEXT NOT NULL,
                    completion_date TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    inspector TEXT,
                    month_year TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT,
                    UNIQUE(asset_id, month_year)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_asset_month 
                ON asset_inspections(asset_id, month_year)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_month 
                ON asset_inspections(status, month_year)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_inspection_date 
                ON asset_inspections(inspection_date)
            """)
            
            # Create monthly_summaries table for reporting
            conn.execute("""
                CREATE TABLE IF NOT EXISTS monthly_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month_year TEXT UNIQUE NOT NULL,
                    total_assets INTEGER DEFAULT 0,
                    completed_inspections INTEGER DEFAULT 0,
                    pending_inspections INTEGER DEFAULT 0,
                    failed_inspections INTEGER DEFAULT 0,
                    completion_rate REAL DEFAULT 0.0,
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    async def initialize_database(self):
        """Initialize the database with required tables."""
        await self._execute_async(self._initialize_database_sync)
    
    def _get_current_month_year(self) -> str:
        """Get current month-year string."""
        return datetime.now().strftime("%Y-%m")
    
    def _check_asset_completed_this_month_sync(self, asset_id: str, month_year: str) -> bool:
        """Check if an asset has already been inspected this month (sync version)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM asset_inspections 
                WHERE asset_id = ? AND month_year = ? AND status = 'completed'
            """, (asset_id, month_year))
            
            count = cursor.fetchone()
            return count[0] > 0
    
    async def check_asset_completed_this_month(self, asset_id: str, month_year: Optional[str] = None) -> bool:
        """Check if an asset has already been inspected this month."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(self._check_asset_completed_this_month_sync, asset_id, month_year)
    
    def _get_asset_inspection_status_sync(self, asset_id: str, month_year: str) -> Optional[str]:
        """Get the current inspection status for an asset this month (sync version)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT status FROM asset_inspections 
                WHERE asset_id = ? AND month_year = ?
            """, (asset_id, month_year))
            
            result = cursor.fetchone()
            return result[0] if result else None
    
    async def get_asset_inspection_status(self, asset_id: str, month_year: Optional[str] = None) -> Optional[str]:
        """Get the current inspection status for an asset this month."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(self._get_asset_inspection_status_sync, asset_id, month_year)
    
    def _register_asset_for_inspection_sync(
        self,
        asset_id: str,
        asset_name: str,
        asset_type: str,
        location: str,
        template_id: str,
        template_name: str,
        inspector: str,
        month_year: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Register an asset for inspection (sync version)."""
        # Check if already completed
        if self._check_asset_completed_this_month_sync(asset_id, month_year):
            return False
        
        current_time = datetime.now().isoformat()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO asset_inspections (
                        asset_id, asset_name, asset_type, location,
                        template_id, template_name, inspection_date,
                        status, inspector, month_year, created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    asset_id, asset_name, asset_type, location,
                    template_id, template_name, current_time,
                    'pending', inspector, month_year, current_time, current_time,
                    json.dumps(metadata)
                ))
                
                conn.commit()
                return True
        
        except sqlite3.IntegrityError:
            # Asset already registered for this month
            return False
    
    async def register_asset_for_inspection(
        self,
        asset_id: str,
        asset_name: str,
        asset_type: str,
        location: str,
        template_id: str,
        template_name: str,
        inspector: str = "SafetyCulture Agent",
        month_year: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register an asset for inspection. Returns False if already exists."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(
            self._register_asset_for_inspection_sync,
            asset_id, asset_name, asset_type, location,
            template_id, template_name, inspector, month_year, metadata or {}
        )
    
    def _get_asset_metadata_sync(self, asset_id: str, month_year: str) -> Dict[str, Any]:
        """Get existing metadata for an asset (sync version)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT metadata FROM asset_inspections 
                WHERE asset_id = ? AND month_year = ?
            """, (asset_id, month_year))
            
            result = cursor.fetchone()
            if result and result[0]:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return {}
            return {}
    
    def _update_inspection_status_sync(
        self,
        asset_id: str,
        status: str,
        month_year: str,
        inspection_id: Optional[str] = None,
        completion_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update the inspection status for an asset (sync version)."""
        current_time = datetime.now().isoformat()
        
        # Prepare update fields
        update_fields = ["status = ?", "updated_at = ?"]
        update_values = [status, current_time]
        
        if inspection_id:
            update_fields.append("inspection_id = ?")
            update_values.append(inspection_id)
        
        if completion_date:
            update_fields.append("completion_date = ?")
            update_values.append(completion_date)
        elif status == 'completed':
            update_fields.append("completion_date = ?")
            update_values.append(current_time)
        
        if metadata:
            # Merge with existing metadata
            existing_metadata = self._get_asset_metadata_sync(asset_id, month_year)
            existing_metadata.update(metadata)
            update_fields.append("metadata = ?")
            update_values.append(json.dumps(existing_metadata))
        
        # Add WHERE clause values
        update_values.extend([asset_id, month_year])
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"""
                UPDATE asset_inspections 
                SET {', '.join(update_fields)}
                WHERE asset_id = ? AND month_year = ?
            """, update_values)
            
            conn.commit()
            return cursor.rowcount > 0
    
    async def update_inspection_status(
        self,
        asset_id: str,
        status: str,
        inspection_id: Optional[str] = None,
        completion_date: Optional[str] = None,
        month_year: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update the inspection status for an asset."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(
            self._update_inspection_status_sync,
            asset_id, status, month_year, inspection_id, completion_date, metadata
        )
    
    def _get_pending_assets_sync(self, month_year: str, limit: Optional[int] = None) -> List[AssetInspectionRecord]:
        """Get all pending asset inspections for a month (sync version)."""
        query = """
            SELECT * FROM asset_inspections 
            WHERE month_year = ? AND status = 'pending'
            ORDER BY created_at ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, (month_year,))
            rows = cursor.fetchall()
            
            return [self._row_to_record(row) for row in rows]
    
    async def get_pending_assets(self, month_year: Optional[str] = None, limit: Optional[int] = None) -> List[AssetInspectionRecord]:
        """Get all pending asset inspections for a month."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(self._get_pending_assets_sync, month_year, limit)
    
    def _get_completed_assets_sync(self, month_year: str) -> List[AssetInspectionRecord]:
        """Get all completed asset inspections for a month (sync version)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM asset_inspections 
                WHERE month_year = ? AND status = 'completed'
                ORDER BY completion_date DESC
            """, (month_year,))
            
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]
    
    async def get_completed_assets(self, month_year: Optional[str] = None) -> List[AssetInspectionRecord]:
        """Get all completed asset inspections for a month."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(self._get_completed_assets_sync, month_year)
    
    def _get_monthly_summary_sync(self, month_year: str) -> Dict[str, Any]:
        """Get monthly inspection summary statistics (sync version)."""
        with sqlite3.connect(self.db_path) as conn:
            # Get counts by status
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM asset_inspections 
                WHERE month_year = ?
                GROUP BY status
            """, (month_year,))
            
            status_counts = dict(cursor.fetchall())
            
            total_assets = sum(status_counts.values())
            completed = status_counts.get('completed', 0)
            pending = status_counts.get('pending', 0)
            in_progress = status_counts.get('in_progress', 0)
            failed = status_counts.get('failed', 0)
            
            completion_rate = (completed / total_assets * 100) if total_assets > 0 else 0
            
            # Update monthly_summaries table
            current_time = datetime.now().isoformat()
            conn.execute("""
                INSERT OR REPLACE INTO monthly_summaries (
                    month_year, total_assets, completed_inspections, 
                    pending_inspections, failed_inspections, completion_rate, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (month_year, total_assets, completed, pending, failed, completion_rate, current_time))
            
            conn.commit()
            
            return {
                "month_year": month_year,
                "total_assets": total_assets,
                "completed_inspections": completed,
                "pending_inspections": pending,
                "in_progress_inspections": in_progress,
                "failed_inspections": failed,
                "completion_rate": round(completion_rate, 2),
                "last_updated": current_time
            }
    
    async def get_monthly_summary(self, month_year: Optional[str] = None) -> Dict[str, Any]:
        """Get monthly inspection summary statistics."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(self._get_monthly_summary_sync, month_year)
    
    async def mark_asset_completed(
        self,
        asset_id: str,
        inspection_id: str,
        inspector: str = "SafetyCulture Agent",
        month_year: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Mark an asset inspection as completed."""
        return await self.update_inspection_status(
            asset_id=asset_id,
            status='completed',
            inspection_id=inspection_id,
            completion_date=datetime.now().isoformat(),
            month_year=month_year,
            metadata=metadata
        )
    
    async def mark_asset_failed(
        self,
        asset_id: str,
        error_message: str,
        month_year: Optional[str] = None
    ) -> bool:
        """Mark an asset inspection as failed."""
        metadata = {"error_message": error_message, "failed_at": datetime.now().isoformat()}
        return await self.update_inspection_status(
            asset_id=asset_id,
            status='failed',
            month_year=month_year,
            metadata=metadata
        )
    
    def _row_to_record(self, row) -> AssetInspectionRecord:
        """Convert database row to AssetInspectionRecord."""
        metadata = {}
        if row[15]:  # metadata column
            try:
                metadata = json.loads(row[15])
            except json.JSONDecodeError:
                metadata = {}
        
        return AssetInspectionRecord(
            asset_id=row[1],
            asset_name=row[2],
            asset_type=row[3],
            location=row[4],
            inspection_id=row[5] or "",
            template_id=row[6],
            template_name=row[7],
            inspection_date=row[8],
            completion_date=row[9] or "",
            status=row[10],
            inspector=row[11] or "",
            month_year=row[12],
            created_at=row[13],
            updated_at=row[14],
            metadata=metadata
        )
    
    def _export_monthly_report_sync(self, month_year: str) -> Dict[str, Any]:
        """Export a comprehensive monthly report (sync version)."""
        summary = self._get_monthly_summary_sync(month_year)
        completed_assets = self._get_completed_assets_sync(month_year)
        pending_assets = self._get_pending_assets_sync(month_year)
        
        # Group by asset type
        assets_by_type = {}
        all_assets = completed_assets + pending_assets
        
        for asset in all_assets:
            asset_type = asset.asset_type
            if asset_type not in assets_by_type:
                assets_by_type[asset_type] = {"completed": 0, "pending": 0, "total": 0}
            
            assets_by_type[asset_type]["total"] += 1
            if asset.status == "completed":
                assets_by_type[asset_type]["completed"] += 1
            else:
                assets_by_type[asset_type]["pending"] += 1
        
        return {
            "month_year": month_year,
            "summary": summary,
            "assets_by_type": assets_by_type,
            "completed_assets": [
                {
                    "asset_id": asset.asset_id,
                    "asset_name": asset.asset_name,
                    "asset_type": asset.asset_type,
                    "location": asset.location,
                    "completion_date": asset.completion_date,
                    "inspection_id": asset.inspection_id
                }
                for asset in completed_assets
            ],
            "pending_assets": [
                {
                    "asset_id": asset.asset_id,
                    "asset_name": asset.asset_name,
                    "asset_type": asset.asset_type,
                    "location": asset.location,
                    "created_at": asset.created_at
                }
                for asset in pending_assets
            ]
        }
    
    async def export_monthly_report(self, month_year: Optional[str] = None) -> Dict[str, Any]:
        """Export a comprehensive monthly report."""
        if month_year is None:
            month_year = self._get_current_month_year()
        
        return await self._execute_async(self._export_monthly_report_sync, month_year)
