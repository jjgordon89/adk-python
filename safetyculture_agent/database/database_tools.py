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
from typing import Any, Dict, List, Optional

from google.adk.tools.function_tool import FunctionTool

from .asset_tracker import AssetTracker
from ..exceptions import (
  SafetyCultureDatabaseError,
  SafetyCultureValidationError,
)
from ..utils.secure_header_manager import SecureHeaderManager

logger = logging.getLogger(__name__)

# Shared header manager for error sanitization
_header_manager = SecureHeaderManager()


# Global asset tracker instance
_asset_tracker = AssetTracker()


async def initialize_asset_database() -> str:
    """
    Initialize the asset tracking database with required tables and indexes.
    
    Returns:
        Status message indicating success or failure
    """
    try:
        await _asset_tracker.initialize_database()
        return "Asset tracking database initialized successfully"
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Database initialization failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Database initialization failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid database parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Unexpected error initializing database: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Unexpected error initializing database: {safe_error}"
        ) from e


async def check_asset_completion_status(asset_id: str, month_year: Optional[str] = None) -> str:
    """
    Check if an asset has already been inspected this month to prevent duplicates.
    
    Args:
        asset_id: ID of the asset to check
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string with completion status and details
    """
    try:
        is_completed = await _asset_tracker.check_asset_completed_this_month(asset_id, month_year)
        current_status = await _asset_tracker.get_asset_inspection_status(asset_id, month_year)
        
        result = {
            "asset_id": asset_id,
            "month_year": month_year or _asset_tracker._get_current_month_year(),
            "is_completed": is_completed,
            "current_status": current_status,
            "can_create_inspection": not is_completed and current_status != 'in_progress'
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Asset status check failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Asset status check failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid asset ID or parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Unexpected error checking asset status: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Unexpected error checking asset status: {safe_error}"
        ) from e


async def register_asset_for_monthly_inspection(
    asset_id: str,
    asset_name: str,
    asset_type: str,
    location: str,
    template_id: str,
    template_name: str,
    inspector: str = "SafetyCulture Agent",
    month_year: Optional[str] = None
) -> str:
    """
    Register an asset for inspection in the tracking database.
    
    Args:
        asset_id: Unique asset identifier
        asset_name: Human-readable asset name
        asset_type: Type/category of the asset
        location: Physical location of the asset
        template_id: ID of the inspection template to use
        template_name: Name of the inspection template
        inspector: Name of the inspector (defaults to "SafetyCulture Agent")
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string indicating success or failure with details
    """
    try:
        success = await _asset_tracker.register_asset_for_inspection(
            asset_id=asset_id,
            asset_name=asset_name,
            asset_type=asset_type,
            location=location,
            template_id=template_id,
            template_name=template_name,
            inspector=inspector,
            month_year=month_year
        )
        
        result = {
            "success": success,
            "asset_id": asset_id,
            "month_year": month_year or _asset_tracker._get_current_month_year(),
            "message": "Asset registered for inspection" if success else "Asset already completed or registered this month"
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Asset registration failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Asset registration failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid asset registration parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Unexpected error registering asset: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Unexpected error registering asset: {safe_error}"
        ) from e


async def update_asset_inspection_status(
    asset_id: str,
    status: str,
    inspection_id: Optional[str] = None,
    month_year: Optional[str] = None
) -> str:
    """
    Update the inspection status for an asset.
    
    Args:
        asset_id: ID of the asset
        status: New status ('pending', 'in_progress', 'completed', 'failed')
        inspection_id: SafetyCulture inspection ID (optional)
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string indicating success or failure
    """
    try:
        success = await _asset_tracker.update_inspection_status(
            asset_id=asset_id,
            status=status,
            inspection_id=inspection_id,
            month_year=month_year
        )
        
        result = {
            "success": success,
            "asset_id": asset_id,
            "new_status": status,
            "month_year": month_year or _asset_tracker._get_current_month_year(),
            "message": "Status updated successfully" if success else "Asset not found or update failed"
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Asset status update failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Asset status update failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid status update parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Unexpected error updating asset status: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Unexpected error updating asset status: {safe_error}"
        ) from e


async def mark_asset_inspection_completed(
    asset_id: str,
    inspection_id: str,
    inspector: str = "SafetyCulture Agent",
    month_year: Optional[str] = None
) -> str:
    """
    Mark an asset inspection as completed.
    
    Args:
        asset_id: ID of the asset
        inspection_id: SafetyCulture inspection ID
        inspector: Name of the inspector
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string indicating success or failure
    """
    try:
        success = await _asset_tracker.mark_asset_completed(
            asset_id=asset_id,
            inspection_id=inspection_id,
            inspector=inspector,
            month_year=month_year
        )
        
        result = {
            "success": success,
            "asset_id": asset_id,
            "inspection_id": inspection_id,
            "status": "completed",
            "month_year": month_year or _asset_tracker._get_current_month_year(),
            "message": "Asset marked as completed" if success else "Failed to mark asset as completed"
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Asset completion marking failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Asset completion marking failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid completion parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Unexpected error marking asset completed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Unexpected error marking asset completed: {safe_error}"
        ) from e


async def get_pending_assets_for_inspection(
    month_year: Optional[str] = None,
    limit: Optional[int] = None
) -> str:
    """
    Get all pending asset inspections for a month.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
        limit: Maximum number of assets to return (optional)
    
    Returns:
        JSON string with list of pending assets
    """
    try:
        pending_assets = await _asset_tracker.get_pending_assets(month_year, limit)
        
        result = {
            "month_year": month_year or _asset_tracker._get_current_month_year(),
            "total_pending": len(pending_assets),
            "limit_applied": limit,
            "assets": [
                {
                    "asset_id": asset.asset_id,
                    "asset_name": asset.asset_name,
                    "asset_type": asset.asset_type,
                    "location": asset.location,
                    "template_id": asset.template_id,
                    "template_name": asset.template_name,
                    "created_at": asset.created_at
                }
                for asset in pending_assets
            ]
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Pending assets retrieval failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Pending assets retrieval failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid query parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(
            f"Unexpected error getting pending assets: {safe_error}"
        )
        raise SafetyCultureDatabaseError(
            f"Unexpected error getting pending assets: {safe_error}"
        ) from e


async def get_completed_assets_report(month_year: Optional[str] = None) -> str:
    """
    Get all completed asset inspections for a month.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string with list of completed assets
    """
    try:
        completed_assets = await _asset_tracker.get_completed_assets(month_year)
        
        result = {
            "month_year": month_year or _asset_tracker._get_current_month_year(),
            "total_completed": len(completed_assets),
            "assets": [
                {
                    "asset_id": asset.asset_id,
                    "asset_name": asset.asset_name,
                    "asset_type": asset.asset_type,
                    "location": asset.location,
                    "inspection_id": asset.inspection_id,
                    "completion_date": asset.completion_date,
                    "inspector": asset.inspector
                }
                for asset in completed_assets
            ]
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Completed assets retrieval failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Completed assets retrieval failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid query parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(
            f"Unexpected error getting completed assets: {safe_error}"
        )
        raise SafetyCultureDatabaseError(
            f"Unexpected error getting completed assets: {safe_error}"
        ) from e


async def get_monthly_inspection_summary(month_year: Optional[str] = None) -> str:
    """
    Get monthly inspection summary with statistics and completion rates.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string with monthly summary statistics
    """
    try:
        summary = await _asset_tracker.get_monthly_summary(month_year)
        return json.dumps(summary, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Monthly summary retrieval failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Monthly summary retrieval failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid summary parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(
            f"Unexpected error getting monthly summary: {safe_error}"
        )
        raise SafetyCultureDatabaseError(
            f"Unexpected error getting monthly summary: {safe_error}"
        ) from e


async def export_comprehensive_monthly_report(month_year: Optional[str] = None) -> str:
    """
    Export a comprehensive monthly report with all asset details and statistics.
    
    Args:
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string with comprehensive monthly report
    """
    try:
        report = await _asset_tracker.export_monthly_report(month_year)
        return json.dumps(report, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Monthly report export failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Monthly report export failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid export parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(
            f"Unexpected error exporting monthly report: {safe_error}"
        )
        raise SafetyCultureDatabaseError(
            f"Unexpected error exporting monthly report: {safe_error}"
        ) from e


async def filter_assets_to_prevent_duplicates(
    discovered_assets: List[Dict[str, Any]],
    month_year: Optional[str] = None
) -> str:
    """
    Filter a list of discovered assets to remove those already completed this month.
    
    Args:
        discovered_assets: List of asset dictionaries from SafetyCulture API
        month_year: Month-year string (YYYY-MM), defaults to current month
    
    Returns:
        JSON string with filtered assets that need inspection
    """
    try:
        if month_year is None:
            month_year = _asset_tracker._get_current_month_year()
        
        filtered_assets = []
        already_completed = []
        
        for asset in discovered_assets:
            asset_id = asset.get('id', '')
            if asset_id:
                is_completed = await _asset_tracker.check_asset_completed_this_month(asset_id, month_year)
                if not is_completed:
                    filtered_assets.append(asset)
                else:
                    already_completed.append(asset_id)
        
        result = {
            "month_year": month_year,
            "total_discovered": len(discovered_assets),
            "already_completed": len(already_completed),
            "needs_inspection": len(filtered_assets),
            "completed_asset_ids": already_completed,
            "assets_needing_inspection": filtered_assets
        }
        
        return json.dumps(result, indent=2)
    
    except SafetyCultureDatabaseError as e:
        # Sanitize error message before returning
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Asset filtering failed: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Asset filtering failed: {safe_error}"
        ) from e

    except SafetyCultureValidationError as e:
        # Validation errors are safe to pass through
        logger.warning(f"Invalid filtering parameters: {e}")
        raise

    except Exception as e:
        # Catch-all with sanitization
        safe_error = _header_manager.sanitize_error(e)
        logger.error(f"Unexpected error filtering assets: {safe_error}")
        raise SafetyCultureDatabaseError(
            f"Unexpected error filtering assets: {safe_error}"
        ) from e


# Create FunctionTool instances for database management
DATABASE_TOOLS = [
    FunctionTool(initialize_asset_database),
    FunctionTool(check_asset_completion_status),
    FunctionTool(register_asset_for_monthly_inspection),
    FunctionTool(update_asset_inspection_status),
    FunctionTool(mark_asset_inspection_completed),
    FunctionTool(get_pending_assets_for_inspection),
    FunctionTool(get_completed_assets_report),
    FunctionTool(get_monthly_inspection_summary),
    FunctionTool(export_comprehensive_monthly_report),
    FunctionTool(filter_assets_to_prevent_duplicates)
]

# Export individual functions for direct use
__all__ = [
    'initialize_asset_database',
    'check_asset_completion_status',
    'register_asset_for_monthly_inspection',
    'update_asset_inspection_status',
    'mark_asset_inspection_completed',
    'get_pending_assets_for_inspection',
    'get_completed_assets_report',
    'get_monthly_inspection_summary',
    'export_comprehensive_monthly_report',
    'filter_assets_to_prevent_duplicates',
    'DATABASE_TOOLS'
]
