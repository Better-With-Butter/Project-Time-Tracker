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
                f.write(f"| {project_link_md} | {start} | {end} | {duration} | {today_formatted} |\n")
                
        except Exception as e:
            messagebox.showerror("File Error", f"Could not write to log file:\n{e}")
