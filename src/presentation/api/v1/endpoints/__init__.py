from fastapi import APIRouter

from src.presentation.api.v1.endpoints.books import router as book_router
from src.presentation.api.v1.endpoints.loans import router as loans_router
from src.presentation.api.v1.endpoints.readers import router as readers_router
from src.presentation.api.v1.endpoints.auth import router as auth_router

router = APIRouter()
router.include_router(book_router)
router.include_router(loans_router)
router.include_router(readers_router)
router.include_router(auth_router)