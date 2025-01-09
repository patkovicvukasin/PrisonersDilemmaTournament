import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import importlib.util
from utils.abstract_bot import AbstractBot
from simulation.simulate_tournament import TournamentSimulation
from simulation.simulate_games import PrisonersDilemmaSimulation
from .shared_style import Style

class GameUI:
    def __init__(self, parent):
        # Initialize tooltip-related attributes at the start
        self.tooltip = None
        self.tooltip_id = None
        self.current_item = -1
        
        # Add mode detection based on window title
        self.mode = "game"  # default mode
        if parent.winfo_toplevel().title() == "Tournament Mode":
            self.mode = "tournament"
        elif parent.winfo_toplevel().title() == "Test Against Multiple Opponents":
            self.mode = "multiple"
            
        self.parent = parent
        
        # Get screen dimensions
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        
        # Initialize variables first
        self.available_bots = self.load_bots()
        self.filename_to_display = {}
        self.game_button = None
        self.tournament_button = None
        self.player2_path = None
        self.player2_entry = None
        self.bot_paths = []  # Add bot_paths as instance variable
        self.show_prebuilt = tk.BooleanVar(value=True)
        self.show_custom = tk.BooleanVar(value=True)
        
        # Configure parent frame to expand
        parent.grid_rowconfigure(1, weight=1)  # Changed from 0 to 1 to match the content row
        parent.grid_columnconfigure(0, weight=1)
        
        # Configure dark theme
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabelframe', background='#1a1a1a', foreground='white')
        style.configure('TLabelframe.Label', background='#1a1a1a', foreground='white')
        style.configure('TLabel', background='#1a1a1a', foreground='white')
        style.configure('TRadiobutton', background='#1a1a1a', foreground='white')
        
        # Add style for checkbuttons
        style.configure('Custom.TCheckbutton',
                      background=Style.COLORS['bg'],
                      foreground=Style.COLORS['text'])
        
        # Update style configurations
        style = ttk.Style()
        # Main container frame - invisible border
        style.configure('Container.TFrame', 
                       background=Style.COLORS['bg'],
                       borderwidth=0)  # No border for main container
        
        # Content frame - visible white border
        style.configure('Custom.TFrame', 
                       background=Style.COLORS['bg'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=Style.COLORS['text'])  # White border
        
        # Inner frames - white border
        style.configure('Custom.TLabelframe', 
                       background=Style.COLORS['bg'],
                       foreground=Style.COLORS['text'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=Style.COLORS['text'])  # White border
        # Override the default background for all text labels
        style.configure('TLabel',
                       background=Style.COLORS['bg'],
                       foreground=Style.COLORS['text'])
        
        # Create main frame without border
        self.main_frame = ttk.Frame(parent, padding="20", style='Container.TFrame')
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        # Configure main frame size
        self.main_frame.grid_propagate(False)
        self.main_frame.configure(width=screen_width-100, height=screen_height-200)

        # Get mode from window title
        window_title = parent.winfo_toplevel().title()
        self.mode = "game"  # default mode
        if "Tournament" in window_title:
            self.mode = "tournament"
        elif "Multiple" in window_title:
            self.mode = "multiple"
        
        # Initialize frames based on mode
        if self.mode == "tournament":
            # Tournament mode - only center and right frames
            self.main_frame.grid_columnconfigure(0, weight=2)  # Log
            self.main_frame.grid_columnconfigure(1, weight=1)  # Participants
            
            self.center_frame = ttk.LabelFrame(self.main_frame, 
                                             text="Tournament Log", 
                                             padding="10",
                                             style='Custom.TLabelframe')
            self.right_frame = ttk.LabelFrame(self.main_frame, 
                                            text="Participants", 
                                            padding="10",
                                            style='Custom.TLabelframe')
            
            self.center_frame.grid(row=0, column=0, sticky="nsew", pady=20, padx=10)
            self.right_frame.grid(row=0, column=1, sticky="nsew", pady=20, padx=10)

            # Configure frame weights
            for frame in [self.center_frame, self.right_frame]:
                frame.grid_rowconfigure(0, weight=3)
                frame.grid_columnconfigure(0, weight=1)

            # Setup widgets
            self.setup_log_widget()
            self.setup_participants_listbox()

        else:
            # Game or Multiple mode - three column layout
            self.main_frame.grid_columnconfigure(0, weight=1)  # Left bot
            self.main_frame.grid_columnconfigure(1, weight=2)  # Log
            self.main_frame.grid_columnconfigure(2, weight=1)  # Right bot(s)
            
            self.left_frame = ttk.LabelFrame(self.main_frame, 
                                           text="Your Bot", 
                                           padding="10",
                                           style='Custom.TLabelframe')
            self.center_frame = ttk.LabelFrame(self.main_frame, 
                                             text="Game Log", 
                                             padding="10",
                                             style='Custom.TLabelframe')
            self.right_frame = ttk.LabelFrame(self.main_frame, 
                                            text="Player 2" if self.mode == "game" else "Opponents", 
                                            padding="10",
                                            style='Custom.TLabelframe')
            
            self.left_frame.grid(row=0, column=0, sticky="nsew", pady=20, padx=10)
            self.center_frame.grid(row=0, column=1, sticky="nsew", pady=20)
            self.right_frame.grid(row=0, column=2, sticky="nsew", pady=20, padx=10)
            
            # Configure frame weights
            for frame in [self.left_frame, self.center_frame, self.right_frame]:
                frame.grid_rowconfigure(0, weight=3)
                frame.grid_columnconfigure(0, weight=1)

            # Setup player 1 frame
            select_label = ttk.Label(self.left_frame, text="Select Bot File:", style='Custom.TLabel')
            select_label.pack(pady=5)
            
            self.player1_path = tk.StringVar()
            entry = ttk.Entry(self.left_frame, textvariable=self.player1_path, width=50)
            entry.pack(pady=5)
            
            browse_btn = tk.Button(self.left_frame, text="Browse", command=self.browse_file, **Style.button_style())
            browse_btn.pack(pady=5)
            
            # Add hover effect
            browse_btn.bind('<Enter>', lambda e: browse_btn.configure(bg=Style.COLORS['button_hover']))
            browse_btn.bind('<Leave>', lambda e: browse_btn.configure(bg=Style.COLORS['button']))

            # Setup center frame (log)
            self.setup_log_widget()
            
            # Setup right frame (opponents)
            listbox_frame = ttk.Frame(self.right_frame)
            listbox_frame.pack(fill=tk.BOTH, expand=True)
            
            self.bot_listbox = tk.Listbox(listbox_frame,
                                        selectmode=tk.SINGLE if self.mode == "game" else tk.MULTIPLE,
                                        bg=Style.COLORS['button'],
                                        fg=Style.COLORS['text'],
                                        font=Style.FONTS['text'],
                                        selectbackground=Style.COLORS['button_hover'],
                                        selectforeground=Style.COLORS['text'])
            
            scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.bot_listbox.yview)
            self.bot_listbox.configure(yscrollcommand=scrollbar.set)
            
            if self.mode == "multiple":
                # Add Select All checkbox for multiple mode
                self.select_all_var = tk.BooleanVar()
                select_all_btn = ttk.Checkbutton(
                    self.right_frame,
                    text="Select All",
                    variable=self.select_all_var,
                    style='Custom.TCheckbutton',
                    command=self.toggle_select_all)
                select_all_btn.pack(pady=(5,0), anchor="w")
            
            # Add filter checkboxes before the listbox
            filter_frame = ttk.Frame(self.right_frame, style='Custom.TFrame')
            filter_frame.pack(fill=tk.X, pady=(0, 5))
            
            prebuilt_check = ttk.Checkbutton(
                filter_frame,
                text="Show Prebuilt Bots",
                variable=self.show_prebuilt,
                style='Custom.TCheckbutton',
                command=self.filter_bots)
            prebuilt_check.pack(side=tk.LEFT, padx=5)
            
            custom_check = ttk.Checkbutton(
                filter_frame,
                text="Show Custom Bots",
                variable=self.show_custom,
                style='Custom.TCheckbutton',
                command=self.filter_bots)
            custom_check.pack(side=tk.LEFT, padx=5)
            
            self.bot_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Add custom bot button
            custom_btn = tk.Button(self.right_frame, 
                                 text="Add Custom Bot",
                                 command=self.add_custom_bot,
                                 **Style.button_style())
            custom_btn.pack(pady=5)
            
            # Add hover effect
            custom_btn.bind('<Enter>', lambda e: custom_btn.configure(bg=Style.COLORS['button_hover']))
            custom_btn.bind('<Leave>', lambda e: custom_btn.configure(bg=Style.COLORS['button']))
            
            # Update bot list
            self.update_bot_dropdown()
            
            # Bind tooltip events
            self.bot_listbox.bind('<Motion>', self.schedule_tooltip)
            self.bot_listbox.bind('<Leave>', self.schedule_hide_tooltip)

    def create_player_frame(self, title):
        # Helper method to create player frame with file selection
        frame = ttk.LabelFrame(self.main_frame, text=title, padding="10", style='Custom.TLabelframe')
        
        select_label = ttk.Label(frame, text="Select Bot File:", style='Custom.TLabel')
        select_label.pack(pady=5)
        
        self.player1_path = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=self.player1_path, width=50)
        entry.pack(pady=5)
        
        browse_btn = tk.Button(frame, text="Browse", command=self.browse_file, **Style.button_style())
        browse_btn.pack(pady=5)
        
        browse_btn.bind('<Enter>', lambda e: browse_btn.configure(bg=Style.COLORS['button_hover']))
        browse_btn.bind('<Leave>', lambda e: browse_btn.configure(bg=Style.COLORS['button']))
        
        return frame

    def create_log_frame(self, title):
        # Helper method to create log frame
        frame = ttk.LabelFrame(self.main_frame, text=title, padding="10", style='Custom.TLabelframe')
        # ...rest of existing log frame creation code...
        return frame

    def create_bot_frame(self, title):
        # Helper method to create bot selection frame
        frame = ttk.LabelFrame(self.main_frame, text=title, padding="10", style='Custom.TLabelframe')
        # ...rest of existing bot frame creation code...
        return frame

    def setup_log_widget(self):
        # Update log widget with monospace font and increased width
        self.log_text = tk.Text(self.center_frame, 
                               width=80,  # Increased from 50 to 80
                               height=20,
                               bg=Style.COLORS['button'],
                               fg=Style.COLORS['text'],
                               font=('Courier', 10),
                               wrap=tk.NONE)  # Disable text wrapping

        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.center_frame, 
                                  orient="horizontal",
                                  command=self.log_text.xview)
        v_scrollbar = ttk.Scrollbar(self.center_frame, 
                                  orient="vertical",
                                  command=self.log_text.yview)
        self.log_text.configure(xscrollcommand=h_scrollbar.set,
                              yscrollcommand=v_scrollbar.set)
        
        # Grid layout to accommodate both scrollbars
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Update info label
        info_label = ttk.Label(self.center_frame,
                             text="Complete results will be saved in the logs subdirectory",
                             font=Style.FONTS['text'],
                             foreground=Style.COLORS['text'],
                             background=Style.COLORS['bg'])
        info_label.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))

    def update_log(self, text):
        self.log_text.delete(1.0, tk.END)
        
        # Format the text for better alignment with tab stops
        if "Tournament Results" in text:
            # Set tab stops every 15 characters
            self.log_text.tag_configure("align", tabs=("15c", "30c", "45c", "60c"))
            self.log_text.insert(tk.END, text, "align")
        else:
            self.log_text.insert(tk.END, text)
            
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()

    def setup_participants_listbox(self):
        # Update frame style
        listbox_frame = ttk.Frame(self.right_frame, style='Custom.TFrame')
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        # First create select all checkbox if in multiple/tournament mode
        if self.mode != "game":
            self.select_all_var = tk.BooleanVar()
            select_all_btn = ttk.Checkbutton(
                self.right_frame,
                text="Select All",
                variable=self.select_all_var,
                style='Custom.TCheckbutton',
                command=self.toggle_select_all)
            select_all_btn.pack(pady=(5,0), anchor="w")

        # Add filter checkboxes before the listbox
        filter_frame = ttk.Frame(self.right_frame, style='Custom.TFrame')
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        prebuilt_check = ttk.Checkbutton(
            filter_frame,
            text="Show Prebuilt Bots",
            variable=self.show_prebuilt,
            style='Custom.TCheckbutton',
            command=self.filter_bots)
        prebuilt_check.pack(side=tk.LEFT, padx=5)
        
        custom_check = ttk.Checkbutton(
            filter_frame,
            text="Show Custom Bots",
            variable=self.show_custom,
            style='Custom.TCheckbutton',
            command=self.filter_bots)
        custom_check.pack(side=tk.LEFT, padx=5)
        
        # Create the listbox
        self.bot_listbox = tk.Listbox(listbox_frame,
                                     selectmode=tk.SINGLE if self.mode == "game" else tk.MULTIPLE,
                                     bg=Style.COLORS['button'],
                                     fg=Style.COLORS['text'],
                                     font=Style.FONTS['text'],
                                     selectbackground=Style.COLORS['button_hover'],
                                     selectforeground=Style.COLORS['text'])
        
        scrollbar = ttk.Scrollbar(listbox_frame, 
                                orient="vertical",
                                command=self.bot_listbox.yview)
        self.bot_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Pack listbox and scrollbar
        self.bot_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update the listbox content
        self.update_bot_dropdown()
        
        # Create the Add Custom Bot button and store reference
        self.add_custom_bot_button = tk.Button(self.right_frame, 
                             text="Add Custom Bot",
                             command=self.add_custom_bot,
                             **Style.button_style())
        self.add_custom_bot_button.pack(pady=5)
        
        # Add hover effect
        self.add_custom_bot_button.bind('<Enter>', lambda e: self.add_custom_bot_button.configure(bg=Style.COLORS['button_hover']))
        self.add_custom_bot_button.bind('<Leave>', lambda e: self.add_custom_bot_button.configure(bg=Style.COLORS['button']))

        # Bind tooltip events
        self.bot_listbox.bind('<Motion>', self.schedule_tooltip)
        self.bot_listbox.bind('<Leave>', self.schedule_hide_tooltip)

    def toggle_select_all(self):
        """Toggle select all items in the listbox"""
        if self.select_all_var.get():
            self.bot_listbox.select_set(0, tk.END)
        else:
            self.bot_listbox.selection_clear(0, tk.END)

    def add_custom_bot(self):
        filepath = filedialog.askopenfilename(
            title="Select Bot File",
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if filepath:
            try:
                # Try to load the bot to verify it's valid
                spec = importlib.util.spec_from_file_location("custom_bot", filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find the bot class
                bot_class = None
                for item in dir(module):
                    obj = getattr(module, item)
                    if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                        bot_class = obj
                        break
                
                if bot_class:
                    bot_instance = bot_class()
                    display_name = f"{bot_instance.name} (Custom)"
                    self.filename_to_display[display_name] = filepath
                    self.bot_paths.append(filepath)  # Add to bot paths
                    if self.show_custom.get():  # Only add to listbox if custom bots are shown
                        self.bot_listbox.insert(tk.END, display_name)
                else:
                    messagebox.showerror("Error", "No valid bot class found in file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load bot: {str(e)}")

    def get_selected_bots(self):
        """Get selected bots (both built-in and custom)"""
        bots = []
        for idx in self.bot_listbox.curselection():
            bot_name = self.bot_listbox.get(idx)
            filepath = self.filename_to_display.get(bot_name)
            if "(Custom)" in bot_name:
                bots.append(filepath)  # Custom bot - use full path
            else:
                # Built-in bot - construct path
                bots.append(os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'bots',
                    filepath
                ))
        return bots

    def browse_file2(self):
        filename = filedialog.askopenfilename(
            title="Select Bot File",
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if filename:
            self.player2_path.set(filename)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Bot File",
            filetypes=(("Python files", "*.py"), ("All files", "*.*"))
        )
        if filename:
            self.player1_path.set(filename)

    def load_bots(self):
        """Load bot classes from the bots directory and its immediate subfolders"""
        bots = {'prebuilt': {}, 'user_created': {}}
        bots_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'bots'))
        
        if not os.path.exists(bots_dir):
            os.makedirs(bots_dir)
            return bots

        # Process prebuilt and user-created directories
        prebuilt_dir = os.path.join(bots_dir, 'prebuilt')
        user_created_dir = os.path.join(bots_dir, 'user-created')
        
        # Create directories if they don't exist
        for directory in [prebuilt_dir, user_created_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Load bots from each directory
        for entry in os.scandir(prebuilt_dir):
            if entry.is_file() and entry.name.endswith('.py') and not entry.name.startswith('__'):
                try:
                    spec = importlib.util.spec_from_file_location(entry.name[:-3], entry.path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for item in dir(module):
                        obj = getattr(module, item)
                        if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                            bot_instance = obj()
                            rel_path = os.path.relpath(entry.path, bots_dir)
                            bots['prebuilt'][rel_path] = bot_instance
                            break
                except Exception as e:
                    continue

        # Load user-created bots
        for entry in os.scandir(user_created_dir):
            if entry.is_file() and entry.name.endswith('.py') and not entry.name.startswith('__'):
                try:
                    spec = importlib.util.spec_from_file_location(entry.name[:-3], entry.path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    for item in dir(module):
                        obj = getattr(module, item)
                        if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                            bot_instance = obj()
                            rel_path = os.path.relpath(entry.path, bots_dir)
                            bots['user_created'][rel_path] = bot_instance
                            break
                except Exception as e:
                    continue
        
        return bots

    def update_bot_dropdown(self):
        """Update listbox with bot names and maintain bot paths"""
        self.bot_listbox.delete(0, tk.END)
        self.filename_to_display = {}
        self.bot_paths = []
        
        # Load bots based on filter settings
        self.filter_bots()

    def filter_bots(self):
        """Filter bots based on checkbox settings"""
        self.bot_listbox.delete(0, tk.END)
        self.filename_to_display.clear()
        self.bot_paths.clear()
        
        bots_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'bots'))
        
        # Show prebuilt bots
        if self.show_prebuilt.get():
            for rel_path, bot in self.available_bots['prebuilt'].items():
                display_name = bot.name
                full_path = os.path.join(bots_dir, rel_path)
                self.filename_to_display[display_name] = rel_path
                self.bot_paths.append(full_path)
                self.bot_listbox.insert(tk.END, display_name)
        
        # Show user-created bots (including your_bot.py)
        if self.show_custom.get():
            # Add bots from user-created folder
            for rel_path, bot in self.available_bots['user_created'].items():
                display_name = f"{bot.name} (User)"
                full_path = os.path.join(bots_dir, rel_path)
                self.filename_to_display[display_name] = rel_path
                self.bot_paths.append(full_path)
                self.bot_listbox.insert(tk.END, display_name)
            
            # Add custom bots added during runtime
            for display_name, filepath in list(self.filename_to_display.items()):
                if "(Custom)" in display_name:
                    self.bot_listbox.insert(tk.END, display_name)
                    self.bot_paths.append(filepath)

    def schedule_tooltip(self, event):
        # Get the item under cursor
        index = self.bot_listbox.nearest(event.y)
        
        # If mouse is over a different item or no tooltip exists
        if index >= 0 and (index != self.current_item or not self.tooltip):
            self.current_item = index
            
            # Cancel any pending hide operations
            if self.tooltip_id:
                self.bot_listbox.after_cancel(self.tooltip_id)
                self.tooltip_id = None
            
            # Show tooltip immediately
            self.show_bot_description(event)

    def schedule_hide_tooltip(self, event):
        # Schedule hiding with a delay
        if self.tooltip_id:
            self.bot_listbox.after_cancel(self.tooltip_id)
        self.tooltip_id = self.bot_listbox.after(500, self.hide_bot_description)  # 500ms delay

    def show_bot_description(self, event):
        # Get the item under cursor
        index = self.bot_listbox.nearest(event.y)
        if index >= 0:
            bot_name = self.bot_listbox.get(index)
            filename = self.filename_to_display.get(bot_name)
            
            # Get description
            description = ""
            if "(Custom)" in bot_name:
                try:
                    spec = importlib.util.spec_from_file_location("custom_bot", filename)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for item in dir(module):
                        obj = getattr(module, item)
                        if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                            description = obj().description
                            break
                except:
                    description = "Custom bot"
            elif filename in self.available_bots:
                description = self.available_bots[filename].description
            
            # Create or update tooltip
            if description:
                if self.tooltip:
                    self.tooltip.destroy()
                x = self.bot_listbox.winfo_rootx() - 205
                y = self.bot_listbox.winfo_rooty() + event.y
                self.tooltip = tk.Toplevel(self.bot_listbox)
                self.tooltip.wm_overrideredirect(True)
                self.tooltip.wm_geometry(f"+{x}+{y}")
                
                # Add some padding around the text
                frame = ttk.Frame(self.tooltip, style='TFrame')
                frame.pack(fill=tk.BOTH, expand=True)
                
                label = ttk.Label(frame, 
                                 text=description,
                                 background=Style.COLORS['button'],
                                 foreground=Style.COLORS['text'],
                                 wraplength=200,
                                 padding=5)
                label.pack(fill=tk.BOTH, expand=True)

    def hide_bot_description(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
        self.current_item = -1
        self.tooltip_id = None

    def update_log(self, text):
        self.log_text.delete(1.0, tk.END)
        
        # Format the text for better alignment with tab stops
        if "Tournament Results" in text:
            # Set tab stops every 15 characters
            self.log_text.tag_configure("align", tabs=("15c", "30c", "45c", "60c"))
            self.log_text.insert(tk.END, text, "align")
        else:
            self.log_text.insert(tk.END, text)
            
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()

    def read_latest_log(self, summary_type="game"):
        """Read the latest log file of specified type"""
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        try:
            # Get all directories sorted by creation time
            dirs = [d for d in os.listdir(logs_dir) if os.path.isdir(os.path.join(logs_dir, d))]
            if not dirs:
                return "No log directories found"
                
            # Find latest directory based on type
            if summary_type == "tournament":
                tournament_dirs = [d for d in dirs if "tournament" in d]
                if not tournament_dirs:
                    return "No tournament logs found"
                latest_dir = max(tournament_dirs, key=lambda d: d.split('_')[0])
                filepath = os.path.join(logs_dir, latest_dir, "tournament_summary.txt")
            else:
                # For game or games_summary
                game_dirs = [d for d in dirs if "games" in d]
                if not game_dirs:
                    return "No game logs found"
                latest_dir = max(game_dirs, key=lambda d: d.split('_')[0])
                if summary_type == "game":
                    # Find latest vs file
                    game_files = [f for f in os.listdir(os.path.join(logs_dir, latest_dir)) 
                                if f.endswith('.txt') and '_vs_' in f]
                    if not game_files:
                        return "No game logs found in directory"
                    latest_file = max(game_files, key=lambda f: os.path.getmtime(
                        os.path.join(logs_dir, latest_dir, f)))
                    filepath = os.path.join(logs_dir, latest_dir, latest_file)
                else:
                    filepath = os.path.join(logs_dir, latest_dir, "games_summary.txt")
                    
            # Read and return the content
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return f.read()
            return f"Log file not found: {filepath}"
            
        except Exception as e:
            return f"Error reading log: {str(e)}"

    def start_games(self):
        """Run games based on mode."""
        player1_bot = self.player1_path.get()
        if not player1_bot:
            tk.messagebox.showerror("Error", "Please select Player bot")
            return

        opponents = self.get_selected_bots()
        if not opponents:
            tk.messagebox.showerror("Error", "Please select at least one opponent")
            return

        try:
            simulation = PrisonersDilemmaSimulation(player1_bot)
            if self.mode == "game":
                simulation.run_games([opponents[0]])
                self.update_log(self.read_latest_log("game"))
            else:
                # For multiple test mode
                simulation.run_games(opponents)
                # Force a small delay to ensure file is written
                self.parent.after(100)  
                self.update_log(self.read_latest_log("games_summary"))
                self.center_frame.update_idletasks()  # Force UI update
                    
        except Exception as e:
            tk.messagebox.showerror("Error", f"Simulation failed: {str(e)}")

    def load_bot(self, bot_path):
        """Load a bot from a file path."""
        try:
            spec = importlib.util.spec_from_file_location("bot_module", bot_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for item in dir(module):
                obj = getattr(module, item)
                if isinstance(obj, type) and issubclass(obj, AbstractBot) and obj != AbstractBot:
                    return obj()
            raise ValueError("No valid bot class found in file")
        except Exception as e:
            raise Exception(f"Failed to load bot: {str(e)}")

    def start_tournament(self, selected_bot_paths, visualize=True):
        """Start tournament with selected bots."""
        tournament = TournamentSimulation()
        try:
            tournament_dir = tournament.run_all_against_all(selected_bot_paths, visualize=visualize)
            
            # Add a small delay to ensure files are written
            self.parent.after(100)
            
            # Read and display tournament summary
            self.log_text.delete(1.0, tk.END)
            summary = self.read_latest_log("tournament")
            if summary:
                self.update_log(summary)
            else:
                self.log_text.insert(tk.END, "Error: Could not read tournament summary")
            
        except Exception as e:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"Error during tournament: {str(e)}\n")