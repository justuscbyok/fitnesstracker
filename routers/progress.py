from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Optional
from datetime import date
from ..models.schemas import ProgressLog, ProgressLogCreate, UserStats, User
from ..db import crud
from ..utils.auth import get_current_active_user

router = APIRouter(
    prefix="/progress",
    tags=["progress tracking"],
    responses={404: {"description": "Resource not found"}}
)

@router.get("/stats", response_model=UserStats)
def get_user_stats(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's fitness stats
    """
    stats = crud.get_user_stats(current_user.id)
    if stats is None:
        raise HTTPException(status_code=404, detail="User stats not found")
    return stats

@router.get("/logs", response_model=List[ProgressLog])
def get_progress_logs(
    from_date: Optional[date] = Query(None, description="Filter logs from this date"),
    to_date: Optional[date] = Query(None, description="Filter logs to this date"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's progress logs with optional date filtering
    """
    logs = crud.get_progress_logs_by_user(current_user.id)
    
    # Apply date filters if provided
    if from_date:
        logs = [log for log in logs if log.log_date >= from_date]
    if to_date:
        logs = [log for log in logs if log.log_date <= to_date]
        
    return logs

@router.get("/logs/{log_id}", response_model=ProgressLog)
def get_progress_log(
    log_id: int = Path(..., gt=0, description="The ID of the progress log to get"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific progress log by ID
    """
    log = crud.get_progress_log(log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Progress log not found")
        
    # Ensure the log belongs to the current user
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this progress log")
        
    return log

@router.post("/logs", response_model=ProgressLog, status_code=status.HTTP_201_CREATED)
def create_progress_log(
    log: ProgressLogCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new progress log entry
    """
    return crud.create_progress_log(log, current_user.id)

@router.delete("/logs/{log_id}", status_code=204)
def delete_progress_log(
    log_id: int = Path(..., gt=0, description="The ID of the progress log to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a progress log
    """
    # Check if log exists and belongs to current user
    log = crud.get_progress_log(log_id)
    if log is None:
        raise HTTPException(status_code=404, detail="Progress log not found")
        
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this progress log")
    
    if not crud.delete_progress_log(log_id):
        raise HTTPException(status_code=400, detail="Failed to delete progress log")
        
    return None

@router.get("/streak", status_code=200)
def get_workout_streak(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's workout streak
    """
    stats = crud.get_user_stats(current_user.id)
    if stats is None:
        raise HTTPException(status_code=404, detail="User stats not found")
        
    return {"streak_days": stats.streak_days, "last_workout_date": stats.last_workout_date} 