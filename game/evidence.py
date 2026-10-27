"""Evidence availability. Evidence unlocks when its related challenge is reached."""
LOCKED, AVAILABLE, ANALYSED = "LOCKED", "AVAILABLE", "ANALYSED"


def evidence_status(item, mission):
    """LOCKED until the related challenge is unlocked, ANALYSED once it is completed."""
    index = item["challenge"] - 1
    if index in mission.completed:
        return ANALYSED
    if mission.is_unlocked(index):
        return AVAILABLE
    return LOCKED


def evidence_text(item, mission, data):
    """Return (details, findings). Findings are empty until the challenge is solved."""
    status = evidence_status(item, mission)
    if status == LOCKED:
        return "", ""
    findings = item["findings"] if status == ANALYSED else ""
    if status == ANALYSED and item["challenge"] == 4:
        findings = timeline_text(data)
    if status == ANALYSED and item["challenge"] == 5:
        options = data["challenges"][4]["options"]
        findings = "Recommended actions:\n" + "\n".join("- " + o["text"] for o in options if o["correct"])
    return item["available_details"], findings


def timeline_text(data):
    """Plain-text timeline built from the challenge 4 data."""
    ch = data["challenges"][3]
    by_id = {e["id"]: e for e in ch["events"]}
    lines = []
    for event_id in ch["correct_order"]:
        e = by_id[event_id]
        suffix = " (estimated)" if e["time_note"] else ""
        lines.append(f"{e['time']}{suffix}  {e['event']}  [{e['source']}]")
    return "Reconstructed timeline:\n" + "\n".join(lines)
