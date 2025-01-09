import tkinter as tk
from tkinter import ttk
from interface.game_ui import GameUI
from interface.menu_screen import MenuScreen
from .shared_style import Style

class MultipleTestScreen:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Test Against Multiple Opponents")
        self.root.configure(bg=Style.COLORS['bg'])
        self.setup_ui()

    def setup_ui(self):
        # Configure ttk style
        style = ttk.Style()
        style.configure('Custom.TFrame', background=Style.COLORS['bg'])
        style.configure('Custom.TLabelframe', background=Style.COLORS['bg'])
        style.configure('Custom.TButton', **Style.button_style())
        style.configure('Custom.TCheckbutton',
                      background=Style.COLORS['bg'],
                      foreground=Style.COLORS['text'])
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main frame with custom style
        self.main_frame = ttk.Frame(self.root, padding="20", style='Custom.TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.main_frame.grid_rowconfigure(0, weight=0)  # Title
        self.main_frame.grid_rowconfigure(1, weight=0)  # Separator
        self.main_frame.grid_rowconfigure(2, weight=0)  # Description
        self.main_frame.grid_rowconfigure(3, weight=1)  # Content
        self.main_frame.grid_rowconfigure(4, weight=0)  # Back button
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title with shared style
        title_label = tk.Label(self.main_frame, 
                              text="Test Against Multiple Opponents",
                              font=Style.FONTS['title'],
                              fg=Style.COLORS['text'],
                              bg=Style.COLORS['bg'])
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=1, column=0, sticky="ew", pady=10)
        
        # Description with shared style
        description = tk.Label(self.main_frame,
                              text="Select your bot and choose one or more opponents to play against.",
                              font=Style.FONTS['text'],
                              fg=Style.COLORS['text'],
                              bg=Style.COLORS['bg'],
                              wraplength=800)
        description.grid(row=2, column=0, pady=(0, 20))
        
        # Create the game UI with three-column layout
        self.game_ui = GameUI(self.main_frame)
        self.game_ui.main_frame.grid(row=3, column=0, sticky="nsew")
        
        # Create bottom button frame (in row 4)
        button_frame = tk.Frame(self.main_frame, bg=Style.COLORS['bg'])
        button_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        button_frame.grid_columnconfigure(0, weight=0)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=0)
        
        # Back button on left with shared style
        back_btn = tk.Button(button_frame, 
                           text="Back to Menu",
                           command=self.back_to_menu,
                           **Style.button_style())
        back_btn.grid(row=0, column=0, padx=5)
        
        # Start button on right with shared style
        start_btn = tk.Button(button_frame,
                            text="Start Games",
                            command=self.start_games,
                            **Style.button_style())
        start_btn.grid(row=0, column=2, padx=5)
        
        # Add hover effects
        for btn in [back_btn, start_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=Style.COLORS['button_hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=Style.COLORS['button']))

    def start_games(self):
        # Clear the log before starting new games
        self.game_ui.log_text.delete(1.0, tk.END)
        self.game_ui.log_text.update_idletasks()
        self.game_ui.start_games()

    def back_to_menu(self):
        from interface.menu_screen import MenuScreen  # Changed from relative to absolute import
        for widget in self.root.winfo_children():
            widget.destroy()
        MenuScreen(self.root)
