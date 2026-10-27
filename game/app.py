"""Main application controller: owns the mission state and switches between screens."""
import tkinter as tk

from . import storage, theme
from .challenges import load_data
from .dashboard import Dashboard
from .mission import Mission
from .screens import (ABOUT, HOW_TO_PLAY, BriefingScreen, MenuScreen, ReportScreen, StartupScreen,
                      TextScreen)
from .widgets import ask_confirm, show_info, style_ttk

WIDTH, HEIGHT = 1200, 760
MIN_WIDTH, MIN_HEIGHT = 1000, 680


class App(tk.Tk):
    def __init__(self, skip_intro=False):
        super().__init__()
        self.title("CyberQuest: The Midnight Breach")
        self.configure(bg=theme.BG)
        theme.init_fonts(self)
        style_ttk(self)
        self.data = load_data()
        self.mission = Mission(self.data)
        self.current = None
        self._place_window()
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        if skip_intro:
            self.show_menu()
        else:
            self.show_startup()

    def _place_window(self):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(WIDTH, sw - 60), min(HEIGHT, sh - 100)
        self.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 3)}")
        self.minsize(min(MIN_WIDTH, w), min(MIN_HEIGHT, h))

    # ---- screen switching ----------------------------------------------
    def _switch(self, screen):
        if self.current is not None:
            self.current.destroy()
        self.current = screen
        screen.pack(fill="both", expand=True)

    def show_startup(self):
        self._switch(StartupScreen(self))

    def show_menu(self):
        self._switch(MenuScreen(self))

    def show_howto(self):
        self._switch(TextScreen(self, "HOW TO PLAY", HOW_TO_PLAY))

    def show_about(self):
        self._switch(TextScreen(self, "ABOUT PROJECT", ABOUT))

    def show_briefing(self):
        self._switch(BriefingScreen(self))

    def show_dashboard(self, evidence_index=None):
        self._switch(Dashboard(self, evidence_index))

    def show_report(self):
        if not self.mission.is_complete:
            self.show_dashboard()
            return
        self._switch(ReportScreen(self))

    # ---- menu actions ---------------------------------------------------
    def start_new(self):
        if storage.has_save() and not self._confirm_overwrite():
            return
        self.mission.reset()
        storage.clear_save()
        self.show_briefing()

    def _confirm_overwrite(self):
        return ask_confirm(self, "New investigation",
                           "A saved case exists. Starting a new investigation will erase that progress.",
                           "START NEW", "CANCEL", danger=True)

    def accept_mission(self):
        storage.save_progress(self.mission)
        self.show_dashboard()

    def continue_case(self):
        saved = storage.load_saved_dict()
        if saved is None:
            show_info(self, "No saved case", "There is no saved investigation yet.\n\n"
                                             "Choose START INVESTIGATION to begin a new case.")
            return
        if not self.mission.load_dict(saved):
            storage.clear_save()
            show_info(self, "Save file unreadable", "The saved case could not be read, so it was "
                                                    "discarded. Please start a new investigation.")
            self.show_menu()
            return
        if self.mission.is_complete:
            self.show_report()
        else:
            self.show_dashboard()

    def play_again(self):
        if not ask_confirm(self, "Play again", "Start a fresh investigation? The current results stay "
                                               "in any exported report.", "PLAY AGAIN", "CANCEL"):
            return
        self.mission.reset()
        storage.clear_save()
        self.show_briefing()

    def save_and_menu(self):
        storage.save_progress(self.mission)
        self.show_menu()

    def quit_app(self):
        if ask_confirm(self, "Exit", "Close CyberQuest? Your progress is saved automatically.",
                       "EXIT", "STAY", danger=True):
            if self.mission.completed or self.mission.started:
                storage.save_progress(self.mission)
            self.destroy()
