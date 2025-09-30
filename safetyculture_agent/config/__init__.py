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

"""Configuration module for SafetyCulture ADK agent.

This module provides configuration management for model providers and API
settings. It includes classes for loading YAML configurations, creating
model instances, and managing provider-specific settings.
"""

from __future__ import annotations

from .model_config import (
    ModelConfiguration,
    ModelDefinition,
    ProviderConfig,
    RetryOptions,
)
from .model_factory import ModelFactory
from .model_loader import ModelConfigLoader

__all__ = [
    'ModelConfiguration',
    'ModelDefinition',
    'ProviderConfig',
    'RetryOptions',
    'ModelConfigLoader',
    'ModelFactory',
]
