"""Investigation dashboard: case navigation (left), active work (centre), case status (right)."""
import tkinter as tk

from . import evidence as ev
from . import storage
from . import theme as T
from .challenge_views import VIEWS
from .widgets import (Badge, Card, NeonButton, ProgressBar, ScrollFrame, StatusDot, Terminal,
                      Timeline, section_title, schedule, wrap_label)

NARROW_WIDTH = 1120   # below this the right-hand status panel is hidden


class Dashboard(tk.Frame):
    def __init__(self, app, evidence_index=None):
        super().__init__(app, bg=T.BG)
        self.app = app
        self.mission = app.mission
        self.view = None                 # ("challenge", i) or ("evidence", i)
        self._toast_job = None
        self._right_visible = True

        self._build_header()
        self._build_progress_strip()
        self._build_footer()
        body = tk.Frame(self, bg=T.BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.left = tk.Frame(body, bg=T.BG2, width=280, highlightthickness=1, highlightbackground=T.BORDER)
        self.left.grid(row=0, column=0, sticky="ns")
        self.left.pack_propagate(False)
        self.left_scroll = ScrollFrame(self.left, bg=T.BG2)
        self.left_scroll.pack(fill="both", expand=True)
        self.centre = ScrollFrame(body)
        self.centre.grid(row=0, column=1, sticky="nsew", padx=14, pady=12)
        self.right = tk.Frame(body, bg=T.BG2, width=270, highlightthickness=1, highlightbackground=T.BORDER)
        self.right.grid(row=0, column=2, sticky="ns")
        self.right.pack_propagate(False)
        self._build_right()
        self.bind("<Configure>", self._on_resize)

        if evidence_index is not None:
            self.show_evidence(evidence_index)
        else:
            self.open_challenge(self.mission.first_open_index())

    # ---------------------------------------------------------------- layout
    def _build_header(self):
        bar = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER)
        bar.pack(fill="x")
        left = tk.Frame(bar, bg=T.BG2)
        left.pack(side="left", padx=14, pady=10)
        tk.Label(left, text="CYBERQUEST // INVESTIGATION CONSOLE", font=T.mono(12, True),
                 fg=T.GREEN, bg=T.BG2).pack(anchor="w")
        StatusDot(left, "SYSTEM ONLINE", T.GREEN_DIM).pack(anchor="w", pady=(3, 0))
        right = tk.Frame(bar, bg=T.BG2)
        right.pack(side="right", padx=14, pady=10)
        NeonButton(right, "SAVE & MENU", self.app.save_and_menu, "secondary", 9, 12, 6).pack(side="right", padx=(14, 0))
        info = tk.Frame(right, bg=T.BG2)
        info.pack(side="right")
        tk.Label(info, text=f"CASE {self.mission.data['case']['id']}", font=T.mono(11, True),
                 fg=T.TEXT, bg=T.BG2).pack(anchor="e")
        self.status_dot = StatusDot(info, "STATUS: INVESTIGATION ACTIVE", T.RED)
        self.status_dot.pack(anchor="e", pady=(3, 0))

    def _build_progress_strip(self):
        strip = tk.Frame(self, bg=T.BG)
        strip.pack(fill="x", padx=14, pady=(8, 0))
        self.progress_label = tk.Label(strip, text="", font=T.mono(9, True), fg=T.MUTED, bg=T.BG)
        self.progress_label.pack(side="left", padx=(0, 12))
        self.progress_bar = ProgressBar(strip, height=8)
        self.progress_bar.pack(side="left", fill="x", expand=True)

    def _build_footer(self):
        footer = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER)
        footer.pack(side="bottom", fill="x")
        self.toast_label = tk.Label(footer, text="", font=T.mono(9), fg=T.AMBER, bg=T.BG2, anchor="w")
        self.toast_label.pack(side="left", padx=14, pady=4)
        tk.Label(footer, text="SIMULATED TRAINING SCENARIO  |  ALL DATA IS FICTIONAL", font=T.mono(8),
                 fg=T.MUTED, bg=T.BG2).pack(side="right", padx=14)

    def _build_right(self):
        parent = self.right
        section_title(parent, "CASE STATUS", T.BG2).pack(fill="x", padx=14, pady=(14, 6))
        self.score_label = tk.Label(parent, text="000", font=T.mono(30, True), fg=T.GREEN, bg=T.BG2, anchor="w")
        self.score_label.pack(fill="x", padx=14)
        self.max_label = tk.Label(parent, text="", font=T.mono(9), fg=T.MUTED, bg=T.BG2, anchor="w")
        self.max_label.pack(fill="x", padx=14, pady=(0, 8))
        self.stat_done = self._stat_row("CHALLENGES COMPLETED")
        self.stat_hints = self._stat_row("HINTS USED")
        row = tk.Frame(parent, bg=T.BG2)
        row.pack(fill="x", padx=14, pady=2)
        tk.Label(row, text="THREAT LEVEL", font=T.mono(8, True), fg=T.MUTED, bg=T.BG2).pack(side="left")
        self.threat_holder = tk.Frame(row, bg=T.BG2)
        self.threat_holder.pack(side="right")
        self.stat_status = self._stat_row("MISSION STATUS")
        section_title(parent, "EVENT FEED  (SIMULATED)", T.BG2).pack(fill="x", padx=14, pady=(14, 4))
        self.terminal = Terminal(parent)
        self.terminal.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _stat_row(self, label):
        row = tk.Frame(self.right, bg=T.BG2)
        row.pack(fill="x", padx=14, pady=2)
        tk.Label(row, text=label, font=T.mono(8, True), fg=T.MUTED, bg=T.BG2).pack(side="left")
        value = tk.Label(row, text="", font=T.mono(9, True), fg=T.TEXT, bg=T.BG2)
        value.pack(side="right")
        return value

    def _on_resize(self, event):
        if event.widget is not self:
            return
        narrow = event.width < NARROW_WIDTH
        if narrow and self._right_visible:
            self.right.grid_remove()
            self._right_visible = False
        elif not narrow and not self._right_visible:
            self.right.grid()
            self._right_visible = True

    # ---------------------------------------------------------------- navigation
    def toast(self, text, colour=T.AMBER):
        self.toast_label.configure(text=text, fg=colour)
        if self._toast_job:
            try:
                self.after_cancel(self._toast_job)
            except tk.TclError:
                pass
        self._toast_job = schedule(self, 4000, lambda: self.toast_label.configure(text=""))

    def open_challenge(self, index):
        if not self.mission.is_unlocked(index):
            self.toast("STAGE LOCKED: complete the previous stage first.")
            return
        self.mission.mark_started(index)
        storage.save_progress(self.mission)
        self.view = ("challenge", index)
        self._show(lambda: VIEWS[index](self.centre.body, self, index))
        self.refresh()

    def show_evidence(self, index):
        item = self.mission.data["evidence"][index]
        if ev.evidence_status(item, self.mission) == ev.LOCKED:
            self.toast("EVIDENCE LOCKED: reach the related stage to unlock it.")
            return
        self.view = ("evidence", index)
        self._show(lambda: self._evidence_panel(item))
        self.refresh()

    def _show(self, build):
        """Remove the old centre content, then build and show the new one."""
        for child in self.centre.body.winfo_children():
            child.destroy()
        build().pack(fill="both", expand=True, padx=2)
        self.centre.scroll_to_top()

    def scroll_to_bottom(self):
        """Used after feedback appears so the player sees it without scrolling."""
        self.update_idletasks()
        self.centre.canvas.yview_moveto(1.0)

    # ---------------------------------------------------------------- actions used by challenge views
    def use_hint(self, index):
        hint = self.mission.use_hint(index)
        storage.save_progress(self.mission)
        self.refresh()
        return hint

    def submit(self, index, answer):
        result = self.mission.submit(index, answer)
        storage.save_progress(self.mission)
        self.refresh()
        if result.correct and not result.already_completed:
            self.toast("FINDING ADDED TO CASE FILE.", T.GREEN)
        return result

    # ---------------------------------------------------------------- refresh side panels
    def refresh(self):
        m = self.mission
        done = len(m.completed)
        self.progress_label.configure(text=f"INVESTIGATION PROGRESS: {done} / {m.total}")
        self.progress_bar.set(done / m.total)
        self.score_label.configure(text=f"{m.score:03d}")
        self.max_label.configure(text=f"/ {m.max_score} MAX POINTS")
        self.stat_done.configure(text=f"{done} / {m.total}")
        self.stat_hints.configure(text=str(len(m.hints_used)))
        for child in self.threat_holder.winfo_children():
            child.destroy()
        if m.is_complete:
            Badge(self.threat_holder, "CONTAINED", T.GREEN, T.BG2).pack()
            self.stat_status.configure(text="CASE CLOSED", fg=T.GREEN)
            self.status_dot.set("STATUS: CASE CLOSED", T.GREEN)
        else:
            Badge(self.threat_holder, m.data["case"]["threat_level"], T.RED, T.BG2).pack()
            self.stat_status.configure(text="ACTIVE", fg=T.RED)
            self.status_dot.set("STATUS: INVESTIGATION ACTIVE", T.RED)
        self.terminal.render(m.feed)
        self._build_left()

    def _build_left(self):
        host = self.left_scroll.body
        for child in host.winfo_children():
            child.destroy()
        m = self.mission
        tk.Label(host, text=f"CASE {m.data['case']['id']}", font=T.mono(11, True), fg=T.GREEN,
                 bg=T.BG2, anchor="w").pack(fill="x", padx=14, pady=(14, 0))
        tk.Label(host, text=m.data["case"]["name"], font=T.mono(8), fg=T.MUTED, bg=T.BG2,
                 anchor="w").pack(fill="x", padx=14, pady=(0, 10))
        if m.is_complete:
            NeonButton(host, "VIEW FINAL REPORT", self.app.show_report, "primary", 9).pack(
                fill="x", padx=14, pady=(0, 10))

        section_title(host, "CHALLENGES", T.BG2).pack(fill="x", padx=14, pady=(0, 4))
        for i, ch in enumerate(m.challenge_list):
            self._nav_row(host, f"{i + 1:02d}  {ch['title'].upper()}", m.status_of(i),
                          selected=self.view == ("challenge", i),
                          command=lambda i=i: self.open_challenge(i))

        section_title(host, "EVIDENCE", T.BG2).pack(fill="x", padx=14, pady=(14, 4))
        for i, item in enumerate(m.data["evidence"]):
            status = ev.evidence_status(item, m)
            label = {ev.LOCKED: "LOCKED", ev.AVAILABLE: "NEW", ev.ANALYSED: "ANALYSED"}[status]
            self._nav_row(host, f"{item['id']}  {item['name']}", label,
                          selected=self.view == ("evidence", i),
                          command=lambda i=i: self.show_evidence(i))
        tk.Frame(host, bg=T.BG2, height=10).pack()

    def _nav_row(self, host, text, status, selected, command):
        locked = status == "LOCKED"
        colour = T.STATUS_COLOURS.get(status, T.MUTED)
        bg = T.CARD_HI if selected else T.BG2
        row = tk.Frame(host, bg=bg, highlightthickness=1,
                       highlightbackground=T.GREEN if selected else T.BG2,
                       cursor="arrow" if locked else "hand2")
        row.pack(fill="x", padx=10, pady=1)
        title = tk.Label(row, text=text, font=T.mono(8, True),
                         fg=T.MUTED if locked else T.TEXT, bg=bg, anchor="w", padx=6)
        mark = "\u2713 " if status in ("COMPLETED", "ANALYSED") else ""
        badge = tk.Label(row, text=mark + status, font=T.mono(7, True), fg=colour, bg=bg, anchor="w", padx=6)
        title.pack(fill="x", pady=(4, 0))
        badge.pack(fill="x", pady=(0, 4))
        for w in (row, title, badge):
            w.bind("<Button-1>", lambda e: command())

    # ---------------------------------------------------------------- evidence viewer
    def _evidence_panel(self, item):
        m = self.mission
        status = ev.evidence_status(item, m)
        details, findings = ev.evidence_text(item, m, m.data)
        panel = tk.Frame(self.centre.body, bg=T.BG)
        top = tk.Frame(panel, bg=T.BG)
        top.pack(fill="x")
        tk.Label(top, text=f"EVIDENCE {item['id']}", font=T.mono(9, True), fg=T.MUTED, bg=T.BG).pack(side="left")
        label = "ANALYSED" if status == ev.ANALYSED else "NEW"
        Badge(top, label, T.STATUS_COLOURS[label], T.BG).pack(side="right")
        tk.Label(panel, text=item["name"], font=T.ui(18, True), fg=T.TEXT, bg=T.BG, anchor="w").pack(fill="x", pady=(2, 4))
        wrap_label(panel, item["description"], T.ui(10), T.MUTED, T.BG).pack(fill="x", pady=(0, 4))
        related = m.challenge_list[item["challenge"] - 1]["title"]
        tk.Label(panel, text=f"RELATED CHALLENGE: {item['challenge']:02d} {related.upper()}",
                 font=T.mono(8, True), fg=T.GREEN_DIM, bg=T.BG, anchor="w").pack(fill="x", pady=(0, 12))
        card = Card(panel)
        card.pack(fill="x", pady=(0, 12))
        section_title(card.body, "RELEVANT DETAILS").pack(fill="x", pady=(0, 6))
        wrap_label(card.body, details, T.mono(10), T.TEXT).pack(fill="x")
        found = Card(panel, border=T.GREEN_DIM if findings else T.BORDER)
        found.pack(fill="x", pady=(0, 12))
        section_title(found.body, "FINDINGS", fg=T.GREEN if findings else T.GREEN_DIM).pack(fill="x", pady=(0, 6))
        if status == ev.ANALYSED and item["challenge"] == 4:
            self._timeline_into(found.body)
        elif findings:
            wrap_label(found.body, findings, T.ui(10), T.TEXT).pack(fill="x")
        else:
            wrap_label(found.body, "Not analysed yet. Complete the related challenge to add findings "
                                   "to the case file.", T.ui(10), T.MUTED).pack(fill="x")
        NeonButton(panel, "BACK TO INVESTIGATION", lambda: self.open_challenge(
            min(m.first_open_index(), m.total - 1)), "secondary").pack(anchor="w")
        return panel

    def _timeline_into(self, parent):
        ch = self.mission.challenge_list[3]
        by_id = {e["id"]: e for e in ch["events"]}
        entries = []
        for event_id in ch["correct_order"]:
            e = by_id[event_id]
            entries.append({"time": e["time"] + (" (est.)" if e["time_note"] else ""),
                            "event": e["event"], "source": e["source"], "note": e["note"]})
        Timeline(parent, entries).pack(fill="x")
