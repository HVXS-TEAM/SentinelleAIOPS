from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
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
api_router.include_router(security.router, prefix="/securite", tags=["Module Sécurité"], dependencies=[Depends(get_current_user)])
api_router.include_router(supervision.router, prefix="/supervision", tags=["Module Supervision"], dependencies=[Depends(get_current_user)])
api_router.include_router(netdevops.router, prefix="/netdevops", tags=["Module NetDevOps"], dependencies=[Depends(get_current_user)])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Module Parc Informatique"], dependencies=[Depends(get_current_user)])
api_router.include_router(admin.router, prefix="/admin", tags=["Reporting & Administration"], dependencies=[Depends(get_current_user)])
api_router.include_router(assistant.router, prefix="/assistant", tags=["Assistant IA"], dependencies=[Depends(get_current_user)])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation Démo"], dependencies=[Depends(get_current_user)])
