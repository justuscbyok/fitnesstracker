from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

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
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    
class User(UserBase):
    id: int
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

# Token Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Exercise Models
class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_groups: List[MuscleGroup]
    equipment_needed: Optional[str] = None
    
class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    created_by: Optional[int] = None
    
    class Config:
        from_attributes = True

# Exercise Set Models
class ExerciseSetBase(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration_seconds: Optional[int] = None
    distance: Optional[float] = None
    notes: Optional[str] = None

class ExerciseSetCreate(ExerciseSetBase):
    exercise_id: int

class ExerciseSet(ExerciseSetBase):
    id: int
    exercise_id: int
    
    class Config:
        from_attributes = True

# Workout Models
class WorkoutBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: WorkoutCategory
    duration_minutes: int = Field(gt=0)
    calories_burned: Optional[int] = None
    notes: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    exercise_sets: Optional[List[ExerciseSetCreate]] = None

class Workout(WorkoutBase):
    id: int
    created_at: datetime
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class WorkoutDetail(Workout):
    exercise_sets: List[ExerciseSet] = []

# Workout Plan Models
class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_weeks: int = Field(gt=0)
    target_muscle_groups: List[MuscleGroup] = []
    difficulty_level: int = Field(ge=1, le=5)

class WorkoutPlanCreate(WorkoutPlanBase):
    pass

class WorkoutPlan(WorkoutPlanBase):
    id: int
    created_at: datetime
    created_by: int
    workouts: List[int] = []  # Workout IDs
    
    class Config:
        from_attributes = True

# User Stats Models
class UserStatsBase(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    total_workouts: int = 0
    total_workout_minutes: int = 0
    streak_days: int = 0
    last_workout_date: Optional[date] = None

class UserStats(UserStatsBase):
    user_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

# Progress Log Models
class ProgressLogBase(BaseModel):
    log_date: date
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    notes: Optional[str] = None
    measurements: Optional[Dict[str, float]] = None  # e.g., {"chest": 42.5, "waist": 32.0}

class ProgressLogCreate(ProgressLogBase):
    pass

class ProgressLog(ProgressLogBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Search and Filter Models
class WorkoutFilter(BaseModel):
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    categories: Optional[List[WorkoutCategory]] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    muscle_groups: Optional[List[MuscleGroup]] = None 