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

"""Model provider configuration dataclasses.

This module defines the configuration structure for model providers in the
SafetyCulture ADK agent. It supports multiple providers (Gemini, Llama,
Nvidia, Ollama) with both native and LiteLLM implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class RetryOptions:
  """Configuration for model retry behavior.

  Attributes:
    max_retries: Maximum number of retry attempts for failed requests.
    initial_delay: Initial delay in seconds before the first retry.
    max_delay: Maximum delay in seconds between retries.
    exponential_base: Base for exponential backoff calculation.
  """
  max_retries: int = 3
  initial_delay: float = 1.0
  max_delay: float = 60.0
  exponential_base: float = 2.0


@dataclass
class ModelDefinition:
  """Configuration for a single model variant.

  Attributes:
    model_id: The identifier used to reference this model in code.
    display_name: Human-readable name for the model.
    temperature: Sampling temperature for response generation (0.0-2.0).
    max_output_tokens: Maximum number of tokens in the model's response.
    top_p: Nucleus sampling parameter (0.0-1.0).
    top_k: Top-k sampling parameter.
    retry: Retry configuration for this model.
    description: Optional description of the model's purpose or
      characteristics.
  """
  model_id: str
  display_name: str
  temperature: float = 0.7
  max_output_tokens: int = 8192
  top_p: float = 0.95
  top_k: int = 40
  retry: RetryOptions = field(default_factory=RetryOptions)
  description: Optional[str] = None


@dataclass
class ProviderConfig:
  """Configuration for a model provider.

  Attributes:
    name: The name of the provider (e.g., "gemini", "llama").
    implementation: The implementation type, either "native" for direct
      integration or "litellm" for LiteLLM proxy.
    enabled: Whether this provider is currently enabled.
    models: Dictionary mapping model variant names to their definitions.
    environment_vars: Dictionary of required environment variables for this
      provider.
    default_model: The default model variant to use if none is specified.
    region: Optional cloud region for the provider.
    project_id: Optional Google Cloud project ID.
    endpoint: Optional custom endpoint URL for the provider.
  """
  name: str
  implementation: Literal['native', 'litellm']
  enabled: bool
  models: dict[str, ModelDefinition] = field(default_factory=dict)
  environment_vars: dict[str, str] = field(default_factory=dict)
  default_model: Optional[str] = None
  region: Optional[str] = None
  project_id: Optional[str] = None
  endpoint: Optional[str] = None


@dataclass
class ModelConfiguration:
  """Root configuration object for all model providers.

  Attributes:
    providers: Dictionary mapping provider names to their configurations.
    model_aliases: Dictionary mapping semantic aliases (e.g., "coordinator")
      to specific provider/model combinations.
    default_provider: The default provider to use if none is specified.
  """
  providers: dict[str, ProviderConfig] = field(default_factory=dict)
  model_aliases: dict[str, str] = field(default_factory=dict)
  default_provider: Optional[str] = None