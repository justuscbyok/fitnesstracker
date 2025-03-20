from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Optional
from ..models.schemas import (
    Workout, WorkoutCreate, WorkoutCategory, WorkoutDetail,
    User, WorkoutFilter, MuscleGroup
)
from ..db import crud
from ..utils.auth import get_current_active_user

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"],
    responses={404: {"description": "Workout not found"}}
)

# Dependency for category validation
def validate_category(
    category: Optional[WorkoutCategory] = Query(None, description="Filter workouts by category")
) -> Optional[WorkoutCategory]:
    return category

@router.get("/", response_model=List[Workout])
def get_workouts(
    category: Optional[WorkoutCategory] = Depends(validate_category),
    from_date: Optional[str] = Query(None, description="Filter workouts from this date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter workouts to this date (YYYY-MM-DD)"),
    min_duration: Optional[int] = Query(None, ge=0, description="Minimum duration in minutes"),
    max_duration: Optional[int] = Query(None, ge=0, description="Maximum duration in minutes"),
    muscle_group: Optional[MuscleGroup] = Query(None, description="Filter by muscle group targeted"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all workouts or filter by various parameters
    """
    # Create filter object if any filter parameters provided
    if any([from_date, to_date, category, min_duration, max_duration, muscle_group]):
        filters = WorkoutFilter(
            from_date=from_date,
            to_date=to_date,
            categories=[category] if category else None,
            min_duration=min_duration,
            max_duration=max_duration,
            muscle_groups=[muscle_group] if muscle_group else None
        )
        return crud.get_workouts(filters)
    
    return crud.get_workouts()

@router.get("/my", response_model=List[Workout])
def get_my_workouts(
    category: Optional[WorkoutCategory] = Depends(validate_category),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's workouts with optional category filter
    """
    workouts = crud.get_workouts_by_user(current_user.id)
    
    if category:
        workouts = [w for w in workouts if w.category == category]
        
    return workouts

@router.get("/{workout_id}", response_model=WorkoutDetail)
def get_workout(
    workout_id: int = Path(..., gt=0, description="The ID of the workout to get"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific workout by ID with detailed information including exercise sets
    """
    workout = crud.get_workout_detail(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.post("/", response_model=WorkoutDetail, status_code=status.HTTP_201_CREATED)
def create_workout(
    workout: WorkoutCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new workout with optional exercise sets
    """
    return crud.create_workout(workout, current_user.id)

@router.put("/{workout_id}", response_model=WorkoutDetail)
def update_workout(
    workout_id: int = Path(..., gt=0, description="The ID of the workout to update"),
    workout: WorkoutCreate = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing workout
    """
    # Check if workout exists and belongs to current user
    existing_workout = crud.get_workout(workout_id)
    if existing_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
        
    if existing_workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workout")
    
    updated_workout = crud.update_workout(workout_id, workout)
    if updated_workout is None:
        raise HTTPException(status_code=400, detail="Failed to update workout")
        
    return updated_workout

@router.delete("/{workout_id}", status_code=204)
def delete_workout(
    workout_id: int = Path(..., gt=0, description="The ID of the workout to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a workout
    """
    # Check if workout exists and belongs to current user
    existing_workout = crud.get_workout(workout_id)
    if existing_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
        
    if existing_workout.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workout")
    
    if not crud.delete_workout(workout_id):
        raise HTTPException(status_code=400, detail="Failed to delete workout")
        
    return None

@router.get("/category/{category}", response_model=List[Workout])
def get_workouts_by_category(
    category: WorkoutCategory = Path(..., description="Category to filter by"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get workouts by category
    """
    return crud.get_workouts_by_category(category) 