"""Startup, main menu, text pages, mission briefing and final report screens."""
import tkinter as tk

from . import report as report_mod
from . import storage
from . import theme as T
from .widgets import (Card, NeonButton, ProgressBar, ScrollFrame, StatusDot, Terminal, Timeline,
                      schedule, section_title, wrap_label)

TITLE = "CYBERQUEST"
SUBTITLE = "THE MIDNIGHT BREACH"


class Screen(tk.Frame):
    def __init__(self, app):
        super().__init__(app, bg=T.BG)
        self.app = app


# ================================================================ startup
class StartupScreen(Screen):
    LINES = [
        "INITIALISING SECURITY INTERFACE...",
        "LOADING INVESTIGATION MODULE...",
        "CONNECTING TO SIMULATED CASE DATABASE...",
        "CASE NXS-0217 READY",
        "WELCOME, INVESTIGATOR.",
    ]
    STEP_MS = 650

    def __init__(self, app):
        super().__init__(app)
        self.finished = False
        centre = tk.Frame(self, bg=T.BG)
        centre.place(relx=0.5, rely=0.46, anchor="center")
        tk.Label(centre, text=TITLE, font=T.mono(46, True), fg=T.GREEN, bg=T.BG).pack()
        tk.Label(centre, text=SUBTITLE, font=T.mono(14, True), fg=T.TEXT, bg=T.BG).pack(pady=(0, 24))
        self.log = tk.Text(centre, width=52, height=6, bg=T.BG, fg=T.GREEN, font=T.mono(10), relief="flat",
                           highlightthickness=1, highlightbackground=T.BORDER, state="disabled", cursor="arrow")
        self.log.pack()
        self.bar = ProgressBar(centre, height=6, bg=T.BG2)
        self.bar.pack(fill="x", pady=(14, 0))
        self.status = tk.Label(centre, text="STARTING...", font=T.mono(9), fg=T.MUTED, bg=T.BG)
        self.status.pack(pady=(6, 0))
        NeonButton(self, "SKIP  >>", self.finish, "secondary", 9, 12, 6).place(relx=0.97, rely=0.96, anchor="se")
        for key in ("<Return>", "<space>", "<Escape>"):
            app.bind(key, lambda e: self.finish())
        self.focus_set()
        self._step(0)

    def _step(self, i):
        if self.finished:
            return
        self.bar.set((i + 1) / (len(self.LINES) + 1))
        if i < len(self.LINES):
            self.log.configure(state="normal")
            self.log.insert("end", "> " + self.LINES[i] + "\n")
            self.log.configure(state="disabled")
            self.status.configure(text=self.LINES[i])
            schedule(self, self.STEP_MS, lambda: self._step(i + 1))
        else:
            self.finish()

    def finish(self):
        if self.finished:
            return
        self.finished = True
        for key in ("<Return>", "<space>", "<Escape>"):
            self.app.unbind(key)
        self.app.show_menu()


# ================================================================ main menu
class MenuScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.canvas = tk.Canvas(self, bg=T.BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        holder = tk.Frame(self.canvas, bg=T.BG)
        self.window = self.canvas.create_window(0, 0, window=holder, anchor="center")
        self.canvas.bind("<Configure>", self._on_resize)

        StatusDot(holder, "SYSTEM ONLINE", T.GREEN, T.BG).pack(pady=(0, 14))
        tk.Label(holder, text=TITLE, font=T.mono(48, True), fg=T.GREEN, bg=T.BG).pack()
        tk.Label(holder, text=SUBTITLE, font=T.mono(15, True), fg=T.TEXT, bg=T.BG).pack()
        tk.Label(holder, text="Every clue matters. Every decision counts.", font=T.ui(11), fg=T.MUTED,
                 bg=T.BG).pack(pady=(8, 26))
        buttons = [("START INVESTIGATION", app.start_new, "primary"),
                   ("CONTINUE CASE", app.continue_case, "secondary"),
                   ("HOW TO PLAY", app.show_howto, "secondary"),
                   ("ABOUT PROJECT", app.show_about, "secondary"),
                   ("EXIT", app.quit_app, "danger")]
        for text, command, style in buttons:
            NeonButton(holder, text, command, style, 11, 10, 9).pack(fill="x", pady=4, ipadx=40)
        self.save_label = tk.Label(holder, text=self._save_text(), font=T.mono(9), fg=T.MUTED, bg=T.BG)
        self.save_label.pack(pady=(16, 0))

    @staticmethod
    def _save_text():
        saved = storage.load_saved_dict()
        if saved and isinstance(saved.get("completed"), list):
            return f"SAVED CASE FOUND: {len(saved['completed'])} / 5 STAGES COMPLETE"
        return "NO SAVED CASE"

    def _on_resize(self, event):
        self.canvas.coords(self.window, event.width / 2, event.height / 2)
        self.canvas.delete("grid")
        for x in range(0, event.width, 48):
            self.canvas.create_line(x, 0, x, event.height, fill="#0F1311", tags="grid")
        for y in range(0, event.height, 48):
            self.canvas.create_line(0, y, event.width, y, fill="#0F1311", tags="grid")
        self.canvas.tag_lower("grid")


# ================================================================ how to play / about
HOW_TO_PLAY = [
    ("YOUR ROLE", "You are a junior cybersecurity investigator working on Case NXS-0217. Examine the "
                  "evidence, solve each stage and recommend a response."),
    ("NAVIGATION", "Use the left panel to move between stages and evidence. Stages unlock one at a time, "
                   "in order. Completed stages can be reviewed, but they cannot earn points again."),
    ("SUBMITTING ANSWERS", "Choose or type your answer, then press the submit button. You get an "
                           "explanation after a wrong or a correct answer. Partly correct answers do not count."),
    ("SCORING", "Correct on the first try: +100. Correct after a wrong attempt: +60. Completing all five "
                "stages: +100 bonus. Maximum score: 600. The score never drops below zero."),
    ("HINTS", "Every stage has a hint. Using it costs 15 points ONCE per stage. Reading the same hint "
              "again is free. Revealing the cipher answer also counts as a hint."),
    ("EVIDENCE", "Each stage unlocks a piece of evidence. Findings are added to the evidence entry "
                 "when you complete the stage."),
    ("FINAL REPORT", "After the fifth stage the final incident report becomes available. It uses your real "
                     "results and can be exported as a .txt file."),
    ("SIMULATION", "All names, addresses, logs and events are fictional and simulated. Nothing connects to "
                   "real systems."),
]

ABOUT = [
    ("PROJECT", "CyberQuest: The Midnight Breach is a student-developed cybersecurity learning project "
                "(BCA Cybersecurity, Mini Project).\nDeveloped by Angel Karanwal."),
    ("PURPOSE", "To teach beginners how to recognise suspicious activity and make safe decisions through "
                "a story-driven investigation. All scenarios are simulated and intended for education."),
    ("TOPICS DEMONSTRATED", "Phishing awareness  |  Basic cryptography (Caesar cipher)  |  Security log "
                            "analysis  |  Incident timeline reconstruction  |  Basic incident-response "
                            "decisions  |  GUI development with Python"),
    ("TECHNOLOGIES", "Python 3, Tkinter / ttk (standard library only), JSON for mission data and saved "
                     "progress, unittest for the game logic tests."),
]


class TextScreen(Screen):
    def __init__(self, app, title, sections):
        super().__init__(app)
        head = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER)
        head.pack(fill="x")
        tk.Label(head, text=title, font=T.mono(13, True), fg=T.GREEN, bg=T.BG2).pack(side="left", padx=18, pady=12)
        NeonButton(head, "BACK TO MENU", app.show_menu, "secondary", 9, 12, 6).pack(side="right", padx=18)
        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=16)
        for heading, text in sections:
            card = Card(scroll.body)
            card.pack(fill="x", pady=5)
            section_title(card.body, heading).pack(fill="x", pady=(0, 4))
            wrap_label(card.body, text, T.ui(11), T.TEXT).pack(fill="x")


# ================================================================ briefing
class BriefingScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        case = app.data["case"]
        banner = tk.Frame(self, bg=T.RED_TINT, highlightthickness=1, highlightbackground=T.RED)
        banner.pack(fill="x")
        self.alert = tk.Label(banner, text=f"ALERT  //  HIGH THREAT INCIDENT DETECTED  //  {case['alert_time']}",
                              font=T.mono(11, True), fg=T.RED, bg=T.RED_TINT, pady=8)
        self.alert.pack()
        self._blink_state = True
        schedule(self, 800, self._blink)

        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=14)
        body = scroll.body
        tk.Label(body, text=f"MISSION BRIEFING // CASE {case['id']}", font=T.mono(11, True), fg=T.MUTED,
                 bg=T.BG, anchor="w").pack(fill="x")
        tk.Label(body, text=case["name"], font=T.mono(26, True), fg=T.GREEN, bg=T.BG, anchor="w").pack(fill="x", pady=(0, 10))

        card = Card(body)
        card.pack(fill="x", pady=5)
        section_title(card.body, "SCENARIO").pack(fill="x", pady=(0, 4))
        wrap_label(card.body, case["scenario"], T.ui(11), T.TEXT).pack(fill="x")

        columns = tk.Frame(body, bg=T.BG)
        columns.pack(fill="x", pady=5)
        columns.columnconfigure((0, 1), weight=1, uniform="c")
        obj = Card(columns)
        obj.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        section_title(obj.body, "MISSION OBJECTIVES").pack(fill="x", pady=(0, 6))
        for text in case["objectives"]:
            wrap_label(obj.body, "[ ]  " + text, T.mono(10), T.TEXT).pack(fill="x", pady=2)
        details = Card(columns)
        details.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        section_title(details.body, "CASE DETAILS").pack(fill="x", pady=(0, 6))
        rows = [("CASE ID", case["id"], T.TEXT), ("STATUS", "OPEN", T.GREEN),
                ("INITIAL THREAT LEVEL", case["threat_level"], T.RED),
                ("EVIDENCE ITEMS", str(len(app.data["evidence"])), T.TEXT),
                ("CHALLENGES", str(len(app.data["challenges"])), T.TEXT),
                ("ESTIMATED PLAY TIME", "10\u201315 minutes", T.TEXT)]
        for label, value, colour in rows:
            row = tk.Frame(details.body, bg=T.CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=T.mono(8, True), fg=T.MUTED, bg=T.CARD).pack(side="left")
            tk.Label(row, text=value, font=T.mono(10, True), fg=colour, bg=T.CARD).pack(side="right")

        buttons = tk.Frame(body, bg=T.BG)
        buttons.pack(fill="x", pady=(14, 8))
        NeonButton(buttons, "ACCEPT MISSION", app.accept_mission, "primary", 12, 24, 10).pack(side="left")
        NeonButton(buttons, "BACK TO MENU", app.show_menu, "secondary", 10, 16, 10).pack(side="left", padx=10)

    def _blink(self):
        self._blink_state = not self._blink_state
        self.alert.configure(fg=T.RED if self._blink_state else "#7A1F25")
        schedule(self, 800, self._blink)


# ================================================================ final report
class ReportScreen(Screen):
    def __init__(self, app):
        super().__init__(app)
        self.report = report_mod.build_report(app.mission, app.data)
        r = self.report

        head = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER)
        head.pack(fill="x")
        tk.Label(head, text=r["heading"], font=T.mono(13, True), fg=T.GREEN, bg=T.BG2).pack(side="left", padx=18, pady=12)
        StatusDot(head, "CASE CLOSED", T.GREEN).pack(side="right", padx=18)

        bottom = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER)
        bottom.pack(side="bottom", fill="x")
        for text, command, style in (("EXPORT REPORT", self.export, "primary"),
                                     ("REVIEW EVIDENCE", lambda: app.show_dashboard(evidence_index=0), "secondary"),
                                     ("PLAY AGAIN", app.play_again, "secondary"),
                                     ("RETURN TO MAIN MENU", app.show_menu, "secondary")):
            NeonButton(bottom, text, command, style, 9, 14, 8).pack(side="left", padx=(14, 0), pady=10)
        self.export_label = tk.Label(bottom, text="", font=T.mono(8), fg=T.GREEN, bg=T.BG2, anchor="w")
        self.export_label.pack(side="left", padx=14, fill="x", expand=True)

        scroll = ScrollFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=14)
        body = scroll.body
        tk.Label(body, text=f"CASE {r['case_id']}  //  {r['case_name']}", font=T.mono(16, True), fg=T.TEXT,
                 bg=T.BG, anchor="w").pack(fill="x")
        tk.Label(body, text=f"FINAL STATUS: {r['status']}    GENERATED: {r['generated']}", font=T.mono(9),
                 fg=T.MUTED, bg=T.BG, anchor="w").pack(fill="x", pady=(2, 10))

        stats = tk.Frame(body, bg=T.BG)
        stats.pack(fill="x", pady=4)
        values = [("TOTAL SCORE", f"{r['score']} / {r['max_score']}"),
                  ("CHALLENGES", f"{r['completed']} / {r['total']}"),
                  ("HINTS USED", str(r["hints_used"])),
                  ("WRONG ATTEMPTS", str(r["wrong_attempts"]))]
        for c, (label, value) in enumerate(values):
            stats.columnconfigure(c, weight=1, uniform="s")
            card = Card(stats, pad=10)
            card.grid(row=0, column=c, sticky="nsew", padx=3)
            tk.Label(card.body, text=label, font=T.mono(8, True), fg=T.MUTED, bg=T.CARD).pack()
            tk.Label(card.body, text=value, font=T.mono(15, True), fg=T.GREEN, bg=T.CARD).pack()
        rating = Card(body, border=T.GREEN_DIM)
        rating.pack(fill="x", pady=6)
        tk.Label(rating.body, text="OVERALL PERFORMANCE:  " + r["rating"], font=T.mono(12, True),
                 fg=T.GREEN, bg=T.CARD).pack()

        self._list_card(body, "OBSERVED EVIDENCE (FACTS FROM THE LOGS AND MESSAGES)", r["observed"])
        card = Card(body)
        card.pack(fill="x", pady=5)
        section_title(card.body, "POSSIBLE EXPLANATION  (INFERENCE, NOT CONFIRMED)", fg=T.AMBER).pack(fill="x", pady=(0, 4))
        wrap_label(card.body, r["possible_explanation"], T.ui(10), T.TEXT).pack(fill="x")

        card = Card(body)
        card.pack(fill="x", pady=5)
        section_title(card.body, "INCIDENT TIMELINE").pack(fill="x", pady=(0, 8))
        Timeline(card.body, r["timeline"]).pack(fill="x")

        self._list_card(body, "IDENTIFIED WARNING SIGNS", r["warning_signs"])
        self._list_card(body, "RECOMMENDED RESPONSE ACTIONS", r["response_actions"])
        card = Card(body)
        card.pack(fill="x", pady=5)
        section_title(card.body, "EDUCATIONAL CONCLUSION").pack(fill="x", pady=(0, 4))
        wrap_label(card.body, r["conclusion"], T.ui(10), T.TEXT).pack(fill="x")

    @staticmethod
    def _list_card(parent, title, items):
        card = Card(parent)
        card.pack(fill="x", pady=5)
        section_title(card.body, title).pack(fill="x", pady=(0, 4))
        for item in items:
            wrap_label(card.body, "-  " + item, T.ui(10), T.TEXT).pack(fill="x", pady=1)

    def export(self):
        try:
            path = report_mod.export_report(self.report)
        except OSError as err:
            from .widgets import show_info
            show_info(self.app, "Export failed", f"The report could not be saved.\n\n{err}")
            return
        self.export_label.configure(text=f"EXPORTED: {path}")
