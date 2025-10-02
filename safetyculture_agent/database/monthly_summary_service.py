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

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)


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


class MonthlySummaryService:
  """Service for monthly inspection summary calculations.
  
  Handles aggregation and statistical calculations for monthly
  inspection data, including completion rates, status distributions,
  and asset metadata.
  
  Attributes:
      db_path: Path to SQLite database file
  """
  
  def __init__(self, db_path: str):
    """Initialize monthly summary service.
    
    Args:
        db_path: Path to SQLite database file
    """
    self.db_path = db_path
    logger.info("MonthlySummaryService initialized")
  
  def _get_current_month_year(self) -> str:
    """Get current month-year string in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")
  
  def _row_to_record(self, row) -> AssetInspectionRecord:
    """Convert database row to AssetInspectionRecord.
    
    Args:
        row: Database row tuple
        
    Returns:
        AssetInspectionRecord instance
    """
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
  
  async def get_monthly_summary(
      self,
      month_year: Optional[str] = None
  ) -> Dict[str, Any]:
    """Get monthly inspection summary statistics.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
        
    Returns:
        Dictionary containing monthly summary statistics
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    async with aiosqlite.connect(self.db_path) as db:
      # Get counts by status
      async with db.execute("""
          SELECT status, COUNT(*) FROM asset_inspections
          WHERE month_year = ?
          GROUP BY status
      """, (month_year,)) as cursor:
        rows = await cursor.fetchall()
        status_counts = dict(rows)
      
      total_assets = sum(status_counts.values())
      completed = status_counts.get('completed', 0)
      pending = status_counts.get('pending', 0)
      in_progress = status_counts.get('in_progress', 0)
      failed = status_counts.get('failed', 0)
      
      completion_rate = (
        (completed / total_assets * 100) if total_assets > 0 else 0
      )
      
      # Update monthly_summaries table
      current_time = datetime.now().isoformat()
      await db.execute("""
          INSERT OR REPLACE INTO monthly_summaries (
              month_year, total_assets, completed_inspections,
              pending_inspections, failed_inspections, completion_rate,
              last_updated
          ) VALUES (?, ?, ?, ?, ?, ?, ?)
      """, (
        month_year, total_assets, completed, pending, failed,
        completion_rate, current_time
      ))
      
      await db.commit()
      
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
  
  async def get_completed_assets(
      self,
      month_year: Optional[str] = None
  ) -> List[AssetInspectionRecord]:
    """Get all completed asset inspections for a month.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
        
    Returns:
        List of completed asset inspection records
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    async with aiosqlite.connect(self.db_path) as db:
      async with db.execute("""
          SELECT * FROM asset_inspections
          WHERE month_year = ? AND status = 'completed'
          ORDER BY completion_date DESC
      """, (month_year,)) as cursor:
        rows = await cursor.fetchall()
        return [self._row_to_record(row) for row in rows]
  
  async def get_pending_assets(
      self,
      month_year: Optional[str] = None,
      limit: Optional[int] = None
  ) -> List[AssetInspectionRecord]:
    """Get all pending asset inspections for a month.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
        limit: Optional maximum number of results to return
        
    Returns:
        List of pending asset inspection records
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    query = """
        SELECT * FROM asset_inspections
        WHERE month_year = ? AND status = 'pending'
        ORDER BY created_at ASC
    """
    
    if limit:
      query += f" LIMIT {limit}"
    
    async with aiosqlite.connect(self.db_path) as db:
      async with db.execute(query, (month_year,)) as cursor:
        rows = await cursor.fetchall()
        return [self._row_to_record(row) for row in rows]
  
  async def export_monthly_report(
      self,
      month_year: Optional[str] = None
  ) -> Dict[str, Any]:
    """Export a comprehensive monthly report.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
        
    Returns:
        Dictionary containing comprehensive monthly report data
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    # Fetch data using async methods
    summary = await self.get_monthly_summary(month_year)
    completed_assets = await self.get_completed_assets(month_year)
    pending_assets = await self.get_pending_assets(month_year)
    
    # Group by asset type
    assets_by_type = {}
    all_assets = completed_assets + pending_assets
    
    for asset in all_assets:
      asset_type = asset.asset_type
      if asset_type not in assets_by_type:
        assets_by_type[asset_type] = {
          "completed": 0,
          "pending": 0,
          "total": 0
        }
      
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
  
  async def _get_asset_metadata(
      self,
      asset_id: str,
      month_year: str
  ) -> Dict[str, Any]:
    """Get existing metadata for an asset.
    
    Args:
        asset_id: Unique asset identifier
        month_year: Month-year string (YYYY-MM)
        
    Returns:
        Metadata dictionary, empty dict if not found or invalid JSON
    """
    async with aiosqlite.connect(self.db_path) as db:
      async with db.execute("""
          SELECT metadata FROM asset_inspections
          WHERE asset_id = ? AND month_year = ?
      """, (asset_id, month_year)) as cursor:
        result = await cursor.fetchone()
        if result and result[0]:
          try:
            return json.loads(result[0])
          except json.JSONDecodeError:
            return {}
        return {}