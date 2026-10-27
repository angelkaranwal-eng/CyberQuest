"""Run with:  python -m unittest discover tests   (from the project folder)"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game import challenges, report, scoring, storage  # noqa: E402
from game.mission import Mission  # noqa: E402

DATA = challenges.load_data()
RIGHT = {
    0: {0, 1, 2, 3},
    1: "logins from a new location  ",
    2: (0, 4),
    3: ["E1", "E2", "E3", "E4"],
    4: {0, 1, 2, 3},
}


class ValidationTests(unittest.TestCase):
    def ch(self, i):
        return DATA["challenges"][i]

    def test_phishing(self):
        self.assertTrue(challenges.validate(self.ch(0), {0, 1, 2, 3}).correct)
        self.assertFalse(challenges.validate(self.ch(0), {0}).correct)            # incomplete
        self.assertFalse(challenges.validate(self.ch(0), {0, 1, 2, 3, 4}).correct)  # extra wrong
        self.assertFalse(challenges.validate(self.ch(0), set()).correct)

    def test_caesar(self):
        self.assertEqual(challenges.caesar_shift("ORJLQV", -3), "LOGINS")
        self.assertEqual(challenges.caesar_shift(self.ch(1)["ciphertext"], -3), self.ch(1)["plaintext"])
        self.assertTrue(challenges.validate(self.ch(1), "  Logins from a NEW location ").correct)
        self.assertFalse(challenges.validate(self.ch(1), "something unrelated").correct)
        self.assertFalse(challenges.validate(self.ch(1), "").correct)

    def test_login(self):
        self.assertTrue(challenges.validate(self.ch(2), (0, 4)).correct)
        self.assertFalse(challenges.validate(self.ch(2), (0, 1)).correct)
        self.assertFalse(challenges.validate(self.ch(2), (1, 4)).correct)
        self.assertFalse(challenges.validate(self.ch(2), (0, None)).correct)
        self.assertFalse(challenges.validate(self.ch(2), (None, None)).correct)

    def test_timeline(self):
        self.assertTrue(challenges.validate(self.ch(3), ["E1", "E2", "E3", "E4"]).correct)
        self.assertFalse(challenges.validate(self.ch(3), ["E3", "E1", "E4", "E2"]).correct)

    def test_response(self):
        self.assertTrue(challenges.validate(self.ch(4), {0, 1, 2, 3}).correct)
        self.assertFalse(challenges.validate(self.ch(4), {0, 1, 2}).correct)
        self.assertFalse(challenges.validate(self.ch(4), {0, 1, 2, 3, 4}).correct)

    def test_start_order_is_not_solved(self):
        self.assertNotEqual(self.ch(3)["start_order"], self.ch(3)["correct_order"])


class ScoringAndMissionTests(unittest.TestCase):
    def test_penalty_floor(self):
        self.assertEqual(scoring.apply_hint_penalty(10), 0)
        self.assertEqual(scoring.apply_hint_penalty(100), 85)

    def test_perfect_run(self):
        m = Mission(DATA)
        for i in range(5):
            res = m.submit(i, RIGHT[i])
            self.assertTrue(res.correct)
        self.assertEqual(m.score, 600)
        self.assertTrue(m.is_complete)
        self.assertEqual(scoring.performance_rating(m.score), "EXCELLENT INVESTIGATION")

    def test_retry_points(self):
        m = Mission(DATA)
        m.submit(0, {0})
        res = m.submit(0, RIGHT[0])
        self.assertEqual(res.points, 60)

    def test_empty_submit_not_penalised(self):
        m = Mission(DATA)
        m.submit(0, set())
        self.assertEqual(m.submit(0, RIGHT[0]).points, 100)

    def test_hint_penalty_once_per_challenge(self):
        m = Mission(DATA)
        m.score = 200
        m.use_hint(0)
        m.use_hint(0)
        m.use_hint(0)
        self.assertEqual(m.score, 185)
        self.assertEqual(len(m.hints_used), 1)

    def test_no_double_reward(self):
        m = Mission(DATA)
        m.submit(0, RIGHT[0])
        again = m.submit(0, RIGHT[0])
        self.assertTrue(again.already_completed)
        self.assertEqual(m.score, 100)
        self.assertEqual(len(m.completed), 1)

    def test_locked_stage_cannot_be_submitted(self):
        m = Mission(DATA)
        self.assertFalse(m.submit(2, RIGHT[2]).correct)
        self.assertEqual(m.score, 0)
        self.assertEqual(m.status_of(2), "LOCKED")

    def test_bonus_once(self):
        m = Mission(DATA)
        for i in range(5):
            m.submit(i, RIGHT[i])
        m.submit(4, RIGHT[4])
        self.assertEqual(m.score, 600)


class SaveAndReportTests(unittest.TestCase):
    def test_save_roundtrip_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            self.assertFalse(storage.has_save(path))            # missing file
            m = Mission(DATA)
            m.submit(0, RIGHT[0])
            m.use_hint(1)
            storage.save_progress(m, path)
            m2 = Mission(DATA)
            self.assertTrue(m2.load_dict(storage.load_saved_dict(path)))
            self.assertEqual((m2.score, m2.completed, m2.hints_used), (85, [0], [1]))
            path.write_text("{not json", encoding="utf-8")       # corrupted file
            self.assertIsNone(storage.load_saved_dict(path))
            self.assertFalse(Mission(DATA).load_dict({"completed": [3]}))  # invalid content

    def test_report_uses_real_results_and_exports(self):
        m = Mission(DATA)
        for i in range(5):
            m.use_hint(i) if i < 2 else None
            m.submit(i, RIGHT[i])
        r = report.build_report(m, DATA)
        self.assertEqual(r["score"], m.score)
        self.assertEqual(r["hints_used"], 2)
        with tempfile.TemporaryDirectory() as tmp:
            path = report.export_report(r, Path(tmp))
            text = path.read_text(encoding="utf-8")
            self.assertIn(f"{m.score} / 600", text)
            self.assertIn("NEXUS SYSTEMS // INCIDENT REPORT", text)


if __name__ == "__main__":
    unittest.main()
