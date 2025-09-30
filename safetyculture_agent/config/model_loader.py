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

"""Configuration loader for model providers.

This module provides functionality to load and merge model configurations from
YAML files with environment variable override support. It handles both base
configuration (models.yaml) and optional user overrides (models.local.yaml).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml

from .model_config import (
    ModelConfiguration,
    ModelDefinition,
    ProviderConfig,
    RetryOptions,
)


class ModelConfigLoader:
  """Loads and manages model provider configuration.

  This class handles loading configuration from YAML files, merging overrides,
  and resolving model aliases to specific provider/model combinations.

  Example:
    >>> loader = ModelConfigLoader()
    >>> config = loader.load()
    >>> provider = loader.get_provider('gemini')
    >>> provider_name, model_name = loader.resolve_alias('coordinator')
  """

  def __init__(
      self,
      config_path: Optional[Path] = None,
      allow_overrides: bool = True
  ):
    """Initialize the configuration loader.

    Args:
      config_path: Path to models.yaml. Defaults to models.yaml in the same
        directory as this module.
      allow_overrides: If True, loads models.local.yaml if present to
        override base configuration.
    """
    self._base_path = config_path or Path(__file__).parent / 'models.yaml'
    self._override_path = self._base_path.parent / 'models.local.yaml'
    self._allow_overrides = allow_overrides
    self._config: Optional[ModelConfiguration] = None

  def load(self) -> ModelConfiguration:
    """Load configuration with environment variable interpolation.

    Loads the base models.yaml configuration and optionally merges with
    models.local.yaml if present. Also applies environment variable overrides.

    Returns:
      Fully loaded and merged ModelConfiguration.

    Raises:
      ValueError: If models.yaml is not found or cannot be parsed.
    """
    # Load base configuration
    if not self._base_path.exists():
      raise ValueError(
          f"Configuration file not found: {self._base_path}"
      )

    with open(self._base_path, encoding='utf-8') as f:
      config_dict = yaml.safe_load(f)

    # Apply local overrides if present
    if self._allow_overrides and self._override_path.exists():
      with open(self._override_path, encoding='utf-8') as f:
        override_dict = yaml.safe_load(f)
        config_dict = self._merge_configs(config_dict, override_dict)

    # Parse into dataclass
    self._config = self._parse_config(config_dict)

    # Apply environment variable overrides
    self._apply_env_overrides()

    return self._config

  def get_provider(
      self,
      provider_name: Optional[str] = None
  ) -> ProviderConfig:
    """Get provider configuration with environment override support.

    Checks the MODEL_PROVIDER environment variable first, then falls back
    to the provided name or the default provider from configuration.

    Args:
      provider_name: Name of the provider to retrieve. If None, uses default.

    Returns:
      The requested ProviderConfig.

    Raises:
      ValueError: If the provider name is unknown.
    """
    if not self._config:
      self.load()

    # At this point, config is guaranteed to be loaded
    assert self._config is not None

    # Check environment variable override
    env_provider = os.getenv('MODEL_PROVIDER')
    provider_name = (
        env_provider or provider_name or self._config.default_provider
    )

    if provider_name not in self._config.providers:
      raise ValueError(
          f"Unknown provider: {provider_name}. "
          f"Available: {', '.join(self._config.providers.keys())}"
      )

    return self._config.providers[provider_name]

  def resolve_alias(self, alias: str) -> tuple[str, str]:
    """Resolve model alias to (provider, model) tuple.

    Resolves aliases defined in the configuration to their full
    provider:model specification.

    Args:
      alias: The alias to resolve (e.g., 'coordinator', 'gemini:fast').

    Returns:
      Tuple of (provider_name, model_name).

    Raises:
      ValueError: If the alias is unknown or format is invalid.

    Example:
      >>> loader = ModelConfigLoader()
      >>> loader.load()
      >>> provider, model = loader.resolve_alias('coordinator')
      >>> print(f"{provider}:{model}")  # 'gemini:fast'
    """
    if not self._config:
      self.load()

    # At this point, config is guaranteed to be loaded
    assert self._config is not None

    # Check if it's a defined alias
    if alias in self._config.model_aliases:
      full_name = self._config.model_aliases[alias]
      if '/' in full_name:
        provider, model = full_name.split('/', 1)
      else:
        raise ValueError(
            f"Invalid alias format '{full_name}'. "
            f"Expected 'provider/model'."
        )
      return provider, model

    # Not an alias, might be provider/model or provider:model format
    if '/' in alias:
      parts = alias.split('/', 1)
      return parts[0], parts[1]
    if ':' in alias:
      parts = alias.split(':', 1)
      return parts[0], parts[1]

    raise ValueError(
        f"Unknown alias or invalid format: '{alias}'. "
        f"Expected format: 'alias', 'provider/model', or 'provider:model'."
    )

  def _merge_configs(
      self,
      base: dict[str, Any],
      override: dict[str, Any]
  ) -> dict[str, Any]:
    """Deep merge two configuration dictionaries.

    Recursively merges override into base. For nested dictionaries, this
    performs a deep merge rather than replacement.

    Args:
      base: Base configuration dictionary.
      override: Override configuration dictionary.

    Returns:
      Merged configuration dictionary.
    """
    result = base.copy()

    for key, value in override.items():
      if key in result and isinstance(result[key], dict) and isinstance(
          value, dict
      ):
        # Recursively merge nested dictionaries
        result[key] = self._merge_configs(result[key], value)
      else:
        # Override the value
        result[key] = value

    return result

  def _parse_config(self, config_dict: dict[str, Any]) -> ModelConfiguration:
    """Parse configuration dictionary into dataclass structure.

    Args:
      config_dict: Raw configuration dictionary from YAML.

    Returns:
      Parsed ModelConfiguration instance.

    Raises:
      ValueError: If configuration structure is invalid.
    """
    providers = {}

    for provider_name, provider_data in config_dict.get('providers',
                                                         {}).items():
      # Parse retry options if present
      retry_options = None
      if 'retry' in provider_data.get('models', {}).get(
          provider_data.get('default_model', ''), {}
      ):
        retry_data = provider_data['models'][
            provider_data['default_model']
        ]['retry']
        retry_options = RetryOptions(**retry_data)

      # Parse model definitions
      models = {}
      for model_name, model_data in provider_data.get('models', {}).items():
        # Parse retry options for this model
        model_retry = None
        if 'retry' in model_data:
          model_retry = RetryOptions(**model_data['retry'])

        models[model_name] = ModelDefinition(
            model_id=model_data['model_id'],
            display_name=model_data['display_name'],
            temperature=model_data.get('temperature', 0.7),
            max_output_tokens=model_data.get('max_output_tokens', 8192),
            top_p=model_data.get('top_p', 0.95),
            top_k=model_data.get('top_k', 40),
            retry=model_retry or RetryOptions(),
            description=model_data.get('description'),
        )

      # Parse provider configuration
      providers[provider_name] = ProviderConfig(
          name=provider_data['name'],
          implementation=provider_data['implementation'],
          enabled=provider_data.get('enabled', True),
          models=models,
          environment_vars=provider_data.get('environment_vars', {}),
          default_model=provider_data.get('default_model'),
          region=provider_data.get('region'),
          project_id=provider_data.get('project_id'),
          endpoint=provider_data.get('endpoint'),
      )

    return ModelConfiguration(
        providers=providers,
        model_aliases=config_dict.get('model_aliases', {}),
        default_provider=config_dict.get('default_provider', 'gemini'),
    )

  def _apply_env_overrides(self):
    """Apply environment variable overrides to configuration.

    Checks for the MODEL_PROVIDER environment variable and applies it
    as an override to the default provider if set.
    """
    if not self._config:
      return

    # Apply MODEL_PROVIDER environment variable
    env_provider = os.getenv('MODEL_PROVIDER')
    if env_provider and env_provider in self._config.providers:
      # The get_provider method already handles this, so we don't need
      # to modify the config itself. This method is kept for potential
      # future environment variable overrides.
      pass