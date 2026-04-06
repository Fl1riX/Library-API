import pytest
from unittest.mock import AsyncMock, MagicMock

from src.domain.services.readers_service import ReadersService

@pytest.mark.asyncio
async def test_reader_search():
    mock_db = AsyncMock()
    fake_readers = [MagicMock(), MagicMock()]
    fake_readers[0].full_name = "Test Name John"
    fake_readers[1].full_name = "Test Name John2"
    
    mock_result = MagicMock()
    
    mock_db.execute.return_value = mock_result
    mock_db.scalar.return_value = 1
    mock_result.scalars().all.return_value = fake_readers
    
    readers, total = await ReadersService.search_reader(db=mock_db, full_name="Test Name John")
    
    assert readers == fake_readers
    assert total == 1