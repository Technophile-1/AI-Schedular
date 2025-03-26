"""
AI Optimizer for study scheduling.

This module contains algorithms for optimizing study schedules based on
user data, preferences, and performance history.
"""

from typing import Dict, List, Any, Tuple
import random
from datetime import datetime, timedelta

class StudyOptimizer:
    """
    AI-based optimizer for creating personalized study schedules.
    """
    
    def __init__(self):
        """Initialize the study optimizer."""
        self.productivity_weights = {
            "morning": 1.0,
            "afternoon": 0.8,
            "evening": 0.7,
            "night": 0.5
        }
        
        # Default subject difficulty weights
        self.difficulty_weights = {
            "very_easy": 0.5,
            "easy": 0.7,
            "medium": 1.0,
            "hard": 1.3,
            "very_hard": 1.5
        }
    
    def create_optimized_schedule(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an optimized study schedule based on user data.
        
        Args:
            user_data: Dictionary containing user preferences and patterns
            
        Returns:
            Dictionary containing the optimized schedule
        """
        # Extract relevant data
        availability = user_data.get("time_availability", {})
        preferences = user_data.get("study_preferences", {})
        productivity = user_data.get("productivity_patterns", {})
        
        # Get subjects and their priorities
        subjects = self._extract_subjects(preferences)
        
        # Create empty schedule
        schedule = {
            "daily_schedule": {},
            "weekly_overview": {},
            "generated_at": datetime.now().isoformat(),
            "version": 1
        }
        
        # Generate daily schedules
        for day, time_slots in availability.items():
            schedule["daily_schedule"][day] = self._generate_day_schedule(
                day, time_slots, subjects, productivity
            )
        
        # Generate weekly overview
        schedule["weekly_overview"] = self._generate_weekly_overview(schedule["daily_schedule"])
        
        return schedule
    
    def _extract_subjects(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract and prepare subject data with priorities.
        
        Args:
            preferences: User study preferences
            
        Returns:
            List of subject dictionaries with metadata
        """
        preferred = preferences.get("preferred_subjects", [])
        difficult = preferences.get("difficult_subjects", [])
        
        subjects = []
        
        # Process preferred subjects
        for subject in preferred:
            difficulty = "medium"
            if subject in difficult:
                difficulty = "hard"
                
            subjects.append({
                "name": subject,
                "difficulty": difficulty,
                "priority": "high" if subject in difficult else "medium",
                "optimal_time": self._determine_optimal_time(subject, difficulty)
            })
        
        # Add any difficult subjects not already included
        for subject in difficult:
            if subject not in preferred:
                subjects.append({
                    "name": subject,
                    "difficulty": "hard",
                    "priority": "high",
                    "optimal_time": self._determine_optimal_time(subject, "hard")
                })
        
        return subjects
    
    def _determine_optimal_time(self, subject: str, difficulty: str) -> str:
        """
        Determine the optimal time of day to study a subject.
        In a real application, this would use machine learning based on user data.
        
        Args:
            subject: Subject name
            difficulty: Subject difficulty level
            
        Returns:
            Time of day (morning, afternoon, evening, night)
        """
        # This is a simplified placeholder implementation
        if difficulty == "hard":
            return "morning"  # Study difficult subjects when fresh
        elif difficulty == "medium":
            return "afternoon"
        else:
            return "evening"
    
    def _generate_day_schedule(
        self, 
        day: str, 
        time_slots: List[Dict[str, Any]], 
        subjects: List[Dict[str, Any]],
        productivity: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate a schedule for a single day.
        
        Args:
            day: Day of the week
            time_slots: Available time slots for the day
            subjects: List of subjects to schedule
            productivity: User productivity patterns
            
        Returns:
            List of scheduled study sessions
        """
        day_schedule = []
        
        # Sort subjects by priority
        sorted_subjects = sorted(
            subjects, 
            key=lambda x: 0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2
        )
        
        # Get peak productivity times
        peak_times = productivity.get("peak_productivity_times", [])
        
        # Preferred session length
        session_length = productivity.get("session_length_preference", 45)
        
        # Break parameters
        break_frequency = productivity.get("break_frequency", 25)
        break_duration = productivity.get("break_duration", 5)
        
        # For each available time slot
        for slot in time_slots:
            start_time = slot.get("start", "")
            end_time = slot.get("end", "")
            
            if not start_time or not end_time:
                continue
                
            # Calculate duration in minutes
            try:
                start_dt = datetime.strptime(start_time, "%H:%M")
                end_dt = datetime.strptime(end_time, "%H:%M")
                duration_minutes = (end_dt - start_dt).seconds // 60
            except ValueError:
                continue
            
            # Skip if slot is too short
            if duration_minutes < 20:
                continue
            
            # Determine time of day
            hour = start_dt.hour
            time_of_day = self._determine_time_of_day(hour)
            
            # Find suitable subjects for this time slot
            suitable_subjects = [
                s for s in sorted_subjects 
                if s["optimal_time"] == time_of_day or time_of_day in peak_times
            ]
            
            if not suitable_subjects and sorted_subjects:
                # If no suitable subjects, use any available subjects
                suitable_subjects = sorted_subjects
            
            # Schedule study sessions within this time slot
            current_time = start_dt
            while (current_time + timedelta(minutes=session_length)) <= end_dt and suitable_subjects:
                # Select a subject
                subject = suitable_subjects.pop(0)
                
                # Add to schedule
                session_end = current_time + timedelta(minutes=session_length)
                day_schedule.append({
                    "subject": subject["name"],
                    "start_time": current_time.strftime("%H:%M"),
                    "end_time": session_end.strftime("%H:%M"),
                    "duration_minutes": session_length,
                    "difficulty": subject["difficulty"],
                    "break_after": break_duration if session_end < end_dt else 0
                })
                
                # Move to next time slot (including break if needed)
                current_time = session_end + timedelta(minutes=break_duration if session_end < end_dt else 0)
                
                # Put the subject back at the end if we still have time for more sessions
                if suitable_subjects:
                    suitable_subjects.append(subject)
        
        return day_schedule
    
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
    
    def _generate_weekly_overview(self, daily_schedule: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Generate a weekly overview of the study schedule.
        
        Args:
            daily_schedule: Dictionary of daily schedules
            
        Returns:
            Dictionary containing weekly statistics and overview
        """
        total_study_time = 0
        subject_time = {}
        subject_sessions = {}
        
        # Calculate statistics
        for day, sessions in daily_schedule.items():
            for session in sessions:
                subject = session["subject"]
                duration = session["duration_minutes"]
                
                total_study_time += duration
                
                if subject not in subject_time:
                    subject_time[subject] = 0
                    subject_sessions[subject] = 0
                    
                subject_time[subject] += duration
                subject_sessions[subject] += 1
        
        # Calculate percentages
        subject_percentage = {}
        for subject, time in subject_time.items():
            if total_study_time > 0:
                subject_percentage[subject] = round((time / total_study_time) * 100, 1)
            else:
                subject_percentage[subject] = 0
        
        return {
            "total_study_time_minutes": total_study_time,
            "total_study_time_hours": round(total_study_time / 60, 1),
            "subject_time_minutes": subject_time,
            "subject_sessions": subject_sessions,
            "subject_percentage": subject_percentage
        }
    
    def adjust_schedule_from_feedback(
        self, 
        schedule: Dict[str, Any], 
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adjust a study schedule based on user feedback.
        
        Args:
            schedule: Current study schedule
            feedback: User feedback on the schedule
            
        Returns:
            Adjusted study schedule
        """
        # Clone the schedule to avoid modifying the original
        adjusted_schedule = {
            "daily_schedule": {day: sessions.copy() for day, sessions in schedule["daily_schedule"].items()},
            "weekly_overview": schedule["weekly_overview"].copy(),
            "generated_at": datetime.now().isoformat(),
            "version": schedule.get("version", 1) + 1,
            "adjusted_based_on": feedback
        }
        
        # Apply adjustments based on feedback
        # This is a simplified implementation - a real system would use more sophisticated algorithms
        
        # Example: Adjust session lengths
        if "preferred_session_length" in feedback:
            new_length = feedback["preferred_session_length"]
            for day, sessions in adjusted_schedule["daily_schedule"].items():
                for i, session in enumerate(sessions):
                    # Adjust session length
                    old_end_time = datetime.strptime(session["end_time"], "%H:%M")
                    start_time = datetime.strptime(session["start_time"], "%H:%M")
                    
                    # Calculate new end time
                    new_end_time = start_time + timedelta(minutes=new_length)
                    
                    # Update session
                    sessions[i]["end_time"] = new_end_time.strftime("%H:%M")
                    sessions[i]["duration_minutes"] = new_length
        
        # Example: Adjust subject difficulty
        if "subject_difficulty_adjustments" in feedback:
            for subject, new_difficulty in feedback["subject_difficulty_adjustments"].items():
                for day, sessions in adjusted_schedule["daily_schedule"].items():
                    for i, session in enumerate(sessions):
                        if session["subject"] == subject:
                            sessions[i]["difficulty"] = new_difficulty
        
        # Regenerate weekly overview with adjusted schedule
        adjusted_schedule["weekly_overview"] = self._generate_weekly_overview(
            adjusted_schedule["daily_schedule"]
        )
        
        return adjusted_schedule
    
    def predict_optimal_study_time(
        self, 
        subject: str, 
        performance_history: List[Dict[str, Any]]
    ) -> str:
        """
        Predict the optimal time to study a specific subject based on past performance.
        
        Args:
            subject: Subject name
            performance_history: List of past study sessions with performance data
            
        Returns:
            Optimal time of day to study the subject
        """
        # Filter history for this subject
        subject_history = [
            session for session in performance_history 
            if session.get("subject") == subject
        ]
        
        if not subject_history:
            return "morning"  # Default if no history
        
        # Calculate average performance by time of day
        performance_by_time = {
            "morning": [],
            "afternoon": [],
            "evening": [],
            "night": []
        }
        
        for session in subject_history:
            time = session.get("start_time", "")
            performance = session.get("performance_rating", 0)
            
            if not time or performance == 0:
                continue
                
            try:
                hour = datetime.strptime(time, "%H:%M").hour
                time_of_day = self._determine_time_of_day(hour)
                performance_by_time[time_of_day].append(performance)
            except ValueError:
                continue
        
        # Calculate averages
        averages = {}
        for time_of_day, ratings in performance_by_time.items():
            if ratings:
                averages[time_of_day] = sum(ratings) / len(ratings)
            else:
                averages[time_of_day] = 0
        
        # Find time of day with highest average performance
        best_time = max(averages.items(), key=lambda x: x[1])
        
        return best_time[0] if best_time[1] > 0 else "morning"