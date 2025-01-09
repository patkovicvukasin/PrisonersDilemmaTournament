import tkinter as tk
from tkinter import ttk
import os
from interface.game_ui import GameUI
from interface.menu_screen import MenuScreen
from simulation.simulate_tournament import TournamentSimulation
from .shared_style import Style

class TournamentScreen:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Tournament Mode")
        self.root.configure(bg=Style.COLORS['bg'])
        self.setup_ui()

    def setup_ui(self):
        # Configure ttk style
        style = ttk.Style()
        style.configure('Custom.TFrame', background=Style.COLORS['bg'])
        style.configure('Custom.TLabelframe', background=Style.COLORS['bg'], foreground=Style.COLORS['text'])
        style.configure('Custom.TLabelframe.Label', background=Style.COLORS['bg'], foreground=Style.COLORS['text'])
        style.configure('Custom.TButton', **Style.button_style())
        style.configure('Custom.TCheckbutton', background=Style.COLORS['bg'], foreground=Style.COLORS['text'])
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20", style='Custom.TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.main_frame.grid_rowconfigure(0, weight=0)  # Title
        self.main_frame.grid_rowconfigure(1, weight=0)  # Separator
        self.main_frame.grid_rowconfigure(2, weight=0)  # Description
        self.main_frame.grid_rowconfigure(3, weight=1)  # Content
        self.main_frame.grid_rowconfigure(4, weight=0)  # Back button
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title (moved up)
        title_label = tk.Label(self.main_frame,
                              text="Tournament Mode",
                              font=Style.FONTS['title'],
                              fg=Style.COLORS['text'],
                              bg=Style.COLORS['bg'])
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Separator
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.grid(row=1, column=0, sticky="ew", pady=10)
        
        # Description with correct background color
        description = ttk.Label(self.main_frame,
                              text="Select multiple bots to participate in a round-robin tournament. Each bot will play against every other bot.",
                              font=Style.FONTS['text'],
                              foreground=Style.COLORS['text'],
                              background=Style.COLORS['bg'],  # Match the background
                              wraplength=800)
        description.grid(row=2, column=0, pady=(0, 20))
        
        # Update the style for LabelFrames
        style.configure('Custom.TLabelframe', 
                      background=Style.COLORS['bg'],
                      foreground=Style.COLORS['text'])
        style.configure('Custom.TLabelframe.Label', 
                      background=Style.COLORS['bg'],
                      foreground=Style.COLORS['text'])
        
        # Create the game UI with custom style
        self.game_ui = GameUI(self.main_frame)
        self.game_ui.main_frame.grid(row=3, column=0, sticky="nsew")
        self.game_ui.bot_listbox.configure(selectmode=tk.MULTIPLE)
        
        # Update only the frames that exist in tournament mode
        for frame in [self.game_ui.center_frame, self.game_ui.right_frame]:
            frame.configure(style='Custom.TLabelframe')
        
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
        
        # Tournament button on right with shared style
        start_btn = tk.Button(button_frame,
                            text="Start Tournament",
                            command=self.start_tournament,
                            **Style.button_style())
        start_btn.grid(row=0, column=2, padx=5)
        
        # Add hover effects
        for btn in [back_btn, start_btn]:
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=Style.COLORS['button_hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=Style.COLORS['button']))
        
    def start_tournament(self):
        selected_indices = self.game_ui.bot_listbox.curselection()
        if len(selected_indices) < 2:
            self.game_ui.log_text.delete(1.0, tk.END)
            self.game_ui.log_text.insert(tk.END, "Please select at least 2 bots for the tournament.\n")
            return
        
        selected_bot_paths = self.game_ui.get_selected_bots()
        self.game_ui.log_text.delete(1.0, tk.END)
        self.game_ui.log_text.update_idletasks()
        
        # Start tournament and display summary in widget
        tournament = TournamentSimulation()
        try:
            # Run tournament with visualization disabled
            tournament_dir = tournament.run_all_against_all(selected_bot_paths, visualize=False)
            
            # Add delay to ensure files are written
            self.root.after(100)
            
            # Read and display tournament summary
            with open(os.path.join(tournament_dir, "tournament_summary.txt"), 'r') as f:
                summary = f.read()
                self.game_ui.update_log(summary)
                
        except Exception as e:
            self.game_ui.log_text.delete(1.0, tk.END)
            self.game_ui.log_text.insert(tk.END, f"Error during tournament: {str(e)}\n")

    def back_to_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MenuScreen(self.root)
