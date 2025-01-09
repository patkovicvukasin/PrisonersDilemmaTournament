class Style:
    COLORS = {
        'bg': '#1E2337',           # Dark blue background
        'button': '#2A3F54',       # Button color
        'button_hover': '#3C5876', # Button hover color
        'text': '#E0E7FF',         # Light text color - also used for borders
        'accent': '#4A90E2',       # Accent color
    }
    
    FONTS = {
        'title': ('Segoe UI', 42, 'bold'),
        'subtitle': ('Segoe UI Light', 24),
        'heading': ('Segoe UI', 28, 'bold'),
        'button': ('Segoe UI', 12),
        'text': ('Segoe UI', 11)
    }
    
    @classmethod
    def button_style(cls):
        return {
            'font': cls.FONTS['button'],
            'bg': cls.COLORS['button'],
            'fg': cls.COLORS['text'],
            'activebackground': cls.COLORS['button_hover'],
            'activeforeground': cls.COLORS['text'],
            'bd': 0,
            'cursor': 'hand2',
            'padx': 20,
            'pady': 10
        }
