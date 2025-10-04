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

from unittest.mock import Mock
from unittest.mock import patch

from google.adk.auth.exchanger.base_credential_exchanger import CredentialExchangError
from google.adk.auth.exchanger.oauth2_credential_exchanger import OAuth2CredentialExchanger
import pytest


class TestOAuth2CredentialExchanger:
  """Test suite for OAuth2CredentialExchanger."""

  @pytest.mark.asyncio
  async def test_exchange_with_existing_token(
      self, oauth2_credential, openid_connect_scheme
  ):
    """Test exchange method when access token already exists."""
    oauth2_credential.oauth2.access_token = "existing_token"

    exchanger = OAuth2CredentialExchanger()
    result = await exchanger.exchange(
        oauth2_credential, openid_connect_scheme
    )

    # Should return the same credential since access token already exists
    assert result == oauth2_credential
    assert result.oauth2.access_token == "existing_token"

  @patch("google.adk.auth.oauth2_credential_util.OAuth2Session")
  @pytest.mark.asyncio
  async def test_exchange_success(
      self,
      mock_oauth2_session,
      oauth2_credential,
      openid_connect_scheme,
      oauth2_token_factory,
  ):
    """Test successful token exchange."""
    # Setup mock
    mock_client = Mock()
    mock_oauth2_session.return_value = mock_client
    mock_tokens = oauth2_token_factory(
        access_token="new_access_token",
        refresh_token="new_refresh_token",
    )
    mock_client.fetch_token.return_value = mock_tokens

    oauth2_credential.oauth2.auth_response_uri = (
        "https://example.com/callback?code=auth_code"
    )
    oauth2_credential.oauth2.auth_code = "auth_code"

    exchanger = OAuth2CredentialExchanger()
    result = await exchanger.exchange(
        oauth2_credential, openid_connect_scheme
    )

    # Verify token exchange was successful
    assert result.oauth2.access_token == "new_access_token"
    assert result.oauth2.refresh_token == "new_refresh_token"
    mock_client.fetch_token.assert_called_once()

  @pytest.mark.asyncio
  async def test_exchange_missing_auth_scheme(self, oauth2_credential):
    """Test exchange with missing auth_scheme raises ValueError."""
    exchanger = OAuth2CredentialExchanger()
    try:
      await exchanger.exchange(oauth2_credential, None)
      assert False, "Should have raised ValueError"
    except CredentialExchangError as e:
      assert "auth_scheme is required" in str(e)

  @patch("google.adk.auth.oauth2_credential_util.OAuth2Session")
  @pytest.mark.asyncio
  async def test_exchange_no_session(
      self, mock_oauth2_session, oauth2_credential, openid_connect_scheme
  ):
    """Test exchange when OAuth2Session cannot be created."""
    # Mock to return None for create_oauth2_session
    mock_oauth2_session.return_value = None

    # Missing client_secret to trigger session creation failure
    oauth2_credential.oauth2.client_secret = None

    exchanger = OAuth2CredentialExchanger()
    result = await exchanger.exchange(
        oauth2_credential, openid_connect_scheme
    )

    # Should return original credential when session creation fails
    assert result == oauth2_credential
    assert result.oauth2.access_token is None

  @patch("google.adk.auth.oauth2_credential_util.OAuth2Session")
  @pytest.mark.asyncio
  async def test_exchange_fetch_token_failure(
      self, mock_oauth2_session, oauth2_credential, openid_connect_scheme
  ):
    """Test exchange when fetch_token fails."""
    # Setup mock to raise exception during fetch_token
    mock_client = Mock()
    mock_oauth2_session.return_value = mock_client
    mock_client.fetch_token.side_effect = Exception("Token fetch failed")

    oauth2_credential.oauth2.auth_response_uri = (
        "https://example.com/callback?code=auth_code"
    )
    oauth2_credential.oauth2.auth_code = "auth_code"

    exchanger = OAuth2CredentialExchanger()
    result = await exchanger.exchange(
        oauth2_credential, openid_connect_scheme
    )

    # Should return original credential when fetch_token fails
    assert result == oauth2_credential
    assert result.oauth2.access_token is None
    mock_client.fetch_token.assert_called_once()

  @pytest.mark.asyncio
  async def test_exchange_authlib_not_available(
      self, oauth2_credential, openid_connect_scheme
  ):
    """Test exchange when authlib is not available."""
    oauth2_credential.oauth2.auth_response_uri = (
        "https://example.com/callback?code=auth_code"
    )
    oauth2_credential.oauth2.auth_code = "auth_code"

    exchanger = OAuth2CredentialExchanger()

    # Mock AUTHLIB_AVAILABLE to False
    with patch(
        "google.adk.auth.exchanger.oauth2_credential_exchanger.AUTHLIB_AVAILABLE",
        False,
    ):
      result = await exchanger.exchange(
          oauth2_credential, openid_connect_scheme
      )

    # Should return original credential when authlib is not available
    assert result == oauth2_credential
    assert result.oauth2.access_token is None
