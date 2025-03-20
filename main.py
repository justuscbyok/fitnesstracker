from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import time
from datetime import datetime, date
from enum import Enum

# Models
from pydantic import BaseModel, Field

# Create FastAPI app
app = FastAPI(
    title="Fitness Tracker API",
    description="API for tracking fitness workouts with user authentication and progress tracking",
    version="2.0.0"
)

# Add CORS middleware - allows the API to be accessed from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request processing time header middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# In-memory storage for a simple demo
db = {
    "users": [],
    "workouts": [],
    "exercises": [],
    "workout_plans": [],
    "progress_logs": []
}

# ----- Models -----

class WorkoutCategory(str, Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    MOBILITY = "mobility"
    HIIT = "hiit"
    YOGA = "yoga"
    CROSSFIT = "crossfit"

class MuscleGroup(str, Enum):
    CHEST = "chest"
    BACK = "back"
    LEGS = "legs"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    CORE = "core"
    FULL_BODY = "full_body"

# User Models
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

# Workout Models
class WorkoutBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: WorkoutCategory
    duration_minutes: int = Field(gt=0)
    calories_burned: Optional[int] = None
    notes: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    pass

class Workout(WorkoutBase):
    id: int
    created_at: datetime
    user_id: int

# Exercise Models
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_group: MuscleGroup
    instructions: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    created_at: datetime

# Workout Plan Models
class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_weeks: int = Field(gt=0)

class WorkoutPlanCreate(WorkoutPlanBase):
    pass

class WorkoutPlan(WorkoutPlanBase):
    id: int
    created_at: datetime
    user_id: int
    workouts: List[int] = []  # List of workout IDs

# Progress Log Models
class ProgressLogBase(BaseModel):
    date: date
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    notes: Optional[str] = None

class ProgressLogCreate(ProgressLogBase):
    pass

class ProgressLog(ProgressLogBase):
    id: int
    user_id: int
    created_at: datetime

# ----- Simple dependency to demonstrate dependency injection -----
def get_api_info() -> Dict[str, str]:
    return {
        "app_name": "Fitness Tracker",
        "version": "2.0.0",
        "description": "Track and manage your workouts, exercises, and fitness progress"
    }

# ----- Endpoints -----

@app.get("/", tags=["root"])
def read_root(api_info: Dict[str, str] = Depends(get_api_info)):
    """
    Root endpoint that returns basic API information
    """
    return {
        "message": "Welcome to the Fitness Tracker API!",
        "api_info": api_info,
        "endpoints": {
            "users": "User registration and authentication",
            "workouts": "Create and manage workouts",
            "exercises": "Repository of exercises",
            "workout_plans": "Create structured workout plans",
            "progress": "Track fitness metrics and progress"
        }
    }

@app.get("/healthz", tags=["default"])
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

# ----- User endpoints -----
@app.post("/users/register", response_model=User, status_code=201, tags=["users"])
def register_user(user: UserCreate):
    """
    Register a new user
    """
    # Generate a new ID (in a real app, the database would handle this)
    user_id = len(db["users"]) + 1
    
    new_user = User(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        created_at=datetime.now()
    )
    
    db["users"].append(new_user)
    return new_user

@app.get("/users/", response_model=List[User], tags=["users"])
def read_users(skip: int = 0, limit: int = 100):
    """
    Retrieve users
    """
    return db["users"][skip:skip+limit]

@app.get("/users/{user_id}", response_model=User, tags=["users"])
def read_user(user_id: int):
    """
    Get a specific user by ID
    """
    for user in db["users"]:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User, tags=["users"])
def update_user(user_id: int, user_update: UserBase):
    """
    Update a user's information
    """
    for i, user in enumerate(db["users"]):
        if user.id == user_id:
            # Update fields while preserving id and created_at
            updated_user = User(
                id=user.id,
                username=user_update.username,
                email=user_update.email,
                full_name=user_update.full_name,
                created_at=user.created_at,
                is_active=user.is_active
            )
            db["users"][i] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}", status_code=204, tags=["users"])
def delete_user(user_id: int):
    """
    Delete a user
    """
    for i, user in enumerate(db["users"]):
        if user.id == user_id:
            db["users"].pop(i)
            return
    raise HTTPException(status_code=404, detail="User not found")

# ----- Workout endpoints -----
@app.post("/workouts/", response_model=Workout, status_code=201, tags=["workouts"])
def create_workout(workout: WorkoutCreate):
    """
    Create a new workout
    """
    # Dummy user_id for demo
    user_id = 1
    if not db["users"]:
        # Create a demo user if none exists
        db["users"].append(User(
            id=user_id,
            username="demouser",
            email="demo@example.com",
            created_at=datetime.now()
        ))
    
    # Generate a new ID
    workout_id = len(db["workouts"]) + 1
    
    new_workout = Workout(
        id=workout_id,
        title=workout.title,
        description=workout.description,
        category=workout.category,
        duration_minutes=workout.duration_minutes,
        calories_burned=workout.calories_burned,
        notes=workout.notes,
        created_at=datetime.now(),
        user_id=user_id
    )
    
    db["workouts"].append(new_workout)
    return new_workout

@app.get("/workouts/", response_model=List[Workout], tags=["workouts"])
def read_workouts(skip: int = 0, limit: int = 100):
    """
    Retrieve workouts
    """
    return db["workouts"][skip:skip+limit]

@app.get("/workouts/{workout_id}", response_model=Workout, tags=["workouts"])
def read_workout(workout_id: int):
    """
    Get a specific workout by ID
    """
    for workout in db["workouts"]:
        if workout.id == workout_id:
            return workout
    raise HTTPException(status_code=404, detail="Workout not found")

@app.put("/workouts/{workout_id}", response_model=Workout, tags=["workouts"])
def update_workout(workout_id: int, workout_update: WorkoutBase):
    """
    Update a workout
    """
    for i, workout in enumerate(db["workouts"]):
        if workout.id == workout_id:
            # Update fields while preserving id, created_at, and user_id
            updated_workout = Workout(
                id=workout.id,
                title=workout_update.title,
                description=workout_update.description,
                category=workout_update.category,
                duration_minutes=workout_update.duration_minutes,
                calories_burned=workout_update.calories_burned,
                notes=workout_update.notes,
                created_at=workout.created_at,
                user_id=workout.user_id
            )
            db["workouts"][i] = updated_workout
            return updated_workout
    raise HTTPException(status_code=404, detail="Workout not found")

@app.delete("/workouts/{workout_id}", status_code=204, tags=["workouts"])
def delete_workout(workout_id: int):
    """
    Delete a workout
    """
    for i, workout in enumerate(db["workouts"]):
        if workout.id == workout_id:
            db["workouts"].pop(i)
            return
    raise HTTPException(status_code=404, detail="Workout not found")

# ----- Exercise endpoints -----
@app.post("/exercises/", response_model=Exercise, status_code=201, tags=["exercises"])
def create_exercise(exercise: ExerciseCreate):
    """
    Create a new exercise
    """
    # Generate a new ID
    exercise_id = len(db["exercises"]) + 1
    
    new_exercise = Exercise(
        id=exercise_id,
        name=exercise.name,
        description=exercise.description,
        muscle_group=exercise.muscle_group,
        instructions=exercise.instructions,
        created_at=datetime.now()
    )
    
    db["exercises"].append(new_exercise)
    return new_exercise

@app.get("/exercises/", response_model=List[Exercise], tags=["exercises"])
def read_exercises(skip: int = 0, limit: int = 100):
    """
    Retrieve exercises
    """
    return db["exercises"][skip:skip+limit]

@app.get("/exercises/{exercise_id}", response_model=Exercise, tags=["exercises"])
def read_exercise(exercise_id: int):
    """
    Get a specific exercise by ID
    """
    for exercise in db["exercises"]:
        if exercise.id == exercise_id:
            return exercise
    raise HTTPException(status_code=404, detail="Exercise not found")

@app.put("/exercises/{exercise_id}", response_model=Exercise, tags=["exercises"])
def update_exercise(exercise_id: int, exercise_update: ExerciseBase):
    """
    Update an exercise
    """
    for i, exercise in enumerate(db["exercises"]):
        if exercise.id == exercise_id:
            # Update fields while preserving id and created_at
            updated_exercise = Exercise(
                id=exercise.id,
                name=exercise_update.name,
                description=exercise_update.description,
                muscle_group=exercise_update.muscle_group,
                instructions=exercise_update.instructions,
                created_at=exercise.created_at
            )
            db["exercises"][i] = updated_exercise
            return updated_exercise
    raise HTTPException(status_code=404, detail="Exercise not found")

@app.delete("/exercises/{exercise_id}", status_code=204, tags=["exercises"])
def delete_exercise(exercise_id: int):
    """
    Delete an exercise
    """
    for i, exercise in enumerate(db["exercises"]):
        if exercise.id == exercise_id:
            db["exercises"].pop(i)
            return
    raise HTTPException(status_code=404, detail="Exercise not found")

@app.get("/exercises/muscle-group/{muscle_group}", response_model=List[Exercise], tags=["exercises"])
def read_exercises_by_muscle_group(muscle_group: MuscleGroup):
    """
    Get exercises by muscle group
    """
    return [ex for ex in db["exercises"] if ex.muscle_group == muscle_group]

# ----- Workout Plan endpoints -----
@app.post("/workout-plans/", response_model=WorkoutPlan, status_code=201, tags=["workout_plans"])
def create_workout_plan(plan: WorkoutPlanCreate):
    """
    Create a new workout plan
    """
    # Dummy user_id for demo
    user_id = 1
    if not db["users"]:
        # Create a demo user if none exists
        db["users"].append(User(
            id=user_id,
            username="demouser",
            email="demo@example.com",
            created_at=datetime.now()
        ))
    
    # Generate a new ID
    plan_id = len(db["workout_plans"]) + 1
    
    new_plan = WorkoutPlan(
        id=plan_id,
        name=plan.name,
        description=plan.description,
        duration_weeks=plan.duration_weeks,
        created_at=datetime.now(),
        user_id=user_id
    )
    
    db["workout_plans"].append(new_plan)
    return new_plan

@app.get("/workout-plans/", response_model=List[WorkoutPlan], tags=["workout_plans"])
def read_workout_plans(skip: int = 0, limit: int = 100):
    """
    Retrieve workout plans
    """
    return db["workout_plans"][skip:skip+limit]

@app.get("/workout-plans/{plan_id}", response_model=WorkoutPlan, tags=["workout_plans"])
def read_workout_plan(plan_id: int):
    """
    Get a specific workout plan by ID
    """
    for plan in db["workout_plans"]:
        if plan.id == plan_id:
            return plan
    raise HTTPException(status_code=404, detail="Workout plan not found")

@app.put("/workout-plans/{plan_id}", response_model=WorkoutPlan, tags=["workout_plans"])
def update_workout_plan(plan_id: int, plan_update: WorkoutPlanBase):
    """
    Update a workout plan
    """
    for i, plan in enumerate(db["workout_plans"]):
        if plan.id == plan_id:
            # Update fields while preserving id, created_at, user_id, and workouts
            updated_plan = WorkoutPlan(
                id=plan.id,
                name=plan_update.name,
                description=plan_update.description,
                duration_weeks=plan_update.duration_weeks,
                created_at=plan.created_at,
                user_id=plan.user_id,
                workouts=plan.workouts
            )
            db["workout_plans"][i] = updated_plan
            return updated_plan
    raise HTTPException(status_code=404, detail="Workout plan not found")

@app.delete("/workout-plans/{plan_id}", status_code=204, tags=["workout_plans"])
def delete_workout_plan(plan_id: int):
    """
    Delete a workout plan
    """
    for i, plan in enumerate(db["workout_plans"]):
        if plan.id == plan_id:
            db["workout_plans"].pop(i)
            return
    raise HTTPException(status_code=404, detail="Workout plan not found")

@app.post("/workout-plans/{plan_id}/workouts/{workout_id}", tags=["workout_plans"])
def add_workout_to_plan(plan_id: int, workout_id: int):
    """
    Add a workout to a plan
    """
    # Find the plan
    plan = None
    for p in db["workout_plans"]:
        if p.id == plan_id:
            plan = p
            break
    
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Check if workout exists
    workout_exists = False
    for w in db["workouts"]:
        if w.id == workout_id:
            workout_exists = True
            break
    
    if not workout_exists:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    # Add workout to plan if not already added
    if workout_id not in plan.workouts:
        plan.workouts.append(workout_id)
    
    return {"message": "Workout added to plan successfully"}

@app.delete("/workout-plans/{plan_id}/workouts/{workout_id}", tags=["workout_plans"])
def remove_workout_from_plan(plan_id: int, workout_id: int):
    """
    Remove a workout from a plan
    """
    # Find the plan
    plan = None
    for p in db["workout_plans"]:
        if p.id == plan_id:
            plan = p
            break
    
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    
    # Remove workout from plan if it exists
    if workout_id in plan.workouts:
        plan.workouts.remove(workout_id)
        return {"message": "Workout removed from plan successfully"}
    else:
        raise HTTPException(status_code=404, detail="Workout not found in this plan")

# ----- Progress tracking endpoints -----
@app.post("/progress/logs/", response_model=ProgressLog, status_code=201, tags=["progress"])
def create_progress_log(log: ProgressLogCreate):
    """
    Create a new progress log
    """
    # Dummy user_id for demo
    user_id = 1
    if not db["users"]:
        # Create a demo user if none exists
        db["users"].append(User(
            id=user_id,
            username="demouser",
            email="demo@example.com",
            created_at=datetime.now()
        ))
    
    # Generate a new ID
    log_id = len(db["progress_logs"]) + 1
    
    new_log = ProgressLog(
        id=log_id,
        date=log.date,
        weight=log.weight,
        body_fat_percentage=log.body_fat_percentage,
        notes=log.notes,
        created_at=datetime.now(),
        user_id=user_id
    )
    
    db["progress_logs"].append(new_log)
    return new_log

@app.get("/progress/logs/", response_model=List[ProgressLog], tags=["progress"])
def read_progress_logs(skip: int = 0, limit: int = 100):
    """
    Retrieve progress logs
    """
    return db["progress_logs"][skip:skip+limit]

@app.get("/progress/logs/{log_id}", response_model=ProgressLog, tags=["progress"])
def read_progress_log(log_id: int):
    """
    Get a specific progress log by ID
    """
    for log in db["progress_logs"]:
        if log.id == log_id:
            return log
    raise HTTPException(status_code=404, detail="Progress log not found")

@app.put("/progress/logs/{log_id}", response_model=ProgressLog, tags=["progress"])
def update_progress_log(log_id: int, log_update: ProgressLogBase):
    """
    Update a progress log
    """
    for i, log in enumerate(db["progress_logs"]):
        if log.id == log_id:
            # Update fields while preserving id, created_at, and user_id
            updated_log = ProgressLog(
                id=log.id,
                date=log_update.date,
                weight=log_update.weight,
                body_fat_percentage=log_update.body_fat_percentage,
                notes=log_update.notes,
                created_at=log.created_at,
                user_id=log.user_id
            )
            db["progress_logs"][i] = updated_log
            return updated_log
    raise HTTPException(status_code=404, detail="Progress log not found")

@app.delete("/progress/logs/{log_id}", status_code=204, tags=["progress"])
def delete_progress_log(log_id: int):
    """
    Delete a progress log
    """
    for i, log in enumerate(db["progress_logs"]):
        if log.id == log_id:
            db["progress_logs"].pop(i)
            return
    raise HTTPException(status_code=404, detail="Progress log not found")

@app.get("/progress/stats/", tags=["progress"])
def get_fitness_stats():
    """
    Get user's fitness stats (demo implementation)
    """
    # Dummy implementation
    return {
        "workout_count": len(db["workouts"]),
        "total_duration_minutes": sum(w.duration_minutes for w in db["workouts"]),
        "total_calories_burned": sum(w.calories_burned or 0 for w in db["workouts"]),
        "streak_days": 5,  # Dummy value
        "most_trained_category": WorkoutCategory.STRENGTH if db["workouts"] else None
    }

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# Run the app with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)