"""
Study planner module for creating and managing study plans.

This module integrates user data and AI optimization to create
comprehensive study plans.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from study_scheduler.ai.optimizer import StudyOptimizer
from study_scheduler.data.user_data import UserDataManager

class StudyPlanner:
    """
    Study planner that creates and manages personalized study plans.
    """
    
    def __init__(self, user_data_manager: UserDataManager):
        """
        Initialize the study planner.
        
        Args:
            user_data_manager: Manager for user data
        """
        self.user_data_manager = user_data_manager
        self.optimizer = StudyOptimizer()
        
    def create_study_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Create a personalized study plan for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Study plan dictionary or None if user data not found
        """
        # Load user data
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data:
            return None
            
        # Create optimized schedule
        schedule = self.optimizer.create_optimized_schedule(user_data)
        
        # Create complete study plan
        plan = {
            "plan_id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "schedule": schedule,
            "metadata": {
                "version": 1,
                "optimization_factors": [
                    "productivity_patterns",
                    "subject_difficulty",
                    "time_availability"
                ]
            }
        }
        
        # Save the plan
        self._save_plan(user_id, plan)
        
        return plan
    
    def _save_plan(self, user_id: str, plan: Dict[str, Any]) -> None:
        """
        Save a study plan to the user's data.
        
        Args:
            user_id: Unique identifier for the user
            plan: Study plan to save
        """
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data:
            return
            
        if "study_plans" not in user_data:
            user_data["study_plans"] = {}
            
        user_data["study_plans"][plan["plan_id"]] = plan
        self.user_data_manager.save_user_data(user_id, user_data)
    
    def get_study_plan(self, user_id: str, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific study plan.
        
        Args:
            user_id: Unique identifier for the user
            plan_id: Unique identifier for the plan
            
        Returns:
            Study plan dictionary or None if not found
        """
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data or "study_plans" not in user_data:
            return None
            
        return user_data["study_plans"].get(plan_id)
    
    def get_latest_study_plan(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest study plan for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Latest study plan or None if no plans exist
        """
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data or "study_plans" not in user_data:
            return None
            
        plans = user_data["study_plans"]
        if not plans:
            return None
            
        # Find the latest plan by creation date
        latest_plan = max(
            plans.values(), 
            key=lambda p: datetime.fromisoformat(p["created_at"])
        )
        
        return latest_plan
    
    def update_plan_from_feedback(
        self, 
        user_id: str, 
        plan_id: str, 
        feedback: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a study plan based on user feedback.
        
        Args:
            user_id: Unique identifier for the user
            plan_id: Unique identifier for the plan
            feedback: User feedback on the plan
            
        Returns:
            Updated study plan or None if original plan not found
        """
        # Get the original plan
        original_plan = self.get_study_plan(user_id, plan_id)
        if not original_plan:
            return None
            
        # Adjust the schedule based on feedback
        adjusted_schedule = self.optimizer.adjust_schedule_from_feedback(
            original_plan["schedule"],
            feedback
        )
        
        # Create a new plan version
        new_plan = {
            "plan_id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "schedule": adjusted_schedule,
            "based_on": plan_id,
            "feedback_applied": feedback,
            "metadata": {
                "version": original_plan["metadata"]["version"] + 1,
                "optimization_factors": original_plan["metadata"]["optimization_factors"] + ["user_feedback"]
            }
        }
        
        # Save the new plan
        self._save_plan(user_id, new_plan)
        
        return new_plan
    
    def get_daily_schedule(self, user_id: str, date: datetime) -> List[Dict[str, Any]]:
        """
        Get the study schedule for a specific day.
        
        Args:
            user_id: Unique identifier for the user
            date: Date to get schedule for
            
        Returns:
            List of study sessions for the day
        """
        # Get the latest plan
        plan = self.get_latest_study_plan(user_id)
        if not plan:
            return []
            
        # Get the day of the week
        day_name = date.strftime("%A")
        
        # Get the schedule for that day
        daily_schedule = plan["schedule"]["daily_schedule"].get(day_name, [])
        
        # Add the actual date to each session
        for session in daily_schedule:
            session["date"] = date.strftime("%Y-%m-%d")
            
        return daily_schedule
    
    def get_weekly_schedule(self, user_id: str, start_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get the study schedule for a week.
        
        Args:
            user_id: Unique identifier for the user
            start_date: Start date of the week
            
        Returns:
            Dictionary mapping dates to study sessions
        """
        weekly_schedule = {}
        
        # Get schedule for each day of the week
        for i in range(7):
            date = start_date + timedelta(days=i)
            daily_schedule = self.get_daily_schedule(user_id, date)
            weekly_schedule[date.strftime("%Y-%m-%d")] = daily_schedule
            
        return weekly_schedule
    
    def record_session_completion(
        self, 
        user_id: str, 
        session_data: Dict[str, Any], 
        completion_data: Dict[str, Any]
    ) -> None:
        """
        Record the completion of a study session.
        
        Args:
            user_id: Unique identifier for the user
            session_data: Data about the study session
            completion_data: Data about the completion (rating, notes, etc.)
        """
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data:
            return
            
        if "completed_sessions" not in user_data:
            user_data["completed_sessions"] = []
            
        # Combine session and completion data
        session_record = {
            **session_data,
            **completion_data,
            "completed_at": datetime.now().isoformat()
        }
        
        user_data["completed_sessions"].append(session_record)
        self.user_data_manager.save_user_data(user_id, user_data)
        
        # Update performance metrics
        self._update_performance_metrics(user_id, session_record)
    
    def _update_performance_metrics(self, user_id: str, session_record: Dict[str, Any]) -> None:
        """
        Update performance metrics based on completed sessions.
        
        Args:
            user_id: Unique identifier for the user
            session_record: Data about the completed session
        """
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data:
            return
            
        if "performance_metrics" not in user_data:
            user_data["performance_metrics"] = {
                "subjects": {},
                "time_of_day": {
                    "morning": {"sessions": 0, "total_rating": 0},
                    "afternoon": {"sessions": 0, "total_rating": 0},
                    "evening": {"sessions": 0, "total_rating": 0},
                    "night": {"sessions": 0, "total_rating": 0}
                },
                "days_of_week": {}
            }
            
        metrics = user_data["performance_metrics"]
        
        # Update subject metrics
        subject = session_record.get("subject")
        if subject:
            if subject not in metrics["subjects"]:
                metrics["subjects"][subject] = {
                    "sessions": 0,
                    "total_rating": 0,
                    "total_duration": 0
                }
                
            subject_metrics = metrics["subjects"][subject]
            subject_metrics["sessions"] += 1
            subject_metrics["total_duration"] += session_record.get("duration_minutes", 0)
            
            if "rating" in session_record:
                subject_metrics["total_rating"] += session_record["rating"]
        
        # Update time of day metrics
        start_time = session_record.get("start_time")
        if start_time:
            try:
                hour = datetime.strptime(start_time, "%H:%M").hour
                time_of_day = self._determine_time_of_day(hour)
                
                time_metrics = metrics["time_of_day"][time_of_day]
                time_metrics["sessions"] += 1
                
                if "rating" in session_record:
                    time_metrics["total_rating"] += session_record["rating"]
            except ValueError:
                pass
        
        # Update day of week metrics
        date_str = session_record.get("date")
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                day_name = date.strftime("%A")
                
                if day_name not in metrics["days_of_week"]:
                    metrics["days_of_week"][day_name] = {
                        "sessions": 0,
                        "total_rating": 0
                    }
                    
                day_metrics = metrics["days_of_week"][day_name]
                day_metrics["sessions"] += 1
                
                if "rating" in session_record:
                    day_metrics["total_rating"] += session_record["rating"]
            except ValueError:
                pass
        
        # Save updated metrics
        self.user_data_manager.save_user_data(user_id, user_data)
    
    def _determine_time_of_day(self, hour: int) -> str:
        """
        Determine the time of day category based on hour.
        
        Args:
            hour: Hour of the day (0-23)
            
        Returns:
            Time of day category (morning, afternoon, evening, night)
        """
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"