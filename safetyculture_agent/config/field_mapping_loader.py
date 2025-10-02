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

"""Field mapping loader for SafetyCulture API field IDs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..exceptions import SafetyCultureValidationError


class FieldMappingLoader:
  """Loads and manages SafetyCulture field ID mappings from YAML config.

  This class provides a centralized way to access SafetyCulture API field IDs,
  which are otherwise hardcoded as UUIDs throughout the codebase. It supports
  caching for performance and template-specific field overrides.

  Attributes:
    _mappings: Cached field mappings loaded from YAML configuration
    _config_path: Path to the field mappings YAML file
  """

  def __init__(self, config_path: Optional[str] = None):
    """Initialize the field mapping loader.

    Args:
      config_path: Path to field_mappings.yaml. If None, uses default path
        relative to this module.
    """
    self._mappings: Optional[Dict[str, Any]] = None
    
    if config_path is None:
      # Default to field_mappings.yaml in the same directory as this module
      module_dir = Path(__file__).parent
      config_path = str(module_dir / 'field_mappings.yaml')
    
    self._config_path = config_path

  def _load_mappings(self) -> None:
    """Load field mappings from YAML configuration file.

    This method is called lazily on first access and caches the result.

    Raises:
      SafetyCultureValidationError: If config file cannot be loaded or parsed
    """
    if self._mappings is not None:
      return  # Already loaded and cached

    if not os.path.exists(self._config_path):
      raise SafetyCultureValidationError(
          f"Field mappings configuration file not found: "
          f"{self._config_path}"
      )

    try:
      with open(self._config_path, 'r', encoding='utf-8') as f:
        self._mappings = yaml.safe_load(f)
    except yaml.YAMLError as e:
      raise SafetyCultureValidationError(
          f"Failed to parse field mappings YAML: {e}"
      ) from e
    except OSError as e:
      raise SafetyCultureValidationError(
          f"Failed to read field mappings file: {e}"
      ) from e

    # Validate required structure
    if not isinstance(self._mappings, dict):
      raise SafetyCultureValidationError(
          "Field mappings YAML must contain a dictionary at root level"
      )

    if 'safetyculture_fields' not in self._mappings:
      raise SafetyCultureValidationError(
          "Field mappings YAML must contain 'safetyculture_fields' key"
      )

  def get_field_id(
      self,
      field_name: str,
      template_name: Optional[str] = None
  ) -> str:
    """Get the UUID field ID for a given field name.

    This method first checks for template-specific overrides, then falls back
    to standard field mappings.

    Args:
      field_name: Name of the field (e.g., 'standard_title', 'inspector_name')
      template_name: Optional template name for template-specific overrides

    Returns:
      UUID string for the requested field

    Raises:
      SafetyCultureValidationError: If field name is not found in mappings
    """
    self._load_mappings()

    # Check for template-specific override first
    if template_name:
      overrides = self._mappings.get('template_overrides', {})
      template_override = overrides.get(template_name, {})
      if field_name in template_override:
        return template_override[field_name]

    # Fall back to standard fields
    standard_fields = self._mappings['safetyculture_fields']
    if field_name not in standard_fields:
      raise SafetyCultureValidationError(
          f"Field '{field_name}' not found in field mappings. "
          f"Available fields: {', '.join(standard_fields.keys())}"
      )

    return standard_fields[field_name]

  def get_all_fields(self) -> Dict[str, str]:
    """Get all standard field mappings as a dictionary.

    Returns:
      Dictionary mapping field names to UUID strings

    Raises:
      SafetyCultureValidationError: If mappings cannot be loaded
    """
    self._load_mappings()
    return dict(self._mappings['safetyculture_fields'])

  def reload(self) -> None:
    """Force reload of field mappings from configuration file.

    Use this to pick up changes to the YAML file without restarting the
    application.

    Raises:
      SafetyCultureValidationError: If config file cannot be loaded or parsed
    """
    self._mappings = None
    self._load_mappings()


# Singleton instance for global access
_field_loader: Optional[FieldMappingLoader] = None


def get_field_loader(
    config_path: Optional[str] = None
) -> FieldMappingLoader:
  """Get the singleton FieldMappingLoader instance.

  Args:
    config_path: Path to field_mappings.yaml. Only used on first call.

  Returns:
    Singleton FieldMappingLoader instance
  """
  global _field_loader
  
  if _field_loader is None:
    _field_loader = FieldMappingLoader(config_path)
  
  return _field_loader