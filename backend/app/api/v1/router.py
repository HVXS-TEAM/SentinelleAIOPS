from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    security,
    supervision,
    netdevops,
    inventory,
    admin,
    assistant,
    simulation
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentification"])
api_router.include_router(security.router, prefix="/securite", tags=["Module Sécurité"])
api_router.include_router(supervision.router, prefix="/supervision", tags=["Module Supervision"])
api_router.include_router(netdevops.router, prefix="/netdevops", tags=["Module NetDevOps"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Module Parc Informatique"])
api_router.include_router(admin.router, prefix="/admin", tags=["Reporting & Administration"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["Assistant IA"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation Démo"])
