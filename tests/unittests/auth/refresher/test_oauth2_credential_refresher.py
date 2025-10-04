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

from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.auth.refresher.oauth2_credential_refresher import OAuth2CredentialRefresher
import pytest


class TestOAuth2CredentialRefresher:
  """Test suite for OAuth2CredentialRefresher."""

  @patch("google.adk.auth.refresher.oauth2_credential_refresher.OAuth2Token")
  @pytest.mark.asyncio
  async def test_needs_refresh_token_not_expired(
      self, mock_oauth2_token, oauth2_credential, openid_connect_scheme
  ):
    """Test needs_refresh when token is not expired."""
    mock_token_instance = Mock()
    mock_token_instance.is_expired.return_value = False
    mock_oauth2_token.return_value = mock_token_instance

    oauth2_credential.oauth2.access_token = "existing_token"

    refresher = OAuth2CredentialRefresher()
    needs_refresh = await refresher.is_refresh_needed(
        oauth2_credential, openid_connect_scheme
    )

    assert not needs_refresh

  @patch("google.adk.auth.refresher.oauth2_credential_refresher.OAuth2Token")
  @pytest.mark.asyncio
  async def test_needs_refresh_token_expired(
      self, mock_oauth2_token, oauth2_credential, openid_connect_scheme
  ):
    """Test needs_refresh when token is expired."""
    mock_token_instance = Mock()
    mock_token_instance.is_expired.return_value = True
    mock_oauth2_token.return_value = mock_token_instance

    oauth2_credential.oauth2.access_token = "existing_token"

    refresher = OAuth2CredentialRefresher()
    needs_refresh = await refresher.is_refresh_needed(
        oauth2_credential, openid_connect_scheme
    )

    assert needs_refresh

  @patch("google.adk.auth.oauth2_credential_util.OAuth2Session")
  @patch("google.adk.auth.oauth2_credential_util.OAuth2Token")
  @pytest.mark.asyncio
  async def test_refresh_token_expired_success(
      self,
      mock_oauth2_token,
      mock_oauth2_session,
      oauth2_credential,
      openid_connect_scheme,
      oauth2_token_factory,
  ):
    """Test successful token refresh when token is expired."""
    import time
    
    # Setup mock token
    mock_token_instance = Mock()
    mock_token_instance.is_expired.return_value = True
    mock_oauth2_token.return_value = mock_token_instance

    # Setup mock session
    mock_client = Mock()
    mock_oauth2_session.return_value = mock_client
    mock_tokens = oauth2_token_factory(
        access_token="refreshed_access_token",
        refresh_token="refreshed_refresh_token",
    )
    mock_client.refresh_token.return_value = mock_tokens

    oauth2_credential.oauth2.access_token = "old_token"
    oauth2_credential.oauth2.refresh_token = "old_refresh_token"
    oauth2_credential.oauth2.expires_at = int(time.time()) - 3600  # Expired

    refresher = OAuth2CredentialRefresher()
    result = await refresher.refresh(
        oauth2_credential, openid_connect_scheme
    )

    # Verify token refresh was successful
    assert result.oauth2.access_token == "refreshed_access_token"
    assert result.oauth2.refresh_token == "refreshed_refresh_token"
    mock_client.refresh_token.assert_called_once()

  @pytest.mark.asyncio
  async def test_refresh_no_oauth2_credential(self, openid_connect_scheme):
    """Test refresh with no OAuth2 credential returns original."""
    credential = AuthCredential(
        auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
        # No oauth2 field
    )

    refresher = OAuth2CredentialRefresher()
    result = await refresher.refresh(credential, openid_connect_scheme)

    assert result == credential

  @pytest.mark.asyncio
  async def test_needs_refresh_no_oauth2_credential(self):
    """Test needs_refresh with no OAuth2 credential returns False."""
    credential = AuthCredential(
        auth_type=AuthCredentialTypes.HTTP,
        # No oauth2 field
    )

    refresher = OAuth2CredentialRefresher()
    needs_refresh = await refresher.is_refresh_needed(credential, None)

    assert not needs_refresh
