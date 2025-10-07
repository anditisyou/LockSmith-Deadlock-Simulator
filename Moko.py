import tkinter as tk 
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from collections import defaultdict, deque
import random
from PIL import Image, ImageTk
import os
#------------------------------------------Vaishnavi-GUI------------------------------------------#
class Phase2DeadlockSimulator(tk.Tk):
    """
    Phase 2 Deadlock Simulator with automatic image toggling based on system states
    """

    def __init__(self):
        super().__init__()
        self.title("Phase 2 Deadlock Simulator")
        self.geometry("1200x800")
        self.configure(bg="#2c3e50")
        self.minsize(1000, 700)
        
        # State
        self.processes = []
        self.resources = []
        self.resource_instances = []
        self.available = []
        self.allocation = defaultdict(list)
        self.max_need = defaultdict(list)
        self.request = defaultdict(list)
        self.process_descriptions = {}
        self.cli_history = []
        self.history_index = -1

        # Drag state
        self.dragging = False
        self.drag_item = None
        self.drag_type = None
        self.drag_start_x = 0
        self.drag_start_y = 0

        # NPC images and toggle state - CRITICAL: Keep references to prevent garbage collection
        self.npc_images = {}
        self.current_npc_state = "sad"
        self.target_npc_state = "sad"
        self.toggle_enabled = False
        self.is_toggling = False
        self.toggle_after_id = None
        self.last_banker_result = None
        self.last_detection_result = None
        
        # UI - Create NPC label early so we can update it later
        self.npc_label = None
        self.npc_status_text = None
        
        self.create_toolbox()
        self.create_main_panels()
        self.create_status_bar()
        self.load_npc_images()

        self.cli_print("Welcome to the Phase 2 Deadlock Simulator! Type 'help' in the CLI.")

    def load_npc_images(self):
        """Load NPC images for different states - FIXED VERSION"""
        try:
            # Create a simple directory check and use fallback images
            image_states = ["sad", "normal", "deadlock", "conflict"]
            
            for state in image_states:
                filename = f"{state}.png"
                # Try to use generic fallback names if specific ones don't exist
                if state == "sad":
                    filenames_to_try = ["101.png", "sad.png", "default.png"]
                elif state == "normal":
                    filenames_to_try = ["102.png", "normal.png", "happy.png"]
                elif state == "deadlock":
                    filenames_to_try = ["103.png", "deadlock.png", "error.png"]
                elif state == "conflict":
                    filenames_to_try = ["104.png", "conflict.png", "warning.png"]
                self.update_npc_display("normal")
                image_loaded = False
                for try_filename in filenames_to_try:
                    if os.path.exists(try_filename):
                        img = Image.open(try_filename)
                        img = img.resize((180, 180), Image.Resampling.LANCZOS)  # Slightly smaller for toolbox
                        self.npc_images[state] = ImageTk.PhotoImage(img)
                        print(f"Loaded image: {try_filename} for state: {state}")
                        image_loaded = True
                        break
                
                if not image_loaded:
                    # Create colored placeholder
                    self.create_placeholder_image(state)
                    
        except Exception as e:
            print(f"Error loading NPC images: {e}")
            # Create placeholders for all states
            for state in ["sad", "normal", "deadlock", "conflict"]:
                self.create_placeholder_image(state)

    def create_placeholder_image(self, state):
        """Create a colored placeholder image"""
        from PIL import ImageDraw, ImageFont
        
        color_map = {
            "normal": "#3498db",  # Blue
            "deadlock": "#e74c3c",  # Red
            "conflict": "#f39c12",  # Orange
            "sad": "#95a5a6"  # Gray
        }
        
        color = color_map.get(state, "#7f8c8d")
        img = Image.new('RGB', (180, 180), color)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            
        # Draw state text
        draw.text((90, 70), state.upper(), fill="white", font=font, anchor="mm")
        # Draw emoji based on state
        emoji_map = {
            "normal": "✓",
            "deadlock": "⚡", 
            "conflict": "⚠",
            "sad": "☹"
        }
        draw.text((90, 110), emoji_map.get(state, "?"), fill="white", font=font, anchor="mm")
        
        self.npc_images[state] = ImageTk.PhotoImage(img)
        print(f"Created placeholder for: {state}")

    def create_toolbox(self):#_______________________________________________________________________________________P
        self.toolbox = tk.Frame(self, bg="#34495e", width=180)
        self.toolbox.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.toolbox.pack_propagate(False)
        
        # Toolbox title
        title_label = tk.Label(self.toolbox, text="Toolbox", font=("Helvetica", 13, "bold"),
                bg="#34495e", fg="#ecf0f1")
        title_label.pack(pady=10)
        
        # Process tool
        process_tool = tk.Frame(self.toolbox, bg="#3498db", relief=tk.RAISED, bd=2)
        process_tool.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(process_tool, text="Process", bg="#3498db", fg="white",
                font=("Helvetica", 10)).pack(pady=5)
        process_tool.bind("<Button-1>", lambda e: self.start_drag("process", e))
        
        # Resource tool
        resource_tool = tk.Frame(self.toolbox, bg="#e67e22", relief=tk.RAISED, bd=2)
        resource_tool.pack(pady=5, padx=10, fill=tk.X)
        tk.Label(resource_tool, text="Resource", bg="#e67e22", fg="white",
                font=("Helvetica", 10)).pack(pady=5)
        resource_tool.bind("<Button-1>", lambda e: self.start_drag("resource", e))
        
        ttk.Separator(self.toolbox, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Controls
        config_frame = tk.Frame(self.toolbox, bg="#34495e")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Button(config_frame, text="Configure All", command=self.configure_all,
                bg="#2ecc71", fg="white").pack(fill=tk.X, pady=2)
        tk.Button(config_frame, text="Random State", command=self.generate_random_state,
                bg="#9b59b6", fg="white").pack(fill=tk.X, pady=2)
        tk.Button(config_frame, text="Run Banker's", command=self.check_safe_state,
                bg="#3498db", fg="white").pack(fill=tk.X, pady=2)
        tk.Button(config_frame, text="Detect Deadlock", command=self.detect_deadlock,
                bg="#e74c3c", fg="white").pack(fill=tk.X, pady=2)
        tk.Button(config_frame, text="Recover", command=self.recover_from_deadlock,
                bg="#f39c12", fg="white").pack(fill=tk.X, pady=2)

        # NPC Image Display Area - FIXED: Proper structure
        ttk.Separator(self.toolbox, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # NPC Display Frame
        npc_frame = tk.Frame(self.toolbox, bg="#34495e")
        npc_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(npc_frame, text="System Status", font=("Helvetica", 11, "bold"),
                bg="#34495e", fg="#ecf0f1").pack(pady=(0, 10))
        
        # Image display label - FIXED: Create it here and store reference
        self.npc_label = tk.Label(npc_frame, bg="#34495e", width=180, height=180)
        self.npc_label.pack(pady=5)
        
        # Status text below image
        self.npc_status_text = tk.Label(npc_frame, text="Sad State", 
                                       font=("Helvetica", 10, "bold"), bg="#34495e", fg="#95a5a6")
        self.npc_status_text.pack(pady=5)
        
        # Initialize with sad state - FIXED: Call this after creating the label
        self.update_npc_display("sad")

    def start_toggling(self, target_state):
        """Start automatic toggling between sad and target state"""
        if self.toggle_after_id:
            self.after_cancel(self.toggle_after_id)
        
        self.target_npc_state = target_state
        self.toggle_enabled = True
        self.is_toggling = True
        self._toggle_animation()

    def stop_toggling(self):
        """Stop automatic toggling and return to sad state"""
        self.toggle_enabled = False
        self.is_toggling = False
        if self.toggle_after_id:
            self.after_cancel(self.toggle_after_id)
            self.toggle_after_id = None
        self.update_npc_display("sad")

    def _toggle_animation(self):
        """Internal method for handling the toggle animation"""
        if not self.toggle_enabled or not self.is_toggling:
            return
            
        if self.current_npc_state == "sad":
            self.update_npc_display(self.target_npc_state)
        else:
            self.update_npc_display("sad")
            
        # Schedule next toggle
        self.toggle_after_id = self.after(500, self._toggle_animation)

    def update_npc_display(self, state):
        """Update the NPC image display based on state - FIXED VERSION"""
        self.current_npc_state = state
        
        if state in self.npc_images and self.npc_label:
            self.npc_label.config(image=self.npc_images[state])
            
            # Update status text and color
            status_config = {
                "normal": ("Normal State", "#2ecc71"),
                "deadlock": ("Deadlock Detected!", "#e74c3c"),
                "conflict": ("Conflict State", "#f39c12"),
                "sad": ("Sad State", "#95a5a6")
            }
            
            text, color = status_config.get(state, ("Unknown State", "#7f8c8d"))
            if self.npc_status_text:
                self.npc_status_text.config(text=text, fg=color)
        else:
            print(f"Warning: Cannot update NPC display. State: {state}, Label exists: {self.npc_label is not None}") 

    def create_main_panels(self):#_______________________________________________________________________________________A
        main_frame = tk.Frame(self, bg="#2c3e50")
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Workspace
        workspace_frame = tk.LabelFrame(main_frame, text="Workspace", font=("Helvetica", 10, "bold"),
                                        bg="#2c3e50", fg="#ecf0f1")
        workspace_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas = tk.Canvas(workspace_frame, bg="#ecf0f1", highlightthickness=1,
                                highlightbackground="#7f8c8d")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)
        self.canvas.bind("<Double-Button-1>", self.canvas_double_click)
        self.canvas.bind("<Button-3>", self.canvas_right_click)
        
        # CLI
        self.cli_frame = tk.LabelFrame(main_frame, text="Command Line Interface", font=("Helvetica", 10, "bold"),
                                       bg="#2c3e50", fg="#ecf0f1")
        self.cli_frame.pack(fill=tk.X, padx=5, pady=5)
        self.cli_output = scrolledtext.ScrolledText(self.cli_frame, height=8,
                                                    bg="#1c2833", fg="#ecf0f1", font=("Consolas", 10))
        self.cli_output.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.cli_output.config(state=tk.DISABLED)
        
        input_frame = tk.Frame(self.cli_frame, bg="#2c3e50")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(input_frame, text=">", bg="#2c3e50", fg="#ecf0f1").pack(side=tk.LEFT)
        self.cli_input = tk.Entry(input_frame, bg="#34495e", fg="#ecf0f1", insertbackground="white")
        self.cli_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.cli_input.bind("<Return>", self.process_cli_command)
        self.cli_input.bind("<Up>", self.cli_history_up)
        self.cli_input.bind("<Down>", self.cli_history_down)
        

    def create_status_bar(self):
        status_frame = tk.Frame(self, bg="#34495e", height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        self.status_label = tk.Label(status_frame, text="Ready", bg="#34495e", fg="#ecf0f1",
                                     font=("Helvetica", 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.message_box = tk.Label(status_frame, text="Drag items from toolbox to workspace", fg="#2ecc71",
                                    bg="#34495e", font=("Helvetica", 9, "bold"))
        self.message_box.pack(side=tk.RIGHT, padx=10)

    # === Drag and Drop Methods ===
    def start_drag(self, item_type, event):
        self.dragging = True
        self.drag_type = item_type
        self.drag_item = None
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.cli_print(f"Dragging {item_type} from toolbox")

    def canvas_click(self, event):
        items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        if items:
            item = items[-1]
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("process_"):
                    self.dragging = True
                    self.drag_item = tag
                    self.drag_type = "process"
                    self.drag_start_x = event.x
                    self.drag_start_y = event.y
                    return
                elif tag.startswith("resource_"):
                    self.dragging = True
                    self.drag_item = tag
                    self.drag_type = "resource"
                    self.drag_start_x = event.x
                    self.drag_start_y = event.y
                    return

    def canvas_drag(self, event):
        if self.dragging:
            self.canvas.delete("drag_preview")
            if self.drag_item is None and self.drag_type:
                if self.drag_type == "process":
                    self.canvas.create_oval(event.x-20, event.y-20, event.x+20, event.y+20,
                                           fill="#3498db", outline="#2980b9", width=2, tags="drag_preview")
                else:
                    self.canvas.create_rectangle(event.x-15, event.y-15, event.x+15, event.y+15,
                                                fill="#e67e22", outline="#d35400", width=2, tags="drag_preview")
            elif self.drag_item:
                dx = event.x - self.drag_start_x
                dy = event.y - self.drag_start_y
                item_parts = self.canvas.find_withtag(self.drag_item)
                for part in item_parts:
                    self.canvas.move(part, dx, dy)
                if self.drag_type == "resource":
                    resource_id = self.drag_item.split("_")[1]
                    text_tag = f"resource_{resource_id}_text"
                    if self.canvas.find_withtag(text_tag):
                        self.canvas.move(text_tag, dx, dy)
                self.drag_start_x = event.x
                self.drag_start_y = event.y

    def canvas_release(self, event):
        if self.dragging:
            self.canvas.delete("drag_preview")
            if self.drag_item is None and self.drag_type:
                if self.drag_type == "process":
                    self.create_process(event.x, event.y)
                else:
                    self.create_resource(event.x, event.y)
            self.dragging = False
            self.drag_item = None
            self.drag_type = None

    def canvas_double_click(self, event):
        items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        if items:
            item = items[-1]
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("process_"):
                    process_id = tag.split("_")[1]
                    self.configure_process(process_id)
                    return
                elif tag.startswith("resource_"):
                    resource_id = tag.split("_")[1]
                    self.configure_resource(resource_id)
                    return

    def canvas_right_click(self, event):
        items = self.canvas.find_overlapping(event.x - 5, event.y - 5, event.x + 5, event.y + 5)
        if items:
            item = items[-1]
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("process_"):
                    process_id = tag.split("_")[1]
                    menu = tk.Menu(self, tearoff=0)
                    menu.add_command(label=f"Request Resource", command=lambda: self.request_resource(process_id))
                    menu.add_command(label=f"Release Resources", command=lambda: self.release_resources(process_id))
                    menu.add_command(label=f"Delete {process_id}", command=lambda: self.delete_item(process_id, "process"))
                    menu.post(event.x_root, event.y_root)
                    return
                elif tag.startswith("resource_"):
                    resource_id = tag.split("_")[1]
                    menu = tk.Menu(self, tearoff=0)
                    menu.add_command(label=f"Delete {resource_id}", command=lambda: self.delete_item(resource_id, "resource"))
                    menu.post(event.x_root, event.y_root)
                    return
                
    # === Process/Resource Management ===
    def create_process(self, x, y):#_______________________________________________________________________________________P
        process_id = f"P{len(self.processes)}"
        self.processes.append(process_id)
        # Initialize with zeros for all existing resources
        self.allocation[process_id] = [0] * len(self.resources)
        self.max_need[process_id] = [0] * len(self.resources)
        self.request[process_id] = [0] * len(self.resources)
        self.process_descriptions[process_id] = f"Process {process_id}"
        
        self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="#3498db",
                               outline="#2980b9", width=2, tags=f"process_{process_id}")
        self.canvas.create_text(x, y, text=process_id, font=("Helvetica", 10, "bold"),
                               fill="white", tags=f"process_{process_id}")
        
        self.cli_print(f"Created {process_id} at ({x}, {y})")
        self.message_box.config(text=f"Created {process_id}. Double-click to configure.", fg="#2ecc71")

    def create_resource(self, x, y):#_______________________________________________________________________________________P
        resource_id = f"R{len(self.resources)}"
        self.resources.append(resource_id)
        self.resource_instances.append(1)
        self.available.append(1)
        
        # Add a new resource column to all existing processes
        for process_id in self.processes:
            self.allocation[process_id].append(0)
            self.max_need[process_id].append(0)
            self.request[process_id].append(0)
            
        self.canvas.create_rectangle(x-15, y-15, x+15, y+15, fill="#e67e22",
                                   outline="#d35400", width=2, tags=f"resource_{resource_id}")
        self.canvas.create_text(x, y, text=resource_id, font=("Helvetica", 10, "bold"),
                               fill="white", tags=f"resource_{resource_id}")
        self.canvas.create_text(x, y+30, text=f"Available: 1", font=("Helvetica", 8),
                               fill="#7f8c8d", tags=f"resource_{resource_id}_text")
        
        self.cli_print(f"Created {resource_id} at ({x}, {y})")
        self.message_box.config(text=f"Created {resource_id}. Double-click to configure.", fg="#2ecc71")

    def delete_item(self, item_id, item_type):#_______________________________________________________________________________________A
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {item_id}?"):
            if item_type == "process":
                if item_id in self.processes:
                    self.processes.remove(item_id)
                if item_id in self.allocation:
                    del self.allocation[item_id]
                if item_id in self.max_need:
                    del self.max_need[item_id]
                if item_id in self.request:
                    del self.request[item_id]
                if item_id in self.process_descriptions:
                    del self.process_descriptions[item_id]
            elif item_type == "resource":
                if item_id in self.resources:
                    idx = self.resources.index(item_id)
                    self.resources.pop(idx)
                    self.available.pop(idx)
                    self.resource_instances.pop(idx)
                    for p in self.processes:
                        if p in self.allocation and len(self.allocation[p]) > idx:
                            self.allocation[p].pop(idx)
                        if p in self.max_need and len(self.max_need[p]) > idx:
                            self.max_need[p].pop(idx)
                        if p in self.request and len(self.request[p]) > idx:
                            self.request[p].pop(idx)
                    
            self.canvas.delete(f"{item_type}_{item_id}")
            self.canvas.delete(f"{item_type}_{item_id}_text")
            self.cli_print(f"Deleted {item_id}")
            self.message_box.config(text=f"Deleted {item_id}", fg="#e74c3c")
            self.update_available_resources()
            self.draw_resource_graph()

    def configure_process(self, process_id):
        if process_id not in self.processes:
            messagebox.showerror("Error", f"Process {process_id} not found.")
            return
            
        popup = tk.Toplevel(self)
        popup.title(f"Configure {process_id}")
        popup.geometry("400x300")
        popup.transient(self)
        popup.grab_set()
        
        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Description:").grid(row=0, column=0, sticky="w", pady=5)
        desc_entry = tk.Entry(frame, width=30)
        desc_entry.insert(0, self.process_descriptions.get(process_id, ""))
        desc_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        
        if self.resources:
            tk.Label(frame, text="Resource", relief=tk.GROOVE).grid(row=1, column=0, sticky="ew", pady=2)
            tk.Label(frame, text="Allocation", relief=tk.GROOVE).grid(row=1, column=1, sticky="ew", pady=2)
            tk.Label(frame, text="Max Need", relief=tk.GROOVE).grid(row=1, column=2, sticky="ew", pady=2)
        
        alloc_entries = {}
        max_entries = {}
        
        for i, resource_id in enumerate(self.resources):
            tk.Label(frame, text=resource_id).grid(row=i+2, column=0, sticky="w", pady=2)
            
            alloc_var = tk.StringVar(value=str(self.allocation[process_id][i]))
            alloc_entry = tk.Spinbox(frame, from_=0, to=self.resource_instances[i],
                                     textvariable=alloc_var, width=5)
            alloc_entry.grid(row=i+2, column=1, pady=2, padx=2)
            alloc_entries[resource_id] = alloc_var
            
            max_var = tk.StringVar(value=str(self.max_need[process_id][i]))
            max_entry = tk.Spinbox(frame, from_=0, to=self.resource_instances[i],
                                   textvariable=max_var, width=5)
            max_entry.grid(row=i+2, column=2, pady=2, padx=2)
            max_entries[resource_id] = max_var

        def save_config():
            self.process_descriptions[process_id] = desc_entry.get()
            for i, resource_id in enumerate(self.resources):
                try:
                    alloc = int(alloc_entries[resource_id].get())
                    max_need = int(max_entries[resource_id].get())
                except ValueError:
                    messagebox.showerror("Error", f"Invalid number for {resource_id}")
                    return
                    
                if alloc > max_need:
                    messagebox.showerror("Error", f"Allocation cannot exceed max need for {resource_id}")
                    return
                    
                if alloc > self.resource_instances[i]:
                    messagebox.showerror("Error", f"Allocation cannot exceed total instances for {resource_id}")
                    return
                    
                self.allocation[process_id][i] = alloc
                self.max_need[process_id][i] = max_need
                self.request[process_id][i] = max(0, max_need - alloc)
                
            self.update_available_resources()
            self.draw_resource_graph()
            popup.destroy()
            self.cli_print(f"Updated configuration for {process_id}")
            self.message_box.config(text=f"Updated {process_id}", fg="#2ecc71")
            
        tk.Button(popup, text="Save", command=save_config).pack(pady=10)

    def configure_resource(self, resource_id):
        if resource_id not in self.resources:
            messagebox.showerror("Error", f"Resource {resource_id} not found.")
            return
            
        popup = tk.Toplevel(self)
        popup.title(f"Configure {resource_id}")
        popup.geometry("300x150")
        popup.transient(self)
        popup.grab_set()
        
        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        idx = self.resources.index(resource_id)
        tk.Label(frame, text="Number of instances:").grid(row=0, column=0, sticky="w", pady=5)
        instances_var = tk.StringVar(value=str(self.resource_instances[idx]))
        instances_entry = tk.Spinbox(frame, from_=1, to=10, textvariable=instances_var, width=5)
        instances_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        def save_config():
            try:
                new_instances = int(instances_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
                return
                
            old_instances = self.resource_instances[idx]
            
            if new_instances < sum(self.allocation[p][idx] for p in self.processes):
                messagebox.showerror("Error", "New instances cannot be less than total allocated instances.")
                return
                
            self.resource_instances[idx] = new_instances
            self.available[idx] += (new_instances - old_instances)
            self.update_available_resources()
            self.draw_resource_graph()
            popup.destroy()
            self.cli_print(f"Updated {resource_id} to {new_instances} instances")
            self.message_box.config(text=f"Updated {resource_id}", fg="#2ecc71")
            
        tk.Button(popup, text="Save", command=save_config).pack(pady=10)

    def configure_all(self):
        if not self.processes:
            messagebox.showinfo("Info", "No processes to configure. Add processes first.")
            return
            
        popup = tk.Toplevel(self)
        popup.title("Configure All Processes")
        popup.geometry("600x400")
        popup.transient(self)
        popup.grab_set()
        
        notebook = ttk.Notebook(popup)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        frames = {}
        for process_id in self.processes:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=process_id)
            
            tk.Label(frame, text="Description:").grid(row=0, column=0, sticky="w", pady=5)
            desc_entry = tk.Entry(frame, width=30)
            desc_entry.insert(0, self.process_descriptions.get(process_id, ""))
            desc_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5, columnspan=2)
            
            if self.resources:
                tk.Label(frame, text="Resource", relief=tk.GROOVE).grid(row=1, column=0, sticky="ew", pady=2)
                tk.Label(frame, text="Allocation", relief=tk.GROOVE).grid(row=1, column=1, sticky="ew", pady=2)
                tk.Label(frame, text="Max Need", relief=tk.GROOVE).grid(row=1, column=2, sticky="ew", pady=2)
            
            alloc_entries = {}
            max_entries = {}
            
            for i, resource_id in enumerate(self.resources):
                tk.Label(frame, text=resource_id).grid(row=i+2, column=0, sticky="w", pady=2)
                
                alloc_var = tk.StringVar(value=str(self.allocation[process_id][i]))
                alloc_entry = tk.Spinbox(frame, from_=0, to=self.resource_instances[i],
                                         textvariable=alloc_var, width=5)
                alloc_entry.grid(row=i+2, column=1, pady=2, padx=2)
                alloc_entries[resource_id] = alloc_var
                
                max_var = tk.StringVar(value=str(self.max_need[process_id][i]))
                max_entry = tk.Spinbox(frame, from_=0, to=self.resource_instances[i],
                                       textvariable=max_var, width=5)
                max_entry.grid(row=i+2, column=2, pady=2, padx=2)
                max_entries[resource_id] = max_var
                
            frame.desc_entry = desc_entry
            frame.alloc_entries = alloc_entries
            frame.max_entries = max_entries
            frames[process_id] = frame

        def save_all_config():#_______________________________________________________________________________________A
            for process_id in self.processes:
                frame = frames[process_id]
                self.process_descriptions[process_id] = frame.desc_entry.get()
                for i, resource_id in enumerate(self.resources):
                    try:
                        alloc = int(frame.alloc_entries[resource_id].get())
                        max_need = int(frame.max_entries[resource_id].get())
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid number for {process_id} on {resource_id}")
                        return
                        
                    if alloc > max_need:
                        messagebox.showerror("Error",
                                            f"Allocation cannot exceed max need for {process_id} on {resource_id}")
                        return
                        
                    if alloc > self.resource_instances[i]:
                        messagebox.showerror("Error",
                                            f"Allocation cannot exceed total instances for {process_id} on {resource_id}")
                        return
                        
                    self.allocation[process_id][i] = alloc
                    self.max_need[process_id][i] = max_need
                    self.request[process_id][i] = max(0, max_need - alloc)
                    
            self.update_available_resources()
            self.draw_resource_graph()
            popup.destroy()
            self.cli_print("Updated configuration for all processes")
            self.message_box.config(text="Updated all processes", fg="#2ecc71")
            
        tk.Button(popup, text="Save All", command=save_all_config).pack(pady=10)

    def update_available_resources(self):
        if not self.resources:
            return
            
        for i in range(len(self.resources)):
            total_allocated = sum(self.allocation[process_id][i] for process_id in self.processes)
            self.available[i] = self.resource_instances[i] - total_allocated
            resource_id = self.resources[i]
            
            self.canvas.delete(f"resource_{resource_id}_text")
            coords = self.canvas.coords(f"resource_{resource_id}")
            if coords:
                x = (coords[0] + coords[2]) / 2
                y = (coords[1] + coords[3]) / 2
                self.canvas.create_text(
                    x, y + 30,
                    text=f"Available: {self.available[i]}", font=("Helvetica", 8),
                    fill="#7f8c8d", tags=f"resource_{resource_id}_text"
                )

    def draw_resource_graph(self, highlight_path=None):
        self.canvas.delete("graph_arrow")
        if highlight_path is None:
            highlight_path = []
            
        # Allocation arrows (Resource -> Process)
        for p_id in self.processes:
            p_coords = self.canvas.coords(f"process_{p_id}")
            if not p_coords: continue
            p_x, p_y = (p_coords[0] + p_coords[2]) / 2, (p_coords[1] + p_coords[3]) / 2
            for r_idx, r_id in enumerate(self.resources):
                if self.allocation[p_id][r_idx] > 0:
                    r_coords = self.canvas.coords(f"resource_{r_id}")
                    if not r_coords: continue
                    r_x, r_y = (r_coords[0] + r_coords[2]) / 2, (r_coords[1] + r_coords[3]) / 2
                    fill_color = "#2ecc71"
                    if (r_id, p_id) in highlight_path:
                        fill_color = "#e74c3c"
                    self.canvas.create_line(r_x, r_y, p_x, p_y, arrow=tk.LAST,
                                            fill=fill_color, width=2, tags="graph_arrow")
                                            
        # Request arrows (Process -> Resource)
        for p_id in self.processes:
            p_coords = self.canvas.coords(f"process_{p_id}")
            if not p_coords: continue
            p_x, p_y = (p_coords[0] + p_coords[2]) / 2, (p_coords[1] + p_coords[3]) / 2
            for r_idx, r_id in enumerate(self.resources):
                if self.request[p_id][r_idx] > 0:
                    r_coords = self.canvas.coords(f"resource_{r_id}")
                    if not r_coords: continue
                    r_x, r_y = (r_coords[0] + r_coords[2]) / 2, (r_coords[1] + r_coords[3]) / 2
                    fill_color = "#f39c12"
                    if (p_id, r_id) in highlight_path:
                        fill_color = "#e74c3c"
                    self.canvas.create_line(p_x, p_y, r_x, r_y, arrow=tk.LAST,
                                            fill=fill_color, width=2, tags="graph_arrow")

    def request_resource(self, process_id):#_______________________________________________________________________________________P
        """Process requests a resource"""
        if not self.resources:
            messagebox.showinfo("Info", "No resources available to request.")
            return
            
        popup = tk.Toplevel(self)
        popup.title(f"Request Resource for {process_id}")
        popup.geometry("300x200")
        popup.transient(self)
        popup.grab_set()
        
        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Select Resource:").pack(pady=5)
        resource_var = tk.StringVar()
        resource_menu = ttk.Combobox(frame, textvariable=resource_var, 
                                    values=self.resources, state="readonly")
        resource_menu.pack(pady=5)
        
        tk.Label(frame, text="Number of instances:").pack(pady=5)
        instances_var = tk.StringVar(value="1")
        instances_entry = tk.Entry(frame, textvariable=instances_var)
        instances_entry.pack(pady=5)

        def make_request():
            resource_id = resource_var.get()
            if not resource_id:
                messagebox.showerror("Error", "Please select a resource")
                return
                
            try:
                instances = int(instances_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
                return
                
            r_idx = self.resources.index(resource_id)
            current_request = self.request[process_id][r_idx]
            max_need = self.max_need[process_id][r_idx]
            current_alloc = self.allocation[process_id][r_idx]
            
            if current_alloc + instances > max_need:
                messagebox.showerror("Error", f"Cannot exceed max need of {max_need} for {resource_id}")
                return
                
            if instances > self.available[r_idx]:
                self.cli_print(f"Request denied: {process_id} requests {instances} of {resource_id} but only {self.available[r_idx]} available")
                self.message_box.config(text=f"Request denied for {process_id}", fg="#e74c3c")
                self.start_toggling("conflict")
                popup.destroy()
                return
                
            # Simulate granting the request
            self.allocation[process_id][r_idx] += instances
            self.request[process_id][r_idx] = max(0, max_need - self.allocation[process_id][r_idx])
            self.available[r_idx] -= instances
            
            self.update_available_resources()
            self.draw_resource_graph()
            self.cli_print(f"Request granted: {process_id} allocated {instances} of {resource_id}")
            self.message_box.config(text=f"Request granted for {process_id}", fg="#2ecc71")
            self.stop_toggling()
            self.update_npc_display("normal")
            popup.destroy()

        tk.Button(popup, text="Request", command=make_request).pack(pady=10)

    def release_resources(self, process_id):#_______________________________________________________________________________________A
        """Process releases all its resources"""
        if not self.resources:
            messagebox.showinfo("Info", "No resources to release.")
            return
            
        resources_to_release = []
        for r_idx, r_id in enumerate(self.resources):
            if self.allocation[process_id][r_idx] > 0:
                resources_to_release.append((r_id, self.allocation[process_id][r_idx]))
                
        if not resources_to_release:
            messagebox.showinfo("Info", f"{process_id} has no allocated resources to release.")
            return
            
        for r_id, count in resources_to_release:
            r_idx = self.resources.index(r_id)
            self.available[r_idx] += count
            self.allocation[process_id][r_idx] = 0
            self.request[process_id][r_idx] = self.max_need[process_id][r_idx]
            
        self.update_available_resources()
        self.draw_resource_graph()
        self.cli_print(f"{process_id} released all resources")
        self.message_box.config(text=f"{process_id} released resources", fg="#2ecc71")
        self.stop_toggling()
        self.update_npc_display("normal")

#------------------------------------------Priyancy-ALGO------------------------------------------#

    # === Algorithm Implementations ===
    def check_safe_state(self):
        """Banker's Algorithm for deadlock avoidance"""
        if not self.processes or not self.resources:
            messagebox.showinfo("Info", "Add processes and resources first.")
            return
            
        work = self.available.copy()
        finish = {p: False for p in self.processes}
        need = {p: [self.max_need[p][i] - self.allocation[p][i] for i in range(len(self.resources))]
                for p in self.processes}
        safe_sequence = []
        
        while len(safe_sequence) < len(self.processes):
            found = False
            for p in self.processes:
                if not finish[p]:
                    # Check if need[p] <= work
                    can_allocate = True
                    for i in range(len(self.resources)):
                        if need[p][i] > work[i]:
                            can_allocate = False
                            break
                            
                    if can_allocate:
                        # Simulate allocation
                        for i in range(len(self.resources)):
                            work[i] += self.allocation[p][i]
                        finish[p] = True
                        safe_sequence.append(p)
                        found = True
                        break
                        
            if not found:
                break
                
        if len(safe_sequence) == len(self.processes):
            result = f"System is in a safe state.\nSafe sequence: {' -> '.join(safe_sequence)}"
            self.last_banker_result = True
            self.stop_toggling()
            self.update_npc_display("normal")
        else:
            result = "System is in an unsafe state (potential deadlock)."
            self.last_banker_result = False
            self.start_toggling("conflict")
            
        self.cli_print("=== Banker's Algorithm Result ===")
        self.cli_print(result)
        self.message_box.config(text="Banker's algorithm executed", fg="#2ecc71" if self.last_banker_result else "#e74c3c")
        
        return len(safe_sequence) == len(self.processes)

    def detect_deadlock(self):
        """Deadlock detection algorithm"""
        if not self.processes or not self.resources:
            messagebox.showinfo("Info", "Add processes and resources first.")
            return
            
        work = self.available.copy()
        finish = {p: sum(self.allocation[p]) == 0 for p in self.processes}
        deadlocked_processes = []
        
        while True:
            found = False
            for p in self.processes:
                if not finish[p]:
                    can_finish = True
                    for i in range(len(self.resources)):
                        if self.request[p][i] > work[i]:
                            can_finish = False
                            break
                            
                    if can_finish:
                        for i in range(len(self.resources)):
                            work[i] += self.allocation[p][i]
                        finish[p] = True
                        found = True
                        
            if not found:
                break
                
        deadlocked_processes = [p for p in self.processes if not finish[p]]
        
        if deadlocked_processes:
            result = f"Deadlock detected! Deadlocked processes: {', '.join(deadlocked_processes)}"
            self.last_detection_result = True
            self.start_toggling("deadlock")
        else:
            result = "No deadlock detected."
            self.last_detection_result = False
            self.stop_toggling()
            self.update_npc_display("normal")
            
        self.cli_print("=== Deadlock Detection Result ===")
        self.cli_print(result)
        self.message_box.config(text="Deadlock detection executed", fg="#e74c3c" if deadlocked_processes else "#2ecc71")
        
        return deadlocked_processes

    def recover_from_deadlock(self):
        """Deadlock recovery by terminating processes"""
        deadlocked_processes = self.detect_deadlock()
        if not deadlocked_processes:
            messagebox.showinfo("Info", "No deadlock to recover from.")
            return
            
        popup = tk.Toplevel(self)
        popup.title("Recover from Deadlock")
        popup.geometry("400x300")
        popup.transient(self)
        popup.grab_set()
        
        frame = tk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Select process to terminate:").pack(pady=5)
        process_var = tk.StringVar()
        process_menu = ttk.Combobox(frame, textvariable=process_var,
                                   values=deadlocked_processes, state="readonly")
        process_menu.pack(pady=5)
        
        def terminate_process():
            process_id = process_var.get()
            if not process_id:
                messagebox.showerror("Error", "Please select a process to terminate")
                return
                
            # Release all resources held by the process
            for r_idx, r_id in enumerate(self.resources):
                self.available[r_idx] += self.allocation[process_id][r_idx]
                self.allocation[process_id][r_idx] = 0
                self.max_need[process_id][r_idx] = 0
                self.request[process_id][r_idx] = 0
                
            self.update_available_resources()
            self.draw_resource_graph()
            self.cli_print(f"Terminated {process_id} to recover from deadlock")
            self.message_box.config(text=f"Terminated {process_id} for recovery", fg="#f39c12")
            self.stop_toggling()
            self.update_npc_display("normal")
            popup.destroy()
            
        tk.Button(popup, text="Terminate Process", command=terminate_process).pack(pady=10)

    def generate_random_state(self):
        """Generate a random system state for testing"""
        if not self.processes or not self.resources:
            messagebox.showinfo("Info", "Add processes and resources first.")
            return
            
        for p in self.processes:
            for r_idx in range(len(self.resources)):
                max_instances = self.resource_instances[r_idx]
                alloc = random.randint(0, max_instances)
                max_need = random.randint(alloc, max_instances)
                self.allocation[p][r_idx] = alloc
                self.max_need[p][r_idx] = max_need
                self.request[p][r_idx] = max_need - alloc
                
        self.update_available_resources()
        self.draw_resource_graph()
        self.cli_print("Generated random system state")
        self.message_box.config(text="Generated random state", fg="#9b59b6")


#------------------------------------------Aarti-CLI------------------------------------------#
    # === CLI Methods ===
    def cli_print(self, message):
        self.cli_output.config(state=tk.NORMAL)
        self.cli_output.insert(tk.END, f"{message}\n")
        self.cli_output.see(tk.END)
        self.cli_output.config(state=tk.DISABLED)

    def process_cli_command(self, event):
        command = self.cli_input.get().strip()
        if not command:
            return
            
        self.cli_input.delete(0, tk.END)
        self.cli_history.append(command)
        self.history_index = len(self.cli_history)
        
        self.cli_print(f"> {command}")
        
        parts = command.lower().split()
        cmd = parts[0]
        
        if cmd == "help":
            self.cli_print("Available commands:")
            self.cli_print("  help - Show this help")
            self.cli_print("  add process - Add a new process")
            self.cli_print("  add resource - Add a new resource")
            self.cli_print("  list - List all processes and resources")
            self.cli_print("  banker - Run Banker's algorithm")
            self.cli_print("  detect - Detect deadlock")
            self.cli_print("  recover - Recover from deadlock")
            self.cli_print("  random - Generate random state")
            self.cli_print("  clear - Clear CLI output")
            
        elif cmd == "add":
            if len(parts) > 1:
                if parts[1] == "process":
                    self.create_process(100, 100)
                elif parts[1] == "resource":
                    self.create_resource(100, 100)
                else:
                    self.cli_print("Usage: add [process|resource]")
            else:
                self.cli_print("Usage: add [process|resource]")
                
        elif cmd == "list":
            self.cli_print("Processes: " + ", ".join(self.processes))
            self.cli_print("Resources: " + ", ".join(self.resources))
            
        elif cmd == "banker":
            self.check_safe_state()
            
        elif cmd == "detect":
            self.detect_deadlock()
            
        elif cmd == "recover":
            self.recover_from_deadlock()
            
        elif cmd == "random":
            self.generate_random_state()
            
        elif cmd == "clear":
            self.cli_output.config(state=tk.NORMAL)
            self.cli_output.delete(1.0, tk.END)
            self.cli_output.config(state=tk.DISABLED)
            
        else:
            self.cli_print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    def cli_history_up(self, event):
        if self.cli_history and self.history_index > 0:
            self.history_index -= 1
            self.cli_input.delete(0, tk.END)
            self.cli_input.insert(0, self.cli_history[self.history_index])

    def cli_history_down(self, event):
        if self.cli_history and self.history_index < len(self.cli_history) - 1:
            self.history_index += 1
            self.cli_input.delete(0, tk.END)
            self.cli_input.insert(0, self.cli_history[self.history_index])
        elif self.history_index == len(self.cli_history) - 1:
            self.history_index = len(self.cli_history)
            self.cli_input.delete(0, tk.END)

    def update_status(self, message, color="#ecf0f1"):
        self.status_label.config(text=message, fg=color)

if __name__ == "__main__":
    app = Phase2DeadlockSimulator()
    app.mainloop()