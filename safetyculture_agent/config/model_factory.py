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

"""Model factory for creating configured model instances.

This module provides a factory class that instantiates model instances based
on configuration. It supports both native Gemini models and LiteLLM-based
providers with proper environment validation and parameter handling.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm

try:
  from google.genai import types
except ImportError:
  # Fallback for type hints if google.genai not available
  types = None  # type: ignore

from .model_config import ModelDefinition, ProviderConfig
from .model_loader import ModelConfigLoader


class ModelFactory:
  """Factory for creating model instances from configuration.

  This class handles the instantiation of both native Gemini models and
  LiteLLM-based models, with proper environment variable validation and
  configuration parameter handling.

  Example:
    >>> factory = ModelFactory()
    >>> # Create model using alias
    >>> model = factory.create_model('coordinator')
    >>> # Create model using provider:model format
    >>> model = factory.create_model('gemini:fast')
    >>> # Create model using default configuration
    >>> model = factory.create_model()
  """

  def __init__(self, config_loader: Optional[ModelConfigLoader] = None) -> None:
    """Initialize model factory.

    Args:
      config_loader: Configuration loader instance. If None, creates a
        default ModelConfigLoader.
    """
    self._loader = config_loader or ModelConfigLoader()
    # Ensure configuration is loaded
    if not self._loader._config:
      self._loader.load()

  def create_model(
      self,
      model_spec: Optional[str] = None,
      **kwargs: Any
  ) -> Gemini | LiteLlm:
    """Create a model instance from specification.

    This method resolves the model specification to a concrete provider and
    model, validates environment variables, and instantiates the appropriate
    model class with configured parameters.

    Args:
      model_spec: Model specification in one of these formats:
        - None: Uses default provider and model from configuration
        - 'alias': Uses a defined alias (e.g., 'coordinator', 'local_dev')
        - 'provider:model': Direct specification (e.g., 'gemini:fast')
        - 'provider/model': Alternative format (e.g., 'ollama/llama3')
        - 'provider': Uses provider with its default model
      **kwargs: Additional arguments passed to model constructor. These
        override any configured parameters.

    Returns:
      Model instance (Gemini for native, LiteLlm for others).

    Raises:
      ValueError: If model specification is invalid or environment variables
        are missing.

    Example:
      >>> factory = ModelFactory()
      >>> # Using alias
      >>> coordinator = factory.create_model('coordinator')
      >>> # Using direct specification with overrides
      >>> custom = factory.create_model(
      ...     'gemini:pro',
      ...     temperature=0.3
      ... )
    """
    # Ensure config is loaded
    assert self._loader._config is not None

    # Resolve model specification to provider and model names
    if model_spec:
      # Check if it's an alias or contains separator
      if ':' in model_spec or '/' in model_spec:
        provider_name, model_name = self._loader.resolve_alias(model_spec)
      elif model_spec in self._loader._config.model_aliases:
        provider_name, model_name = self._loader.resolve_alias(model_spec)
      else:
        # Treat as provider name, use default model
        provider = self._loader.get_provider(model_spec)
        provider_name = model_spec
        model_name = provider.default_model
        if not model_name:
          raise ValueError(
              f"Provider '{provider_name}' has no default model configured"
          )
    else:
      # Use defaults
      provider = self._loader.get_provider()
      provider_name = self._loader._config.default_provider
      model_name = provider.default_model
      if not model_name:
        raise ValueError(
            f"Default provider '{provider_name}' has no default model "
            f"configured"
        )

    # Get provider configuration
    provider = self._loader.get_provider(provider_name)

    # Validate environment variables and apply defaults
    self._validate_environment(provider)
    self._apply_env_defaults(provider)

    # Create model instance based on implementation type
    if provider.implementation == 'native':
      return self._create_native_model(provider, model_name, **kwargs)
    else:  # litellm
      return self._create_litellm_model(provider, model_name, **kwargs)

  def _create_native_model(
      self,
      provider: ProviderConfig,
      model_name: str,
      **kwargs: Any
  ) -> Gemini:
    """Create native Gemini model instance.

    Args:
      provider: Provider configuration.
      model_name: Name of the model variant to create.
      **kwargs: Additional arguments for model constructor.

    Returns:
      Configured Gemini model instance.

    Raises:
      ValueError: If model_name is not found in provider configuration.
    """
    if model_name not in provider.models:
      raise ValueError(
          f"Model '{model_name}' not found in provider '{provider.name}'. "
          f"Available: {', '.join(provider.models.keys())}"
      )

    model_def = provider.models[model_name]

    # Build generation config from model definition
    generation_config = {
        'temperature': model_def.temperature,
        'max_output_tokens': model_def.max_output_tokens,
        'top_p': model_def.top_p,
        'top_k': model_def.top_k,
    }

    # Override with any kwargs
    generation_config.update(kwargs.pop('generation_config', {}))

    # Build retry options if configured
    retry_options = None
    if model_def.retry and types is not None:
      retry_options = types.HttpOptions(
          retry=types.HttpRetryOptions(
              max_retries=model_def.retry.max_retries,
              initial_delay=model_def.retry.initial_delay,
              max_delay=model_def.retry.max_delay,
              exponential_base=model_def.retry.exponential_base,
          )
      )

    # Prepare Gemini constructor arguments
    gemini_kwargs = {
        'model': model_def.model_id,
        'generation_config': generation_config,
    }

    if retry_options:
      gemini_kwargs['http_options'] = retry_options

    # Add any additional kwargs
    gemini_kwargs.update(kwargs)

    return Gemini(**gemini_kwargs)

  def _create_litellm_model(
      self,
      provider: ProviderConfig,
      model_name: str,
      **kwargs: Any
  ) -> LiteLlm:
    """Create LiteLLM model instance.

    Args:
      provider: Provider configuration.
      model_name: Name of the model variant to create.
      **kwargs: Additional arguments for model constructor.

    Returns:
      Configured LiteLlm model instance.

    Raises:
      ValueError: If model_name is not found in provider configuration.
    """
    if model_name not in provider.models:
      raise ValueError(
          f"Model '{model_name}' not found in provider '{provider.name}'. "
          f"Available: {', '.join(provider.models.keys())}"
      )

    model_def = provider.models[model_name]

    # Build full model string: format varies by provider
    # For most LiteLLM providers, format is: provider_name/model_id
    full_model_name = f"{provider.name}/{model_def.model_id}"

    # Build generation config from model definition
    generation_config = {
        'temperature': model_def.temperature,
        'max_output_tokens': model_def.max_output_tokens,
        'top_p': model_def.top_p,
        'top_k': model_def.top_k,
    }

    # Override with any kwargs
    generation_config.update(kwargs.pop('generation_config', {}))

    # Prepare LiteLLM constructor arguments
    litellm_kwargs = {
        'model': full_model_name,
        'generation_config': generation_config,
    }

    # Add any additional kwargs
    litellm_kwargs.update(kwargs)

    return LiteLlm(**litellm_kwargs)

  def _validate_environment(self, provider: ProviderConfig) -> None:
    """Validate required environment variables are set.

    Args:
      provider: Provider configuration to validate.

    Raises:
      ValueError: If any required environment variables are missing.
    """
    missing = []

    for var_name, var_value in provider.environment_vars.items():
      # Check if this is a required variable (value is 'required')
      if var_value == 'required':
        if not os.getenv(var_name):
          missing.append(var_name)

    if missing:
      raise ValueError(
          f"Missing required environment variables for provider "
          f"'{provider.name}': {', '.join(missing)}. "
          f"Please set these variables in your .env file or environment."
      )

  def _apply_env_defaults(self, provider: ProviderConfig) -> None:
    """Apply default environment variable values if not set.

    This method sets default values for environment variables that have
    defaults defined in the configuration but are not already set.

    Args:
      provider: Provider configuration with potential defaults.
    """
    for var_name, var_value in provider.environment_vars.items():
      # If variable is not required and has a default value, apply it
      if var_value != 'required' and not os.getenv(var_name):
        # The value in the config is the default
        os.environ[var_name] = var_value