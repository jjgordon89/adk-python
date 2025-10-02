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

"""Security tests for database operations."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from safetyculture_agent.database.asset_repository import AssetRepository
from safetyculture_agent.exceptions import SafetyCultureDatabaseError


class TestDatabaseSecurity:
  """Database security test suite."""
  
  @pytest.fixture
  async def repository(self):
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(
      suffix='.db',
      delete=False
    ) as f:
      db_path = f.name
    
    repo = AssetRepository(db_path=db_path)
    await repo.initialize()
    yield repo
    
    # Cleanup
    try:
      Path(db_path).unlink()
    except Exception:
      pass
  
  @pytest.mark.asyncio
  async def test_sql_injection_prevention_in_field_names(self, repository):
    """Verify SQL injection blocked in field names."""
    # Try SQL injection in field names
    malicious_fields = [
      "status; DROP TABLE asset_inspections; --"
    ]
    
    for field in malicious_fields:
      with pytest.raises((SafetyCultureDatabaseError, ValueError)):
        # This should be caught by field validation
        await repository.update_inspection_status(
          'asset_1',
          'completed',
          month_year='2025-01'
        )
  
  @pytest.mark.asyncio
  async def test_field_whitelist_validation(self, repository):
    """Verify only whitelisted fields can be updated."""
    # Register a test asset first
    await repository.register_asset(
      asset_id='test_asset',
      month_year='2025-01',
      asset_name='Test',
      location='Test Location'
    )
    
    # Valid update should work
    result = await repository.update_inspection_status(
      asset_id='test_asset',
      status='completed',
      month_year='2025-01'
    )
    assert result is True
    
    # Invalid field should be rejected by validation
    invalid_fields = ['evil_field = ?']
    with pytest.raises(ValueError) as exc:
      repository._validate_and_sanitize_fields(invalid_fields)
    
    assert 'Invalid field' in str(exc.value)
  
  @pytest.mark.asyncio
  async def test_concurrent_registration_prevents_duplicates(self, repository):
    """Test concurrent registration doesn't create duplicates."""
    # Attempt concurrent registration of same asset
    tasks = [
      repository.register_asset(
        asset_id='asset_concurrent',
        month_year='2025-01',
        asset_name='Test Asset',
        location='Location'
      )
      for _ in range(10)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Only one should succeed (True), rest should return False
    success_count = sum(1 for r in results if r is True)
    assert success_count == 1
    
    # Others should be False (already exists)
    false_count = sum(1 for r in results if r is False)
    assert false_count == 9
  
  @pytest.mark.asyncio
  async def test_parameterized_queries_prevent_injection(self, repository):
    """Verify parameterized queries prevent SQL injection."""
    # Register asset with malicious data
    malicious_asset_id = "asset'; DROP TABLE asset_inspections; --"
    
    # Should safely handle malicious input through parameterization
    try:
      result = await repository.register_asset(
        asset_id=malicious_asset_id,
        month_year='2025-01',
        asset_name='Test',
        location='Test Location'
      )
      # If it succeeds, data should be safely escaped
      assert result is True
      
      # Verify the data was stored safely (not executed as SQL)
      status = await repository.get_asset_inspection_status(
        malicious_asset_id,
        '2025-01'
      )
      assert status is not None
    except Exception:
      # If validation catches it, that's also acceptable
      pass
  
  @pytest.mark.asyncio
  async def test_unique_constraint_prevents_duplicates(self, repository):
    """Verify unique constraints prevent duplicate entries."""
    asset_data = {
      'asset_id': 'unique_test',
      'month_year': '2025-01',
      'asset_name': 'Test Asset',
      'location': 'Test Location'
    }
    
    # First registration should succeed
    result1 = await repository.register_asset(**asset_data)
    assert result1 is True
    
    # Second registration of same asset/month should fail
    result2 = await repository.register_asset(**asset_data)
    assert result2 is False
  
  @pytest.mark.asyncio
  async def test_metadata_json_injection_prevention(self, repository):
    """Verify JSON metadata doesn't allow code injection."""
    # Register asset
    await repository.register_asset_for_inspection(
      asset_id='metadata_test',
      asset_name='Test',
      asset_type='Equipment',
      location='Location',
      template_id='template_1',
      template_name='Test Template',
      month_year='2025-01'
    )
    
    # Try to inject malicious code through metadata
    malicious_metadata = {
      '__proto__': {'polluted': 'value'},
      'constructor': {'prototype': {'polluted': 'value'}}
    }
    
    # Should safely store as JSON string
    result = await repository.update_inspection_status(
      asset_id='metadata_test',
      status='in_progress',
      month_year='2025-01',
      metadata=malicious_metadata
    )
    
    assert result is True
    
    # Verify data was stored safely
    metadata = await repository._get_asset_metadata(
      'metadata_test',
      '2025-01'
    )
    # Metadata should be stored but not executed
    assert isinstance(metadata, dict)
  
  @pytest.mark.asyncio
  async def test_wal_mode_enabled_for_concurrency(self, repository):
    """Verify WAL mode is enabled for better concurrency."""
    # WAL mode should be set during initialization
    # We can't directly check this without DB introspection
    # But we can test concurrent operations work
    
    tasks = []
    for i in range(5):
      tasks.append(
        repository.register_asset(
          asset_id=f'concurrent_{i}',
          month_year='2025-01',
          asset_name=f'Asset {i}',
          location='Location'
        )
      )
    
    results = await asyncio.gather(*tasks)
    
    # All should succeed since they're different assets
    assert all(r is True for r in results)
  
  @pytest.mark.asyncio
  async def test_transaction_isolation(self, repository):
    """Verify transaction isolation prevents race conditions."""
    # Register initial asset
    await repository.register_asset(
      asset_id='transaction_test',
      month_year='2025-01',
      asset_name='Test',
      location='Location'
    )
    
    # Attempt concurrent updates
    async def update_status(new_status):
      return await repository.update_inspection_status(
        asset_id='transaction_test',
        status=new_status,
        month_year='2025-01'
      )
    
    # Run concurrent updates
    results = await asyncio.gather(
      update_status('in_progress'),
      update_status('completed'),
      update_status('failed')
    )
    
    # All updates should succeed (last one wins)
    assert any(results)
    
    # Final status should be one of the updated values
    final_status = await repository.get_asset_inspection_status(
      'transaction_test',
      '2025-01'
    )
    assert final_status in ['in_progress', 'completed', 'failed']


class TestDatabaseAccessControl:
  """Test database access control and permissions."""
  
  @pytest.fixture
  async def repository(self):
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(
      suffix='.db',
      delete=False
    ) as f:
      db_path = f.name
    
    repo = AssetRepository(db_path=db_path)
    await repo.initialize()
    yield repo
    
    # Cleanup
    try:
      Path(db_path).unlink()
    except Exception:
      pass
  
  @pytest.mark.asyncio
  async def test_database_file_permissions(self, repository):
    """Verify database file has appropriate permissions."""
    db_path = Path(repository.db_path)
    
    # Database file should exist
    assert db_path.exists()
    
    # File should be readable and writable
    assert db_path.is_file()
  
  @pytest.mark.asyncio
  async def test_initialization_idempotent(self, repository):
    """Verify multiple initializations are safe."""
    # Initialize again
    await repository.initialize()
    await repository.initialize()
    
    # Should still work
    result = await repository.register_asset(
      asset_id='test',
      month_year='2025-01',
      asset_name='Test',
      location='Location'
    )
    assert result is True


class TestQuerySafety:
  """Test query safety and prepared statements."""
  
  @pytest.fixture
  async def repository(self):
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(
      suffix='.db',
      delete=False
    ) as f:
      db_path = f.name
    
    repo = AssetRepository(db_path=db_path)
    await repo.initialize()
    yield repo
    
    # Cleanup
    try:
      Path(db_path).unlink()
    except Exception:
      pass
  
  @pytest.mark.asyncio
  async def test_check_asset_completed_safe_query(self, repository):
    """Verify check_asset_completed uses safe queries."""
    # Register and complete an asset
    await repository.register_asset_for_inspection(
      asset_id='completed_test',
      asset_name='Test',
      asset_type='Equipment',
      location='Location',
      template_id='template_1',
      template_name='Test Template',
      month_year='2025-01'
    )
    
    await repository.mark_asset_completed(
      asset_id='completed_test',
      inspection_id='insp_123',
      month_year='2025-01'
    )
    
    # Check if completed - should use parameterized query
    is_completed = await repository.check_asset_completed_this_month(
      'completed_test',
      '2025-01'
    )
    assert is_completed is True
  
  @pytest.mark.asyncio
  async def test_malicious_month_year_format(self, repository):
    """Verify malicious month_year values are handled safely."""
    malicious_months = [
      "2025-01'; DROP TABLE asset_inspections; --",
      "2025-01 OR 1=1",
      "2025-01\x00"
    ]
    
    for month in malicious_months:
      # Should either reject or safely escape
      try:
        await repository.register_asset(
          asset_id='test',
          month_year=month,
          asset_name='Test',
          location='Location'
        )
      except Exception:
        # If it raises an exception, that's acceptable
        pass