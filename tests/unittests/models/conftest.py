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

"""Shared test fixtures for models tests."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, Mock

from google.adk.models.llm_request import LlmRequest
from google.genai import types
from litellm.types.utils import Choices
from litellm.types.utils import Delta
from litellm.types.utils import ModelResponse
from litellm.types.utils import StreamingChoices
import pytest


# ===================================================================
# LLM Response Fixtures
# ===================================================================


@pytest.fixture
def mock_llm_response():
  """Factory for creating mock LLM responses.
  
  Returns:
      Callable: Function that creates GenerateContentResponse instances
  """
  def _create_response(
    text: str = 'Test response',
    role: str = 'model',
    function_calls: Optional[List[Dict[str, Any]]] = None,
  ) -> types.GenerateContentResponse:
    """Create a mock LLM response.
    
    Args:
        text: Response text content
        role: Response role (model, user, etc.)
        function_calls: List of function call dictionaries
    
    Returns:
        types.GenerateContentResponse: Mock LLM response
    """
    parts = []
    if text:
      parts.append(types.Part.from_text(text=text))
    
    if function_calls:
      for fc in function_calls:
        part = types.Part.from_function_call(
          name=fc.get('name', 'test_function'),
          args=fc.get('args', {}),
        )
        if 'id' in fc:
          part.function_call.id = fc['id']
        parts.append(part)
    
    content = types.Content(role=role, parts=parts)
    return types.GenerateContentResponse(content=content)
  
  return _create_response


@pytest.fixture
def simple_llm_response(mock_llm_response):
  """Provide a simple text LLM response.
  
  Args:
      mock_llm_response: Factory fixture for creating responses
  
  Returns:
      types.GenerateContentResponse: Simple text response
  """
  return mock_llm_response(text='Hello, how can I help you?')


@pytest.fixture
def function_call_response(mock_llm_response):
  """Provide an LLM response with function call.
  
  Args:
      mock_llm_response: Factory fixture for creating responses
  
  Returns:
      types.GenerateContentResponse: Response with function call
  """
  return mock_llm_response(
    text='Calling function',
    function_calls=[{
      'name': 'test_function',
      'args': {'arg1': 'value1'},
      'id': 'test_call_id',
    }]
  )


# ===================================================================
# LLM Request Fixtures
# ===================================================================


@pytest.fixture
def simple_llm_request():
  """Provide a simple LLM request.
  
  Returns:
      LlmRequest: Basic LLM request with user message
  """
  return LlmRequest(
    contents=[
      types.Content(
        role='user',
        parts=[types.Part.from_text(text='Test prompt')]
      )
    ]
  )


@pytest.fixture
def llm_request_with_system_instruction():
  """Provide LLM request with system instruction.
  
  Returns:
      LlmRequest: LLM request with system instruction
  """
  return LlmRequest(
    contents=[
      types.Content(
        role='user',
        parts=[types.Part.from_text(text='Test prompt')]
      )
    ],
    config=types.GenerateContentConfig(
      system_instruction='You are a helpful assistant.'
    )
  )


@pytest.fixture
def llm_request_with_tools():
  """Provide LLM request with tool declarations.
  
  Returns:
      LlmRequest: LLM request with function tools
  """
  return LlmRequest(
    contents=[
      types.Content(
        role='user',
        parts=[types.Part.from_text(text='Test prompt')]
      )
    ],
    config=types.GenerateContentConfig(
      tools=[
        types.Tool(
          function_declarations=[
            types.FunctionDeclaration(
              name='test_function',
              description='Test function description',
              parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                  'arg1': types.Schema(type=types.Type.STRING),
                },
              ),
            )
          ]
        )
      ]
    )
  )


# ===================================================================
# Gemini Connection Fixtures
# ===================================================================


@pytest.fixture
def mock_gemini_session():
  """Provide mock Gemini session for testing.
  
  Returns:
      AsyncMock: Mock Gemini session with send and close methods
  """
  session = AsyncMock()
  session.send = AsyncMock()
  session.close = AsyncMock()
  return session


@pytest.fixture
def mock_gemini_connection(mock_gemini_session):
  """Provide mock Gemini LLM connection.
  
  Args:
      mock_gemini_session: Mock Gemini session fixture
  
  Returns:
      Mock: Mock GeminiLlmConnection instance
  """
  from google.adk.models.gemini_llm_connection import GeminiLlmConnection
  return GeminiLlmConnection(mock_gemini_session)


# ===================================================================
# Generate Content Mock Fixtures
# ===================================================================


@pytest.fixture
def mock_generate_content():
  """Provide mock generate_content method.
  
  Returns:
      AsyncMock: Mock generate_content that returns a response
  """
  mock_response = types.GenerateContentResponse(
    content=types.Content(
      role='model',
      parts=[types.Part.from_text(text='Mock response')]
    )
  )
  return AsyncMock(return_value=mock_response)


@pytest.fixture
def mock_generate_content_stream():
  """Provide mock streaming generate_content.
  
  Returns:
      AsyncMock: Mock that yields streaming responses
  """
  async def _stream():
    responses = [
      types.GenerateContentResponse(
        content=types.Content(
          role='model',
          parts=[types.Part.from_text(text='Chunk 1 ')]
        )
      ),
      types.GenerateContentResponse(
        content=types.Content(
          role='model',
          parts=[types.Part.from_text(text='Chunk 2')]
        )
      ),
    ]
    for response in responses:
      yield response
  
  return _stream


# ===================================================================
# Streaming Response Fixtures
# ===================================================================


@pytest.fixture
def mock_streaming_response_factory():
  """Factory for creating mock streaming responses.
  
  Returns:
      Callable: Function that creates lists of streaming chunks
  """
  def _create_stream(
    text_chunks: Optional[List[str]] = None,
    function_calls: Optional[List[Dict[str, Any]]] = None,
  ) -> List[types.GenerateContentResponse]:
    """Create a stream of mock responses.
    
    Args:
        text_chunks: List of text chunks to stream
        function_calls: List of function call dicts to include
    
    Returns:
        List[types.GenerateContentResponse]: Streaming responses
    """
    responses = []
    
    if text_chunks:
      for chunk in text_chunks:
        responses.append(
          types.GenerateContentResponse(
            content=types.Content(
              role='model',
              parts=[types.Part.from_text(text=chunk)]
            )
          )
        )
    
    if function_calls:
      for fc in function_calls:
        part = types.Part.from_function_call(
          name=fc.get('name', 'test_function'),
          args=fc.get('args', {}),
        )
        if 'id' in fc:
          part.function_call.id = fc['id']
        responses.append(
          types.GenerateContentResponse(
            content=types.Content(role='model', parts=[part])
          )
        )
    
    return responses
  
  return _create_stream


# ===================================================================
# LiteLLM Response Fixtures
# ===================================================================


@pytest.fixture
def mock_litellm_response():
  """Provide mock LiteLLM response.
  
  Returns:
      ModelResponse: Mock LiteLLM ModelResponse
  """
  return ModelResponse(
    choices=[
      Choices(
        message={
          'role': 'assistant',
          'content': 'Test response from LiteLLM',
        }
      )
    ]
  )


@pytest.fixture
def mock_litellm_streaming_response():
  """Provide mock LiteLLM streaming response.
  
  Returns:
      List[ModelResponse]: List of streaming model responses
  """
  return [
    ModelResponse(
      choices=[
        StreamingChoices(
          finish_reason=None,
          delta=Delta(
            role='assistant',
            content='Chunk 1 ',
          ),
        )
      ]
    ),
    ModelResponse(
      choices=[
        StreamingChoices(
          finish_reason=None,
          delta=Delta(
            role='assistant',
            content='Chunk 2',
          ),
        )
      ]
    ),
    ModelResponse(
      choices=[
        StreamingChoices(
          finish_reason='stop',
        )
      ]
    ),
  ]


# ===================================================================
# Model Config Fixtures
# ===================================================================


@pytest.fixture
def basic_generate_config():
  """Provide basic generation config.
  
  Returns:
      types.GenerateContentConfig: Basic generation configuration
  """
  return types.GenerateContentConfig(
    temperature=0.7,
    max_output_tokens=1024,
    top_p=0.9,
    top_k=40,
  )


@pytest.fixture
def generate_config_factory():
  """Factory for creating custom generation configs.
  
  Returns:
      Callable: Function that creates GenerateContentConfig instances
  """
  def _create_config(
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    system_instruction: Optional[str] = None,
    **kwargs: Any
  ) -> types.GenerateContentConfig:
    """Create a generation config with specified parameters.
    
    Args:
        temperature: Sampling temperature
        max_output_tokens: Maximum output tokens
        top_p: Top-p sampling parameter
        top_k: Top-k sampling parameter
        system_instruction: System instruction text
        **kwargs: Additional config parameters
    
    Returns:
        types.GenerateContentConfig: Configured generation config
    """
    config_dict = {}
    if temperature is not None:
      config_dict['temperature'] = temperature
    if max_output_tokens is not None:
      config_dict['max_output_tokens'] = max_output_tokens
    if top_p is not None:
      config_dict['top_p'] = top_p
    if top_k is not None:
      config_dict['top_k'] = top_k
    if system_instruction is not None:
      config_dict['system_instruction'] = system_instruction
    config_dict.update(kwargs)
    return types.GenerateContentConfig(**config_dict)
  
  return _create_config


# ===================================================================
# Content Fixtures
# ===================================================================


@pytest.fixture
def user_content():
  """Provide user content for testing.
  
  Returns:
      types.Content: User content with text part
  """
  return types.Content(
    role='user',
    parts=[types.Part.from_text(text='Hello')]
  )


@pytest.fixture
def model_content():
  """Provide model content for testing.
  
  Returns:
      types.Content: Model content with text part
  """
  return types.Content(
    role='model',
    parts=[types.Part.from_text(text='Hello! How can I help you?')]
  )


@pytest.fixture
def multimodal_content():
  """Provide multimodal content for testing.
  
  Returns:
      types.Content: Content with text and image parts
  """
  return types.Content(
    role='user',
    parts=[
      types.Part.from_text(text='What is in this image?'),
      types.Part.from_bytes(data=b'fake_image_data', mime_type='image/png'),
    ]
  )


# ===================================================================
# Usage Metadata Fixtures
# ===================================================================


@pytest.fixture
def mock_usage_metadata():
  """Provide mock usage metadata.
  
  Returns:
      types.UsageMetadata: Mock usage metadata with token counts
  """
  return types.UsageMetadata(
    prompt_token_count=10,
    candidates_token_count=20,
    total_token_count=30,
  )


@pytest.fixture
def usage_metadata_factory():
  """Factory for creating custom usage metadata.
  
  Returns:
      Callable: Function that creates UsageMetadata instances
  """
  def _create_metadata(
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
  ) -> types.UsageMetadata:
    """Create usage metadata with specified token counts.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
    
    Returns:
        types.UsageMetadata: Usage metadata instance
    """
    return types.UsageMetadata(
      prompt_token_count=prompt_tokens,
      candidates_token_count=completion_tokens,
      total_token_count=prompt_tokens + completion_tokens,
    )
  
  return _create_metadata