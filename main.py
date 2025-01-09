import tkinter as tk
from interface.menu_screen import MenuScreen

if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')
    menu = MenuScreen(root)
    root.mainloop()
    