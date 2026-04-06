import pytest

from src.domain.services.readers_service import ReadersService
from src.shared.schemas.readers_schema import CreateReader
from src.infrastructure.db.models import Readers
from src.domain.services.exceptions import NotFoundException

@pytest.mark.asyncio
async def test_search_reader(db_session):
    full_name = "Test Name John"
    phone = "+79998876501"
    email = "test@test.mail"
    
    new_reader = CreateReader(full_name=full_name, phone=phone, email=email).model_dump()
    
    db_session.add(Readers(**new_reader))
    await db_session.commit()
    
    readers, total = await ReadersService.search_reader(db_session, full_name=full_name, phone=phone, email=email, skip=0)
    assert readers is not None, "Ошибка, нет результатов поиска"
    assert total == 1

@pytest.mark.asyncio
async def test_search_reader_neg(db_session):
    full_name = "Test Name John"
    phone = "+79998876501"
    email = "test@test.mail"
    
    with pytest.raises(NotFoundException):
        await ReadersService.search_reader(db_session, full_name=full_name, phone=phone, email=email)