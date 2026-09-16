"""
Therapity — Health Router
Simple health check endpoint.
"""

import datetime
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": "Therapity",
        "timestamp": datetime.datetime.now().isoformat(),
    }
