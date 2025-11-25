import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
from datetime import datetime, timedelta

# --- CONFIGURATION & COLORS ---
CONFIG_FILE = os.path.join(os.path.expanduser("~"), "time_tracker_config.json")
LOG_DIR_KEY = "log_directory"

# Modern Dark Theme Palette
COLOR_BG = "#1e1e1e"        
COLOR_FG = "#ffffff"        
COLOR_ACCENT = "#007acc"    
COLOR_ACCENT_HOVER = "#005f9e"
COLOR_INPUT_BG = "#3c3c3c"  
COLOR_LIST_BG = "#252526"   

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Time Tracker")
        self.root.geometry("450x650")
        self.root.configure(bg=COLOR_BG)

        self.log_directory = self.load_config(LOG_DIR_KEY)
        
        self.is_running = False
        self.is_minimal = False # State variable for the view mode
        self.start_time = None
        self.timer_id = None
        self.elapsed_seconds = 0
        
        # --- Variables ---
        self.project_var = tk.StringVar(root)
        self.timer_label_var = tk.StringVar(value="00:00:00")

        # --- TTK Style (Only needed for Treeview now) ---
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure custom Listbox styling for the log area
        style.configure("Treeview", 
                        background=COLOR_LIST_BG, 
                        foreground=COLOR_FG,
                        fieldbackground=COLOR_LIST_BG,
                        bordercolor=COLOR_LIST_BG,
                        rowheight=25,
                        font=("Segoe UI", 10))
        style.map('Treeview', background=[('selected', '#37373d')])

        # --- UI Setup ---
        
        # 1. MINIMIZE BUTTON (TOP POSITION)
        # This button is packed first, securing its top position in the layout flow.
        self.minimize_btn = tk.Button(root, text="Minimize View 🔽", 
                                      font=("Segoe UI", 9), 
                                      bg=COLOR_BG, fg="#666666", activebackground=COLOR_BG,
                                      activeforeground="#999999", relief="flat", cursor="hand2",
                                      command=self.toggle_minimal_view)
        self.minimize_btn.pack(pady=(10, 5)) 

        # 2. Project Input and Label
        self.project_label = tk.Label(root, text="Current Task/Project:", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG)
        self.project_label.pack(pady=(20, 5)) 
        
        self.project_entry = tk.Entry(root, textvariable=self.project_var, 
                                     font=("Segoe UI", 12), width=35,
                                     bg=COLOR_INPUT_BG, fg=COLOR_FG, 
                                     insertbackground="white", relief="flat", highlightthickness=1, 
                                     highlightbackground="#555555", highlightcolor=COLOR_ACCENT)
        self.project_entry.pack(pady=5, ipady=4)
        
        # 3. Timer Display (Remains always visible)
        self.timer_info_label = tk.Label(root, text="Elapsed Time:", font=("Segoe UI", 10), 
                 bg=COLOR_BG, fg="#888888")
        self.timer_info_label.pack(pady=(20, 0))
        
        self.timer_display = tk.Label(root, textvariable=self.timer_label_var, 
                                      font=("Consolas", 48, "bold"), 
                                      bg=COLOR_BG, fg=COLOR_ACCENT)
        self.timer_display.pack(pady=10)

        # 4. Start/Stop Button (Remains always visible)
        self.start_stop_btn = tk.Button(root, text="START", 
                                        font=("Segoe UI", 16, "bold"), 
                                        bg="#28a745", fg="white", 
                                        activebackground="#1e7e34", activeforeground="white",
                                        relief="flat", width=15, height=2, cursor="hand2",
                                        command=self.toggle_timer)
        self.start_stop_btn.pack(pady=30)
        
        # 5. Log Display (Treeview) and Label
        self.sessions_label = tk.Label(root, text="Today's Sessions:", font=("Segoe UI", 12), 
                 bg=COLOR_BG, fg=COLOR_FG)
        self.sessions_label.pack(pady=(20, 5), padx=20, anchor="w")

        self.log_tree = ttk.Treeview(root, columns=('Project', 'Start', 'End', 'Duration'), show='headings')
        self.log_tree.heading('Project', text='Project')
        self.log_tree.heading('Start', text='Start')
        self.log_tree.heading('End', text='End')
        self.log_tree.heading('Duration', text='Duration')
        
        self.log_tree.column('Project', width=150, anchor=tk.W)
        self.log_tree.column('Start', width=60, anchor=tk.CENTER)
        self.log_tree.column('End', width=60, anchor=tk.CENTER)
        self.log_tree.column('Duration', width=60, anchor=tk.CENTER)
        
        self.log_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
        
        # 6. Log Directory Setup Button
        self.set_folder_btn = tk.Button(root, text="Set Log Folder", font=("Segoe UI", 9), 
                  bg=COLOR_BG, fg="#666666", activebackground=COLOR_BG,
                  activeforeground="#999999", relief="flat", cursor="hand2",
                  command=self.set_log_directory)
        self.set_folder_btn.pack(pady=(0, 10))

        # --- Initialization ---
        if not self.log_directory:
            self.root.after(100, self.set_log_directory)
    
    # --- METHOD: TOGGLE VIEW ---
    def toggle_minimal_view(self):
        """Toggles between the full and minimal view of the application."""
        
        if not self.is_minimal:
            # --- Switch to Minimal View (Shrink) ---
            self.is_minimal = True
            
            # 1. Hide non-essential widgets
            self.project_label.pack_forget()
            self.project_entry.pack_forget()
            self.sessions_label.pack_forget()
            self.log_tree.pack_forget()
            self.set_folder_btn.pack_forget()
            
            # 2. Tighten Timer Spacing (Repack with smaller pady)
            self.timer_info_label.pack_forget()
            self.timer_info_label.pack(pady=(5, 0))
            self.timer_display.pack_forget()
            self.timer_display.pack(pady=5)
            self.start_stop_btn.pack_forget()
            self.start_stop_btn.pack(pady=5)
            
            # 3. Shrink the main window
            self.root.geometry("450x250")
            self.minimize_btn.config(text="Expand View 🔼")
            
        else:
            # --- Switch to Full View (Expand) ---
            self.is_minimal = False
            
            # 1. Restore Spacing and Size
            self.root.geometry("450x650")

            # 2. Restore hidden widgets (Project input and label)
            self.project_label.pack(pady=(20, 5))
            self.project_entry.pack(pady=5, ipady=4)

            # 3. Restore Timer Area spacing
            self.timer_info_label.pack_forget()
            self.timer_info_label.pack(pady=(20, 0))
            self.timer_display.pack_forget()
            self.timer_display.pack(pady=10)
            self.start_stop_btn.pack_forget()
            self.start_stop_btn.pack(pady=30)
            
            # 4. Restore Log Area
            self.sessions_label.pack(pady=(20, 5), padx=20, anchor="w")
            self.log_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))
            self.set_folder_btn.pack(pady=(0, 10))
            
            # 5. Update Button Text
            self.minimize_btn.config(text="Minimize View 🔽")


    # ----------------------------------------------------------------------
    # --- CONFIGURATION AND FILE PATH METHODS ---
    # ----------------------------------------------------------------------

    def load_config(self, key):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f).get(key, "")
            except: return ""
        return ""

    def save_config(self, key, value):
        data = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
            except: pass
        
        data[key] = value
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

    def set_log_directory(self):
        messagebox.showinfo("Setup", "Select the FOLDER where your daily Markdown logs will be saved (e.g., your Obsidian vault folder).")
        new_dir = filedialog.askdirectory(title="Select Log Folder")
        if new_dir:
            self.log_directory = new_dir
            self.save_config(LOG_DIR_KEY, new_dir)
            messagebox.showinfo("Success", f"Log files will be saved to:\n{new_dir}")
        elif not self.log_directory:
            self.root.destroy()
            
    # ----------------------------------------------------------------------
    # --- TIMER LOGIC AND LOGGING METHODS ---
    # ----------------------------------------------------------------------

    def update_timer(self):
        """Updates the timer display every second."""
        if self.is_running:
            self.elapsed_seconds = (datetime.now() - self.start_time).total_seconds()
            
            # Format time as HH:MM:SS
            td = timedelta(seconds=int(self.elapsed_seconds))
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            self.timer_label_var.set(formatted_time)
            
            # Recurse the function after 1000ms (1 second)
            self.timer_id = self.root.after(1000, self.update_timer)

    def toggle_timer(self):
        project_on_start = self.project_var.get().strip()
        
        if not self.is_running:
            # START the timer
            if not project_on_start:
                messagebox.showerror("Error", "Please enter a Project name before starting the timer.")
                return

            self.is_running = True
            self.start_time = datetime.now()
            
            self.start_stop_btn.config(text="STOP", bg="#d32f2f", activebackground="#a00000") 
            self.update_timer()
        else:
            # STOP the timer
            
            # Capture the project name *before* clearing the input field!
            project_to_log = self.project_var.get().strip()

            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
                
            self.is_running = False
            self.start_stop_btn.config(text="START", bg="#28a745", activebackground="#1e7e34")
            
            # Log the finished session using the captured project name
            self.log_session(project_to_log) 
            
            # Now, clear the input field after logging
            self.project_var.set("") 
            
            # Reset the display after logging
            self.timer_label_var.set("00:00:00")
            self.elapsed_seconds = 0
            
    def log_session(self, project): 
        """Logs the session details to the Markdown file and updates the Treeview."""
        if not self.start_time or not self.log_directory:
            return
            
        end_time = datetime.now()
        
        # Format the project name as an Obsidian Wikilink
        project_link_md = f"[[{project}]]"
        
        duration_td = end_time - self.start_time
        
        # Formatting for the log entry
        start_str = self.start_time.strftime("%H:%M:%S")
        end_str = end_time.strftime("%H:%M:%S")
        
        # Duration formatted for Obsidian table
        duration_minutes = round(duration_td.total_seconds() / 60)
        duration_str = f"{duration_minutes}m"
        
        # Update the local display (Treeview) using the original project name
        self.log_tree.insert('', tk.END, values=(project, start_str, end_str, duration_str))

        # Write to the Obsidian-friendly Markdown file using the wikilink format
        self.write_markdown_log(project_link_md, start_str, end_str, duration_str)

    def write_markdown_log(self, project_link_md, start, end, duration):
        """Handles the creation and appending to the daily Markdown log file."""
        if not self.log_directory: return
        
        # 1. Sanitize the project link to prevent breaking the table structure
        project_link_md = project_link_md.replace("|", "-")

        # Date Format: MM-DD-YY
        today_formatted = datetime.now().strftime("%m-%d-%y")
        filename = "Work Log.md"
        filepath = os.path.join(self.log_directory, filename)
        
        # 2. Check logic: Does file exist? Is it empty?
        file_exists = os.path.exists(filepath)
        is_empty = False
        
        if file_exists:
            if os.path.getsize(filepath) == 0:
                is_empty = True
        else:
            is_empty = True

        try:
            with open(filepath, "a", encoding="utf-8") as f:
                # 3. Only write headers if the file is brand new OR empty
                if is_empty:
                    f.write("| Project | Start | End | Duration | Date |\n")
                    f.write("| :--- | :--- | :--- | :--- | :--- |\n")
                
                # Check for newline integrity using '2' (which means End of File)
                if not is_empty:
                    with open(filepath, "r", encoding="utf-8") as r:
                        r.seek(0, 2)  # <--- CHANGED THIS: 0 bytes from end (2)
                        if r.tell() > 0:
                            r.seek(r.tell() - 1, 0)
                            if r.read(1) != '\n':
                                f.write("\n")

                # Append the new session row
                f.write(f"| {project_link_md} | {start} | {end} | {duration} | {today_formatted} |")
                
        except Exception as e:
            messagebox.showerror("File Error", f"Could not write to log file:\n{e}")

# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
