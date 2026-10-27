"""One view class per challenge. The base class handles hints, submit, feedback and review mode."""
import random
import string
import tkinter as tk

from . import scoring
from . import theme as T
from .challenges import caesar_shift
from .widgets import (Badge, Card, ChoiceList, DataTable, FeedbackPanel, NeonButton, Timeline,
                      section_title, wrap_label)


class ChallengeView(tk.Frame):
    submit_label = "SUBMIT FINDING"

    def __init__(self, parent, dash, index):
        super().__init__(parent, bg=T.BG)
        self.dash, self.index = dash, index
        self.mission = dash.mission
        self.ch = self.mission.challenge_list[index]
        self.done = index in self.mission.completed

        self._build_header()
        evidence = Card(self)
        evidence.pack(fill="x", pady=(0, 12))
        section_title(evidence.body, f"EVIDENCE  E-0{index + 1}").pack(fill="x", pady=(0, 8))
        self.build_evidence(evidence.body)

        task = Card(self)
        task.pack(fill="x", pady=(0, 12))
        section_title(task.body, "TASK").pack(fill="x", pady=(0, 4))
        wrap_label(task.body, self.ch["task"], T.ui(11, True), T.TEXT).pack(fill="x", pady=(0, 8))
        self.build_task(task.body)

        self.extra = tk.Frame(self, bg=T.BG)        # used for the timeline reveal
        self.extra.pack(fill="x")
        self.actions = tk.Frame(self, bg=T.BG)
        self.actions.pack(fill="x")
        self.submit_btn = NeonButton(self.actions, self.submit_label, self.on_submit)
        self.submit_btn.pack(side="left")
        self.hint_btn = NeonButton(self.actions, self._hint_text(), self.on_hint, "secondary")
        self.hint_btn.pack(side="left", padx=(8, 0))
        self.feedback = FeedbackPanel(self)
        self.feedback.pack(fill="x", pady=(0, 12))

        if self.done:
            self._enter_review_mode()
        else:
            self.after_wrong()   # restores the reveal button after resuming a saved case

    # ---- hooks for subclasses ------------------------------------------
    def build_evidence(self, parent):
        raise NotImplementedError

    def build_task(self, parent):
        raise NotImplementedError

    def collect_answer(self):
        raise NotImplementedError

    def lock(self):
        pass

    def show_solved(self):
        pass

    def after_wrong(self):
        pass

    # ---- shared behaviour ---------------------------------------------
    def _build_header(self):
        top = tk.Frame(self, bg=T.BG)
        top.pack(fill="x")
        tk.Label(top, text=f"STAGE {self.index + 1:02d} / {self.mission.total:02d}", font=T.mono(9, True),
                 fg=T.MUTED, bg=T.BG).pack(side="left")
        status = self.mission.status_of(self.index)
        self.status_badge = Badge(top, status, T.STATUS_COLOURS[status], T.BG)
        self.status_badge.pack(side="right")
        tk.Label(self, text=self.ch["title"], font=T.ui(18, True), fg=T.TEXT, bg=T.BG,
                 anchor="w").pack(fill="x", pady=(2, 4))
        wrap_label(self, self.ch["scenario"], T.ui(10), T.MUTED, T.BG).pack(fill="x", pady=(0, 12))

    def _hint_text(self):
        if self.index in self.mission.hints_used:
            return "SHOW HINT"
        return f"HINT  (-{scoring.HINT_PENALTY} PTS)"

    def shuffled_order(self, count):
        """Fixed shuffle (same every time) so the correct options are not always first."""
        order = list(range(count))
        random.Random(100 + self.index).shuffle(order)
        return order

    def on_hint(self):
        first_time = self.index not in self.mission.hints_used
        hint = self.dash.use_hint(self.index)
        if first_time and not self.done:
            title = f"HINT  //  -{scoring.HINT_PENALTY} POINTS (ONCE PER CHALLENGE)"
        else:
            title = "HINT  //  ALREADY COUNTED, NO EXTRA PENALTY"
        self.feedback.show("warning", title, hint)
        self.hint_btn.configure(text=self._hint_text())
        self.dash.scroll_to_bottom()

    def on_submit(self):
        if self.done:
            return
        result = self.dash.submit(self.index, self.collect_answer())
        if result.correct and not result.already_completed:
            self._on_solved(result)
        elif not result.correct:
            self.feedback.show("warning", "INVESTIGATION NOTE", result.note)
            self.after_wrong()
            self.dash.scroll_to_bottom()

    def _on_solved(self, result):
        self.done = True
        self.show_solved()
        self.lock()
        base = result.points - (scoring.COMPLETION_BONUS if result.mission_completed else 0)
        message = f"Your finding has been added to the case file.\n+{base} POINTS"
        if result.mission_completed:
            message += f"\n+{scoring.COMPLETION_BONUS} MISSION COMPLETION BONUS"
        message += "\n\n" + self.ch["explanation"]
        self.feedback.show("success", "EVIDENCE VERIFIED", message)
        self._finish_buttons()
        self.status_badge.configure(text="COMPLETED", fg=T.GREEN, highlightbackground=T.GREEN)
        self.dash.scroll_to_bottom()

    def _enter_review_mode(self):
        self.show_solved()
        self.lock()
        self.feedback.show("success", "EVIDENCE VERIFIED  //  REVIEW MODE",
                           "This stage is complete. No further points can be earned here.\n\n"
                           + self.ch["explanation"])
        self._finish_buttons()

    def _finish_buttons(self):
        self.submit_btn.set_enabled(False)
        self.hint_btn.set_enabled(False)
        if self.mission.is_complete:
            NeonButton(self.actions, "VIEW FINAL REPORT", self.dash.app.show_report).pack(side="right")
        elif self.index + 1 < self.mission.total:
            NeonButton(self.actions, "NEXT STAGE  >", lambda: self.dash.open_challenge(self.index + 1)).pack(side="right")


# ---------------------------------------------------------------- 1: phishing email
class PhishingView(ChallengeView):
    def build_evidence(self, parent):
        mail = self.ch["email"]
        box = tk.Frame(parent, bg=T.BG, highlightthickness=1, highlightbackground=T.BORDER)
        box.pack(fill="x")
        inner = tk.Frame(box, bg=T.BG)
        inner.pack(fill="x", padx=12, pady=10)
        for label, value in (("FROM", mail["from"]), ("TO", mail["to"]), ("SUBJECT", mail["subject"])):
            row = tk.Frame(inner, bg=T.BG)
            row.pack(fill="x")
            tk.Label(row, text=f"{label}:", font=T.mono(9, True), fg=T.MUTED, bg=T.BG, width=9,
                     anchor="w").pack(side="left")
            wrap_label(row, value, T.mono(10), T.TEXT, T.BG).pack(side="left", fill="x", expand=True)
        tk.Frame(inner, bg=T.BORDER, height=1).pack(fill="x", pady=8)
        wrap_label(inner, mail["body"], T.ui(10), T.TEXT, T.BG).pack(fill="x")
        tk.Label(inner, text="LINK IN MESSAGE (display only, not clickable):", font=T.mono(8, True),
                 fg=T.MUTED, bg=T.BG, anchor="w").pack(fill="x", pady=(10, 0))
        tk.Label(inner, text=mail["link"], font=T.mono(10), fg=T.AMBER, bg=T.BG, anchor="w").pack(fill="x")
        tk.Label(parent, text=f"Reference: NEXUS SYSTEMS normal email domain is {mail['normal_domain']}",
                 font=T.mono(9), fg=T.MUTED, bg=T.CARD, anchor="w").pack(fill="x", pady=(8, 0))

    def build_task(self, parent):
        texts = [o["text"] for o in self.ch["options"]]
        self.choices = ChoiceList(parent, texts, multi=True, order=self.shuffled_order(len(texts)))
        self.choices.pack(fill="x")

    def collect_answer(self):
        return self.choices.get()

    def show_solved(self):
        self.choices.set_selection(i for i, o in enumerate(self.ch["options"]) if o["correct"])

    def lock(self):
        self.choices.lock()


# ---------------------------------------------------------------- 2: caesar cipher
class CaesarView(ChallengeView):
    submit_label = "DECODE MESSAGE"

    def build_evidence(self, parent):
        tk.Label(parent, text=self.ch["ciphertext"], font=T.mono(16, True), fg=T.GREEN, bg=T.BG,
                 pady=14, highlightthickness=1, highlightbackground=T.BORDER).pack(fill="x")
        info = tk.Frame(parent, bg=T.CARD)
        info.pack(fill="x", pady=(8, 0))
        tk.Label(info, text=f"CIPHER: {self.ch['cipher_type'].upper()}", font=T.mono(9, True),
                 fg=T.MUTED, bg=T.CARD).pack(side="left")
        tk.Label(info, text=f"SHIFT: {self.ch['shift']}", font=T.mono(9, True), fg=T.AMBER,
                 bg=T.CARD).pack(side="right")
        # Small reference strip: top row = cipher letters, bottom row = real letters
        letters = string.ascii_uppercase
        strip = tk.Frame(parent, bg=T.CARD)
        strip.pack(fill="x", pady=(10, 0))
        tk.Label(strip, text="CIPHER  " + " ".join(caesar_shift(letters, self.ch["shift"])),
                 font=T.mono(8), fg=T.GREEN_DIM, bg=T.CARD, anchor="w").pack(fill="x")
        tk.Label(strip, text="PLAIN   " + " ".join(letters), font=T.mono(8), fg=T.MUTED, bg=T.CARD,
                 anchor="w").pack(fill="x")

    def build_task(self, parent):
        self.entry = tk.Entry(parent, font=T.mono(13), bg=T.BG, fg=T.GREEN, insertbackground=T.GREEN,
                              relief="flat", highlightthickness=1, highlightbackground=T.BORDER,
                              highlightcolor=T.GREEN, disabledbackground=T.BG2, disabledforeground=T.GREEN)
        self.entry.pack(fill="x", ipady=8)
        self.entry.bind("<Return>", lambda e: self.on_submit())

    def collect_answer(self):
        return self.entry.get()

    def show_solved(self):
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, self.ch["plaintext"])

    def lock(self):
        self.entry.configure(state="disabled")

    def after_wrong(self):
        limit = self.ch["max_attempts_before_reveal"]
        if self.mission.wrong_attempts.get(self.index, 0) >= limit and not hasattr(self, "reveal_btn"):
            self.reveal_btn = NeonButton(self.actions, "REVEAL ANSWER", self.on_reveal, "danger")
            self.reveal_btn.pack(side="left", padx=(8, 0))

    def on_reveal(self):
        self.dash.use_hint(self.index)      # revealing counts as using the hint (penalty once)
        self.entry.delete(0, "end")
        self.entry.insert(0, self.ch["plaintext"])
        self.hint_btn.configure(text=self._hint_text())
        self.feedback.show("warning", "ANSWER REVEALED  //  COUNTS AS A HINT",
                           "The decoded text has been placed in the box. Press DECODE MESSAGE to submit it.")


# ---------------------------------------------------------------- 3: login anomaly
class LoginView(ChallengeView):
    def build_evidence(self, parent):
        self.table = DataTable(parent, self.ch["table_columns"], self.ch["table_rows"])
        self.table.pack(fill="x")

    def build_task(self, parent):
        texts = [o["text"] for o in self.ch["options"]]
        self.choices = ChoiceList(parent, texts, multi=False, order=self.shuffled_order(len(texts)))
        self.choices.pack(fill="x")
        tk.Label(parent, text="> " + self.ch["row_task"], font=T.mono(9, True), fg=T.AMBER,
                 bg=T.CARD, anchor="w").pack(fill="x", pady=(10, 0))

    def collect_answer(self):
        return self.choices.get(), self.table.get_selected()

    def show_solved(self):
        correct = [i for i, o in enumerate(self.ch["options"]) if o["correct"]]
        self.choices.set_selection(correct)
        self.table.locked = False
        self.table.mark_suspicious(self.ch["suspicious_row"])

    def lock(self):
        self.choices.lock()
        self.table.lock()


# ---------------------------------------------------------------- 4: timeline
class OrderList(tk.Frame):
    """Event cards that can be moved up or down."""

    def __init__(self, parent, events, start_order):
        super().__init__(parent, bg=T.CARD)
        self.by_id = {e["id"]: e for e in events}
        self.order = list(start_order)
        self.locked = False
        self._render()

    def _render(self):
        for child in self.winfo_children():
            child.destroy()
        for pos, event_id in enumerate(self.order):
            e = self.by_id[event_id]
            row = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=str(pos + 1), font=T.mono(14, True), fg=T.GREEN, bg=T.BG2,
                     width=3).pack(side="left")
            text = tk.Frame(row, bg=T.BG2)
            text.pack(side="left", fill="x", expand=True, pady=6)
            wrap_label(text, e["event"], T.ui(10), T.TEXT, T.BG2).pack(fill="x")
            suffix = " (estimated)" if e["time_note"] else ""
            tk.Label(text, text=f"{e['time']}{suffix}  |  {e['source']}", font=T.mono(8), fg=T.MUTED,
                     bg=T.BG2, anchor="w").pack(fill="x")
            buttons = tk.Frame(row, bg=T.BG2)
            buttons.pack(side="right", padx=6)
            up = NeonButton(buttons, "\u25B2 UP", lambda i=pos: self.move(i, -1), "secondary", 8, 8, 3)
            down = NeonButton(buttons, "\u25BC DOWN", lambda i=pos: self.move(i, 1), "secondary", 8, 8, 3)
            up.pack(side="left", padx=2)
            down.pack(side="left", padx=2)
            up.set_enabled(pos > 0 and not self.locked)
            down.set_enabled(pos < len(self.order) - 1 and not self.locked)

    def move(self, pos, step):
        target = pos + step
        if self.locked or not 0 <= target < len(self.order):
            return
        self.order[pos], self.order[target] = self.order[target], self.order[pos]
        self._render()

    def set_order(self, order):
        self.order = list(order)
        self._render()

    def lock(self):
        self.locked = True
        self._render()


class TimelineView(ChallengeView):
    submit_label = "SUBMIT TIMELINE"

    def build_evidence(self, parent):
        wrap_label(parent, "Evidence collected so far: the suspicious email (E-01), the decoded note "
                           "(E-02) and the login records (E-03). Four event records now need to be "
                           "placed in order.", T.ui(10), T.TEXT).pack(fill="x")

    def build_task(self, parent):
        self.orderlist = OrderList(parent, self.ch["events"], self.ch["start_order"])
        self.orderlist.pack(fill="x")

    def collect_answer(self):
        return list(self.orderlist.order)

    def show_solved(self):
        self.orderlist.set_order(self.ch["correct_order"])
        for child in self.extra.winfo_children():
            child.destroy()
        by_id = {e["id"]: e for e in self.ch["events"]}
        entries = []
        for event_id in self.ch["correct_order"]:
            e = by_id[event_id]
            entries.append({"time": e["time"] + (" (est.)" if e["time_note"] else ""),
                            "event": e["event"], "source": e["source"], "note": e["note"]})
        card = Card(self.extra, border=T.GREEN_DIM)
        card.pack(fill="x", pady=(0, 12))
        section_title(card.body, "RECONSTRUCTED TIMELINE  //  EVIDENCE E-04", fg=T.GREEN).pack(fill="x", pady=(0, 8))
        Timeline(card.body, entries).pack(fill="x")

    def lock(self):
        self.orderlist.lock()


# ---------------------------------------------------------------- 5: response
class ResponseView(ChallengeView):
    submit_label = "SUBMIT RESPONSE PLAN"

    def build_evidence(self, parent):
        wrap_label(parent, "Findings so far: a suspicious email with a misleading domain, a note pointing "
                           "to logins from a new location, repeated failed logins followed by a success "
                           "from a different IP address, and a restricted resource access attempt.",
                   T.ui(10), T.TEXT).pack(fill="x")

    def build_task(self, parent):
        texts = [o["text"] for o in self.ch["options"]]
        self.choices = ChoiceList(parent, texts, multi=True, order=self.shuffled_order(len(texts)))
        self.choices.pack(fill="x")

    def collect_answer(self):
        return self.choices.get()

    def show_solved(self):
        self.choices.set_selection(i for i, o in enumerate(self.ch["options"]) if o["correct"])

    def lock(self):
        self.choices.lock()


VIEWS = [PhishingView, CaesarView, LoginView, TimelineView, ResponseView]
