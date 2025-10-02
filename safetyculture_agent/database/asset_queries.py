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

import csv
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)


class AssetQueries:
  """Query service for asset inspection data.
  
  Provides search, filtering, and retrieval operations for asset
  inspection records. Handles data retention and archival.
  
  Attributes:
      db_path: Path to SQLite database file
      retention_days: Number of days to retain records
  """
  
  def __init__(self, db_path: str, retention_days: int = 365):
    """Initialize asset queries service.
    
    Args:
        db_path: Path to SQLite database file
        retention_days: Days to retain records (default: 365)
    """
    self.db_path = Path(db_path)
    self.retention_days = retention_days
    logger.info(
      f"AssetQueries initialized (retention: {retention_days} days)"
    )
  
  def _get_current_month_year(self) -> str:
    """Get current month-year string in YYYY-MM format."""
    return datetime.now().strftime("%Y-%m")
  
  async def cleanup_old_records(
      self,
      archive: bool = True
  ) -> Dict[str, int]:
    """Archive and delete records older than retention period.
    
    This method moves old records to an archive file before deleting them
    from the active database to comply with data retention policies.
    
    Args:
        archive: If True, archive records before deletion. If False,
                 delete only.
        
    Returns:
        Dictionary with counts:
            - archived: Number of records archived
            - deleted: Number of records deleted
            - errors: Number of errors encountered
        
    Raises:
        SafetyCultureDatabaseError: If cleanup fails
    """
    from ..exceptions import SafetyCultureDatabaseError
    
    try:
      # Calculate cutoff date
      cutoff_date = datetime.now() - timedelta(days=self.retention_days)
      cutoff_str = cutoff_date.strftime('%Y-%m-%d')
      
      logger.info(
        f"Starting cleanup of records older than {cutoff_str} "
        f"({self.retention_days} days)"
      )
      
      async with aiosqlite.connect(self.db_path) as db:
        db.row_factory = aiosqlite.Row
        
        # Get count of records to be deleted
        async with db.execute("""
            SELECT COUNT(*) as count
            FROM asset_inspections
            WHERE created_at < ?
        """, (cutoff_str,)) as cursor:
          row = await cursor.fetchone()
          count_to_delete = row[0]
        
        if count_to_delete == 0:
          logger.info("No old records found for cleanup")
          return {'archived': 0, 'deleted': 0, 'errors': 0}
        
        archived_count = 0
        
        # Archive records if requested
        if archive:
          archived_count = await self._archive_records(db, cutoff_str)
        
        # Delete old records
        async with db.execute("""
            DELETE FROM asset_inspections
            WHERE created_at < ?
        """, (cutoff_str,)) as cursor:
          deleted_count = cursor.rowcount
        
        await db.commit()
      
      logger.info(
        f"Cleanup complete: archived={archived_count}, "
        f"deleted={deleted_count}"
      )
      
      return {
        'archived': archived_count,
        'deleted': deleted_count,
        'errors': 0
      }
      
    except aiosqlite.Error as e:
      raise SafetyCultureDatabaseError(
        f"Cleanup operation failed: {e}"
      ) from e
  
  async def _archive_records(
      self,
      db: aiosqlite.Connection,
      cutoff_date: str
  ) -> int:
    """Archive old records to CSV file.
    
    Args:
        db: Async database connection
        cutoff_date: Cutoff date string (YYYY-MM-DD)
        
    Returns:
        Number of records archived
    """
    # Create archives directory if it doesn't exist
    archive_dir = self.db_path.parent / 'archives'
    archive_dir.mkdir(exist_ok=True)
    
    # Generate archive filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_file = archive_dir / f'asset_inspections_{timestamp}.csv'
    
    # Fetch old records
    async with db.execute("""
        SELECT *
        FROM asset_inspections
        WHERE created_at < ?
        ORDER BY created_at
    """, (cutoff_date,)) as cursor:
      rows = await cursor.fetchall()
    
    if not rows:
      return 0
    
    # Get column names from cursor description
    async with db.execute("SELECT * FROM asset_inspections LIMIT 0") as cur:
      columns = [description[0] for description in cur.description]
    
    # Write to CSV archive (synchronous file I/O)
    with open(archive_file, 'w', newline='', encoding='utf-8') as f:
      writer = csv.writer(f)
      writer.writerow(columns)
      writer.writerows(rows)
    
    logger.info(f"Archived {len(rows)} records to {archive_file}")
    
    return len(rows)
  
  async def get_retention_stats(self) -> Dict[str, Any]:
    """Get statistics about data retention.
    
    Returns:
        Dictionary with:
            - total_records: Total number of records
            - old_records: Number of records exceeding retention period
            - oldest_record_date: Date of oldest record
            - retention_days: Configured retention period
    """
    async with aiosqlite.connect(self.db_path) as db:
      # Get total count
      async with db.execute(
          "SELECT COUNT(*) as count FROM asset_inspections"
      ) as cursor:
        row = await cursor.fetchone()
        total_count = row[0]
      
      # Get count of old records
      cutoff_date = datetime.now() - timedelta(days=self.retention_days)
      async with db.execute("""
          SELECT COUNT(*) as count
          FROM asset_inspections
          WHERE created_at < ?
      """, (cutoff_date.strftime('%Y-%m-%d'),)) as cursor:
        row = await cursor.fetchone()
        old_count = row[0]
      
      # Get oldest record date
      async with db.execute("""
          SELECT MIN(created_at) as oldest
          FROM asset_inspections
      """) as cursor:
        row = await cursor.fetchone()
        oldest_date = row[0] if row and row[0] else None
      
      return {
        'total_records': total_count,
        'old_records': old_count,
        'oldest_record_date': oldest_date,
        'retention_days': self.retention_days
      }