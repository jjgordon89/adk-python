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

"""Facade for coordinating asset inspection database operations.

This module provides a unified interface to asset tracking functionality
by coordinating between AssetRepository, MonthlySummaryService, and
AssetQueries. It maintains backward compatibility with the original API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .asset_queries import AssetQueries
from .asset_repository import AssetRepository
from .monthly_summary_service import (
    AssetInspectionRecord,
    MonthlySummaryService,
)

logger = logging.getLogger(__name__)

# Database retention constants
DEFAULT_RETENTION_DAYS = 365  # Default data retention period in days


class AssetTracker:
  """Facade for coordinating asset inspection operations.
  
  Provides a unified interface to asset tracking by delegating to
  specialized services: AssetRepository for CRUD, MonthlySummaryService
  for aggregations, and AssetQueries for searches.
  
  This maintains backward compatibility with the original AssetTracker API.
  
  Attributes:
      repository: Core CRUD operations
      summary_service: Monthly summaries and statistics
      queries: Search and query operations
      db_path: Path to SQLite database file
  """
  
  def __init__(
      self,
      db_path: str = "safetyculture_assets.db",
      retention_days: int = DEFAULT_RETENTION_DAYS
  ):
    """Initialize asset tracker.
    
    Args:
        db_path: Path to SQLite database file
        retention_days: Days to retain records (default: 365)
    """
    self.db_path = db_path
    
    # Initialize specialized services
    self.repository = AssetRepository(db_path)
    self.summary_service = MonthlySummaryService(db_path)
    self.queries = AssetQueries(db_path, retention_days)
    
    logger.info(f"AssetTracker initialized with db: {db_path}")
  
  def _get_current_month_year(self) -> str:
    """Get current month-year string in YYYY-MM format.
    
    This is a public helper method for backward compatibility with
    database_tools.py that needs to access current month-year.
    
    Returns:
        Current month-year string in YYYY-MM format
    """
    return self.repository._get_current_month_year()
  
  async def initialize_database(self) -> None:
    """Initialize database schema asynchronously.
    
    Raises:
        SafetyCultureDatabaseError: If initialization fails
    """
    await self.repository.initialize()
  
  # Delegate to repository for CRUD operations
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
    return await self.repository.check_asset_completed_this_month(
        asset_id, month_year
    )
  
  async def register_asset(
      self,
      asset_id: str,
      month_year: str,
      asset_name: str,
      location: str
  ) -> bool:
    """Register asset inspection with race condition protection.
    
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
    return await self.repository.register_asset(
        asset_id, month_year, asset_name, location
    )
  
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
    return await self.repository.get_asset_inspection_status(
        asset_id, month_year
    )
  
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
    return await self.repository.register_asset_for_inspection(
        asset_id, asset_name, asset_type, location, template_id,
        template_name, inspector, month_year, metadata
    )
  
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
    return await self.repository.update_inspection_status(
        asset_id, status, inspection_id, completion_date,
        month_year, metadata
    )
  
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
    return await self.repository.mark_asset_completed(
        asset_id, inspection_id, inspector, month_year, metadata
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
    return await self.repository.mark_asset_failed(
        asset_id, error_message, month_year
    )
  
  # Delegate to summary service for aggregations
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
    return await self.summary_service.get_monthly_summary(month_year)
  
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
    return await self.summary_service.get_completed_assets(month_year)
  
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
    return await self.summary_service.get_pending_assets(month_year, limit)
  
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
    return await self.summary_service.export_monthly_report(month_year)
  
  # Delegate to queries for data retention operations
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
    return await self.queries.cleanup_old_records(archive)
  
  async def get_retention_stats(self) -> Dict[str, Any]:
    """Get statistics about data retention.
    
    Returns:
        Dictionary with:
            - total_records: Total number of records
            - old_records: Number of records exceeding retention period
            - oldest_record_date: Date of oldest record
            - retention_days: Configured retention period
    """
    return await self.queries.get_retention_stats()
