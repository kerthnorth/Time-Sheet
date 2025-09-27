import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
import threading
import time

class WorkHoursTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mukuna Work Hours Tracker")
        self.root.geometry("700x800")
        self.root.configure(bg='#667eea')
        
        # Data file path
        self.data_file = "work_sessions.json"
        self.work_sessions = self.load_data()
        
        # Current session tracking
        self.current_session = None
        self.timer_running = False
        self.start_time = None
        self.elapsed_seconds = 0
        
        # Create GUI
        self.setup_gui()
        
        # Start time update thread
        self.update_time_thread()
        
    def load_data(self):
        """Load work sessions from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_data(self):
        """Save work sessions to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.work_sessions, f, indent=2, default=str)
            print(f"Data saved to {self.data_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def setup_gui(self):
        """Create the GUI elements"""
        # Main container with gradient-like effect
        main_frame = tk.Frame(self.root, bg='#667eea')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title section
        title_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="Mukuna Work Hours Tracker", 
                              font=('Arial', 24, 'bold'), bg='white', fg='#667eea')
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(title_frame, text="Track your productivity with style", 
                                 font=('Arial', 12), bg='white', fg='#666')
        subtitle_label.pack(pady=(0, 15))
        
        # Timer section
        timer_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        timer_frame.pack(fill='x', pady=(0, 20))
        
        # Current time display
        self.current_time_label = tk.Label(timer_frame, text="", 
                                          font=('Arial', 14), bg='white', fg='#555')
        self.current_time_label.pack(pady=(20, 10))
        
        # Timer display
        self.timer_label = tk.Label(timer_frame, text="00:00:00", 
                                   font=('Courier New', 36, 'bold'), bg='white', fg='#333')
        self.timer_label.pack(pady=20)
        
        # Control buttons frame
        button_frame = tk.Frame(timer_frame, bg='white')
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(button_frame, text="START WORK", 
                                  font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white',
                                  padx=30, pady=15, command=self.start_work,
                                  relief='raised', bd=3, cursor='hand2')
        self.start_btn.pack(side='left', padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="STOP WORK", 
                                 font=('Arial', 12, 'bold'), bg='#f44336', fg='white',
                                 padx=30, pady=15, command=self.stop_work,
                                 relief='raised', bd=3, cursor='hand2', state='disabled')
        self.stop_btn.pack(side='left', padx=10)
        
        # Status indicator
        self.status_frame = tk.Frame(timer_frame, bg='white')
        self.status_frame.pack(pady=(0, 20))
        
        self.status_canvas = tk.Canvas(self.status_frame, width=20, height=20, bg='white', highlightthickness=0)
        self.status_canvas.pack(side='left')
        self.status_canvas.create_oval(5, 5, 15, 15, fill='#ccc', outline='#ccc')
        
        self.status_label = tk.Label(self.status_frame, text="Ready to work", 
                                    font=('Arial', 12), bg='white', fg='#666')
        self.status_label.pack(side='left', padx=(10, 0))
        
        # Stats section
        stats_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        stats_title = tk.Label(stats_frame, text="Today's Stats", 
                              font=('Arial', 18, 'bold'), bg='white', fg='#333')
        stats_title.pack(pady=(20, 10))
        
        # Stats cards
        cards_frame = tk.Frame(stats_frame, bg='white')
        cards_frame.pack(pady=20, padx=20)
        
        # Total Hours Card
        hours_card = tk.Frame(cards_frame, bg='#84fab0', relief='raised', bd=2)
        hours_card.pack(side='left', padx=10, fill='both', expand=True)
        
        self.hours_value = tk.Label(hours_card, text="0h 0m", 
                                   font=('Arial', 20, 'bold'), bg='#84fab0', fg='white')
        self.hours_value.pack(pady=(15, 5))
        
        hours_label = tk.Label(hours_card, text="Total Hours", 
                              font=('Arial', 10), bg='#84fab0', fg='white')
        hours_label.pack(pady=(0, 15))
        
        # Sessions Card
        sessions_card = tk.Frame(cards_frame, bg='#8fd3f4', relief='raised', bd=2)
        sessions_card.pack(side='left', padx=10, fill='both', expand=True)
        
        self.sessions_value = tk.Label(sessions_card, text="0", 
                                      font=('Arial', 20, 'bold'), bg='#8fd3f4', fg='white')
        self.sessions_value.pack(pady=(15, 5))
        
        sessions_label = tk.Label(sessions_card, text="Sessions", 
                                 font=('Arial', 10), bg='#8fd3f4', fg='white')
        sessions_label.pack(pady=(0, 15))
        
        # Average Card
        avg_card = tk.Frame(cards_frame, bg='#a8edea', relief='raised', bd=2)
        avg_card.pack(side='left', padx=10, fill='both', expand=True)
        
        self.avg_value = tk.Label(avg_card, text="0min", 
                                 font=('Arial', 20, 'bold'), bg='#a8edea', fg='white')
        self.avg_value.pack(pady=(15, 5))
        
        avg_label = tk.Label(avg_card, text="Avg Session", 
                            font=('Arial', 10), bg='#a8edea', fg='white')
        avg_label.pack(pady=(0, 15))
        
        # Sessions table
        table_frame = tk.Frame(stats_frame, bg='white')
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Table headers
        headers_frame = tk.Frame(table_frame, bg='#667eea')
        headers_frame.pack(fill='x')
        
        headers = ["Date", "Start Time", "End Time", "Duration"]
        for i, header in enumerate(headers):
            tk.Label(headers_frame, text=header, font=('Arial', 10, 'bold'), 
                    bg='#667eea', fg='white', relief='ridge', bd=1).grid(row=0, column=i, sticky='ew', ipadx=10, ipady=8)
        
        for i in range(4):
            headers_frame.columnconfigure(i, weight=1)
        
        # Scrollable table content
        table_canvas = tk.Canvas(table_frame, height=200, bg='white')
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table_canvas.yview)
        self.scrollable_frame = tk.Frame(table_canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all"))
        )
        
        table_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        table_canvas.configure(yscrollcommand=scrollbar.set)
        
        table_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Initial updates
        self.update_stats()
        self.update_sessions_table()
    
    def start_work(self):
        """Start a work session"""
        self.current_session = {
            'start_time': datetime.now(),
            'end_time': None
        }
        
        self.timer_running = True
        self.start_time = time.time()
        self.elapsed_seconds = 0
        
        # Update UI
        self.start_btn.configure(state='disabled', bg='#ccc')
        self.stop_btn.configure(state='normal', bg='#f44336')
        
        # Update status
        self.status_canvas.delete("all")
        self.status_canvas.create_oval(5, 5, 15, 15, fill='#4CAF50', outline='#4CAF50')
        self.status_label.configure(text="Working...", fg='#4CAF50')
        
        # Start timer update
        self.update_timer()
        
    def stop_work(self):
        """Stop the current work session"""
        if not self.current_session:
            return
        
        self.current_session['end_time'] = datetime.now()
        self.work_sessions.append(self.current_session)
        
        # Save to file
        self.save_data()
        
        # Reset timer
        self.timer_running = False
        self.current_session = None
        self.elapsed_seconds = 0
        
        # Update UI
        self.start_btn.configure(state='normal', bg='#4CAF50')
        self.stop_btn.configure(state='disabled', bg='#ccc')
        self.timer_label.configure(text="00:00:00", fg='#333')
        
        # Update status
        self.status_canvas.delete("all")
        self.status_canvas.create_oval(5, 5, 15, 15, fill='#ccc', outline='#ccc')
        self.status_label.configure(text="Ready to work", fg='#666')
        
        # Update stats and table
        self.update_stats()
        self.update_sessions_table()
        
    def update_timer(self):
        """Update the timer display"""
        if self.timer_running and self.start_time:
            self.elapsed_seconds = int(time.time() - self.start_time)
            time_str = self.format_time(self.elapsed_seconds)
            self.timer_label.configure(text=time_str, fg='#4CAF50')
            
            # Schedule next update
            self.root.after(1000, self.update_timer)
    
    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def format_duration(self, start_time, end_time):
        """Format duration between two datetime objects"""
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
        duration = end_time - start_time
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def update_stats(self):
        """Update the statistics display"""
        today = datetime.now().date()
        today_sessions = [
            session for session in self.work_sessions 
            if session.get('end_time') and 
            (datetime.fromisoformat(session['start_time'].replace('Z', '+00:00')) if isinstance(session['start_time'], str) 
             else session['start_time']).date() == today
        ]
        
        total_minutes = 0
        for session in today_sessions:
            start_time = session['start_time']
            end_time = session['end_time']
            
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if end_time:
                duration = (end_time - start_time).total_seconds() / 60
                total_minutes += duration
        
        # Update display
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        
        if hours > 0:
            self.hours_value.configure(text=f"{hours}h {minutes}m")
        else:
            self.hours_value.configure(text=f"{minutes}m")
        
        self.sessions_value.configure(text=str(len(today_sessions)))
        
        avg_minutes = int(total_minutes / len(today_sessions)) if today_sessions else 0
        self.avg_value.configure(text=f"{avg_minutes}min")
    
    def update_sessions_table(self):
        """Update the sessions table"""
        # Clear existing table
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.work_sessions:
            tk.Label(self.scrollable_frame, text="No sessions recorded yet", 
                    font=('Arial', 12), bg='white', fg='#666', 
                    relief='ridge', bd=1).grid(row=0, column=0, columnspan=4, sticky='ew', pady=5, ipady=10)
            return
        
        # Show last 10 sessions
        recent_sessions = self.work_sessions[-10:][::-1]  # Last 10, reversed
        
        for i, session in enumerate(recent_sessions):
            start_time = session['start_time']
            end_time = session['end_time']
            
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if isinstance(end_time, str) and end_time:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            # Date
            tk.Label(self.scrollable_frame, text=start_time.strftime('%Y-%m-%d'), 
                    font=('Arial', 9), bg='white', relief='ridge', bd=1).grid(row=i, column=0, sticky='ew', ipadx=5, ipady=5)
            
            # Start time
            tk.Label(self.scrollable_frame, text=start_time.strftime('%H:%M:%S'), 
                    font=('Arial', 9), bg='white', relief='ridge', bd=1).grid(row=i, column=1, sticky='ew', ipadx=5, ipady=5)
            
            # End time
            end_text = end_time.strftime('%H:%M:%S') if end_time else 'In progress'
            tk.Label(self.scrollable_frame, text=end_text, 
                    font=('Arial', 9), bg='white', relief='ridge', bd=1).grid(row=i, column=2, sticky='ew', ipadx=5, ipady=5)
            
            # Duration
            duration_text = self.format_duration(start_time, end_time) if end_time else '0m'
            tk.Label(self.scrollable_frame, text=duration_text, 
                    font=('Arial', 9), bg='white', relief='ridge', bd=1).grid(row=i, column=3, sticky='ew', ipadx=5, ipady=5)
        
        # Configure column weights
        for i in range(4):
            self.scrollable_frame.columnconfigure(i, weight=1)
    
    def update_time_thread(self):
        """Update current time display"""
        def update_time():
            while True:
                current_time = datetime.now().strftime('%Y-%m-%d - %H:%M:%S')
                self.current_time_label.configure(text=current_time)
                time.sleep(1)
        
        thread = threading.Thread(target=update_time, daemon=True)
        thread.start()
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.timer_running:
            if messagebox.askokcancel("Quit", "You have an active work session. Do you want to stop it and quit?"):
                self.stop_work()
                self.root.destroy()
        else:
            self.root.destroy()
            
    def schedule_daily_summary(self):
        """Runs every day at 23:59 to save total hours"""
    def task():
        while True:
            now = datetime.now()
            # wait until 23:59
            target = datetime.combine(now.date(), datetime.min.time()) + timedelta(days=0, hours=23, minutes=59)
            if now > target:  # if already past today 23:59, target is tomorrow
                target += timedelta(days=1)
            sleep_seconds = (target - now).total_seconds()
            time.sleep(sleep_seconds)

            # at 23:59 → calculate total for today
            self.update_stats()
            self.save_data()
            print("✅ Daily summary saved at", datetime.now())

    thread = threading.Thread(target=task, daemon=True)
    thread.start()


if __name__ == "__main__":
    app = WorkHoursTracker()
    app.run()