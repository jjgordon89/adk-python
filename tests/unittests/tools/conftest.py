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

"""Shared test fixtures for tools tests."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional
from unittest.mock import AsyncMock, Mock

from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.sessions.in_memory_session_service import (
  InMemorySessionService
)
from google.adk.sessions.session import Session
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import pytest


# ===================================================================
# Tool Context Fixtures
# ===================================================================


@pytest.fixture
async def tool_context():
  """Provide a ToolContext instance for testing.
  
  Creates a complete tool context with session, agent, and invocation
  context. Use this when you need a realistic tool execution environment.
  
  Returns:
      ToolContext: Configured tool context ready for testing
  """
  session_service = InMemorySessionService()
  session = await session_service.create_session(
    app_name='test_app', user_id='test_user'
  )
  agent = SequentialAgent(name='test_agent')
  invocation_context = InvocationContext(
    invocation_id='test_invocation_id',
    agent=agent,
    session=session,
    session_service=session_service,
  )
  return ToolContext(invocation_context)


@pytest.fixture
def mock_tool_context():
  """Provide a mocked ToolContext for lightweight testing.
  
  Use this when you need a tool context but don't require full
  functionality. Faster than creating a real context.
  
  Returns:
      Mock: Mocked ToolContext with basic attributes
  """
  mock_invocation_context = Mock(spec=InvocationContext)
  mock_invocation_context.session = Mock(spec=Session)
  mock_invocation_context.session.state = Mock()
  return ToolContext(invocation_context=mock_invocation_context)


# ===================================================================
# Function Declaration Fixtures
# ===================================================================


@pytest.fixture
def simple_function_declaration():
  """Provide a simple function declaration for testing.
  
  Returns:
      types.FunctionDeclaration: Basic function with string parameter
  """
  return types.FunctionDeclaration(
    name='test_function',
    description='Test function description',
    parameters=types.Schema(
      type=types.Type.OBJECT,
      properties={
        'test_arg': types.Schema(type=types.Type.STRING),
      },
    ),
  )


@pytest.fixture
def complex_function_declaration():
  """Provide a complex function declaration for testing.
  
  Includes nested objects, arrays, and multiple parameter types.
  
  Returns:
      types.FunctionDeclaration: Complex function with various parameters
  """
  return types.FunctionDeclaration(
    name='complex_function',
    description='Complex test function',
    parameters=types.Schema(
      type=types.Type.OBJECT,
      properties={
        'string_arg': types.Schema(type=types.Type.STRING),
        'array_arg': types.Schema(
          type=types.Type.ARRAY,
          items=types.Schema(type=types.Type.STRING),
        ),
        'nested_arg': types.Schema(
          type=types.Type.OBJECT,
          properties={
            'nested_key1': types.Schema(type=types.Type.STRING),
            'nested_key2': types.Schema(type=types.Type.INTEGER),
          },
          required=['nested_key1'],
        ),
      },
      required=['string_arg', 'nested_arg'],
    ),
  )


@pytest.fixture
def function_declaration_factory():
  """Factory for creating custom function declarations.
  
  Returns:
      Callable: Function that creates FunctionDeclaration instances
      
  Example:
      func_decl = function_declaration_factory(
          name='my_func',
          properties={'arg1': types.Schema(type=types.Type.STRING)}
      )
  """
  def _create_declaration(
    name: str = 'test_function',
    description: str = 'Test function',
    properties: Optional[Dict[str, types.Schema]] = None,
    required: Optional[list[str]] = None,
  ) -> types.FunctionDeclaration:
    """Create a function declaration with specified parameters.
    
    Args:
        name: Function name
        description: Function description
        properties: Parameter properties dictionary
        required: List of required parameter names
    
    Returns:
        types.FunctionDeclaration: Configured function declaration
    """
    if properties is None:
      properties = {'arg': types.Schema(type=types.Type.STRING)}
    
    return types.FunctionDeclaration(
      name=name,
      description=description,
      parameters=types.Schema(
        type=types.Type.OBJECT,
        properties=properties,
        required=required or [],
      ),
    )
  
  return _create_declaration


# ===================================================================
# Mock Tool Fixtures
# ===================================================================


@pytest.fixture
def mock_async_tool():
  """Provide an AsyncMock tool with execute method.
  
  Use this for testing tool execution without actual implementation.
  
  Returns:
      AsyncMock: Tool mock with async execute method
  """
  tool = AsyncMock()
  tool.execute = AsyncMock(return_value={'result': 'success'})
  tool.name = 'mock_tool'
  tool.description = 'Mock tool for testing'
  return tool


@pytest.fixture
def mock_tool_response_factory():
  """Factory for creating mock tool execution responses.
  
  Returns:
      Callable: Function that creates tool response dictionaries
      
  Example:
      response = mock_tool_response_factory(
          success=True,
          data={'key': 'value'}
      )
  """
  def _create_response(
    success: bool = True,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
  ) -> Dict[str, Any]:
    """Create a mock tool response.
    
    Args:
        success: Whether the tool execution succeeded
        data: Response data dictionary
        error: Error message if success is False
    
    Returns:
        Dict[str, Any]: Tool response dictionary
    """
    if success:
      return {'success': True, 'data': data or {}}
    else:
      return {'success': False, 'error': error or 'Tool execution failed'}
  
  return _create_response


# ===================================================================
# Credential Manager Fixtures
# ===================================================================


@pytest.fixture
def mock_credentials():
  """Provide mock Google credentials.
  
  Returns:
      Mock: Mock credentials object with common attributes
  """
  creds = Mock()
  creds.token = 'test_token'
  creds.valid = True
  creds.expired = False
  creds.refresh_token = 'test_refresh_token'
  return creds


@pytest.fixture
def mock_credentials_manager():
  """Provide a mock credentials manager.
  
  Returns:
      AsyncMock: Mock credentials manager with get_credentials method
  """
  manager = AsyncMock()
  mock_creds = Mock()
  mock_creds.token = 'test_token'
  manager.get_credentials = AsyncMock(return_value=mock_creds)
  return manager


# ===================================================================
# Tool Config Fixtures
# ===================================================================


@pytest.fixture
def basic_tool_config():
  """Provide basic tool configuration dictionary.
  
  Returns:
      Dict[str, Any]: Basic tool configuration
  """
  return {
    'name': 'test_tool',
    'description': 'Test tool description',
    'enabled': True,
    'timeout': 30,
  }


@pytest.fixture
def tool_config_factory():
  """Factory for creating custom tool configurations.
  
  Returns:
      Callable: Function that creates tool config dictionaries
  """
  def _create_config(
    name: str = 'test_tool',
    description: str = 'Test tool',
    enabled: bool = True,
    timeout: int = 30,
    **kwargs: Any
  ) -> Dict[str, Any]:
    """Create a tool configuration dictionary.
    
    Args:
        name: Tool name
        description: Tool description
        enabled: Whether tool is enabled
        timeout: Execution timeout in seconds
        **kwargs: Additional configuration parameters
    
    Returns:
        Dict[str, Any]: Tool configuration dictionary
    """
    config = {
      'name': name,
      'description': description,
      'enabled': enabled,
      'timeout': timeout,
    }
    config.update(kwargs)
    return config
  
  return _create_config


# ===================================================================
# API Client Mock Fixtures
# ===================================================================


@pytest.fixture
def mock_api_client():
  """Provide a generic mocked API client.
  
  Use this for tools that interact with external APIs.
  
  Returns:
      AsyncMock: Mock API client with common methods
  """
  client = AsyncMock()
  client.get = AsyncMock(return_value={'status': 'success'})
  client.post = AsyncMock(return_value={'status': 'success'})
  client.put = AsyncMock(return_value={'status': 'success'})
  client.delete = AsyncMock(return_value={'status': 'success'})
  return client


@pytest.fixture
def mock_api_response_factory():
  """Factory for creating mock API responses.
  
  Returns:
      Callable: Function that creates API response objects
  """
  def _create_response(
    status_code: int = 200,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
  ) -> Mock:
    """Create a mock API response.
    
    Args:
        status_code: HTTP status code
        data: Response data dictionary
        headers: Response headers
    
    Returns:
        Mock: Mock response object
    """
    response = Mock()
    response.status_code = status_code
    response.json = Mock(return_value=data or {})
    response.headers = headers or {}
    response.ok = 200 <= status_code < 300
    return response
  
  return _create_response