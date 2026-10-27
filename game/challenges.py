"""Challenge data loading and answer validation (no GUI code here)."""
import json
from dataclasses import dataclass
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "mission_data.json"


@dataclass
class Verdict:
    correct: bool
    note: str = ""
    counts_as_attempt: bool = True   # False for "nothing entered" prompts


def load_data(path=DATA_FILE):
    """Load mission_data.json. Raises a readable error if it is missing/broken."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Mission data file not found: {path}")
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Mission data file is not valid JSON: {err}")


def caesar_shift(text, shift):
    """Shift letters by `shift` positions (negative = backwards). Other characters stay."""
    result = []
    for ch in text:
        if ch.isalpha() and ch.isascii():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def _normalise(text):
    """Uppercase and collapse extra spaces so formatting does not matter."""
    return " ".join(str(text).upper().split())


# ---- one validation function per challenge --------------------------------

def check_phishing(challenge, selected):
    """`selected` is a set of option indices."""
    options = challenge["options"]
    correct_set = {i for i, o in enumerate(options) if o["correct"]}
    selected = set(selected)
    if not selected:
        return Verdict(False, "Nothing selected. Choose every warning sign you can find.", False)
    if selected == correct_set:
        return Verdict(True)
    missed = [options[i]["text"] for i in sorted(correct_set - selected)]
    wrong = [options[i]["text"] for i in sorted(selected - correct_set)]
    lines = []
    if missed:
        lines.append("Missed clue(s): " + " | ".join(missed))
    if wrong:
        lines.append("Not a warning sign by itself: " + " | ".join(wrong))
    lines.append(challenge["wrong_note"])
    return Verdict(False, "\n".join(lines))


def check_caesar(challenge, text):
    expected = _normalise(caesar_shift(challenge["ciphertext"], -challenge["shift"]))
    if not str(text).strip():
        return Verdict(False, "Type the decoded message first.", False)
    if _normalise(text) == expected:
        return Verdict(True)
    return Verdict(False, challenge["wrong_note"])


def check_login(challenge, answer):
    """`answer` is (pattern_option_index, row_index_or_None)."""
    pattern, row = answer
    if pattern is None:
        return Verdict(False, "Select the pattern that deserves investigation.", False)
    correct_pattern = [i for i, o in enumerate(challenge["options"]) if o["correct"]][0]
    if pattern != correct_pattern:
        return Verdict(False, "The selected pattern does not match the evidence. " + challenge["wrong_note"])
    if row is None:
        return Verdict(False, "Pattern noted. Now select the unusual record in the table.", False)
    if row != challenge["suspicious_row"]:
        return Verdict(False, "That record is not the unusual one. " + challenge["wrong_note"])
    return Verdict(True)


def check_timeline(challenge, order):
    """`order` is a list of event ids in the player's order."""
    if list(order) == challenge["correct_order"]:
        return Verdict(True)
    return Verdict(False, challenge["wrong_note"])


def check_response(challenge, selected):
    options = challenge["options"]
    correct_set = {i for i, o in enumerate(options) if o["correct"]}
    selected = set(selected)
    if not selected:
        return Verdict(False, "Nothing selected. Choose the actions the team should take.", False)
    if selected == correct_set:
        return Verdict(True)
    lines = []
    missed = [options[i]["text"] for i in sorted(correct_set - selected)]
    bad = [options[i]["text"] for i in sorted(selected - correct_set)]
    if missed:
        lines.append("Missing action(s): " + " | ".join(missed))
    if bad:
        lines.append("Inappropriate action(s) selected: " + " | ".join(bad))
    lines.append(challenge["wrong_note"])
    return Verdict(False, "\n".join(lines))


CHECKERS = {1: check_phishing, 2: check_caesar, 3: check_login, 4: check_timeline, 5: check_response}


def validate(challenge, answer):
    """Validate an answer for any challenge using its id."""
    return CHECKERS[challenge["id"]](challenge, answer)
