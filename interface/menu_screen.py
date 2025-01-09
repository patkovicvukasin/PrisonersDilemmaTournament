import tkinter as tk
from tkinter import ttk

class MenuScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Prisoner's Dilemma")
        
        # Configure theme colors
        self.colors = {
            'bg': '#1E2337',           # Dark blue background
            'button': '#2A3F54',       # Button color
            'button_hover': '#3C5876', # Button hover color
            'text': '#E0E7FF'          # Light text color
        }
        
        # Configure window
        self.root.configure(bg=self.colors['bg'])
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        # Create main frame
        main_frame = tk.Frame(root, bg=self.colors['bg'], padx=40, pady=40)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title with custom font and styling
        title = tk.Label(main_frame,
                        text="Prisoner's Dilemma",
                        font=('Segoe UI', 42, 'bold'),
                        fg=self.colors['text'],
                        bg=self.colors['bg'])
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = tk.Label(main_frame,
                          text="Simulator",
                          font=('Segoe UI Light', 24),
                          fg=self.colors['text'],
                          bg=self.colors['bg'])
        subtitle.pack(pady=(0, 40))
        
        # Button style configuration
        button_style = {
            'font': ('Segoe UI', 12),
            'bg': self.colors['button'],
            'fg': self.colors['text'],
            'activebackground': self.colors['button_hover'],
            'activeforeground': self.colors['text'],
            'width': 30,
            'height': 2,
            'bd': 0,
            'cursor': 'hand2'
        }
        
        # Create buttons with hover effect
        buttons = [
            ("Start Game", self.start_game),
            ("Start Tournament", self.start_tournament),
            ("Test Against Multiple Opponents", self.test_multiple),
            ("Exit", root.quit)
        ]
        
        for text, command in buttons:
            btn = tk.Button(main_frame, text=text, command=command, **button_style)
            btn.pack(pady=8)
            # Add hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg=self.colors['button_hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.colors['button']))

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self):
        self.clear_window()
        from .game_screen import GameScreen  # Import here instead
        GameScreen(self.root)

    def start_tournament(self):
        self.clear_window()
        from .tournament_screen import TournamentScreen  # Import here instead
        TournamentScreen(self.root)

    def test_multiple(self):
        self.clear_window()
        from .multiple_test_screen import MultipleTestScreen  # Import here instead
        MultipleTestScreen(self.root)
