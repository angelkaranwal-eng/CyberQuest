"""Colours, fonts and spacing used by every screen."""
import tkinter.font as tkfont

# --- colour palette -------------------------------------------------------
BG = "#0B0D0C"          # main background
BG2 = "#121715"         # secondary background
CARD = "#171E1A"        # card background
CARD_HI = "#1F2923"     # card hover / highlight
GREEN = "#39FF88"       # neon green (primary, success)
GREEN_DIM = "#1D8F5A"   # muted green
RED = "#FF3B46"         # threats and failures
AMBER = "#FFB547"       # warnings and pending
TEXT = "#E8F0EB"        # primary text
MUTED = "#8D9B92"       # secondary text
BORDER = "#29362F"      # borders
GREEN_TINT = "#0F2A1C"  # tinted backgrounds for feedback boxes
RED_TINT = "#2A1214"
AMBER_TINT = "#2A2010"

# --- spacing ---------------------------------------------------------------
PAD = 16
PAD_SM = 8

_mono_family = "Courier New"
_ui_family = "Arial"


def init_fonts(root):
    """Pick the best installed fonts (must be called after the root window exists)."""
    global _mono_family, _ui_family
    installed = set(tkfont.families(root))
    for name in ("Cascadia Mono", "Consolas", "DejaVu Sans Mono", "Menlo", "Courier New"):
        if name in installed:
            _mono_family = name
            break
    for name in ("Segoe UI", "Helvetica Neue", "DejaVu Sans", "Arial"):
        if name in installed:
            _ui_family = name
            break


def mono(size=10, bold=False):
    return (_mono_family, size, "bold" if bold else "normal")


def ui(size=10, bold=False):
    return (_ui_family, size, "bold" if bold else "normal")


STATUS_COLOURS = {
    "LOCKED": MUTED,
    "AVAILABLE": GREEN_DIM,
    "IN PROGRESS": AMBER,
    "COMPLETED": GREEN,
    "NEW": AMBER,
    "ANALYSED": GREEN,
}
