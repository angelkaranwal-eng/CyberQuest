"""Build and export the final incident report from the real session results."""
from datetime import datetime
from pathlib import Path

from . import scoring

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def build_report(mission, data):
    """Return the report as a dictionary. The GUI and the .txt export both use it."""
    case = data["case"]
    chs = data["challenges"]
    ch4 = chs[3]
    by_id = {e["id"]: e for e in ch4["events"]}
    timeline = []
    for event_id in ch4["correct_order"]:
        e = by_id[event_id]
        time = e["time"] + (" (est.)" if e["time_note"] else "")
        timeline.append({"time": time, "event": e["event"], "source": e["source"], "note": e["note"]})
    return {
        "heading": f"{case['company']} // INCIDENT REPORT",
        "case_id": case["id"],
        "case_name": case["name"],
        "status": "CLOSED - INVESTIGATION COMPLETE" if mission.is_complete else "OPEN - INCOMPLETE",
        "score": mission.score,
        "max_score": mission.max_score,
        "completed": len(mission.completed),
        "total": mission.total,
        "hints_used": len(mission.hints_used),
        "wrong_attempts": sum(mission.wrong_attempts.values()),
        "rating": scoring.performance_rating(mission.score) if mission.is_complete else "INCOMPLETE",
        "observed": data["report"]["observed"],
        "possible_explanation": data["report"]["possible_explanation"],
        "timeline": timeline,
        "warning_signs": [o["text"] for o in chs[0]["options"] if o["correct"]],
        "response_actions": [o["text"] for o in chs[4]["options"] if o["correct"]],
        "conclusion": data["report"]["conclusion"],
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def report_to_text(r):
    """Plain-text version of the report."""
    line = "=" * 64
    out = [line, r["heading"], line,
           f"Case ID        : {r['case_id']}",
           f"Case title     : {r['case_name']}",
           f"Final status   : {r['status']}",
           f"Generated      : {r['generated']}",
           "",
           f"Total score    : {r['score']} / {r['max_score']}",
           f"Challenges     : {r['completed']} / {r['total']} completed",
           f"Hints used     : {r['hints_used']}",
           f"Wrong attempts : {r['wrong_attempts']}",
           f"Performance    : {r['rating']}",
           "", "OBSERVED EVIDENCE", "-" * 17]
    out += [f"- {item}" for item in r["observed"]]
    out += ["", "POSSIBLE EXPLANATION (NOT CONFIRMED)", "-" * 36, r["possible_explanation"],
            "", "INCIDENT TIMELINE", "-" * 17]
    out += [f"{t['time']:<18}{t['event']}\n{'':<18}Source: {t['source']} - {t['note']}" for t in r["timeline"]]
    out += ["", "IDENTIFIED WARNING SIGNS", "-" * 24] + [f"- {s}" for s in r["warning_signs"]]
    out += ["", "RECOMMENDED RESPONSE ACTIONS", "-" * 28] + [f"- {s}" for s in r["response_actions"]]
    out += ["", "CONCLUSION", "-" * 10, r["conclusion"], "", "(All events in this report are fictional.)"]
    return "\n".join(out) + "\n"


def export_report(report, folder=REPORT_DIR):
    """Write the report to reports/ and return the file path. Raises OSError on failure."""
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = folder / f"incident_report_{report['case_id']}_{stamp}.txt"
    path.write_text(report_to_text(report), encoding="utf-8")
    return path
