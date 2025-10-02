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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)

# Allowed fields for UPDATE operations to prevent SQL injection
ALLOWED_UPDATE_FIELDS = {
  'status',
  'inspection_count',
  'last_inspection_date',
  'inspector_id',
  'completion_date',
  'notes',
  'inspection_id',
  'metadata',
  'updated_at'
}


class AssetRepository:
  """Core repository for asset inspection database operations.
  
  Handles direct database operations for asset inspections including
  registration, status updates, and existence checks. Uses aiosqlite
  for async database access.
  
  Attributes:
      db_path: Path to SQLite database file
  """
  
  def __init__(self, db_path: str):
    """Initialize asset repository.
    
    Args:
        db_path: Path to SQLite database file
    """
    self.db_path = Path(db_path)
    self.db_path.parent.mkdir(parents=True, exist_ok=True)
    self._initialized = False
    logger.info(f"AssetRepository initialized with db: {db_path}")
  
  def _validate_and_sanitize_fields(
      self,
      update_fields: List[str]
  ) -> List[str]:
    """Validate update fields against whitelist to prevent SQL injection.
    
    Args:
        update_fields: List of field names to update
        
    Returns:
        List of validated field names
        
    Raises:
        ValueError: If any field is not in the allowed whitelist
    """
    safe_fields = []
    for field in update_fields:
      # Extract field name from "field = ?" format
      field_name = field.split('=')[0].strip()
      if field_name not in ALLOWED_UPDATE_FIELDS:
        raise ValueError(
          f"Invalid field for update: {field_name}. "
          f"Allowed fields: {', '.join(sorted(ALLOWED_UPDATE_FIELDS))}"
        )
      safe_fields.append(field)
    return safe_fields
  
  async def initialize(self) -> None:
    """Initialize database schema.
    
    Raises:
        SafetyCultureDatabaseError: If initialization fails
    """
    if self._initialized:
      return
    
    try:
      async with aiosqlite.connect(self.db_path) as db:
        # Enable WAL mode for better concurrency
        await db.execute("PRAGMA journal_mode=WAL")
        
        # Create asset_inspections table
        await db.execute("""
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
        
        # Create unique index for asset_id + month_year
        await db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_month_unique
            ON asset_inspections(asset_id, month_year)
        """)
        
        # Create status + month index for faster queries
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_status_month
            ON asset_inspections(status, month_year)
        """)
        
        # Create inspection_date index
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_inspection_date
            ON asset_inspections(inspection_date)
        """)
        
        # Create monthly_summaries table for reporting
        await db.execute("""
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
        
        await db.commit()
      
      self._initialized = True
      logger.info(f"Database schema initialized: {self.db_path}")
      
    except aiosqlite.Error as e:
      from ..exceptions import SafetyCultureDatabaseError
      raise SafetyCultureDatabaseError(
        f"Failed to initialize database: {e}"
      ) from e
  
  def _get_current_month_year(self) -> str:
    """Get current month-year string in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")
  
  async def check_asset_completed_this_month(
      self,
      asset_id: str,
      month_year: Optional[str] = None
  ) -> bool:
    """Check if an asset has already been inspected this month.
    
    Args:
        asset_id: Unique asset identifier
        month_year: Month-year string (YYYY-MM), defaults to current month
        
    Returns:
        True if asset has completed inspection this month, False otherwise
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    async with aiosqlite.connect(self.db_path) as db:
      async with db.execute("""
          SELECT COUNT(*) FROM asset_inspections
          WHERE asset_id = ? AND month_year = ? AND status = 'completed'
      """, (asset_id, month_year)) as cursor:
        count = await cursor.fetchone()
        return count[0] > 0
  
  async def register_asset(
      self,
      asset_id: str,
      month_year: str,
      asset_name: str,
      location: str
  ) -> bool:
    """Register asset inspection with race condition protection.
    
    Uses database-level UNIQUE constraint instead of check-then-act
    to prevent race conditions in concurrent registration.
    
    Args:
        asset_id: Unique asset identifier
        month_year: Month and year in YYYY-MM format
        asset_name: Name of the asset
        location: Asset location
        
    Returns:
        True if asset was newly registered, False if already existed
        
    Raises:
        SafetyCultureDatabaseError: If database operation fails
    """
    from ..exceptions import SafetyCultureDatabaseError
    
    try:
      async with aiosqlite.connect(self.db_path) as db:
        # Try to insert directly - will fail if already exists
        await db.execute("""
            INSERT INTO asset_inspections (
                asset_id,
                month_year,
                asset_name,
                location,
                asset_type,
                template_id,
                template_name,
                inspection_date,
                status,
                created_at,
                updated_at
            ) VALUES (
                ?, ?, ?, ?, '', '', '', datetime('now'),
                'pending', datetime('now'), datetime('now')
            )
        """, (asset_id, month_year, asset_name, location))
        
        await db.commit()
      
      logger.info(
        f"Registered new asset: {asset_id} for {month_year}"
      )
      return True
      
    except aiosqlite.IntegrityError:
      # Asset already exists for this month - this is expected
      logger.debug(
        f"Asset {asset_id} already registered for {month_year}"
      )
      return False
      
    except aiosqlite.Error as e:
      raise SafetyCultureDatabaseError(
        f"Failed to register asset {asset_id}: {e}"
      ) from e
  
  async def get_asset_inspection_status(
      self,
      asset_id: str,
      month_year: Optional[str] = None
  ) -> Optional[str]:
    """Get the current inspection status for an asset this month.
    
    Args:
        asset_id: Unique asset identifier
        month_year: Month-year string (YYYY-MM), defaults to current month
        
    Returns:
        Current status string or None if asset not found
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    async with aiosqlite.connect(self.db_path) as db:
      async with db.execute("""
          SELECT status FROM asset_inspections
          WHERE asset_id = ? AND month_year = ?
      """, (asset_id, month_year)) as cursor:
        result = await cursor.fetchone()
        return result[0] if result else None
  
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
    """Register an asset for inspection.
    
    Args:
        asset_id: Unique asset identifier
        asset_name: Name of the asset
        asset_type: Type/category of the asset
        location: Asset location
        template_id: Inspection template ID
        template_name: Name of the inspection template
        inspector: Inspector name (default: "SafetyCulture Agent")
        month_year: Month-year string (YYYY-MM), defaults to current month
        metadata: Optional metadata dictionary
        
    Returns:
        True if asset was registered, False if already completed this month
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
    # Check if already completed
    if await self.check_asset_completed_this_month(asset_id, month_year):
      return False
    
    current_time = datetime.now().isoformat()
    
    try:
      async with aiosqlite.connect(self.db_path) as db:
        await db.execute("""
            INSERT OR REPLACE INTO asset_inspections (
                asset_id, asset_name, asset_type, location,
                template_id, template_name, inspection_date,
                status, inspector, month_year, created_at, updated_at,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            asset_id, asset_name, asset_type, location,
            template_id, template_name, current_time,
            'pending', inspector, month_year, current_time, current_time,
            json.dumps(metadata or {})
        ))
        
        await db.commit()
        return True
    
    except aiosqlite.IntegrityError:
      # Asset already registered for this month
      return False
  
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
  
  async def update_inspection_status(
      self,
      asset_id: str,
      status: str,
      inspection_id: Optional[str] = None,
      completion_date: Optional[str] = None,
      month_year: Optional[str] = None,
      metadata: Optional[Dict[str, Any]] = None
  ) -> bool:
    """Update the inspection status for an asset.
    
    Args:
        asset_id: Unique asset identifier
        status: New status value
        inspection_id: Optional inspection ID
        completion_date: Optional completion date
        month_year: Month-year string (YYYY-MM), defaults to current month
        metadata: Optional metadata to merge with existing
        
    Returns:
        True if update was successful, False otherwise
    """
    if month_year is None:
      month_year = self._get_current_month_year()
    
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
      existing_metadata = await self._get_asset_metadata(
        asset_id, month_year
      )
      existing_metadata.update(metadata)
      update_fields.append("metadata = ?")
      update_values.append(json.dumps(existing_metadata))
    
    # Validate fields against whitelist to prevent SQL injection
    safe_fields = self._validate_and_sanitize_fields(update_fields)
    
    # Add WHERE clause values
    update_values.extend([asset_id, month_year])
    
    async with aiosqlite.connect(self.db_path) as db:
      # Construct parameterized query with validated fields
      async with db.execute(f"""
          UPDATE asset_inspections
          SET {', '.join(safe_fields)}
          WHERE asset_id = ? AND month_year = ?
      """, update_values) as cursor:
        await db.commit()
        return cursor.rowcount > 0
  
  async def mark_asset_completed(
      self,
      asset_id: str,
      inspection_id: str,
      inspector: str = "SafetyCulture Agent",
      month_year: Optional[str] = None,
      metadata: Optional[Dict[str, Any]] = None
  ) -> bool:
    """Mark an asset inspection as completed.
    
    Args:
        asset_id: Unique asset identifier
        inspection_id: Inspection ID
        inspector: Inspector name
        month_year: Month-year string (YYYY-MM), defaults to current month
        metadata: Optional metadata
        
    Returns:
        True if update was successful, False otherwise
    """
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
    """Mark an asset inspection as failed.
    
    Args:
        asset_id: Unique asset identifier
        error_message: Error message explaining the failure
        month_year: Month-year string (YYYY-MM), defaults to current month
        
    Returns:
        True if update was successful, False otherwise
    """
    metadata = {
      "error_message": error_message,
      "failed_at": datetime.now().isoformat()
    }
    return await self.update_inspection_status(
        asset_id=asset_id,
        status='failed',
        month_year=month_year,
        metadata=metadata
    )