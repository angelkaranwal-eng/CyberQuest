"""CyberQuest: The Midnight Breach - entry point. Run with:  python main.py"""
import sys
import tkinter as tk
from tkinter import messagebox


def main():
    try:
        from game.app import App
        app = App()
    except RuntimeError as err:          # e.g. missing or broken mission_data.json
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("CyberQuest", str(err))
        sys.exit(1)
    app.mainloop()


if __name__ == "__main__":
    main()
