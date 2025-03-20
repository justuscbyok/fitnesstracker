from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Optional
from ..models.schemas import Exercise, ExerciseCreate, MuscleGroup, User
from ..db import crud
from ..utils.auth import get_current_active_user

router = APIRouter(
    prefix="/exercises",
    tags=["exercises"],
    responses={404: {"description": "Exercise not found"}}
)

@router.get("/", response_model=List[Exercise])
def get_exercises(
    muscle_group: Optional[MuscleGroup] = Query(None, description="Filter by muscle group"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all exercises with optional filtering by muscle group
    """
    if muscle_group:
        return crud.get_exercises_by_muscle_group(muscle_group)
    return crud.get_exercises()

@router.get("/{exercise_id}", response_model=Exercise)
def get_exercise(
    exercise_id: int = Path(..., gt=0, description="The ID of the exercise to get"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific exercise by ID
    """
    exercise = crud.get_exercise(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.post("/", response_model=Exercise, status_code=status.HTTP_201_CREATED)
def create_exercise(
    exercise: ExerciseCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new exercise
    """
    return crud.create_exercise(exercise, current_user.id)

@router.put("/{exercise_id}", response_model=Exercise)
def update_exercise(
    exercise_id: int = Path(..., gt=0, description="The ID of the exercise to update"),
    exercise: ExerciseCreate = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing exercise
    """
    # Check if exercise exists
    existing_exercise = crud.get_exercise(exercise_id)
    if existing_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Only allow updating exercises created by the user or if no creator is specified
    if existing_exercise.created_by and existing_exercise.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this exercise")
    
    updated_exercise = crud.update_exercise(exercise_id, exercise)
    if updated_exercise is None:
        raise HTTPException(status_code=400, detail="Failed to update exercise")
    
    return updated_exercise

@router.delete("/{exercise_id}", status_code=204)
def delete_exercise(
    exercise_id: int = Path(..., gt=0, description="The ID of the exercise to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an exercise if it's not used in any workout
    """
    # Check if exercise exists
    existing_exercise = crud.get_exercise(exercise_id)
    if existing_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    # Only allow deleting exercises created by the user or if no creator is specified
    if existing_exercise.created_by and existing_exercise.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this exercise")
    
    if not crud.delete_exercise(exercise_id):
        raise HTTPException(
            status_code=400, 
            detail="Failed to delete exercise. It may be in use in one or more workouts."
        )
    
    return None

@router.get("/muscle-group/{muscle_group}", response_model=List[Exercise])
def get_exercises_by_muscle_group(
    muscle_group: MuscleGroup = Path(..., description="Muscle group to filter by"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get exercises by muscle group
    """
    return crud.get_exercises_by_muscle_group(muscle_group)