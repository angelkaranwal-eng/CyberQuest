"""Scoring rules. Every rule lives here so it is defined only once."""

POINTS_FIRST_TRY = 100      # correct on the first attempt
POINTS_RETRY = 60           # correct after at least one wrong attempt
HINT_PENALTY = 15           # applied ONCE per challenge, the first time a hint is used
COMPLETION_BONUS = 100      # awarded once when all challenges are completed


def points_for_correct(wrong_attempts):
    """Points for solving a challenge, depending on earlier wrong attempts."""
    return POINTS_FIRST_TRY if wrong_attempts == 0 else POINTS_RETRY


def apply_hint_penalty(score):
    """Subtract the hint penalty. The score never drops below zero."""
    return max(0, score - HINT_PENALTY)


def max_score(challenge_count):
    return challenge_count * POINTS_FIRST_TRY + COMPLETION_BONUS


def performance_rating(score):
    """Map a final score (out of 600) to a rating label."""
    if score >= 560:
        return "EXCELLENT INVESTIGATION"
    if score >= 480:
        return "STRONG INVESTIGATION"
    if score >= 380:
        return "INVESTIGATION COMPLETED"
    return "MORE PRACTICE RECOMMENDED"
