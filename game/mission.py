"""Mission state: progress, score, hints, event feed. No GUI code."""
from dataclasses import dataclass

from . import challenges, scoring


@dataclass
class SubmitResult:
    correct: bool
    note: str = ""
    points: int = 0
    already_completed: bool = False
    mission_completed: bool = False


class Mission:
    def __init__(self, data):
        self.data = data
        self.challenge_list = data["challenges"]
        self.total = len(self.challenge_list)
        self.reset()

    def reset(self):
        self.completed = []       # indices of completed challenges, in order
        self.score = 0
        self.hints_used = []      # indices of challenges where a hint was used
        self.wrong_attempts = {}  # challenge index -> number of wrong submissions
        self.started = []         # indices the player has opened
        self.bonus_awarded = False
        self.feed = [list(e) for e in self.data["case"]["start_events"]]

    # ---- progress ---------------------------------------------------
    @property
    def is_complete(self):
        return len(self.completed) == self.total

    @property
    def max_score(self):
        return scoring.max_score(self.total)

    @property
    def completion_percent(self):
        return round(100 * len(self.completed) / self.total)

    def first_open_index(self):
        """Index of the first challenge not yet completed (or the last one)."""
        for i in range(self.total):
            if i not in self.completed:
                return i
        return self.total - 1

    def is_unlocked(self, index):
        return index <= len(self.completed) and index < self.total

    def status_of(self, index):
        if index in self.completed:
            return "COMPLETED"
        if not self.is_unlocked(index):
            return "LOCKED"
        if index in self.started or self.wrong_attempts.get(index) or index in self.hints_used:
            return "IN PROGRESS"
        return "AVAILABLE"

    def mark_started(self, index):
        if self.is_unlocked(index) and index not in self.started:
            self.started.append(index)

    # ---- actions ----------------------------------------------------
    def use_hint(self, index):
        """Return the hint text. The penalty applies only the first time per challenge."""
        if not self.is_unlocked(index):
            return ""
        if index not in self.hints_used and index not in self.completed:
            self.hints_used.append(index)
            self.score = scoring.apply_hint_penalty(self.score)
        return self.challenge_list[index]["hint"]

    def submit(self, index, answer):
        """Validate an answer and update score/progress."""
        if not self.is_unlocked(index):
            return SubmitResult(False, "This stage is still locked.")
        if index in self.completed:
            return SubmitResult(True, "", 0, already_completed=True)
        verdict = challenges.validate(self.challenge_list[index], answer)
        if not verdict.correct:
            if verdict.counts_as_attempt:  # empty submissions are not penalised
                self.wrong_attempts[index] = self.wrong_attempts.get(index, 0) + 1
            return SubmitResult(False, verdict.note)
        points = scoring.points_for_correct(self.wrong_attempts.get(index, 0))
        self.score += points
        self.completed.append(index)
        self.feed.extend(list(e) for e in self.challenge_list[index]["feed_complete"])
        finished = self.is_complete
        if finished and not self.bonus_awarded:
            self.score += scoring.COMPLETION_BONUS
            self.bonus_awarded = True
            points += scoring.COMPLETION_BONUS
        return SubmitResult(True, "", points, mission_completed=finished)

    # ---- save/restore -----------------------------------------------
    def to_dict(self):
        return {
            "completed": self.completed, "score": self.score, "hints_used": self.hints_used,
            "wrong_attempts": {str(k): v for k, v in self.wrong_attempts.items()},
            "started": self.started, "bonus_awarded": self.bonus_awarded, "feed": self.feed,
        }

    def load_dict(self, saved):
        """Restore progress. Returns True on success, False if data is invalid (state is reset)."""
        try:
            completed = [int(i) for i in saved["completed"]]
            if completed != list(range(len(completed))) or len(completed) > self.total:
                raise ValueError("completed list is not a valid sequence")
            self.reset()
            self.completed = completed
            self.score = max(0, int(saved["score"]))
            self.hints_used = [int(i) for i in saved["hints_used"] if 0 <= int(i) < self.total]
            self.wrong_attempts = {int(k): int(v) for k, v in saved["wrong_attempts"].items()}
            self.started = [int(i) for i in saved["started"] if 0 <= int(i) < self.total]
            self.bonus_awarded = bool(saved["bonus_awarded"])
            self.feed = [[str(a), str(b)] for a, b in saved["feed"]]
            return True
        except (KeyError, TypeError, ValueError, AttributeError):
            self.reset()
            return False
