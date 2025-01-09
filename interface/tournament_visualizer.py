import tkinter as tk
from tkinter import font
import pandas as pd
from .shared_style import Style

class TournamentVisualizer:
    def __init__(self, csv_path):
        self.PLACE_WIDTH = 150
        self.BOT_WIDTH = 500
        self.SCORE_WIDTH = 150
        
        self.df = pd.read_csv(csv_path)
        self.df = self.df.sort_values('Average', ascending=False)
        self.current_index = 0
        
        self.root = tk.Toplevel()  # Changed from Tk() to Toplevel()
        self.root.title("Tournament Results")
        self.root.state('zoomed')
        self.root.configure(bg=Style.COLORS['bg'])  # Add background to root
        
        # Create persistent header frame (outside scrollable area)
        header_frame = tk.Frame(self.root, bg=Style.COLORS['bg'])
        header_frame.pack(fill='x', padx=20, pady=(20,0))
        
        # Configure header columns with fixed widths
        place_header = tk.Frame(header_frame, width=self.PLACE_WIDTH, bg=Style.COLORS['bg'])
        bot_header = tk.Frame(header_frame, width=self.BOT_WIDTH, bg=Style.COLORS['bg'])
        score_header = tk.Frame(header_frame, width=self.SCORE_WIDTH, bg=Style.COLORS['bg'])
        
        place_header.pack(side='left', padx=(0,20))
        bot_header.pack(side='left', padx=20, expand=True, fill='x')
        score_header.pack(side='right', padx=20)
        
        # Add header labels
        tk.Label(place_header, text="Place", font=Style.FONTS['heading'], 
                bg=Style.COLORS['bg'], fg=Style.COLORS['text']).pack(anchor='w')
        tk.Label(bot_header, text="Bot", font=Style.FONTS['heading'], 
                bg=Style.COLORS['bg'], fg=Style.COLORS['text']).pack(anchor='center', padx=(100, 0))  # Changed anchor and added left padding
        tk.Label(score_header, text="Score", font=Style.FONTS['heading'],
                bg=Style.COLORS['bg'], fg=Style.COLORS['text']).pack(anchor='e')
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(self.root, bg=Style.COLORS['bg'], 
                              highlightthickness=0)  # Remove canvas border
        scrollbar = tk.Scrollbar(self.root, orient="vertical", 
                               command=self.canvas.yview,
                               bg=Style.COLORS['bg'],  # Add background to scrollbar
                               troughcolor=Style.COLORS['bg'])  # Color the scrollbar trough
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0,20))
        
        # Create main container inside canvas
        self.container = tk.Frame(self.canvas, bg=Style.COLORS['bg'])
        self.canvas.create_window((0, 0), window=self.container, anchor="nw")
        
        # Configure grid columns in container
        self.container.grid_columnconfigure(0, weight=1)  # Place number
        self.container.grid_columnconfigure(1, weight=3)  # Bot column gets more space
        self.container.grid_columnconfigure(2, weight=1)  # Score column gets less space
        
        # Create row frames using grid
        self.rows = []
        for index in range(len(self.df)):
            row = self.df.iloc[index]
            frame = tk.Frame(self.container, height=150, bg=Style.COLORS['bg'])
            frame.grid(row=index+1, column=0, columnspan=3, sticky='ew', pady=5)
            frame.grid_columnconfigure(0, weight=1)  # Place number
            frame.grid_columnconfigure(1, weight=3)  # Bot name
            frame.grid_columnconfigure(2, weight=1)  # Score
            frame.grid_propagate(False)
            
            # Create place label with medals for top 3
            if index == 0: place_text = "🥇"
            elif index == 1: place_text = "🥈"
            elif index == 2: place_text = "🥉"
            else: place_text = f"#{index + 1}"
                
            place_label = tk.Label(frame, text=place_text,
                                 font=Style.FONTS['heading'], 
                                 bg=Style.COLORS['bg'], 
                                 fg=Style.COLORS['bg'])
            place_label.grid(row=0, column=0, sticky='w', padx=20)
            
            bot_label = tk.Label(frame, text=row['Bot'], 
                               font=Style.FONTS['heading'], 
                               bg=Style.COLORS['bg'], 
                               fg=Style.COLORS['bg'])
            bot_label.grid(row=0, column=1, sticky='w', padx=20)
            
            score_label = tk.Label(frame, text=f"{row['Average']:.2f}", 
                                 font=Style.FONTS['heading'],
                                 bg=Style.COLORS['bg'], 
                                 fg=Style.COLORS['bg'])
            score_label.grid(row=0, column=2, sticky='e', padx=20)
            
            self.rows.append((frame, place_label, bot_label, score_label))
        
        # Configure scrolling
        self.container.bind('<Configure>', self._configure_canvas)
        self.canvas.bind('<Configure>', self._configure_container)
        
        self.root.bind('<space>', self.reveal_next)

    def _configure_canvas(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _configure_container(self, event):
        """Update the container frame's width to fill the canvas"""
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def reveal_next(self, event):
        if self.current_index < len(self.df):
            frame, place_label, bot_label, score_label = self.rows[-(self.current_index + 1)]
            
            # Configure colors based on position with themed colors
            position = len(self.df) - self.current_index - 1
            if position == 0:  # First place
                bg_color = '#FFD700'  # Gold
                font_size = 40  # All top 3 use same larger font size
            elif position == 1:  # Second place
                bg_color = '#C0C0C0'  # Silver
                font_size = 40  # Same as first place
            elif position == 2:  # Third place
                bg_color = '#B8860B'  # DarkGoldenRod
                font_size = 40  # Same as first place
            else:
                bg_color = Style.COLORS['button']
                font_size = 32
            
            frame.configure(bg=bg_color)
            place_label.configure(bg=bg_color, fg=Style.COLORS['text'], 
                                font=('Arial', font_size, 'bold'))
            bot_label.configure(bg=bg_color, fg=Style.COLORS['text'], 
                              font=('Arial', font_size, 'bold'))
            score_label.configure(bg=bg_color, fg=Style.COLORS['text'], 
                                font=('Arial', font_size, 'bold'))
            
            # Scroll revealed row to top
            self.root.update_idletasks()
            row_y = frame.winfo_y()
            self.canvas.yview_moveto(row_y / self.canvas.bbox("all")[3])
            
            self.current_index += 1

    def show(self):
        # Just show window, no animation
        self.root.focus_force()
        self.root.grab_set()
        
        # Scroll to bottom after brief delay to ensure window is fully loaded
        self.root.after(100, lambda: self.canvas.yview_moveto(1.0))
        
        self.root.mainloop()
