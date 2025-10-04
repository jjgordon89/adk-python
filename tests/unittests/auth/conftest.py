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

"""Shared test fixtures for auth tests."""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional
from unittest.mock import AsyncMock, Mock

from authlib.oauth2.rfc6749 import OAuth2Token
from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlowImplicit
from fastapi.openapi.models import OAuthFlows
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.auth.auth_credential import OAuth2Auth
from google.adk.auth.auth_credential import ServiceAccount
from google.adk.auth.auth_credential import ServiceAccountCredential
from google.adk.auth.auth_schemes import AuthScheme
from google.adk.auth.auth_schemes import AuthSchemeType
from google.adk.auth.auth_schemes import ExtendedOAuth2
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.auth_tool import AuthConfig
from google.adk.auth.oauth2_discovery import AuthorizationServerMetadata
import pytest


# ===================================================================
# OAuth2 Token Fixtures
# ===================================================================


@pytest.fixture
def oauth2_token():
  """Provide a basic OAuth2 token for testing.
  
  Returns:
      OAuth2Token: Token with access_token, refresh_token, and expiry
  """
  return OAuth2Token({
    'access_token': 'test_access_token',
    'refresh_token': 'test_refresh_token',
    'expires_at': int(time.time()) + 3600,
    'expires_in': 3600,
    'token_type': 'Bearer',
  })


@pytest.fixture
def oauth2_token_factory():
  """Factory for creating custom OAuth2 tokens.
  
  Returns:
      Callable: Function that creates OAuth2Token instances
  """
  def _create_token(
    access_token: str = 'test_access_token',
    refresh_token: Optional[str] = 'test_refresh_token',
    expires_in: int = 3600,
    token_type: str = 'Bearer',
    **kwargs: Any
  ) -> OAuth2Token:
    """Create an OAuth2 token with specified parameters.
    
    Args:
        access_token: Access token string
        refresh_token: Refresh token string (optional)
        expires_in: Token expiry time in seconds
        token_type: Token type (usually 'Bearer')
        **kwargs: Additional token parameters
    
    Returns:
        OAuth2Token: Configured OAuth2 token
    """
    token_dict = {
      'access_token': access_token,
      'expires_at': int(time.time()) + expires_in,
      'expires_in': expires_in,
      'token_type': token_type,
    }
    if refresh_token:
      token_dict['refresh_token'] = refresh_token
    token_dict.update(kwargs)
    return OAuth2Token(token_dict)
  
  return _create_token


# ===================================================================
# Auth Credential Fixtures
# ===================================================================


@pytest.fixture
def oauth2_credential():
  """Provide OAuth2 credential for testing.
  
  Returns:
      AuthCredential: OAuth2 credential with client credentials
  """
  return AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
      client_id='test_client_id',
      client_secret='test_client_secret',
      redirect_uri='https://example.com/callback',
    ),
  )


@pytest.fixture
def service_account_credential():
  """Provide service account credential for testing.
  
  Returns:
      AuthCredential: Service account credential with key file data
  """
  return AuthCredential(
    auth_type=AuthCredentialTypes.SERVICE_ACCOUNT,
    service_account=ServiceAccount(
      service_account_credential=ServiceAccountCredential(
        type='service_account',
        project_id='test_project',
        private_key_id='test_key_id',
        private_key=(
          '-----BEGIN PRIVATE KEY-----\ntest_key\n-----END PRIVATE'
          ' KEY-----\n'
        ),
        client_email='test@test.iam.gserviceaccount.com',
        client_id='test_client_id',
        auth_uri='https://accounts.google.com/o/oauth2/auth',
        token_uri='https://oauth2.googleapis.com/token',
        auth_provider_x509_cert_url=(
          'https://www.googleapis.com/oauth2/v1/certs'
        ),
        client_x509_cert_url=(
          'https://www.googleapis.com/robot/v1/metadata/x509/'
          'test%40test.iam.gserviceaccount.com'
        ),
        universe_domain='googleapis.com',
      ),
      scopes=['https://www.googleapis.com/auth/cloud-platform'],
    ),
  )


@pytest.fixture
def api_key_credential():
  """Provide API key credential for testing.
  
  Returns:
      AuthCredential: API key credential
  """
  return AuthCredential(
    auth_type=AuthCredentialTypes.API_KEY,
    api_key='test_api_key',
  )


@pytest.fixture
def http_bearer_credential():
  """Provide HTTP bearer credential for testing.
  
  Returns:
      AuthCredential: HTTP bearer credential
  """
  return AuthCredential(
    auth_type=AuthCredentialTypes.HTTP,
    http=Mock(),
  )


# ===================================================================
# Auth Scheme Fixtures
# ===================================================================


@pytest.fixture
def oauth2_auth_scheme():
  """Provide OAuth2 auth scheme for testing.
  
  Returns:
      AuthScheme: OAuth2 authentication scheme
  """
  auth_scheme = Mock(spec=AuthScheme)
  auth_scheme.type_ = AuthSchemeType.oauth2
  return auth_scheme


@pytest.fixture
def openid_auth_scheme():
  """Provide OpenID Connect auth scheme for testing.
  
  Returns:
      AuthScheme: OpenID Connect authentication scheme
  """
  auth_scheme = Mock(spec=AuthScheme)
  auth_scheme.type_ = AuthSchemeType.openIdConnect
  return auth_scheme


@pytest.fixture
def bearer_auth_scheme():
  """Provide bearer auth scheme for testing.
  
  Returns:
      AuthScheme: HTTP bearer authentication scheme
  """
  auth_scheme = Mock(spec=AuthScheme)
  auth_scheme.type_ = AuthSchemeType.http
  return auth_scheme


@pytest.fixture
def extended_oauth2_scheme():
  """Provide ExtendedOAuth2 scheme with empty endpoints.
  
  Returns:
      ExtendedOAuth2: OAuth2 scheme requiring endpoint discovery
  """
  return ExtendedOAuth2(
    issuer_url='https://auth.example.com',
    flows=OAuthFlows(
      authorizationCode=OAuthFlowAuthorizationCode(
        authorizationUrl='',
        tokenUrl='',
      )
    ),
  )


@pytest.fixture
def implicit_oauth2_scheme():
  """Provide OAuth2 scheme with implicit flow.
  
  Returns:
      OAuth2: OAuth2 scheme with implicit flow configured
  """
  return OAuth2(
    flows=OAuthFlows(
      implicit=OAuthFlowImplicit(
        authorizationUrl='https://auth.example.com/authorize'
      )
    )
  )


@pytest.fixture
def openid_connect_scheme():
  """Provide OpenID Connect scheme with config.
  
  Returns:
      OpenIdConnectWithConfig: OpenID Connect scheme with endpoints
  """
  return OpenIdConnectWithConfig(
    openIdConnectUrl='https://example.com/.well-known/openid_configuration',
    authorization_endpoint='https://example.com/auth',
    token_endpoint='https://example.com/token',
    scopes=['openid', 'profile', 'email'],
  )


# ===================================================================
# Auth Config Fixtures
# ===================================================================


@pytest.fixture
def mock_auth_config():
  """Provide mock auth configuration.
  
  Returns:
      Mock: Mock AuthConfig with basic attributes
  """
  config = Mock(spec=AuthConfig)
  config.raw_auth_credential = None
  config.exchanged_auth_credential = None
  config.auth_scheme = Mock()
  return config


@pytest.fixture
def auth_config_factory():
  """Factory for creating custom auth configurations.
  
  Returns:
      Callable: Function that creates AuthConfig mocks
  """
  def _create_config(
    raw_credential: Optional[AuthCredential] = None,
    exchanged_credential: Optional[AuthCredential] = None,
    auth_scheme: Optional[AuthScheme] = None,
  ) -> Mock:
    """Create a mock auth configuration.
    
    Args:
        raw_credential: Raw authentication credential
        exchanged_credential: Exchanged/processed credential
        auth_scheme: Authentication scheme
    
    Returns:
        Mock: Configured AuthConfig mock
    """
    config = Mock(spec=AuthConfig)
    config.raw_auth_credential = raw_credential
    config.exchanged_auth_credential = exchanged_credential
    config.auth_scheme = auth_scheme or Mock()
    return config
  
  return _create_config


# ===================================================================
# Authorization Server Metadata Fixtures
# ===================================================================


@pytest.fixture
def auth_server_metadata():
  """Provide authorization server metadata for testing.
  
  Returns:
      AuthorizationServerMetadata: Server metadata with endpoints
  """
  return AuthorizationServerMetadata(
    issuer='https://auth.example.com',
    authorization_endpoint='https://auth.example.com/authorize',
    token_endpoint='https://auth.example.com/token',
    scopes_supported=['read', 'write', 'openid'],
  )


# ===================================================================
# Credentials Manager Fixtures
# ===================================================================


@pytest.fixture
def mock_credentials_manager():
  """Provide mock credentials manager.
  
  Returns:
      AsyncMock: Mock credentials manager with common methods
  """
  manager = AsyncMock()
  manager.get_auth_credential = AsyncMock(return_value=None)
  manager.request_credential = AsyncMock()
  manager._validate_credential = AsyncMock()
  manager._refresh_credential = AsyncMock(return_value=(None, False))
  manager._exchange_credential = AsyncMock(return_value=(None, False))
  return manager


# ===================================================================
# Token Response Fixtures
# ===================================================================


@pytest.fixture
def mock_token_response_factory():
  """Factory for creating mock token responses.
  
  Returns:
      Callable: Function that creates token response dictionaries
  """
  def _create_response(
    access_token: str = 'new_access_token',
    refresh_token: Optional[str] = 'new_refresh_token',
    expires_in: int = 3600,
    token_type: str = 'Bearer',
    scope: Optional[str] = None,
    error: Optional[str] = None,
  ) -> Dict[str, Any]:
    """Create a mock token response.
    
    Args:
        access_token: Access token string
        refresh_token: Refresh token string (optional)
        expires_in: Token expiry time in seconds
        token_type: Token type
        scope: Token scope string
        error: Error message if request failed
    
    Returns:
        Dict[str, Any]: Token response dictionary
    """
    if error:
      return {'error': error, 'error_description': 'Token request failed'}
    
    response = {
      'access_token': access_token,
      'token_type': token_type,
      'expires_in': expires_in,
    }
    if refresh_token:
      response['refresh_token'] = refresh_token
    if scope:
      response['scope'] = scope
    return response
  
  return _create_response


# ===================================================================
# OAuth Client Fixtures
# ===================================================================


@pytest.fixture
def mock_oauth_client():
  """Provide mock OAuth client for testing.
  
  Returns:
      Mock: Mock OAuth client with common methods
  """
  client = Mock()
  client.client_id = 'test_client_id'
  client.client_secret = 'test_client_secret'
  client.fetch_token = Mock(
    return_value={
      'access_token': 'test_token',
      'token_type': 'Bearer',
      'expires_in': 3600,
    }
  )
  return client


# ===================================================================
# Callback Context Fixtures
# ===================================================================


@pytest.fixture
def mock_callback_context():
  """Provide mock callback context for auth operations.
  
  Returns:
      Mock: Mock callback context with auth-related methods
  """
  context = Mock()
  context.request_credential = Mock()
  context.load_credential = AsyncMock(return_value=None)
  context.save_credential = AsyncMock()
  context._invocation_context = Mock()
  context._invocation_context.credential_service = None
  return context


# ===================================================================
# Auth Handler Fixtures
# ===================================================================


@pytest.fixture
def mock_auth_handler():
  """Provide mock auth handler for testing.
  
  Returns:
      AsyncMock: Mock auth handler with process methods
  """
  handler = AsyncMock()
  handler.process_request = AsyncMock()
  handler.process_response = AsyncMock()
  handler.get_auth_header = Mock(
    return_value={'Authorization': 'Bearer test_token'}
  )
  return handler


# ===================================================================
# Refresher/Exchanger Fixtures
# ===================================================================


@pytest.fixture
def mock_refresher():
  """Provide mock credential refresher.
  
  Returns:
      Mock: Mock refresher with is_refresh_needed and refresh methods
  """
  refresher = Mock()
  refresher.is_refresh_needed = AsyncMock(return_value=False)
  refresher.refresh = AsyncMock(return_value=Mock(spec=AuthCredential))
  return refresher


@pytest.fixture
def mock_exchanger():
  """Provide mock credential exchanger.
  
  Returns:
      Mock: Mock exchanger with exchange method
  """
  exchanger = Mock()
  exchanger.exchange = AsyncMock(return_value=Mock(spec=AuthCredential))
  return exchanger