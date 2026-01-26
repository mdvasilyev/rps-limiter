from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter, HTTPException, Request
from starlette import status

from src.adapters.api.v1.routes.model import JobResponse
from src.application.workers import fetch_and_process
from src.core.configurations import get_config

logs_processor_router = APIRouter(prefix="/api/v1", tags=["logs_processor"])

LOGS_PROCESSOR_JOB_ID = "logs_processor_job"


@logs_processor_router.post(
    "/job", status_code=status.HTTP_201_CREATED, response_model=JobResponse
)
async def create_job(request: Request) -> JobResponse:
    """Create a scheduled job."""
    scheduler: AsyncIOScheduler = request.app.state.scheduler

    if scheduler.running and scheduler.get_job(LOGS_PROCESSOR_JOB_ID):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Job already exists"
        )

    config = get_config()

    if not scheduler.running:
        scheduler.start()

    scheduler.add_job(
        fetch_and_process,
        IntervalTrigger(seconds=config.worker.interval),
        id=LOGS_PROCESSOR_JOB_ID,
    )

    return JobResponse(message="Job created successfully")


@logs_processor_router.delete(
    "/job", status_code=status.HTTP_200_OK, response_model=JobResponse
)
async def remove_job(request: Request) -> JobResponse:
    """Remove the scheduled job."""
    scheduler: AsyncIOScheduler = request.app.state.scheduler

    job = scheduler.get_job(LOGS_PROCESSOR_JOB_ID)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    scheduler.remove_job(LOGS_PROCESSOR_JOB_ID)

    return JobResponse(message="Job removed successfully")
