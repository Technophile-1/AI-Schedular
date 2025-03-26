"""
User data collection and management module.

This module handles collecting, storing, and retrieving user data
related to study habits, preferences, and availability.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class UserDataManager:
    """Manages user data collection and storage."""
    
    def __init__(self, data_dir: str = "user_data"):
        """
        Initialize the UserDataManager.
        
        Args:
            data_dir: Directory to store user data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def collect_initial_data(self) -> Dict[str, Any]:
        """
        Collect initial user data through interactive prompts.
        
        Returns:
            Dictionary containing user data
        """
        user_data = {
            "personal_info": self._collect_personal_info(),
            "study_preferences": self._collect_study_preferences(),
            "time_availability": self._collect_time_availability(),
            "productivity_patterns": self._collect_productivity_patterns(),
            "created_at": datetime.now().isoformat()
        }
        return user_data
    
    def _collect_personal_info(self) -> Dict[str, str]:
        """Collect basic personal information."""
        # In a real application, this would be an interactive prompt
        # For now, we'll return a sample
        return {
            "name": "",
            "education_level": "",
            "major": "",
            "goals": ""
        }
    
    def _collect_study_preferences(self) -> Dict[str, Any]:
        """Collect study preferences and subject priorities."""
        return {
            "preferred_subjects": [],
            "difficult_subjects": [],
            "study_environment": "",
            "learning_style": "",
            "session_length_preference": 0  # in minutes
        }
    
    def _collect_time_availability(self) -> Dict[str, List[Dict[str, Any]]]:
        """Collect weekly time availability."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        availability = {}
        
        for day in days:
            availability[day] = []
        
        return availability
    
    def _collect_productivity_patterns(self) -> Dict[str, Any]:
        """Collect productivity patterns and preferences."""
        return {
            "peak_productivity_times": [],
            "break_frequency": 0,  # in minutes
            "break_duration": 0,  # in minutes
            "sleep_schedule": {
                "weekday": {"sleep": "", "wake": ""},
                "weekend": {"sleep": "", "wake": ""}
            }
        }
    
    def save_user_data(self, user_id: str, data: Dict[str, Any]) -> None:
        """
        Save user data to file.
        
        Args:
            user_id: Unique identifier for the user
            data: User data dictionary to save
        """
        file_path = os.path.join(self.data_dir, f"{user_id}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load user data from file.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User data dictionary or None if not found
        """
        file_path = os.path.join(self.data_dir, f"{user_id}.json")
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def update_user_data(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update specific fields in user data.
        
        Args:
            user_id: Unique identifier for the user
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False otherwise
        """
        data = self.load_user_data(user_id)
        if not data:
            return False
            
        # Recursively update nested dictionaries
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    update_dict(d[k], v)
                else:
                    d[k] = v
        
        update_dict(data, updates)
        data["updated_at"] = datetime.now().isoformat()
        self.save_user_data(user_id, data)
        return True
    
    def record_feedback(self, user_id: str, session_id: str, feedback: Dict[str, Any]) -> None:
        """
        Record user feedback on a study session.
        
        Args:
            user_id: Unique identifier for the user
            session_id: Identifier for the study session
            feedback: Feedback data including ratings and comments
        """
        data = self.load_user_data(user_id)
        if not data:
            return
            
        if "session_feedback" not in data:
            data["session_feedback"] = {}
            
        feedback["recorded_at"] = datetime.now().isoformat()
        data["session_feedback"][session_id] = feedback
        self.save_user_data(user_id, data)