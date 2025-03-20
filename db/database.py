from datetime import datetime, date
from ..models.schemas import (
    Workout, WorkoutCategory, 
    User, Exercise, ExerciseSet, WorkoutPlan, 
    UserStats, ProgressLog, MuscleGroup
)

# Dummy user database
users_db = {
    1: User(
        id=1,
        email="john@example.com",
        username="johndoe",
        full_name="John Doe",
        created_at=datetime.now(),
    ),
    2: User(
        id=2,
        email="jane@example.com",
        username="janedoe",
        full_name="Jane Smith",
        created_at=datetime.now(),
    )
}

# Passwords are stored hashed in a separate dictionary for security
users_passwords = {
    "johndoe": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
    "janedoe": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
}

# Exercise database
exercises_db = {
    1: Exercise(
        id=1,
        name="Barbell Bench Press",
        description="Lie on a flat bench and press the barbell upward",
        muscle_groups=[MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.ARMS],
        equipment_needed="Barbell, Bench",
        created_by=1
    ),
    2: Exercise(
        id=2,
        name="Squat",
        description="Lower your body by bending your knees, keeping your back straight",
        muscle_groups=[MuscleGroup.LEGS],
        equipment_needed="Barbell, Squat Rack",
        created_by=1
    ),
    3: Exercise(
        id=3,
        name="Deadlift",
        description="Lift the barbell from the ground to hip level",
        muscle_groups=[MuscleGroup.BACK, MuscleGroup.LEGS],
        equipment_needed="Barbell",
        created_by=1
    ),
    4: Exercise(
        id=4,
        name="Running",
        description="Running at steady pace",
        muscle_groups=[MuscleGroup.LEGS, MuscleGroup.CORE],
        equipment_needed="None",
        created_by=2
    ),
    5: Exercise(
        id=5,
        name="Plank",
        description="Hold the position with your body weight on forearms and toes",
        muscle_groups=[MuscleGroup.CORE],
        equipment_needed="None",
        created_by=2
    )
}

# Exercise sets database
exercise_sets_db = {
    1: ExerciseSet(
        id=1,
        exercise_id=1,
        reps=10,
        weight=135.0,
        duration_seconds=None,
        distance=None,
        notes="Felt strong today"
    ),
    2: ExerciseSet(
        id=2,
        exercise_id=2,
        reps=8,
        weight=225.0,
        duration_seconds=None,
        distance=None,
        notes=None
    ),
    3: ExerciseSet(
        id=3,
        exercise_id=4,
        reps=None,
        weight=None,
        duration_seconds=1800,
        distance=5.0,
        notes="Steady pace"
    ),
    4: ExerciseSet(
        id=4,
        exercise_id=5,
        reps=None,
        weight=None,
        duration_seconds=60,
        distance=None,
        notes="Core engaged"
    )
}

# Workout database
workouts_db = {
    1: Workout(
        id=1,
        title="Morning Run",
        description="5K run around the park",
        category=WorkoutCategory.CARDIO,
        duration_minutes=30,
        calories_burned=300,
        created_at=datetime.now(),
        user_id=2,
        notes="Felt great, good pace"
    ),
    2: Workout(
        id=2,
        title="Chest Day",
        description="Focused on chest exercises",
        category=WorkoutCategory.STRENGTH,
        duration_minutes=45,
        calories_burned=250,
        created_at=datetime.now(),
        user_id=1,
        notes="Increased weight on bench press"
    ),
    3: Workout(
        id=3,
        title="Yoga Session",
        description="Full body stretching",
        category=WorkoutCategory.MOBILITY,
        duration_minutes=60,
        calories_burned=150,
        created_at=datetime.now(),
        user_id=2,
        notes="Focused on breathing techniques"
    )
}

# Map workout IDs to their exercise sets
workout_exercise_sets = {
    1: [3],  # Workout 1 contains exercise set 3
    2: [1],  # Workout 2 contains exercise set 1
    3: [4]   # Workout 3 contains exercise set 4
}

# Workout plans database
workout_plans_db = {
    1: WorkoutPlan(
        id=1,
        name="Beginner Strength Program",
        description="8-week program for beginners to build strength",
        duration_weeks=8,
        target_muscle_groups=[MuscleGroup.FULL_BODY],
        difficulty_level=1,
        created_at=datetime.now(),
        created_by=1,
        workouts=[2, 3]
    ),
    2: WorkoutPlan(
        id=2,
        name="5K Training Plan",
        description="6-week program to prepare for a 5K run",
        duration_weeks=6,
        target_muscle_groups=[MuscleGroup.LEGS, MuscleGroup.CORE],
        difficulty_level=2,
        created_at=datetime.now(),
        created_by=2,
        workouts=[1]
    )
}

# User stats database
user_stats_db = {
    1: UserStats(
        user_id=1,
        weight=180.0,
        height=72.0,
        body_fat_percentage=15.0,
        total_workouts=15,
        total_workout_minutes=750,
        streak_days=3,
        last_workout_date=date.today(),
        last_updated=datetime.now()
    ),
    2: UserStats(
        user_id=2,
        weight=140.0,
        height=65.0,
        body_fat_percentage=22.0,
        total_workouts=22,
        total_workout_minutes=1200,
        streak_days=5,
        last_workout_date=date.today(),
        last_updated=datetime.now()
    )
}

# Progress logs database
progress_logs_db = {
    1: ProgressLog(
        id=1,
        user_id=1,
        log_date=date.today(),
        weight=180.0,
        body_fat_percentage=15.0,
        measurements={"chest": 42.0, "waist": 34.0, "arms": 15.5},
        notes="Feeling stronger this week",
        created_at=datetime.now()
    ),
    2: ProgressLog(
        id=2,
        user_id=2,
        log_date=date.today(),
        weight=140.0,
        body_fat_percentage=21.8,
        measurements={"chest": 36.0, "waist": 28.0, "thighs": 22.0},
        notes="Down 0.2% body fat from last week",
        created_at=datetime.now()
    )
}

# Counters for generating new IDs
user_id_counter = len(users_db) + 1
workout_id_counter = len(workouts_db) + 1
exercise_id_counter = len(exercises_db) + 1
exercise_set_id_counter = len(exercise_sets_db) + 1
workout_plan_id_counter = len(workout_plans_db) + 1
progress_log_id_counter = len(progress_logs_db) + 1 