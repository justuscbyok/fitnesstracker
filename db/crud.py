from datetime import datetime, date
from typing import List, Optional, Dict, Any
from .database import (
    workouts_db, workout_id_counter,
    users_db, user_id_counter, users_passwords,
    exercises_db, exercise_id_counter,
    exercise_sets_db, exercise_set_id_counter,
    workout_plans_db, workout_plan_id_counter,
    progress_logs_db, progress_log_id_counter,
    user_stats_db, workout_exercise_sets
)
from ..models.schemas import (
    Workout, WorkoutCreate, WorkoutCategory, WorkoutDetail,
    User, UserCreate, UserUpdate,
    Exercise, ExerciseCreate,
    ExerciseSet, ExerciseSetCreate,
    WorkoutPlan, WorkoutPlanCreate,
    ProgressLog, ProgressLogCreate,
    UserStats, MuscleGroup, WorkoutFilter
)
from ..utils.auth import get_password_hash

# User CRUD operations
def get_users() -> List[User]:
    return list(users_db.values())

def get_user(user_id: int) -> Optional[User]:
    return users_db.get(user_id)

def get_user_by_username(username: str) -> Optional[User]:
    for user in users_db.values():
        if user.username == username:
            return user
    return None

def get_user_by_email(email: str) -> Optional[User]:
    for user in users_db.values():
        if user.email == email:
            return user
    return None

def create_user(user: UserCreate) -> User:
    global user_id_counter
    
    # Check if username or email already exists
    if get_user_by_username(user.username):
        return None
    if get_user_by_email(user.email):
        return None
    
    new_user = User(
        id=user_id_counter,
        created_at=datetime.now(),
        **user.model_dump(exclude={"password"})
    )
    
    users_db[user_id_counter] = new_user
    users_passwords[user.username] = get_password_hash(user.password)
    
    # Initialize user stats
    user_stats_db[user_id_counter] = UserStats(
        user_id=user_id_counter,
        last_updated=datetime.now()
    )
    
    user_id_counter += 1
    return new_user

def update_user(user_id: int, user_data: UserUpdate) -> Optional[User]:
    if user_id not in users_db:
        return None
    
    current_user = users_db[user_id]
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    users_db[user_id] = current_user
    return current_user

def delete_user(user_id: int) -> bool:
    if user_id not in users_db:
        return False
    
    user = users_db[user_id]
    del users_db[user_id]
    
    # Remove user password
    if user.username in users_passwords:
        del users_passwords[user.username]
    
    # Remove user stats
    if user_id in user_stats_db:
        del user_stats_db[user_id]
    
    return True

# Workout CRUD operations
def get_workouts(filters: Optional[WorkoutFilter] = None) -> List[Workout]:
    workouts = list(workouts_db.values())
    
    if not filters:
        return workouts
    
    filtered_workouts = workouts.copy()
    
    # Apply date filters
    if filters.from_date:
        filtered_workouts = [w for w in filtered_workouts if w.created_at.date() >= filters.from_date]
    if filters.to_date:
        filtered_workouts = [w for w in filtered_workouts if w.created_at.date() <= filters.to_date]
    
    # Apply category filter
    if filters.categories:
        filtered_workouts = [w for w in filtered_workouts if w.category in filters.categories]
    
    # Apply duration filters
    if filters.min_duration:
        filtered_workouts = [w for w in filtered_workouts if w.duration_minutes >= filters.min_duration]
    if filters.max_duration:
        filtered_workouts = [w for w in filtered_workouts if w.duration_minutes <= filters.max_duration]
    
    # Filter by muscle groups is more complex since it requires looking at exercises
    if filters.muscle_groups:
        result = []
        for workout in filtered_workouts:
            # Get exercise sets for workout
            exercise_set_ids = workout_exercise_sets.get(workout.id, [])
            exercise_ids = [exercise_sets_db[es_id].exercise_id for es_id in exercise_set_ids if es_id in exercise_sets_db]
            
            # Check if any exercise targets the requested muscle groups
            for exercise_id in exercise_ids:
                exercise = exercises_db.get(exercise_id)
                if exercise and any(mg in exercise.muscle_groups for mg in filters.muscle_groups):
                    result.append(workout)
                    break
        filtered_workouts = result
    
    return filtered_workouts

def get_workouts_by_user(user_id: int) -> List[Workout]:
    return [workout for workout in workouts_db.values() if workout.user_id == user_id]

def get_workouts_by_category(category: WorkoutCategory) -> List[Workout]:
    return [workout for workout in workouts_db.values() if workout.category == category]

def get_workout(workout_id: int) -> Optional[Workout]:
    return workouts_db.get(workout_id)

def get_workout_detail(workout_id: int) -> Optional[WorkoutDetail]:
    workout = workouts_db.get(workout_id)
    if not workout:
        return None
    
    # Get exercise sets for the workout
    exercise_set_ids = workout_exercise_sets.get(workout_id, [])
    exercise_sets = [exercise_sets_db[es_id] for es_id in exercise_set_ids if es_id in exercise_sets_db]
    
    # Create detailed workout with exercise sets
    workout_detail = WorkoutDetail(
        **workout.model_dump(),
        exercise_sets=exercise_sets
    )
    
    return workout_detail

def create_workout(workout: WorkoutCreate, user_id: Optional[int] = None) -> WorkoutDetail:
    global workout_id_counter, exercise_set_id_counter
    
    # Create workout
    new_workout = Workout(
        id=workout_id_counter,
        created_at=datetime.now(),
        user_id=user_id,
        **workout.model_dump(exclude={"exercise_sets"})
    )
    
    workouts_db[workout_id_counter] = new_workout
    
    # Initialize exercise sets list for this workout
    workout_exercise_sets[workout_id_counter] = []
    
    # Add exercise sets if provided
    exercise_sets = []
    if workout.exercise_sets:
        for es_data in workout.exercise_sets:
            new_exercise_set = ExerciseSet(
                id=exercise_set_id_counter,
                **es_data.model_dump()
            )
            
            exercise_sets_db[exercise_set_id_counter] = new_exercise_set
            workout_exercise_sets[workout_id_counter].append(exercise_set_id_counter)
            exercise_sets.append(new_exercise_set)
            exercise_set_id_counter += 1
    
    # Update user stats if user provided
    if user_id and user_id in user_stats_db:
        user_stats = user_stats_db[user_id]
        user_stats.total_workouts += 1
        user_stats.total_workout_minutes += workout.duration_minutes
        user_stats.last_workout_date = date.today()
        
        # Check for streak
        if user_stats.last_workout_date == date.today():
            user_stats.streak_days += 1
        else:
            user_stats.streak_days = 1
        
        user_stats.last_updated = datetime.now()
    
    workout_id_counter += 1
    
    # Return detailed workout with exercise sets
    return WorkoutDetail(
        **new_workout.model_dump(),
        exercise_sets=exercise_sets
    )

def update_workout(workout_id: int, workout_data: WorkoutCreate) -> Optional[WorkoutDetail]:
    if workout_id not in workouts_db:
        return None
    
    # Update workout
    updated_workout = Workout(
        id=workout_id,
        created_at=workouts_db[workout_id].created_at,
        user_id=workouts_db[workout_id].user_id,
        **workout_data.model_dump(exclude={"exercise_sets"})
    )
    
    workouts_db[workout_id] = updated_workout
    
    # Update exercise sets if provided
    if workout_data.exercise_sets:
        # Remove existing exercise sets
        for es_id in workout_exercise_sets.get(workout_id, []):
            if es_id in exercise_sets_db:
                del exercise_sets_db[es_id]
        
        # Clear exercise sets list
        workout_exercise_sets[workout_id] = []
        
        # Add new exercise sets
        for es_data in workout_data.exercise_sets:
            global exercise_set_id_counter
            new_exercise_set = ExerciseSet(
                id=exercise_set_id_counter,
                **es_data.model_dump()
            )
            
            exercise_sets_db[exercise_set_id_counter] = new_exercise_set
            workout_exercise_sets[workout_id].append(exercise_set_id_counter)
            exercise_set_id_counter += 1
    
    # Return updated workout detail
    return get_workout_detail(workout_id)

def delete_workout(workout_id: int) -> bool:
    if workout_id not in workouts_db:
        return False
    
    # Delete exercise sets associated with the workout
    for es_id in workout_exercise_sets.get(workout_id, []):
        if es_id in exercise_sets_db:
            del exercise_sets_db[es_id]
    
    # Delete workout exercise sets mapping
    if workout_id in workout_exercise_sets:
        del workout_exercise_sets[workout_id]
    
    # Delete workout
    del workouts_db[workout_id]
    
    return True

# Exercise CRUD operations
def get_exercises() -> List[Exercise]:
    return list(exercises_db.values())

def get_exercises_by_muscle_group(muscle_group: MuscleGroup) -> List[Exercise]:
    return [ex for ex in exercises_db.values() if muscle_group in ex.muscle_groups]

def get_exercise(exercise_id: int) -> Optional[Exercise]:
    return exercises_db.get(exercise_id)

def create_exercise(exercise: ExerciseCreate, user_id: Optional[int] = None) -> Exercise:
    global exercise_id_counter
    
    new_exercise = Exercise(
        id=exercise_id_counter,
        created_by=user_id,
        **exercise.model_dump()
    )
    
    exercises_db[exercise_id_counter] = new_exercise
    exercise_id_counter += 1
    
    return new_exercise

def update_exercise(exercise_id: int, exercise_data: ExerciseCreate) -> Optional[Exercise]:
    if exercise_id not in exercises_db:
        return None
    
    updated_exercise = Exercise(
        id=exercise_id,
        created_by=exercises_db[exercise_id].created_by,
        **exercise_data.model_dump()
    )
    
    exercises_db[exercise_id] = updated_exercise
    return updated_exercise

def delete_exercise(exercise_id: int) -> bool:
    if exercise_id not in exercises_db:
        return False
    
    # Check if exercise is used in any exercise set
    for es in exercise_sets_db.values():
        if es.exercise_id == exercise_id:
            return False  # Can't delete exercise that's in use
    
    del exercises_db[exercise_id]
    return True

# Workout Plan CRUD operations
def get_workout_plans() -> List[WorkoutPlan]:
    return list(workout_plans_db.values())

def get_workout_plans_by_user(user_id: int) -> List[WorkoutPlan]:
    return [plan for plan in workout_plans_db.values() if plan.created_by == user_id]

def get_workout_plan(plan_id: int) -> Optional[WorkoutPlan]:
    return workout_plans_db.get(plan_id)

def create_workout_plan(plan: WorkoutPlanCreate, user_id: int) -> WorkoutPlan:
    global workout_plan_id_counter
    
    new_plan = WorkoutPlan(
        id=workout_plan_id_counter,
        created_at=datetime.now(),
        created_by=user_id,
        workouts=[],
        **plan.model_dump()
    )
    
    workout_plans_db[workout_plan_id_counter] = new_plan
    workout_plan_id_counter += 1
    
    return new_plan

def update_workout_plan(plan_id: int, plan_data: WorkoutPlanCreate) -> Optional[WorkoutPlan]:
    if plan_id not in workout_plans_db:
        return None
    
    current_plan = workout_plans_db[plan_id]
    
    updated_plan = WorkoutPlan(
        id=plan_id,
        created_at=current_plan.created_at,
        created_by=current_plan.created_by,
        workouts=current_plan.workouts,
        **plan_data.model_dump()
    )
    
    workout_plans_db[plan_id] = updated_plan
    return updated_plan

def delete_workout_plan(plan_id: int) -> bool:
    if plan_id not in workout_plans_db:
        return False
    
    del workout_plans_db[plan_id]
    return True

def add_workout_to_plan(plan_id: int, workout_id: int) -> Optional[WorkoutPlan]:
    if plan_id not in workout_plans_db or workout_id not in workouts_db:
        return None
    
    plan = workout_plans_db[plan_id]
    
    if workout_id not in plan.workouts:
        plan.workouts.append(workout_id)
    
    return plan

def remove_workout_from_plan(plan_id: int, workout_id: int) -> Optional[WorkoutPlan]:
    if plan_id not in workout_plans_db:
        return None
    
    plan = workout_plans_db[plan_id]
    
    if workout_id in plan.workouts:
        plan.workouts.remove(workout_id)
    
    return plan

# Progress Log CRUD operations
def get_progress_logs_by_user(user_id: int) -> List[ProgressLog]:
    return [log for log in progress_logs_db.values() if log.user_id == user_id]

def get_progress_log(log_id: int) -> Optional[ProgressLog]:
    return progress_logs_db.get(log_id)

def create_progress_log(log: ProgressLogCreate, user_id: int) -> ProgressLog:
    global progress_log_id_counter
    
    new_log = ProgressLog(
        id=progress_log_id_counter,
        user_id=user_id,
        created_at=datetime.now(),
        **log.model_dump()
    )
    
    progress_logs_db[progress_log_id_counter] = new_log
    
    # Update user stats
    if user_id in user_stats_db:
        user_stats = user_stats_db[user_id]
        
        if log.weight:
            user_stats.weight = log.weight
            
        if log.body_fat_percentage:
            user_stats.body_fat_percentage = log.body_fat_percentage
            
        user_stats.last_updated = datetime.now()
    
    progress_log_id_counter += 1
    return new_log

def delete_progress_log(log_id: int) -> bool:
    if log_id not in progress_logs_db:
        return False
    
    del progress_logs_db[log_id]
    return True

# User Stats operations
def get_user_stats(user_id: int) -> Optional[UserStats]:
    return user_stats_db.get(user_id) 