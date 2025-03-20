from fastapi import APIRouter, HTTPException, Depends, Path, Query, status
from typing import List, Optional
from ..models.schemas import WorkoutPlan, WorkoutPlanCreate, User, MuscleGroup
from ..db import crud
from ..utils.auth import get_current_active_user

router = APIRouter(
    prefix="/workout-plans",
    tags=["workout plans"],
    responses={404: {"description": "Workout plan not found"}}
)

@router.get("/", response_model=List[WorkoutPlan])
def get_workout_plans(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all workout plans
    """
    return crud.get_workout_plans()

@router.get("/my", response_model=List[WorkoutPlan])
def get_my_workout_plans(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's workout plans
    """
    return crud.get_workout_plans_by_user(current_user.id)

@router.get("/{plan_id}", response_model=WorkoutPlan)
def get_workout_plan(
    plan_id: int = Path(..., gt=0, description="The ID of the workout plan to get"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific workout plan by ID
    """
    plan = crud.get_workout_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    return plan

@router.post("/", response_model=WorkoutPlan, status_code=status.HTTP_201_CREATED)
def create_workout_plan(
    plan: WorkoutPlanCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new workout plan
    """
    return crud.create_workout_plan(plan, current_user.id)

@router.put("/{plan_id}", response_model=WorkoutPlan)
def update_workout_plan(
    plan_id: int = Path(..., gt=0, description="The ID of the workout plan to update"),
    plan: WorkoutPlanCreate = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing workout plan
    """
    # Check if plan exists and belongs to current user
    existing_plan = crud.get_workout_plan(plan_id)
    if existing_plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
        
    if existing_plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workout plan")
    
    updated_plan = crud.update_workout_plan(plan_id, plan)
    if updated_plan is None:
        raise HTTPException(status_code=400, detail="Failed to update workout plan")
        
    return updated_plan

@router.delete("/{plan_id}", status_code=204)
def delete_workout_plan(
    plan_id: int = Path(..., gt=0, description="The ID of the workout plan to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a workout plan
    """
    # Check if plan exists and belongs to current user
    existing_plan = crud.get_workout_plan(plan_id)
    if existing_plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
        
    if existing_plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this workout plan")
    
    if not crud.delete_workout_plan(plan_id):
        raise HTTPException(status_code=400, detail="Failed to delete workout plan")
        
    return None

@router.post("/{plan_id}/workouts/{workout_id}", response_model=WorkoutPlan)
def add_workout_to_plan(
    plan_id: int = Path(..., gt=0, description="The ID of the workout plan"),
    workout_id: int = Path(..., gt=0, description="The ID of the workout to add"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a workout to a workout plan
    """
    # Check if plan exists and belongs to current user
    existing_plan = crud.get_workout_plan(plan_id)
    if existing_plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
        
    if existing_plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this workout plan")
    
    # Check if workout exists
    existing_workout = crud.get_workout(workout_id)
    if existing_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    updated_plan = crud.add_workout_to_plan(plan_id, workout_id)
    if updated_plan is None:
        raise HTTPException(status_code=400, detail="Failed to add workout to plan")
        
    return updated_plan

@router.delete("/{plan_id}/workouts/{workout_id}", response_model=WorkoutPlan)
def remove_workout_from_plan(
    plan_id: int = Path(..., gt=0, description="The ID of the workout plan"),
    workout_id: int = Path(..., gt=0, description="The ID of the workout to remove"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a workout from a workout plan
    """
    # Check if plan exists and belongs to current user
    existing_plan = crud.get_workout_plan(plan_id)
    if existing_plan is None:
        raise HTTPException(status_code=404, detail="Workout plan not found")
        
    if existing_plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this workout plan")
    
    updated_plan = crud.remove_workout_from_plan(plan_id, workout_id)
    if updated_plan is None:
        raise HTTPException(status_code=400, detail="Failed to remove workout from plan")
        
    return updated_plan 