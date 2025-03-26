"""
Notification system for study reminders and motivational messages.

This module handles sending notifications to users about upcoming study sessions,
breaks, and provides motivational content.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class NotificationManager:
    """
    Manages notifications for study sessions and motivational content.
    """
    
    def __init__(self):
        """Initialize the notification manager."""
        self.motivational_quotes = [
            "The expert in anything was once a beginner.",
            "Success is the sum of small efforts, repeated day in and day out.",
            "The secret of getting ahead is getting started.",
            "Don't wish it were easier; wish you were better.",
            "The harder you work for something, the greater you'll feel when you achieve it.",
            "Learning is never done without errors and defeat.",
            "The beautiful thing about learning is that no one can take it away from you.",
            "Education is the passport to the future.",
            "The more that you read, the more things you will know.",
            "The only way to do great work is to love what you do."
        ]
        
        self.study_tips = [
            "Break your study sessions into 25-minute chunks with 5-minute breaks.",
            "Stay hydrated while studying to maintain focus.",
            "Review your notes within 24 hours of taking them to improve retention.",
            "Teach what you've learned to someone else to solidify your understanding.",
            "Create mind maps to visualize connections between concepts.",
            "Use active recall instead of passive re-reading.",
            "Study in a quiet, well-lit environment with minimal distractions.",
            "Get enough sleep before and after studying to help memory consolidation.",
            "Use spaced repetition to review material at optimal intervals.",
            "Take brief exercise breaks to boost your energy and focus."
        ]
    
    def get_upcoming_session_notifications(
        self, 
        schedule: List[Dict[str, Any]], 
        current_time: datetime,
        notification_window_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for upcoming study sessions.
        
        Args:
            schedule: List of scheduled study sessions
            current_time: Current datetime
            notification_window_minutes: How many minutes before a session to notify
            
        Returns:
            List of notification dictionaries
        """
        notifications = []
        
        for session in schedule:
            session_date = session.get("date", current_time.strftime("%Y-%m-%d"))
            session_time = session.get("start_time", "")
            
            if not session_time:
                continue
                
            try:
                # Parse session datetime
                session_dt = datetime.strptime(
                    f"{session_date} {session_time}", 
                    "%Y-%m-%d %H:%M"
                )
                
                # Calculate time until session
                time_until_session = (session_dt - current_time).total_seconds() / 60
                
                # If session is within notification window
                if 0 <= time_until_session <= notification_window_minutes:
                    notifications.append({
                        "type": "upcoming_session",
                        "subject": session["subject"],
                        "start_time": session_time,
                        "minutes_until": int(time_until_session),
                        "message": f"Your {session['subject']} study session starts in {int(time_until_session)} minutes!"
                    })
            except (ValueError, KeyError):
                continue
        
        return notifications
    
    def get_break_notification(
        self, 
        current_session: Dict[str, Any], 
        current_time: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Get notification for an upcoming break.
        
        Args:
            current_session: Currently active study session
            current_time: Current datetime
            
        Returns:
            Break notification dictionary or None
        """
        session_date = current_session.get("date", current_time.strftime("%Y-%m-%d"))
        end_time = current_session.get("end_time", "")
        
        if not end_time:
            return None
            
        try:
            # Parse session end time
            end_dt = datetime.strptime(
                f"{session_date} {end_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # If session is ending within 5 minutes
            time_until_end = (end_dt - current_time).total_seconds() / 60
            if 0 <= time_until_end <= 5:
                break_duration = current_session.get("break_after", 0)
                
                if break_duration > 0:
                    return {
                        "type": "break",
                        "minutes_until": int(time_until_end),
                        "break_duration": break_duration,
                        "message": f"Your study session is ending soon. Take a {break_duration}-minute break!"
                    }
        except (ValueError, KeyError):
            pass
            
        return None
    
    def get_motivational_message(self) -> Dict[str, Any]:
        """
        Get a random motivational message.
        
        Returns:
            Dictionary with motivational content
        """
        message_type = random.choice(["quote", "tip"])
        
        if message_type == "quote":
            content = random.choice(self.motivational_quotes)
            return {
                "type": "motivation",
                "content_type": "quote",
                "message": content
            }
        else:
            content = random.choice(self.study_tips)
            return {
                "type": "motivation",
                "content_type": "tip",
                "message": content
            }
    
    def get_progress_notification(
        self, 
        completed_sessions: int, 
        total_sessions: int
    ) -> Dict[str, Any]:
        """
        Get a notification about study progress.
        
        Args:
            completed_sessions: Number of completed study sessions
            total_sessions: Total number of scheduled sessions
            
        Returns:
            Progress notification dictionary
        """
        if total_sessions == 0:
            percentage = 0
        else:
            percentage = (completed_sessions / total_sessions) * 100
            
        if percentage == 0:
            message = "Time to start your study sessions for today!"
        elif percentage < 25:
            message = "You're making progress! Keep going!"
        elif percentage < 50:
            message = "You're getting there! Almost halfway through your sessions."
        elif percentage < 75:
            message = "Great progress! You've completed most of your study sessions."
        elif percentage < 100:
            message = "Almost done! Just a few more sessions to go."
        else:
            message = "Congratulations! You've completed all your study sessions for today."
            
        return {
            "type": "progress",
            "completed": completed_sessions,
            "total": total_sessions,
            "percentage": round(percentage, 1),
            "message": message
        }
    
    def get_achievement_notification(
        self, 
        achievement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get a notification for a user achievement.
        
        Args:
            achievement: Achievement data
            
        Returns:
            Achievement notification dictionary
        """
        return {
            "type": "achievement",
            "achievement_id": achievement.get("id", ""),
            "title": achievement.get("title", ""),
            "description": achievement.get("description", ""),
            "message": f"Congratulations! You've earned: {achievement.get('title', '')}"
        }