"""
Main application UI for the AI Study Scheduler.

This module provides a Tkinter-based user interface for interacting with
the AI Study Scheduler application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import uuid
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional, Callable

from study_scheduler.data.user_data import UserDataManager
from study_scheduler.scheduler.planner import StudyPlanner
from study_scheduler.notifications.notifier import NotificationManager

class StudySchedulerApp:
    """
    Main application class for the AI Study Scheduler.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("AI Study Scheduler")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize data managers
        self.user_data_manager = UserDataManager()
        self.planner = StudyPlanner(self.user_data_manager)
        self.notifier = NotificationManager()
        
        # Current user and plan
        self.current_user_id = None
        self.current_plan = None
        
        # Create UI components
        self._create_menu()
        self._create_main_frame()
        
        # Start with login screen
        self._show_login_screen()
    
    def _create_menu(self):
        """Create the application menu bar."""
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New User", command=self._show_new_user_screen)
        file_menu.add_command(label="Login", command=self._show_login_screen)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Plan menu
        plan_menu = tk.Menu(self.menu_bar, tearoff=0)
        plan_menu.add_command(label="Create New Plan", command=self._create_new_plan)
        plan_menu.add_command(label="View Current Plan", command=self._show_current_plan)
        self.menu_bar.add_cascade(label="Plan", menu=plan_menu)
        
        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="Calendar View", command=self._show_calendar_view)
        view_menu.add_command(label="Statistics", command=self._show_statistics)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Help", command=self._show_help)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=self.menu_bar)
    
    def _create_main_frame(self):
        """Create the main application frame."""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _clear_main_frame(self):
        """Clear all widgets from the main frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def _show_login_screen(self):
        """Show the login screen."""
        self._clear_main_frame()
        
        # Create login frame
        login_frame = tk.Frame(self.main_frame)
        login_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            login_frame, 
            text="AI Study Scheduler", 
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=20)
        
        # User selection
        user_frame = tk.Frame(login_frame)
        user_frame.pack(pady=20)
        
        tk.Label(user_frame, text="Select User:").pack(side=tk.LEFT)
        
        # Get available users
        users = self._get_available_users()
        
        user_var = tk.StringVar()
        if users:
            user_dropdown = ttk.Combobox(user_frame, textvariable=user_var)
            user_dropdown['values'] = users
            user_dropdown.pack(side=tk.LEFT, padx=10)
            
            # Login button
            login_button = tk.Button(
                login_frame, 
                text="Login", 
                command=lambda: self._login_user(user_var.get())
            )
            login_button.pack(pady=10)
        else:
            tk.Label(
                user_frame, 
                text="No users found. Please create a new user."
            ).pack(side=tk.LEFT, padx=10)
        
        # New user button
        new_user_button = tk.Button(
            login_frame, 
            text="Create New User", 
            command=self._show_new_user_screen
        )
        new_user_button.pack(pady=10)
    
    def _get_available_users(self) -> List[str]:
        """
        Get a list of available user IDs.
        
        Returns:
            List of user IDs
        """
        # In a real application, this would query a database
        # For now, we'll just check for JSON files in the data directory
        users = []
        if os.path.exists(self.user_data_manager.data_dir):
            for filename in os.listdir(self.user_data_manager.data_dir):
                if filename.endswith(".json"):
                    users.append(filename[:-5])  # Remove .json extension
        return users
    
    def _login_user(self, user_id: str):
        """
        Log in a user.
        
        Args:
            user_id: User ID to log in
        """
        if not user_id:
            messagebox.showerror("Error", "Please select a user.")
            return
            
        # Load user data
        user_data = self.user_data_manager.load_user_data(user_id)
        if not user_data:
            messagebox.showerror("Error", f"Could not load data for user {user_id}.")
            return
            
        self.current_user_id = user_id
        
        # Get the latest plan
        self.current_plan = self.planner.get_latest_study_plan(user_id)
        
        # Show the dashboard
        self._show_dashboard()
    
    def _show_new_user_screen(self):
        """Show the new user creation screen."""
        self._clear_main_frame()
        
        # Create new user frame
        new_user_frame = tk.Frame(self.main_frame)
        new_user_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            new_user_frame, 
            text="Create New User", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Form fields
        form_frame = tk.Frame(new_user_frame)
        form_frame.pack(pady=10, fill=tk.X)
        
        # Personal info
        personal_frame = tk.LabelFrame(form_frame, text="Personal Information")
        personal_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(personal_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        name_var = tk.StringVar()
        tk.Entry(personal_frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(personal_frame, text="Education Level:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        education_var = tk.StringVar()
        education_dropdown = ttk.Combobox(personal_frame, textvariable=education_var, width=28)
        education_dropdown['values'] = ["High School", "Undergraduate", "Graduate", "Doctoral", "Other"]
        education_dropdown.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(personal_frame, text="Major/Field:").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        major_var = tk.StringVar()
        tk.Entry(personal_frame, textvariable=major_var, width=30).grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(personal_frame, text="Goals:").grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        goals_var = tk.StringVar()
        tk.Entry(personal_frame, textvariable=goals_var, width=30).grid(row=3, column=1, pady=5, padx=5)
        
        # Study preferences
        prefs_frame = tk.LabelFrame(form_frame, text="Study Preferences")
        prefs_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(prefs_frame, text="Preferred Subjects (comma-separated):").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        subjects_var = tk.StringVar()
        tk.Entry(prefs_frame, textvariable=subjects_var, width=30).grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(prefs_frame, text="Difficult Subjects (comma-separated):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        difficult_var = tk.StringVar()
        tk.Entry(prefs_frame, textvariable=difficult_var, width=30).grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(prefs_frame, text="Preferred Session Length (minutes):").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        session_length_var = tk.IntVar(value=45)
        tk.Spinbox(prefs_frame, from_=15, to=120, increment=5, textvariable=session_length_var, width=5).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Productivity patterns
        productivity_frame = tk.LabelFrame(form_frame, text="Productivity Patterns")
        productivity_frame.pack(pady=10, fill=tk.X, padx=20)
        
        tk.Label(productivity_frame, text="Peak Productivity Time:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        peak_time_var = tk.StringVar()
        peak_time_dropdown = ttk.Combobox(productivity_frame, textvariable=peak_time_var, width=28)
        peak_time_dropdown['values'] = ["Morning", "Afternoon", "Evening", "Night"]
        peak_time_dropdown.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(productivity_frame, text="Break Frequency (minutes):").grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        break_freq_var = tk.IntVar(value=25)
        tk.Spinbox(productivity_frame, from_=15, to=60, increment=5, textvariable=break_freq_var, width=5).grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        tk.Label(productivity_frame, text="Break Duration (minutes):").grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        break_dur_var = tk.IntVar(value=5)
        tk.Spinbox(productivity_frame, from_=5, to=30, increment=5, textvariable=break_dur_var, width=5).grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Submit button
        submit_button = tk.Button(
            new_user_frame, 
            text="Create User", 
            command=lambda: self._create_new_user({
                "personal_info": {
                    "name": name_var.get(),
                    "education_level": education_var.get(),
                    "major": major_var.get(),
                    "goals": goals_var.get()
                },
                "study_preferences": {
                    "preferred_subjects": [s.strip() for s in subjects_var.get().split(",") if s.strip()],
                    "difficult_subjects": [s.strip() for s in difficult_var.get().split(",") if s.strip()],
                    "session_length_preference": session_length_var.get()
                },
                "productivity_patterns": {
                    "peak_productivity_times": [peak_time_var.get()],
                    "break_frequency": break_freq_var.get(),
                    "break_duration": break_dur_var.get()
                }
            })
        )
        submit_button.pack(pady=20)
        
        # Back button
        back_button = tk.Button(
            new_user_frame, 
            text="Back to Login", 
            command=self._show_login_screen
        )
        back_button.pack(pady=10)
    
    def _create_new_user(self, form_data: Dict[str, Any]):
        """
        Create a new user with the provided form data.
        
        Args:
            form_data: User data from the form
        """
        # Validate required fields
        if not form_data["personal_info"]["name"]:
            messagebox.showerror("Error", "Please enter your name.")
            return
            
        if not form_data["study_preferences"]["preferred_subjects"]:
            messagebox.showerror("Error", "Please enter at least one preferred subject.")
            return
        
        # Generate a user ID
        user_id = str(uuid.uuid4())
        
        # Create user data structure
        user_data = {
            "personal_info": form_data["personal_info"],
            "study_preferences": form_data["study_preferences"],
            "productivity_patterns": form_data["productivity_patterns"],
            "time_availability": self._generate_default_availability(),
            "created_at": datetime.now().isoformat()
        }
        
        # Save user data
        self.user_data_manager.save_user_data(user_id, user_data)
        
        # Set as current user
        self.current_user_id = user_id
        
        # Show time availability screen
        messagebox.showinfo(
            "Success", 
            "User created successfully! Now let's set up your weekly availability."
        )
        self._show_availability_setup()
    
    def _generate_default_availability(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate default time availability for a new user.
        
        Returns:
            Dictionary mapping days to available time slots
        """
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        availability = {}
        
        for day in days:
            # Default to two slots per weekday, one for weekend
            if day in ["Saturday", "Sunday"]:
                availability[day] = [
                    {"start": "10:00", "end": "12:00"}
                ]
            else:
                availability[day] = [
                    {"start": "09:00", "end": "12:00"},
                    {"start": "14:00", "end": "17:00"}
                ]
        
        return availability
    
    def _show_availability_setup(self):
        """Show the time availability setup screen."""
        self._clear_main_frame()
        
        # Load user data
        user_data = self.user_data_manager.load_user_data(self.current_user_id)
        if not user_data:
            messagebox.showerror("Error", "Could not load user data.")
            self._show_login_screen()
            return
            
        # Create availability frame
        avail_frame = tk.Frame(self.main_frame)
        avail_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(
            avail_frame, 
            text="Set Your Weekly Availability", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            avail_frame,
            text="Enter the times you are available to study each day.",
            font=("Arial", 12)
        )
        instructions.pack(pady=10)
        
        # Create a notebook with tabs for each day
        notebook = ttk.Notebook(avail_frame)
        notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Current availability
        availability = user_data.get("time_availability", {})
        
        # Day tabs and time slot entries
        day_frames = {}
        day_slots = {}
        
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            # Create frame for this day
            day_frame = ttk.Frame(notebook)
            notebook.add(day_frame, text=day)
            day_frames[day] = day_frame
            
            # Slots for this day
            day_slots[day] = []
            
            # Add existing slots
            day_availability = availability.get(day, [])
            
            # Slots container
            slots_frame = tk.Frame(day_frame)
            slots_frame.pack(fill=tk.X, pady=10)
            
            # Add header
            tk.Label(slots_frame, text="Start Time", width=15).grid(row=0, column=0, padx=5, pady=5)
            tk.Label(slots_frame, text="End Time", width=15).grid(row=0, column=1, padx=5, pady=5)
            tk.Label(slots_frame, text="Actions", width=10).grid(row=0, column=2, padx=5, pady=5)
            
            # Add existing slots or a default empty one
            if day_availability:
                for i, slot in enumerate(day_availability):
                    self._add_time_slot(slots_frame, i+1, slot, day_slots[day])
            else:
                self._add_time_slot(slots_frame, 1, {"start": "", "end": ""}, day_slots[day])
            
            # Add button
            add_button = tk.Button(
                day_frame,
                text="Add Time Slot",
                command=lambda d=day, sf=slots_frame, ds=day_slots[day]: self._add_time_slot(
                    sf, len(ds)+1, {"start": "", "end": ""}, ds
                )
            )
            add_button.pack(pady=10)
        
        # Save button
        save_button = tk.Button(
            avail_frame,
            text="Save Availability",
            command=lambda: self._save_availability(day_slots)
        )
        save_button.pack(pady=20)
    
    def _add_time_slot(
        self, 
        parent: tk.Frame, 
        row: int, 
        slot: Dict[str, str], 
        slot_list: List
    ):
        """
        Add a time slot entry to a day frame.
        
        Args:
            parent: Parent frame
            row: Row number
            slot: Time slot data
            slot_list: List to store slot variables
        """
        start_var = tk.StringVar(value=slot.get("start", ""))
        end_var = tk.StringVar(value=slot.get("end", ""))
        
        # Create time entry widgets
        start_entry = tk.Entry(parent, textvariable=start_var, width=15)
        start_entry.grid(row=row, column=0, padx=5, pady=5)
        
        end_entry = tk.Entry(parent, textvariable=end_var, width=15)
        end_entry.grid(row=row, column=1, padx=5, pady=5)
        
        # Delete button
        delete_button = tk.Button(
            parent,
            text="Delete",
            command=lambda: self._delete_time_slot(parent, row, slot_list)
        )
        delete_button.grid(row=row, column=2, padx=5, pady=5)
        
        # Store variables
        slot_list.append((start_var, end_var))
    
    def _delete_time_slot(self, parent: tk.Frame, row: int, slot_list: List):
        """
        Delete a time slot entry.
        
        Args:
            parent: Parent frame
            row: Row number
            slot_list: List of slot variables
        """
        # Remove widgets in this row
        for widget in parent.grid_slaves(row=row):
            widget.destroy()
            
        # Remove from slot list
        if row-1 < len(slot_list):
            slot_list.pop(row-1)
            
        # Reposition remaining slots
        for i, r in enumerate(range(row+1, parent.grid_size()[1])):
            for widget in parent.grid_slaves(row=r):
                widget.grid(row=row+i, column=widget.grid_info()["column"])
    
    def _save_availability(self, day_slots: Dict[str, List]):
        """
        Save the user's time availability.
        
        Args:
            day_slots: Dictionary mapping days to time slot variables
        """
        # Load user data
        user_data = self.user_data_manager.load_user_data(self.current_user_id)
        if not user_data:
            messagebox.showerror("Error", "Could not load user data.")
            return
            
        # Create availability dictionary
        availability = {}
        
        for day, slots in day_slots.items():
            availability[day] = []
            
            for start_var, end_var in slots:
                start = start_var.get().strip()
                end = end_var.get().strip()
                
                if start and end:
                    availability[day].append({
                        "start": start,
                        "end": end
                    })
        
        # Update user data
        user_data["time_availability"] = availability
        self.user_data_manager.save_user_data(self.current_user_id, user_data)
        
        # Create initial study plan
        self.current_plan = self.planner.create_study_plan(self.current_user_id)
        
        # Show success message
        messagebox.showinfo(
            "Success", 
            "Availability saved successfully! Your initial study plan has been created."
        )
        
        # Show dashboard
        self._show_dashboard()
    
    def _show_dashboard(self):
        """Show the main dashboard."""
        self._clear_main_frame()
        
        # Load user data
        user_data = self.user_data_manager.load_user_data(self.current_user_id)
        if not user_data:
            messagebox.showerror("Error", "Could not load user data.")
            self._show_login_screen()
            return
            
        # Create dashboard frame
        dashboard_frame = tk.Frame(self.main_frame)
        dashboard_frame.pack(expand=True, fill=tk.BOTH)
        
        # Header with user info
        header_frame = tk.Frame(dashboard_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        name = user_data.get("personal_info", {}).get("name", "User")
        
        welcome_label = tk.Label(
            header_frame,
            text=f"Welcome, {name}!",
            font=("Arial", 18, "bold")
        )
        welcome_label.pack(side=tk.LEFT, padx=20)
        
        # Today's date
        today = datetime.now()
        date_label = tk.Label(
            header_frame,
            text=f"Today: {today.strftime('%A, %B %d, %Y')}",
            font=("Arial", 12)
        )
        date_label.pack(side=tk.RIGHT, padx=20)
        
        # Main content area - split into two columns
        content_frame = tk.Frame(dashboard_frame)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Left column - Today's schedule
        left_frame = tk.Frame(content_frame, width=500)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        schedule_label = tk.Label(
            left_frame,
            text="Today's Study Schedule",
            font=("Arial", 14, "bold")
        )
        schedule_label.pack(pady=10)
        
        # Get today's schedule
        today_schedule = []
        if self.current_plan:
            day_name = today.strftime("%A")
            today_schedule = self.current_plan["schedule"]["daily_schedule"].get(day_name, [])
        
        # Create schedule display
        schedule_frame = tk.Frame(left_frame)
        schedule_frame.pack(fill=tk.BOTH, expand=True)
        
        if today_schedule:
            # Create a treeview for the schedule
            columns = ("Subject", "Start", "End", "Duration")
            schedule_tree = ttk.Treeview(schedule_frame, columns=columns, show="headings")
            
            # Set column headings
            for col in columns:
                schedule_tree.heading(col, text=col)
                schedule_tree.column(col, width=100)
            
            # Add schedule items
            for session in today_schedule:
                schedule_tree.insert(
                    "", 
                    "end", 
                    values=(
                        session["subject"],
                        session["start_time"],
                        session["end_time"],
                        f"{session['duration_minutes']} min"
                    )
                )
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, command=schedule_tree.yview)
            schedule_tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            schedule_tree.pack(fill=tk.BOTH, expand=True)
            
            # Add buttons for session management
            button_frame = tk.Frame(left_frame)
            button_frame.pack(fill=tk.X, pady=10)
            
            start_button = tk.Button(
                button_frame,
                text="Start Selected Session",
                command=lambda: self._start_study_session(schedule_tree)
            )
            start_button.pack(side=tk.LEFT, padx=5)
            
            complete_button = tk.Button(
                button_frame,
                text="Mark as Completed",
                command=lambda: self._complete_study_session(schedule_tree)
            )
            complete_button.pack(side=tk.LEFT, padx=5)
        else:
            # No schedule message
            no_schedule = tk.Label(
                schedule_frame,
                text="No study sessions scheduled for today.",
                font=("Arial", 12)
            )
            no_schedule.pack(expand=True)
            
            # Create plan button
            create_plan_button = tk.Button(
                left_frame,
                text="Create Study Plan",
                command=self._create_new_plan
            )
            create_plan_button.pack(pady=10)
        
        # Right column - Notifications and stats
        right_frame = tk.Frame(content_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        # Notifications section
        notif_label = tk.Label(
            right_frame,
            text="Notifications & Reminders",
            font=("Arial", 14, "bold")
        )
        notif_label.pack(pady=10)
        
        notif_frame = tk.Frame(right_frame, highlightbackground="gray", highlightthickness=1)
        notif_frame.pack(fill=tk.X, pady=5)
        
        # Add a motivational message
        motiv = self.notifier.get_motivational_message()
        motiv_label = tk.Label(
            notif_frame,
            text=motiv["message"],
            font=("Arial", 10, "italic"),
            wraplength=280,
            justify=tk.LEFT
        )
        motiv_label.pack(padx=10, pady=10)
        
        # Progress section
        progress_label = tk.Label(
            right_frame,
            text="Your Progress",
            font=("Arial", 14, "bold")
        )
        progress_label.pack(pady=10)
        
        progress_frame = tk.Frame(right_frame, highlightbackground="gray", highlightthickness=1)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Calculate progress
        completed_sessions = len(user_data.get("completed_sessions", []))
        total_sessions = 0
        
        if self.current_plan:
            for day, sessions in self.current_plan["schedule"]["daily_schedule"].items():
                total_sessions += len(sessions)
        
        # Create progress bar
        if total_sessions > 0:
            progress_pct = min(100, (completed_sessions / total_sessions) * 100)
        else:
            progress_pct = 0
            
        progress_bar = ttk.Progressbar(
            progress_frame, 
            orient=tk.HORIZONTAL, 
            length=280, 
            mode='determinate',
            value=progress_pct
        )
        progress_bar.pack(padx=10, pady=10)
        
        progress_text = tk.Label(
            progress_frame,
            text=f"Completed: {completed_sessions} of {total_sessions} sessions ({progress_pct:.1f}%)"
        )
        progress_text.pack(padx=10, pady=5)
        
        # Quick actions section
        actions_label = tk.Label(
            right_frame,
            text="Quick Actions",
            font=("Arial", 14, "bold")
        )
        actions_label.pack(pady=10)
        
        actions_frame = tk.Frame(right_frame)
        actions_frame.pack(fill=tk.X, pady=5)
        
        calendar_button = tk.Button(
            actions_frame,
            text="View Calendar",
            command=self._show_calendar_view
        )
        calendar_button.pack(fill=tk.X, pady=2)
        
        stats_button = tk.Button(
            actions_frame,
            text="View Statistics",
            command=self._show_statistics
        )
        stats_button.pack(fill=tk.X, pady=2)
        
        update_button = tk.Button(
            actions_frame,
            text="Update Preferences",
            command=self._show_preferences
        )
        update_button.pack(fill=tk.X, pady=2)
    
    def _start_study_session(self, tree: ttk.Treeview):
        """
        Start a selected study session.
        
        Args:
            tree: Treeview containing the schedule
        """
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a study session to start.")
            return
            
        # Get session data
        values = tree.item(selected[0], "values")
        subject = values[0]
        start_time = values[1]
        end_time = values[2]
        duration = values[3]
        
        # Show session window
        self._show_active_session(subject, start_time, end_time)
    
    def _show_active_session(self, subject: str, start_time: str, end_time: str):
        """
        Show the active study session window.
        
        Args:
            subject: Subject being studied
            start_time: Session start time
            end_time: Session end time
        """
        # Create a new top-level window
        session_window = tk.Toplevel(self.root)
        session_window.title(f"Study Session: {subject}")
        session_window.geometry("400x300")
        session_window.transient(self.root)
        
        # Session info
        info_frame = tk.Frame(session_window)
        info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        subject_label = tk.Label(
            info_frame,
            text=f"Subject: {subject}",
            font=("Arial", 14, "bold")
        )
        subject_label.pack(anchor=tk.W)
        
        time_label = tk.Label(
            info_frame,
            text=f"Time: {start_time} - {end_time}",
            font=("Arial", 12)
        )
        time_label.pack(anchor=tk.W, pady=5)
        
        # Timer
        timer_frame = tk.Frame(session_window)
        timer_frame.pack(fill=tk.X, padx=20, pady=10)
        
        timer_label = tk.Label(
            timer_frame,
            text="00:00:00",
            font=("Arial", 24)
        )
        timer_label.pack()
        
        # Start time
        start_datetime = datetime.now()
        
        # Update timer function
        def update_timer():
            try:
                # Check if window still exists
                if session_window.winfo_exists():
                    elapsed = datetime.now() - start_datetime
                    hours, remainder = divmod(elapsed.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
                    session_window.after(1000, update_timer)
            except (tk.TclError, RuntimeError):
                # Window was destroyed, stop timer
                return

        # Start timer
        update_timer()
        
        # Controls
        control_frame = tk.Frame(session_window)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        pause_button = tk.Button(
            control_frame,
            text="Pause",
            width=10
        )
        pause_button.pack(side=tk.LEFT, padx=5)
        
        complete_button = tk.Button(
            control_frame,
            text="Complete",
            width=10,
            command=lambda: self._complete_active_session(session_window, subject, start_time, end_time)
        )
        complete_button.pack(side=tk.LEFT, padx=5)
    
    def _complete_active_session(
        self, 
        window: tk.Toplevel, 
        subject: str, 
        start_time: str, 
        end_time: str
    ):
        """
        Complete an active study session.
        
        Args:
            window: Session window
            subject: Subject being studied
            start_time: Session start time
            end_time: Session end time
        """
        # Create feedback dialog
        feedback_frame = tk.Frame(window)
        feedback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Clear window
        for widget in window.winfo_children():
            if widget != feedback_frame:
                widget.destroy()
        
        # Feedback form
        tk.Label(
            feedback_frame,
            text="Session Completed!",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        tk.Label(
            feedback_frame,
            text="How productive was this session?",
            font=("Arial", 12)
        ).pack(pady=5)
        
        # Rating
        rating_var = tk.IntVar(value=3)
        rating_frame = tk.Frame(feedback_frame)
        rating_frame.pack(pady=10)
        
        for i in range(1, 6):
            rb = tk.Radiobutton(
                rating_frame,
                text=str(i),
                variable=rating_var,
                value=i
            )
            rb.pack(side=tk.LEFT, padx=10)
            
        # Notes
        tk.Label(
            feedback_frame,
            text="Notes:",
            font=("Arial", 12)
        ).pack(pady=5, anchor=tk.W)
        
        notes_var = tk.StringVar()
        notes_entry = tk.Entry(feedback_frame, textvariable=notes_var, width=40)
        notes_entry.pack(fill=tk.X, pady=5)
        
        # Submit button
        submit_button = tk.Button(
            feedback_frame,
            text="Submit Feedback",
            command=lambda: self._submit_session_feedback(
                window,
                {
                    "subject": subject,
                    "start_time": start_time,
                    "end_time": end_time,
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "rating": rating_var.get(),
                    "notes": notes_var.get()
                }
            )
        )
        submit_button.pack(pady=20)
    
    def _submit_session_feedback(
        self,
        window: tk.Toplevel,
        session_data: Dict[str, Any],
        feedback_data: Dict[str, Any]
    ):
        """
        Submit feedback for a completed study session.

        Args:
            window: Session window
            session_data: Data about the study session
            feedback_data: User feedback data
        """
        # Record session completion
        self.planner.record_session_completion(
            self.current_user_id,
            session_data,
            feedback_data
        )

        # Close the window safely
        try:
            if window.winfo_exists():
                window.destroy()
        except tk.TclError:
            # Window might already be destroyed
            pass

        # Refresh dashboard
        self._show_dashboard()
    
    def _complete_study_session(self, tree: ttk.Treeview):
        """
        Mark a selected study session as completed.
        
        Args:
            tree: Treeview containing the schedule
        """
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a study session to complete.")
            return
            
        # Get session data
        values = tree.item(selected[0], "values")
        subject = values[0]
        start_time = values[1]
        end_time = values[2]
        
        # Create a dialog for rating
        rating_dialog = tk.Toplevel(self.root)
        rating_dialog.title("Session Feedback")
        rating_dialog.geometry("300x200")
        rating_dialog.transient(self.root)
        
        # Rating form
        tk.Label(
            rating_dialog,
            text=f"Rate your {subject} session:",
            font=("Arial", 12, "bold")
        ).pack(pady=10)
        
        # Rating
        rating_var = tk.IntVar(value=3)
        rating_frame = tk.Frame(rating_dialog)
        rating_frame.pack(pady=10)
        
        for i in range(1, 6):
            rb = tk.Radiobutton(
                rating_frame,
                text=str(i),
                variable=rating_var,
                value=i
            )
            rb.pack(side=tk.LEFT, padx=5)
        
        # Submit button
        submit_button = tk.Button(
            rating_dialog,
            text="Submit",
            command=lambda: self._submit_quick_feedback(
                rating_dialog,
                {
                    "subject": subject,
                    "start_time": start_time,
                    "end_time": end_time,
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                {
                    "rating": rating_var.get(),
                    "notes": ""
                }
            )
        )
        submit_button.pack(pady=20)
    
    def _submit_quick_feedback(
        self,
        dialog: tk.Toplevel,
        session_data: Dict[str, Any],
        feedback_data: Dict[str, Any]
    ):
        """
        Submit quick feedback for a completed study session.

        Args:
            dialog: Feedback dialog
            session_data: Data about the study session
            feedback_data: User feedback data
        """
        # Record session completion
        self.planner.record_session_completion(
            self.current_user_id,
            session_data,
            feedback_data
        )

        # Close the dialog safely
        try:
            if dialog.winfo_exists():
                dialog.destroy()
        except tk.TclError:
            # Dialog might already be destroyed
            pass

        # Refresh dashboard
        self._show_dashboard()
    
    def _create_new_plan(self):
        """Create a new study plan."""
        if not self.current_user_id:
            messagebox.showerror("Error", "Please log in first.")
            return
            
        # Create a new plan
        plan = self.planner.create_study_plan(self.current_user_id)
        
        if plan:
            self.current_plan = plan
            messagebox.showinfo("Success", "New study plan created successfully!")
            self._show_current_plan()
        else:
            messagebox.showerror("Error", "Failed to create study plan.")
    
    def _show_current_plan(self):
        """Show the current study plan."""
        if not self.current_user_id:
            messagebox.showerror("Error", "Please log in first.")
            return
            
        if not self.current_plan:
            messagebox.showinfo("No Plan", "No study plan exists. Creating a new one...")
            self._create_new_plan()
            return
            
        self._clear_main_frame()
        
        # Create plan view frame
        plan_frame = tk.Frame(self.main_frame)
        plan_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(
            plan_frame, 
            text="Your Study Plan", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Plan metadata
        meta_frame = tk.Frame(plan_frame)
        meta_frame.pack(fill=tk.X, padx=20)
        
        created_date = datetime.fromisoformat(self.current_plan["created_at"])
        
        tk.Label(
            meta_frame,
            text=f"Plan created: {created_date.strftime('%Y-%m-%d %H:%M')}",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        version = self.current_plan["metadata"]["version"]
        tk.Label(
            meta_frame,
            text=f"Version: {version}",
            font=("Arial", 10)
        ).pack(side=tk.RIGHT)
        
        # Create a notebook with tabs for each day
        notebook = ttk.Notebook(plan_frame)
        notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Get schedule
        schedule = self.current_plan["schedule"]["daily_schedule"]
        
        # Create day tabs
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            # Create frame for this day
            day_frame = ttk.Frame(notebook)
            notebook.add(day_frame, text=day)
            
            # Get sessions for this day
            day_schedule = schedule.get(day, [])
            
            if day_schedule:
                # Create a treeview for the schedule
                columns = ("Subject", "Start", "End", "Duration", "Difficulty")
                day_tree = ttk.Treeview(day_frame, columns=columns, show="headings")
                
                # Set column headings
                for col in columns:
                    day_tree.heading(col, text=col)
                    day_tree.column(col, width=100)
                
                # Add schedule items
                for session in day_schedule:
                    day_tree.insert(
                        "", 
                        "end", 
                        values=(
                            session["subject"],
                            session["start_time"],
                            session["end_time"],
                            f"{session['duration_minutes']} min",
                            session["difficulty"]
                        )
                    )
                
                # Add scrollbar
                scrollbar = ttk.Scrollbar(day_frame, orient=tk.VERTICAL, command=day_tree.yview)
                day_tree.configure(yscroll=scrollbar.set)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                day_tree.pack(fill=tk.BOTH, expand=True)
            else:
                # No schedule message
                no_schedule = tk.Label(
                    day_frame,
                    text="No study sessions scheduled for this day.",
                    font=("Arial", 12)
                )
                no_schedule.pack(expand=True)
        
        # Weekly overview
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Weekly Overview")
        
        # Get overview data
        overview = self.current_plan["schedule"]["weekly_overview"]
        
        # Total study time
        total_time = overview.get("total_study_time_hours", 0)
        
        tk.Label(
            overview_frame,
            text=f"Total Weekly Study Time: {total_time} hours",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Subject breakdown
        subject_frame = tk.Frame(overview_frame)
        subject_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            subject_frame,
            text="Time Distribution by Subject:",
            font=("Arial", 12, "bold")
        ).pack(anchor=tk.W)
        
        # Create a canvas for the bar chart
        chart_canvas = tk.Canvas(subject_frame, height=200)
        chart_canvas.pack(fill=tk.X, pady=10)
        
        # Get subject percentages
        subject_pct = overview.get("subject_percentage", {})
        
        # Draw bars
        bar_width = 30
        spacing = 20
        x_offset = 50
        y_offset = 20
        height = 150
        
        # Draw axes
        chart_canvas.create_line(
            x_offset, y_offset, 
            x_offset, y_offset + height, 
            width=2
        )
        chart_canvas.create_line(
            x_offset, y_offset + height, 
            x_offset + (len(subject_pct) * (bar_width + spacing)), y_offset + height, 
            width=2
        )
        
        # Draw bars and labels
        x = x_offset + spacing
        for subject, percentage in subject_pct.items():
            # Calculate bar height
            bar_height = (percentage / 100) * height
            
            # Draw bar
            chart_canvas.create_rectangle(
                x, y_offset + height - bar_height,
                x + bar_width, y_offset + height,
                fill="blue"
            )
            
            # Draw percentage
            chart_canvas.create_text(
                x + bar_width/2, y_offset + height - bar_height - 10,
                text=f"{percentage}%"
            )
            
            # Draw subject label
            chart_canvas.create_text(
                x + bar_width/2, y_offset + height + 15,
                text=subject,
                angle=45,
                anchor=tk.NE
            )
            
            x += bar_width + spacing
        
        # Buttons
        button_frame = tk.Frame(plan_frame)
        button_frame.pack(fill=tk.X, pady=20, padx=20)
        
        back_button = tk.Button(
            button_frame,
            text="Back to Dashboard",
            command=self._show_dashboard
        )
        back_button.pack(side=tk.LEFT)
        
        update_button = tk.Button(
            button_frame,
            text="Update Plan",
            command=self._show_plan_update
        )
        update_button.pack(side=tk.RIGHT)
    
    def _show_plan_update(self):
        """Show the plan update screen."""
        if not self.current_user_id or not self.current_plan:
            messagebox.showerror("Error", "No plan to update.")
            return
            
        self._clear_main_frame()
        
        # Create update frame
        update_frame = tk.Frame(self.main_frame)
        update_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(
            update_frame, 
            text="Update Study Plan", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            update_frame,
            text="Provide feedback to improve your study plan.",
            font=("Arial", 12)
        )
        instructions.pack(pady=10)
        
        # Feedback form
        form_frame = tk.Frame(update_frame)
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Session length
        length_frame = tk.Frame(form_frame)
        length_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            length_frame,
            text="Preferred Session Length (minutes):",
            font=("Arial", 12)
        ).pack(side=tk.LEFT)
        
        length_var = tk.IntVar(value=45)
        length_spinner = tk.Spinbox(
            length_frame,
            from_=15,
            to=120,
            increment=5,
            textvariable=length_var,
            width=5
        )
        length_spinner.pack(side=tk.LEFT, padx=10)
        
        # Subject difficulty adjustments
        diff_frame = tk.LabelFrame(form_frame, text="Subject Difficulty Adjustments")
        diff_frame.pack(fill=tk.X, pady=10)
        
        # Get subjects from the plan
        subjects = set()
        for day, sessions in self.current_plan["schedule"]["daily_schedule"].items():
            for session in sessions:
                subjects.add(session["subject"])
        
        # Create difficulty dropdowns for each subject
        subject_vars = {}
        
        for i, subject in enumerate(subjects):
            subject_frame = tk.Frame(diff_frame)
            subject_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(
                subject_frame,
                text=f"{subject}:",
                width=15,
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=5)
            
            diff_var = tk.StringVar()
            diff_dropdown = ttk.Combobox(
                subject_frame,
                textvariable=diff_var,
                width=15
            )
            diff_dropdown['values'] = ["very_easy", "easy", "medium", "hard", "very_hard"]
            diff_dropdown.current(2)  # Default to medium
            diff_dropdown.pack(side=tk.LEFT, padx=5)
            
            subject_vars[subject] = diff_var
        
        # Additional comments
        comments_frame = tk.Frame(form_frame)
        comments_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            comments_frame,
            text="Additional Comments:",
            font=("Arial", 12)
        ).pack(anchor=tk.W)
        
        comments_var = tk.StringVar()
        comments_entry = tk.Entry(comments_frame, textvariable=comments_var, width=50)
        comments_entry.pack(fill=tk.X, pady=5)
        
        # Submit button
        submit_button = tk.Button(
            update_frame,
            text="Update Plan",
            command=lambda: self._update_plan_from_feedback({
                "preferred_session_length": length_var.get(),
                "subject_difficulty_adjustments": {
                    subject: var.get() for subject, var in subject_vars.items() if var.get()
                },
                "comments": comments_var.get()
            })
        )
        submit_button.pack(pady=20)
        
        # Back button
        back_button = tk.Button(
            update_frame,
            text="Cancel",
            command=self._show_current_plan
        )
        back_button.pack()
    
    def _update_plan_from_feedback(self, feedback: Dict[str, Any]):
        """
        Update the study plan based on user feedback.
        
        Args:
            feedback: User feedback dictionary
        """
        if not self.current_user_id or not self.current_plan:
            messagebox.showerror("Error", "No plan to update.")
            return
            
        # Update the plan
        updated_plan = self.planner.update_plan_from_feedback(
            self.current_user_id,
            self.current_plan["plan_id"],
            feedback
        )
        
        if updated_plan:
            self.current_plan = updated_plan
            messagebox.showinfo("Success", "Study plan updated successfully!")
            self._show_current_plan()
        else:
            messagebox.showerror("Error", "Failed to update study plan.")
    
    def _show_calendar_view(self):
        """Show the calendar view."""
        if not self.current_user_id:
            messagebox.showerror("Error", "Please log in first.")
            return
            
        self._clear_main_frame()
        
        # Create calendar frame
        calendar_frame = tk.Frame(self.main_frame)
        calendar_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(
            calendar_frame, 
            text="Study Calendar", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Current week
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        
        # Week navigation
        nav_frame = tk.Frame(calendar_frame)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)
        
        week_label = tk.Label(
            nav_frame,
            text=f"Week of {start_of_week.strftime('%B %d, %Y')}",
            font=("Arial", 12, "bold")
        )
        week_label.pack(side=tk.LEFT)
        
        # Calendar grid
        grid_frame = tk.Frame(calendar_frame)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Column headers (days of week)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for i, day in enumerate(days):
            header = tk.Label(
                grid_frame,
                text=day,
                font=("Arial", 10, "bold"),
                borderwidth=1,
                relief="solid",
                width=15
            )
            header.grid(row=0, column=i, sticky="nsew")
        
        # Get weekly schedule
        weekly_schedule = {}
        
        if self.current_plan:
            for i, day in enumerate(days):
                date = start_of_week + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                # Get sessions for this day
                day_schedule = self.current_plan["schedule"]["daily_schedule"].get(day, [])
                
                # Add date to each session
                for session in day_schedule:
                    session["date"] = date_str
                    
                weekly_schedule[date_str] = day_schedule
        
        # Create day cells
        for i, day in enumerate(days):
            date = start_of_week + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Create day cell
            day_cell = tk.Frame(
                grid_frame,
                borderwidth=1,
                relief="solid",
                height=300
            )
            day_cell.grid(row=1, column=i, sticky="nsew")
            day_cell.grid_propagate(False)
            
            # Date header
            date_header = tk.Label(
                day_cell,
                text=date.strftime("%b %d"),
                font=("Arial", 9, "bold"),
                bg="lightgray"
            )
            date_header.pack(fill=tk.X)
            
            # Sessions for this day
            sessions = weekly_schedule.get(date_str, [])
            
            if sessions:
                # Create a canvas with scrollbar for sessions
                canvas_frame = tk.Frame(day_cell)
                canvas_frame.pack(fill=tk.BOTH, expand=True)
                
                canvas = tk.Canvas(canvas_frame)
                scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Add sessions
                for session in sessions:
                    session_frame = tk.Frame(
                        scrollable_frame,
                        borderwidth=1,
                        relief="solid",
                        bg="lightblue",
                        width=day_cell.winfo_width() - 20
                    )
                    session_frame.pack(fill=tk.X, padx=5, pady=2)
                    
                    # Session time
                    time_label = tk.Label(
                        session_frame,
                        text=f"{session['start_time']} - {session['end_time']}",
                        font=("Arial", 8),
                        bg="lightblue"
                    )
                    time_label.pack(anchor=tk.W)
                    
                    # Subject
                    subject_label = tk.Label(
                        session_frame,
                        text=session['subject'],
                        font=("Arial", 9, "bold"),
                        bg="lightblue"
                    )
                    subject_label.pack(anchor=tk.W)
            else:
                # No sessions message
                no_sessions = tk.Label(
                    day_cell,
                    text="No sessions",
                    font=("Arial", 9),
                    fg="gray"
                )
                no_sessions.pack(expand=True)
        
        # Make grid cells expandable
        for i in range(7):
            grid_frame.columnconfigure(i, weight=1)
        grid_frame.rowconfigure(1, weight=1)
        
        # Back button
        back_button = tk.Button(
            calendar_frame,
            text="Back to Dashboard",
            command=self._show_dashboard
        )
        back_button.pack(pady=20)
    
    def _show_statistics(self):
        """Show the statistics view."""
        if not self.current_user_id:
            messagebox.showerror("Error", "Please log in first.")
            return
            
        # Load user data
        user_data = self.user_data_manager.load_user_data(self.current_user_id)
        if not user_data:
            messagebox.showerror("Error", "Could not load user data.")
            return
            
        self._clear_main_frame()
        
        # Create statistics frame
        stats_frame = tk.Frame(self.main_frame)
        stats_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(
            stats_frame, 
            text="Study Statistics", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Create notebook for different stats
        notebook = ttk.Notebook(stats_frame)
        notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Overview tab
        overview_tab = ttk.Frame(notebook)
        notebook.add(overview_tab, text="Overview")
        
        # Get completed sessions
        completed_sessions = user_data.get("completed_sessions", [])
        
        # Summary stats
        summary_frame = tk.Frame(overview_tab)
        summary_frame.pack(fill=tk.X, pady=10)
        
        total_sessions = len(completed_sessions)
        total_time = sum(session.get("duration_minutes", 0) for session in completed_sessions)
        avg_rating = 0
        
        if total_sessions > 0:
            ratings = [session.get("rating", 0) for session in completed_sessions if "rating" in session]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
        
        # Create summary boxes
        summary_boxes = [
            {"label": "Total Sessions", "value": str(total_sessions)},
            {"label": "Total Study Time", "value": f"{total_time // 60} hrs {total_time % 60} mins"},
            {"label": "Average Rating", "value": f"{avg_rating:.1f} / 5"}
        ]
        
        for i, box in enumerate(summary_boxes):
            box_frame = tk.Frame(summary_frame, borderwidth=2, relief="ridge", padx=10, pady=10)
            box_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)
            
            tk.Label(
                box_frame,
                text=box["label"],
                font=("Arial", 12)
            ).pack()
            
            tk.Label(
                box_frame,
                text=box["value"],
                font=("Arial", 16, "bold")
            ).pack(pady=5)
        
        # Recent activity
        recent_frame = tk.LabelFrame(overview_tab, text="Recent Activity")
        recent_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create treeview for recent sessions
        columns = ("Date", "Subject", "Duration", "Rating")
        recent_tree = ttk.Treeview(recent_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            recent_tree.heading(col, text=col)
            recent_tree.column(col, width=100)
        
        # Sort sessions by date (newest first)
        sorted_sessions = sorted(
            completed_sessions,
            key=lambda s: s.get("completed_at", ""),
            reverse=True
        )
        
        # Add recent sessions (up to 10)
        for session in sorted_sessions[:10]:
            date = session.get("date", "")
            subject = session.get("subject", "")
            duration = session.get("duration_minutes", 0)
            rating = session.get("rating", "-")
            
            recent_tree.insert(
                "",
                "end",
                values=(date, subject, f"{duration} min", rating)
            )
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL, command=recent_tree.yview)
        recent_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        recent_tree.pack(fill=tk.BOTH, expand=True)
        
        # Subjects tab
        subjects_tab = ttk.Frame(notebook)
        notebook.add(subjects_tab, text="Subjects")
        
        # Get subject stats
        subject_stats = {}
        
        for session in completed_sessions:
            subject = session.get("subject")
            if not subject:
                continue
                
            if subject not in subject_stats:
                subject_stats[subject] = {
                    "sessions": 0,
                    "total_time": 0,
                    "ratings": []
                }
                
            stats = subject_stats[subject]
            stats["sessions"] += 1
            stats["total_time"] += session.get("duration_minutes", 0)
            
            if "rating" in session:
                stats["ratings"].append(session["rating"])
        
        # Create subject stats table
        columns = ("Subject", "Sessions", "Total Time", "Avg Rating")
        subjects_tree = ttk.Treeview(subjects_tab, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            subjects_tree.heading(col, text=col)
            subjects_tree.column(col, width=100)
        
        # Add subject stats
        for subject, stats in subject_stats.items():
            avg_rating = "-"
            if stats["ratings"]:
                avg_rating = f"{sum(stats['ratings']) / len(stats['ratings']):.1f}"
                
            subjects_tree.insert(
                "",
                "end",
                values=(
                    subject,
                    stats["sessions"],
                    f"{stats['total_time']} min",
                    avg_rating
                )
            )
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(subjects_tab, orient=tk.VERTICAL, command=subjects_tree.yview)
        subjects_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        subjects_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Productivity tab
        productivity_tab = ttk.Frame(notebook)
        notebook.add(productivity_tab, text="Productivity")
        
        # Get time of day stats
        time_stats = {
            "morning": {"sessions": 0, "total_rating": 0},
            "afternoon": {"sessions": 0, "total_rating": 0},
            "evening": {"sessions": 0, "total_rating": 0},
            "night": {"sessions": 0, "total_rating": 0}
        }
        
        for session in completed_sessions:
            if "rating" not in session or "start_time" not in session:
                continue
                
            try:
                hour = int(session["start_time"].split(":")[0])
                time_of_day = self._determine_time_of_day(hour)
                
                time_stats[time_of_day]["sessions"] += 1
                time_stats[time_of_day]["total_rating"] += session["rating"]
            except (ValueError, IndexError):
                continue
        
        # Create time of day chart
        chart_frame = tk.LabelFrame(productivity_tab, text="Productivity by Time of Day")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a canvas for the chart
        chart_canvas = tk.Canvas(chart_frame, height=200)
        chart_canvas.pack(fill=tk.X, pady=10)
        
        # Draw bars
        bar_width = 50
        spacing = 30
        x_offset = 50
        y_offset = 20
        height = 150
        
        # Draw axes
        chart_canvas.create_line(
            x_offset, y_offset, 
            x_offset, y_offset + height, 
            width=2
        )
        chart_canvas.create_line(
            x_offset, y_offset + height, 
            x_offset + (len(time_stats) * (bar_width + spacing)), y_offset + height, 
            width=2
        )
        
        # Calculate average ratings
        avg_ratings = {}
        for time, stats in time_stats.items():
            if stats["sessions"] > 0:
                avg_ratings[time] = stats["total_rating"] / stats["sessions"]
            else:
                avg_ratings[time] = 0
        
        # Draw bars and labels
        x = x_offset + spacing
        for time, avg_rating in avg_ratings.items():
            # Calculate bar height
            bar_height = (avg_rating / 5) * height  # Scale to max rating of 5
            
            # Draw bar
            chart_canvas.create_rectangle(
                x, y_offset + height - bar_height,
                x + bar_width, y_offset + height,
                fill="green"
            )
            
            # Draw rating
            chart_canvas.create_text(
                x + bar_width/2, y_offset + height - bar_height - 10,
                text=f"{avg_rating:.1f}"
            )
            
            # Draw time label
            chart_canvas.create_text(
                x + bar_width/2, y_offset + height + 15,
                text=time.capitalize()
            )
            
            x += bar_width + spacing
        
        # Back button
        back_button = tk.Button(
            stats_frame,
            text="Back to Dashboard",
            command=self._show_dashboard
        )
        back_button.pack(pady=20)
    
    def _show_preferences(self):
        """Show the preferences screen."""
        if not self.current_user_id:
            messagebox.showerror("Error", "Please log in first.")
            return
            
        # Load user data
        user_data = self.user_data_manager.load_user_data(self.current_user_id)
        if not user_data:
            messagebox.showerror("Error", "Could not load user data.")
            return
            
        self._clear_main_frame()
        
        # Create preferences frame
        prefs_frame = tk.Frame(self.main_frame)
        prefs_frame.pack(expand=True, fill=tk.BOTH)
        
        # Title
        title_label = tk.Label(
            prefs_frame, 
            text="Update Preferences", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)
        
        # Create notebook for different preference sections
        notebook = ttk.Notebook(prefs_frame)
        notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
        # Study preferences tab
        study_tab = ttk.Frame(notebook)
        notebook.add(study_tab, text="Study Preferences")
        
        # Get current preferences
        preferences = user_data.get("study_preferences", {})
        
        # Create form
        form_frame = tk.Frame(study_tab)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Preferred subjects
        tk.Label(
            form_frame,
            text="Preferred Subjects (comma-separated):",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        preferred_subjects = ", ".join(preferences.get("preferred_subjects", []))
        subjects_var = tk.StringVar(value=preferred_subjects)
        tk.Entry(form_frame, textvariable=subjects_var, width=40).grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Difficult subjects
        tk.Label(
            form_frame,
            text="Difficult Subjects (comma-separated):",
            font=("Arial", 12)
        ).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        difficult_subjects = ", ".join(preferences.get("difficult_subjects", []))
        difficult_var = tk.StringVar(value=difficult_subjects)
        tk.Entry(form_frame, textvariable=difficult_var, width=40).grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Session length
        tk.Label(
            form_frame,
            text="Preferred Session Length (minutes):",
            font=("Arial", 12)
        ).grid(row=2, column=0, sticky=tk.W, pady=10)
        
        session_length = preferences.get("session_length_preference", 45)
        length_var = tk.IntVar(value=session_length)
        tk.Spinbox(
            form_frame,
            from_=15,
            to=120,
            increment=5,
            textvariable=length_var,
            width=5
        ).grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Productivity tab
        productivity_tab = ttk.Frame(notebook)
        notebook.add(productivity_tab, text="Productivity Patterns")
        
        # Get current productivity patterns
        productivity = user_data.get("productivity_patterns", {})
        
        # Create form
        prod_form = tk.Frame(productivity_tab)
        prod_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Peak productivity time
        tk.Label(
            prod_form,
            text="Peak Productivity Time:",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        peak_times = productivity.get("peak_productivity_times", [])
        peak_time = peak_times[0] if peak_times else "morning"
        
        peak_var = tk.StringVar(value=peak_time)
        peak_dropdown = ttk.Combobox(prod_form, textvariable=peak_var, width=15)
        peak_dropdown['values'] = ["morning", "afternoon", "evening", "night"]
        peak_dropdown.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Break frequency
        tk.Label(
            prod_form,
            text="Break Frequency (minutes):",
            font=("Arial", 12)
        ).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        break_freq = productivity.get("break_frequency", 25)
        freq_var = tk.IntVar(value=break_freq)
        tk.Spinbox(
            prod_form,
            from_=15,
            to=60,
            increment=5,
            textvariable=freq_var,
            width=5
        ).grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Break duration
        tk.Label(
            prod_form,
            text="Break Duration (minutes):",
            font=("Arial", 12)
        ).grid(row=2, column=0, sticky=tk.W, pady=10)
        
        break_dur = productivity.get("break_duration", 5)
        dur_var = tk.IntVar(value=break_dur)
        tk.Spinbox(
            prod_form,
            from_=5,
            to=30,
            increment=5,
            textvariable=dur_var,
            width=5
        ).grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Sleep schedule
        tk.Label(
            prod_form,
            text="Sleep Schedule:",
            font=("Arial", 12)
        ).grid(row=3, column=0, sticky=tk.W, pady=10)
        
        sleep_frame = tk.Frame(prod_form)
        sleep_frame.grid(row=3, column=1, sticky=tk.W, pady=10)
        
        sleep_schedule = productivity.get("sleep_schedule", {
            "weekday": {"sleep": "23:00", "wake": "07:00"},
            "weekend": {"sleep": "00:00", "wake": "08:00"}
        })
        
        # Weekday sleep
        tk.Label(sleep_frame, text="Weekday:").grid(row=0, column=0, sticky=tk.W)
        
        weekday_sleep_var = tk.StringVar(value=sleep_schedule["weekday"]["sleep"])
        tk.Label(sleep_frame, text="Sleep:").grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        tk.Entry(sleep_frame, textvariable=weekday_sleep_var, width=8).grid(row=0, column=2, sticky=tk.W)
        
        weekday_wake_var = tk.StringVar(value=sleep_schedule["weekday"]["wake"])
        tk.Label(sleep_frame, text="Wake:").grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        tk.Entry(sleep_frame, textvariable=weekday_wake_var, width=8).grid(row=0, column=4, sticky=tk.W)
        
        # Weekend sleep
        tk.Label(sleep_frame, text="Weekend:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        weekend_sleep_var = tk.StringVar(value=sleep_schedule["weekend"]["sleep"])
        tk.Label(sleep_frame, text="Sleep:").grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        tk.Entry(sleep_frame, textvariable=weekend_sleep_var, width=8).grid(row=1, column=2, sticky=tk.W, pady=(5, 0))
        
        weekend_wake_var = tk.StringVar(value=sleep_schedule["weekend"]["wake"])
        tk.Label(sleep_frame, text="Wake:").grid(row=1, column=3, sticky=tk.W, padx=(10, 0), pady=(5, 0))
        tk.Entry(sleep_frame, textvariable=weekend_wake_var, width=8).grid(row=1, column=4, sticky=tk.W, pady=(5, 0))
        
        # Availability tab
        avail_tab = ttk.Frame(notebook)
        notebook.add(avail_tab, text="Time Availability")
        
        # Add button to open availability editor
        avail_button = tk.Button(
            avail_tab,
            text="Edit Time Availability",
            command=self._show_availability_setup
        )
        avail_button.pack(expand=True, pady=50)
        
        # Save button
        save_button = tk.Button(
            prefs_frame,
            text="Save Preferences",
            command=lambda: self._save_preferences({
                "study_preferences": {
                    "preferred_subjects": [s.strip() for s in subjects_var.get().split(",") if s.strip()],
                    "difficult_subjects": [s.strip() for s in difficult_var.get().split(",") if s.strip()],
                    "session_length_preference": length_var.get()
                },
                "productivity_patterns": {
                    "peak_productivity_times": [peak_var.get()],
                    "break_frequency": freq_var.get(),
                    "break_duration": dur_var.get(),
                    "sleep_schedule": {
                        "weekday": {
                            "sleep": weekday_sleep_var.get(),
                            "wake": weekday_wake_var.get()
                        },
                        "weekend": {
                            "sleep": weekend_sleep_var.get(),
                            "wake": weekend_wake_var.get()
                        }
                    }
                }
            })
        )
        save_button.pack(pady=20)
        
        # Back button
        back_button = tk.Button(
            prefs_frame,
            text="Cancel",
            command=self._show_dashboard
        )
        back_button.pack(pady=10)
    
    def _save_preferences(self, preferences: Dict[str, Any]):
        """
        Save updated user preferences.
        
        Args:
            preferences: Updated preference dictionary
        """
        if not self.current_user_id:
            messagebox.showerror("Error", "Please log in first.")
            return
            
        # Update user data
        success = self.user_data_manager.update_user_data(
            self.current_user_id,
            preferences
        )
        
        if success:
            messagebox.showinfo("Success", "Preferences updated successfully!")
            
            # Ask if user wants to update their study plan
            update_plan = messagebox.askyesno(
                "Update Plan",
                "Would you like to update your study plan with these new preferences?"
            )
            
            if update_plan:
                self._create_new_plan()
            else:
                self._show_dashboard()
        else:
            messagebox.showerror("Error", "Failed to update preferences.")
    
    def _show_about(self):
        """Show the about dialog."""
        about_text = """
        AI Study Scheduler
        Version 1.0
        
        An intelligent application to help students
        create optimized study plans using AI.
        
        Features:
        - Personalized study scheduling
        - AI optimization based on productivity patterns
        - Progress tracking and feedback
        - Adaptive scheduling
        """
        
        messagebox.showinfo("About AI Study Scheduler", about_text)
    
    def _show_help(self):
        """Show the help dialog."""
        help_text = """
        Getting Started:
        1. Create a user profile with your study preferences
        2. Set your weekly availability
        3. The AI will create an optimized study plan
        4. Track your progress and provide feedback
        5. The system will adapt to your performance
        
        Tips:
        - Be honest about your productivity patterns
        - Update your preferences as needed
        - Complete the feedback after study sessions
        - Check the statistics to see your progress
        """
        
        messagebox.showinfo("Help", help_text)
    
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

def launch_app():
    """Launch the AI Study Scheduler application."""
    root = tk.Tk()
    app = StudySchedulerApp(root)
    root.mainloop()