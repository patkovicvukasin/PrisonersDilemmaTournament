import tkinter as tk
from tkinter import ttk
from interface.game_ui import GameUI  # Changed from relative to absolute import
from interface.menu_screen import MenuScreen  # Changed from relative to absolute import
from .shared_style import Style

class GameScreen:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Single Game Mode")
        self.root.configure(bg=Style.COLORS['bg'])
        self.setup_ui()

    def setup_ui(self):
        # Configure dark theme
        self.root.configure(bg=Style.COLORS['bg'])
        
        # Ensure window maximizes properly
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        style.theme_use('default')
        
        # Main container frame - invisible border
        style.configure('Container.TFrame', 
                       background=Style.COLORS['bg'],
                       borderwidth=0)  # No border
        
        # Content frames - white border
        style.configure('Custom.TLabelframe', 
                       background=Style.COLORS['bg'],
                       foreground=Style.COLORS['text'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=Style.COLORS['text'])  # White border
        style.configure('TButton', padding=10, width=30)
        
        # Create main frame without border
        self.main_frame = ttk.Frame(self.root, padding="20", style='Container.TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main frame grid weights
        self.main_frame.grid_rowconfigure(0, weight=0)  # Title
        self.main_frame.grid_rowconfigure(1, weight=0)  # Separator
        self.main_frame.grid_rowconfigure(2, weight=0)  # Description
        self.main_frame.grid_rowconfigure(3, weight=1)  # Content
        self.main_frame.grid_rowconfigure(4, weight=0)  # Back button
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title (moved up one row)
        title_label = tk.Label(self.main_frame, 
                              text="Single Game Mode",
                              font=Style.FONTS['title'],
                              fg=Style.COLORS['text'],
                              bg=Style.COLORS['bg'])
        title_label.grid(row=0, column=0, pady=(0, 5))  # Reduced bottom padding
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=1, column=0, sticky="ew", pady=5)  # Reduced padding
        
        # Description with correct background
        description = ttk.Label(self.main_frame,
                              text="Test your bot against a single opponent. Select your bot and choose who to play against.",
                              font=Style.FONTS['text'],
                              foreground=Style.COLORS['text'],
                              background=Style.COLORS['bg'],  # Match the background
                              wraplength=800)
        description.grid(row=2, column=0, pady=(5, 10))
        
        # Configure LabelFrame style
        style.configure('Custom.TLabelframe', 
                      background=Style.COLORS['bg'],
                      foreground=Style.COLORS['text'])
        style.configure('Custom.TLabelframe.Label', 
                      background=Style.COLORS['bg'],
                      foreground=Style.COLORS['text'])
        
        # Create the game UI (moved up one row)
        self.game_ui = GameUI(self.main_frame)  # Store as instance variable
        self.game_ui.main_frame.grid(row=3, column=0, sticky="nsew")
        self.game_ui.bot_listbox.configure(selectmode=tk.SINGLE)
        # Removed game_ui button configuration
        
        # Create bottom button frame (in row 4)
        button_frame = tk.Frame(self.main_frame, bg=Style.COLORS['bg'])
        button_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_columnconfigure(0, weight=0)  # Back button
        button_frame.grid_columnconfigure(1, weight=1)  # Space
        button_frame.grid_columnconfigure(2, weight=0)  # Start button
        
        # Back button on left with shared style
        back_btn = tk.Button(button_frame, 
                           text="Back to Menu",
                           command=self.back_to_menu,
                           **Style.button_style())
        back_btn.grid(row=0, column=0, padx=5)
        
        # Start button on right with shared style
        start_btn = tk.Button(button_frame,
                            text="Start Game",
                            command=self.start_game,
                            **Style.button_style())
        start_btn.grid(row=0, column=2, padx=5)
        
        # Add hover effects
        for btn in [back_btn, start_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=Style.COLORS['button_hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=Style.COLORS['button']))

    def start_game(self):
        # Clear the log before starting new game
        self.game_ui.log_text.delete(1.0, tk.END)
        self.game_ui.log_text.update_idletasks()
        self.game_ui.start_games()  # Now using the stored instance

    def back_to_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MenuScreen(self.root)
