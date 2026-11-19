from fastapi import APIRouter
from api.v1.endpoints import incubators, companies, auth

api_router = APIRouter()

# Авторизація
api_router.include_router(auth.router)

# Інкубатори
api_router.include_router(incubators.router)

# Компанії (поки вимкнено)
# api_router.include_router(companies.router)