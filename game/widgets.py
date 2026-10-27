"""Reusable styled widgets. Every screen builds its interface from these."""
import tkinter as tk
from tkinter import ttk

from . import theme as T


# ---------------------------------------------------------------- helpers
def schedule(widget, ms, func):
    """widget.after() that quietly does nothing if the widget has been destroyed."""
    def run():
        try:
            if widget.winfo_exists():
                func()
        except tk.TclError:
            pass
    try:
        return widget.after(ms, run)
    except tk.TclError:
        return None


def style_ttk(root):
    """Dark scrollbar style (ttk's 'clam' theme allows custom colours)."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("Cyber.Vertical.TScrollbar", troughcolor=T.BG2, background=T.BORDER,
                    bordercolor=T.BG2, arrowcolor=T.GREEN_DIM, lightcolor=T.BORDER,
                    darkcolor=T.BORDER, gripcount=0, relief="flat")
    style.map("Cyber.Vertical.TScrollbar", background=[("active", T.GREEN_DIM)])


def wrap_label(parent, text, font=None, fg=T.TEXT, bg=T.CARD, justify="left", **kw):
    """Label whose wrapping follows the width it is given."""
    label = tk.Label(parent, text=text, font=font or T.ui(10), fg=fg, bg=bg,
                     justify=justify, anchor="w", wraplength=300, **kw)
    label.bind("<Configure>", lambda e: label.configure(wraplength=max(120, e.width - 4)))
    return label


def section_title(parent, text, bg=T.CARD, fg=T.GREEN_DIM):
    return tk.Label(parent, text=text, font=T.mono(9, True), fg=fg, bg=bg, anchor="w")


# ---------------------------------------------------------------- buttons
_BUTTON_STYLES = {
    "primary": {"bg": T.GREEN, "fg": T.BG, "hover": "#7CFFB0", "border": T.GREEN},
    "danger": {"bg": T.RED, "fg": "#FFFFFF", "hover": "#FF6E76", "border": T.RED},
    "secondary": {"bg": T.CARD, "fg": T.TEXT, "hover": T.CARD_HI, "border": T.BORDER},
}


class NeonButton(tk.Button):
    """Flat button with hover effect. style: primary / danger / secondary."""

    def __init__(self, parent, text, command=None, style="primary", size=10, padx=18, pady=8):
        self._look = _BUTTON_STYLES[style]
        super().__init__(parent, text=text, command=command, font=T.ui(size, True),
                         bg=self._look["bg"], fg=self._look["fg"],
                         activebackground=self._look["hover"], activeforeground=self._look["fg"],
                         relief="flat", bd=0, highlightthickness=1,
                         highlightbackground=self._look["border"], highlightcolor=self._look["border"],
                         cursor="hand2", padx=padx, pady=pady, disabledforeground=T.MUTED)
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def _hover(self, inside):
        if str(self["state"]) == "normal":
            self.configure(bg=self._look["hover"] if inside else self._look["bg"])

    def set_enabled(self, enabled):
        if enabled:
            self.configure(state="normal", bg=self._look["bg"], cursor="hand2",
                           highlightbackground=self._look["border"])
        else:
            self.configure(state="disabled", bg="#1A211D", cursor="arrow", highlightbackground=T.BORDER)


# ---------------------------------------------------------------- containers
class Card(tk.Frame):
    """Dark panel with a thin border. Put content inside `.body`."""

    def __init__(self, parent, bg=T.CARD, border=T.BORDER, pad=T.PAD):
        super().__init__(parent, bg=bg, highlightthickness=1, highlightbackground=border,
                         highlightcolor=border)
        self.body = tk.Frame(self, bg=bg)
        self.body.pack(fill="both", expand=True, padx=pad, pady=pad)


class Badge(tk.Label):
    def __init__(self, parent, text, colour, bg=T.CARD):
        super().__init__(parent, text=text, font=T.mono(8, True), fg=colour, bg=bg,
                         padx=6, pady=1, highlightthickness=1, highlightbackground=colour)


class ProgressBar(tk.Canvas):
    def __init__(self, parent, height=8, bg=T.BG2, fill=T.GREEN):
        super().__init__(parent, height=height, bg=bg, highlightthickness=1,
                         highlightbackground=T.BORDER, bd=0)
        self._fill, self._fraction = fill, 0.0
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, fraction):
        self._fraction = max(0.0, min(1.0, fraction))
        self._draw()

    def _draw(self):
        self.delete("bar")
        width, height = self.winfo_width(), self.winfo_height()
        if self._fraction > 0:
            self.create_rectangle(0, 0, width * self._fraction, height, fill=self._fill,
                                  outline="", tags="bar")


class StatusDot(tk.Frame):
    """Small pulsing indicator with a text label."""

    def __init__(self, parent, text, colour=T.GREEN, bg=T.BG2, pulse=True):
        super().__init__(parent, bg=bg)
        self._bg, self._colour, self._on = bg, colour, True
        self.dot = tk.Canvas(self, width=10, height=10, bg=bg, highlightthickness=0)
        self.dot.pack(side="left", padx=(0, 6))
        self._oval = self.dot.create_oval(1, 1, 9, 9, fill=colour, outline="")
        self.label = tk.Label(self, text=text, font=T.mono(9, True), fg=colour, bg=bg)
        self.label.pack(side="left")
        if pulse:
            schedule(self, 700, self._pulse)

    def set(self, text, colour):
        self._colour = colour
        self.label.configure(text=text, fg=colour)
        self.dot.itemconfigure(self._oval, fill=colour)

    def _pulse(self):
        self._on = not self._on
        self.dot.itemconfigure(self._oval, fill=self._colour if self._on else T.BORDER)
        schedule(self, 700, self._pulse)


class ScrollFrame(tk.Frame):
    """Vertically scrollable area. Add widgets to `.body`."""
    _wheel_bound = False

    def __init__(self, parent, bg=T.BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                       style="Cyber.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=bg)
        self._window = self.canvas.create_window((0, 0), window=self.body, anchor="nw")
        self.body.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._window, width=e.width))
        if not ScrollFrame._wheel_bound:
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                self.bind_all(seq, ScrollFrame._on_wheel, add="+")
            ScrollFrame._wheel_bound = True

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)

    @staticmethod
    def _on_wheel(event):
        """Scroll whichever ScrollFrame is under the mouse pointer."""
        try:
            widget = event.widget.winfo_containing(event.x_root, event.y_root)
        except (tk.TclError, KeyError, AttributeError):
            return
        while widget is not None and not isinstance(widget, ScrollFrame):
            widget = widget.master
        if widget is None:
            return
        bbox = widget.canvas.bbox("all")
        if not bbox or bbox[3] <= widget.canvas.winfo_height():
            return
        if event.num == 4:
            step = -1
        elif event.num == 5:
            step = 1
        else:
            step = -1 if event.delta > 0 else 1
        widget.canvas.yview_scroll(step * 2, "units")


# ---------------------------------------------------------------- feedback
class FeedbackPanel(tk.Frame):
    """Coloured message box: success (green), warning (amber), danger (red)."""
    KINDS = {"success": (T.GREEN, T.GREEN_TINT), "warning": (T.AMBER, T.AMBER_TINT),
             "danger": (T.RED, T.RED_TINT)}

    def __init__(self, parent):
        super().__init__(parent, bg=T.BG)

    def clear(self):
        for child in self.winfo_children():
            child.destroy()

    def show(self, kind, title, message):
        self.clear()
        colour, tint = self.KINDS[kind]
        box = tk.Frame(self, bg=tint, highlightthickness=1, highlightbackground=colour)
        box.pack(fill="x", pady=(10, 0))
        tk.Label(box, text=title, font=T.mono(10, True), fg=colour, bg=tint,
                 anchor="w").pack(fill="x", padx=12, pady=(10, 2))
        wrap_label(box, message, T.ui(10), T.TEXT, tint).pack(fill="x", padx=12, pady=(0, 10))


# ---------------------------------------------------------------- terminal
class Terminal(tk.Text):
    """Read-only, terminal-style feed with a blinking cursor. Purely a visual component."""

    def __init__(self, parent):
        super().__init__(parent, bg="#080A09", fg=T.GREEN, font=T.mono(9), relief="flat", bd=0,
                         highlightthickness=1, highlightbackground=T.BORDER, wrap="word",
                         padx=8, pady=8, cursor="arrow", state="disabled", height=8)
        self.tag_configure("time", foreground=T.MUTED)
        self.tag_configure("alert", foreground=T.RED)
        self.tag_configure("cursor", foreground=T.GREEN)
        self._cursor_on = True
        schedule(self, 600, self._blink)

    def render(self, lines):
        """Replace content with (timestamp, message) pairs."""
        self.configure(state="normal")
        self.delete("1.0", "end")
        for stamp, message in lines:
            self.insert("end", f"[{stamp}] ", "time")
            self.insert("end", message + "\n", "alert" if "ALERT" in message else "")
        self.insert("end", "> ")
        self.insert("end", "\u2588", "cursor")
        self.configure(state="disabled")
        self.see("end")

    def _blink(self):
        self._cursor_on = not self._cursor_on
        self.tag_configure("cursor", foreground=T.GREEN if self._cursor_on else "#080A09")
        schedule(self, 600, self._blink)


# ---------------------------------------------------------------- choices
class ChoiceList(tk.Frame):
    """Clickable option rows. multi=True gives check boxes, otherwise radio buttons.

    Rows are shown in `order` (a list of option indexes); get() returns original indexes.
    """

    def __init__(self, parent, texts, multi, order=None, bg=T.CARD):
        super().__init__(parent, bg=bg)
        self.multi, self.selected, self.locked = multi, set(), False
        self.rows = {}
        for idx in (order if order is not None else range(len(texts))):
            row = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.BORDER, cursor="hand2")
            row.pack(fill="x", pady=3)
            marker = tk.Label(row, text="[ ]" if multi else "( )", font=T.mono(11, True),
                              fg=T.GREEN_DIM, bg=T.BG2, width=4)
            marker.pack(side="left", padx=(8, 2), pady=8)
            text = wrap_label(row, texts[idx], T.ui(10), T.TEXT, T.BG2)
            text.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=8)
            for widget in (row, marker, text):
                widget.bind("<Button-1>", lambda e, i=idx: self._toggle(i))
                widget.bind("<Enter>", lambda e, i=idx: self._hover(i, True))
                widget.bind("<Leave>", lambda e, i=idx: self._hover(i, False))
            self.rows[idx] = (row, marker, text)

    def _toggle(self, idx):
        if self.locked:
            return
        if self.multi:
            self.selected ^= {idx}
        else:
            self.selected = {idx}
        self._paint()

    def _hover(self, idx, inside):
        if self.locked or idx in self.selected:
            return
        self._colour_row(idx, T.CARD_HI if inside else T.BG2)

    def _colour_row(self, idx, bg):
        row, marker, text = self.rows[idx]
        for w in (row, marker, text):
            w.configure(bg=bg)

    def _paint(self):
        for idx, (row, marker, text) in self.rows.items():
            on = idx in self.selected
            self._colour_row(idx, T.GREEN_TINT if on else T.BG2)
            row.configure(highlightbackground=T.GREEN if on else T.BORDER)
            marker.configure(text=(("[X]" if on else "[ ]") if self.multi else ("(*)" if on else "( )")),
                             fg=T.GREEN if on else T.GREEN_DIM)

    def get(self):
        """Set of selected indexes (multi) or a single index / None (radio)."""
        if self.multi:
            return set(self.selected)
        return next(iter(self.selected)) if self.selected else None

    def set_selection(self, indexes):
        self.selected = set(indexes)
        self._paint()

    def lock(self):
        self.locked = True
        for row, marker, text in self.rows.values():
            row.configure(cursor="arrow")


# ---------------------------------------------------------------- table
class DataTable(tk.Frame):
    """Aligned log table with alternating rows, selectable rows and text flags."""

    def __init__(self, parent, columns, rows, selectable=True):
        super().__init__(parent, bg=T.BORDER, highlightthickness=1, highlightbackground=T.BORDER)
        self.rows, self.selectable, self.selected, self.locked = rows, selectable, None, False
        self.cells, self.flags = [], []
        cols = list(columns) + ["FLAG"]
        for c, name in enumerate(cols):
            tk.Label(self, text=name.upper(), font=T.mono(9, True), fg=T.GREEN, bg=T.BG,
                     anchor="w", padx=8, pady=6).grid(row=0, column=c, sticky="nsew")
            self.columnconfigure(c, weight=1 if c != len(cols) - 1 else 0, uniform="")
        for r, values in enumerate(rows):
            bg = T.CARD if r % 2 == 0 else T.BG2
            row_cells = []
            for c, value in enumerate(values):
                colour = T.TEXT
                if value == "FAILED":
                    colour = T.RED
                elif value == "SUCCESS":
                    colour = T.GREEN
                label = tk.Label(self, text=value, font=T.mono(10), fg=colour, bg=bg,
                                 anchor="w", padx=8, pady=6)
                label.grid(row=r + 1, column=c, sticky="nsew")
                row_cells.append(label)
            flag = tk.Label(self, text="", font=T.mono(9, True), fg=T.RED, bg=bg, anchor="w",
                            padx=8, width=12)
            flag.grid(row=r + 1, column=len(values), sticky="nsew")
            row_cells.append(flag)
            self.flags.append(flag)
            self.cells.append(row_cells)
            if selectable:
                for w in row_cells:
                    w.configure(cursor="hand2")
                    w.bind("<Button-1>", lambda e, i=r: self.select(i))

    def _base_bg(self, r):
        return T.CARD if r % 2 == 0 else T.BG2

    def select(self, row):
        if self.locked:
            return
        self.selected = row
        for r, cells in enumerate(self.cells):
            colour = T.GREEN_TINT if r == row else self._base_bg(r)
            for w in cells:
                w.configure(bg=colour)
        self.flags[row].configure(text="SELECTED", fg=T.GREEN)
        for r, flag in enumerate(self.flags):
            if r != row and flag.cget("text") == "SELECTED":
                flag.configure(text="")

    def mark_suspicious(self, row):
        self.selected = row
        for w in self.cells[row]:
            w.configure(bg=T.RED_TINT)
        self.flags[row].configure(text="SUSPICIOUS", fg=T.RED)

    def get_selected(self):
        return self.selected

    def lock(self):
        self.locked = True
        for cells in self.cells:
            for w in cells:
                w.configure(cursor="arrow")


# ---------------------------------------------------------------- timeline
class Timeline(tk.Frame):
    """Vertical timeline: time | marker | event, source and note."""

    def __init__(self, parent, entries, bg=T.CARD):
        super().__init__(parent, bg=bg)
        count = len(entries)
        for i, entry in enumerate(entries):
            row = tk.Frame(self, bg=bg)
            row.pack(fill="x")
            row.columnconfigure(2, weight=1)
            tk.Label(row, text=entry["time"], font=T.mono(10, True), fg=T.GREEN, bg=bg, width=16,
                     anchor="ne").grid(row=0, column=0, sticky="ne", pady=(6, 0))
            marker = tk.Canvas(row, width=26, height=1, bg=bg, highlightthickness=0)
            marker.grid(row=0, column=1, sticky="ns")
            marker.bind("<Configure>", lambda e, c=marker, f=(i == 0), l=(i == count - 1): self._draw(c, f, l))
            info = tk.Frame(row, bg=bg)
            info.grid(row=0, column=2, sticky="new", padx=(4, 0), pady=(4, 10))
            wrap_label(info, entry["event"], T.ui(10, True), T.TEXT, bg).pack(fill="x")
            wrap_label(info, f"Source: {entry['source']}", T.mono(9), T.MUTED, bg).pack(fill="x")
            wrap_label(info, f"Note: {entry['note']}", T.ui(9), T.MUTED, bg).pack(fill="x")

    @staticmethod
    def _draw(canvas, first, last):
        canvas.delete("all")
        height = canvas.winfo_height()
        top = 14 if first else 0
        bottom = 14 if last else height
        canvas.create_line(13, top, 13, bottom, fill=T.GREEN_DIM, width=2)
        canvas.create_oval(8, 9, 18, 19, fill=T.GREEN, outline=T.BG)


# ---------------------------------------------------------------- dialogs
class _Dialog(tk.Toplevel):
    def __init__(self, parent, title, message, yes, no, danger):
        super().__init__(parent)
        self.withdraw()
        self.title(title)
        self.configure(bg=T.BG)
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.result = False
        outer = tk.Frame(self, bg=T.BG2, highlightthickness=1, highlightbackground=T.GREEN_DIM)
        outer.pack(fill="both", expand=True)
        tk.Label(outer, text=title.upper(), font=T.mono(11, True), fg=T.GREEN, bg=T.BG2,
                 anchor="w").pack(fill="x", padx=20, pady=(18, 6))
        tk.Label(outer, text=message, font=T.ui(10), fg=T.TEXT, bg=T.BG2, justify="left",
                 wraplength=380, anchor="w").pack(fill="x", padx=20, pady=(0, 16))
        buttons = tk.Frame(outer, bg=T.BG2)
        buttons.pack(fill="x", padx=20, pady=(0, 18))
        NeonButton(buttons, yes, lambda: self._close(True),
                   "danger" if danger else "primary").pack(side="right")
        if no:
            NeonButton(buttons, no, lambda: self._close(False), "secondary").pack(side="right", padx=(0, 8))
        self.protocol("WM_DELETE_WINDOW", lambda: self._close(False))
        self.bind("<Escape>", lambda e: self._close(False))
        self.update_idletasks()
        top = parent.winfo_toplevel()
        x = top.winfo_rootx() + (top.winfo_width() - self.winfo_reqwidth()) // 2
        y = top.winfo_rooty() + (top.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.deiconify()
        self.wait_visibility()
        self.grab_set()
        self.focus_set()
        self.wait_window()

    def _close(self, value):
        self.result = value
        self.destroy()


def ask_confirm(parent, title, message, yes="CONFIRM", no="CANCEL", danger=False):
    """Modal yes/no dialog. Returns True or False."""
    return _Dialog(parent, title, message, yes, no, danger).result


def show_info(parent, title, message, button="OK"):
    """Modal message dialog with a single button."""
    _Dialog(parent, title, message, button, None, False)
