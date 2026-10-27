# CyberQuest: The Midnight Breach

A gamified cybersecurity investigation and training game built with Python and Tkinter.
You play a junior investigator working on **Case NXS-0217** for the fictional company NEXUS SYSTEMS.

## Main features
- Startup screen (skippable), main menu, mission briefing, three-panel investigation dashboard
- Five connected challenges: phishing email, Caesar cipher, login-log analysis, incident timeline, incident response
- Scoring, hints, evidence that unlocks with progress, and a simulated event feed
- Final incident report built from your real results, exportable as a `.txt` file
- Automatic save and resume (JSON), with safe handling of missing or damaged save files
- Works fully offline. All scenarios are fictional and simulated

## Technologies
Python 3 (3.8 or newer), Tkinter / ttk (included with Python), JSON, `unittest`.
No extra packages are needed, so `requirements.txt` only contains a comment.

## Project structure
```text
CyberQuest/
├── main.py                  entry point
├── requirements.txt         (no external dependencies)
├── game/
│   ├── app.py               controller: owns mission state, switches screens
│   ├── screens.py           startup, menu, how-to/about, briefing, report screens
│   ├── dashboard.py         investigation dashboard + evidence viewer
│   ├── challenge_views.py   the five challenge screens
│   ├── widgets.py           reusable styled buttons, cards, tables, dialogs...
│   ├── theme.py             colours and fonts
│   ├── mission.py           progress, score, hints, event feed (no GUI)
│   ├── challenges.py        data loading and answer validation (no GUI)
│   ├── scoring.py           all scoring rules in one place
│   ├── evidence.py          which evidence is unlocked
│   ├── report.py            builds and exports the report
│   └── storage.py           save / load progress
├── data/mission_data.json   story text, challenges, hints, explanations
├── reports/                 exported reports appear here
├── saves/                   progress.json is stored here
└── tests/test_game_logic.py automated tests for scoring and validation
```

## Installation and running
1. Install Python 3 from python.org. On Windows, tick **Add Python to PATH** during setup.
2. Open the `CyberQuest` folder in Visual Studio Code (File > Open Folder).
3. Open a terminal (Terminal > New Terminal).
4. No packages need installing.
5. Run: `python main.py`

On some Linux systems Tkinter is a separate package: `sudo apt install python3-tk`.

## How to play
- Work through the five stages in the left panel. Each stage unlocks the next.
- Select or type your answer and press the submit button. Read the explanation afterwards.
- Evidence entries (E-01 to E-05) unlock as you reach each stage; findings are added when you finish it.
- **Scoring:** +100 correct first try, +60 correct after a wrong attempt, +100 bonus for finishing
  all stages (max 600). A hint costs 15 points **once per stage** (re-reading it is free). The score
  never goes below zero, and a completed stage cannot award points again.
- After stage 5, press **VIEW FINAL REPORT**.

## Exporting the report
On the report screen press **EXPORT REPORT**. A file named like
`incident_report_NXS-0217_20260101_120000.txt` is created in the `reports/` folder and its path
is shown at the bottom of the screen.

## Running the tests
From the project folder: `python -m unittest discover tests`

## Known limitations
- Designed for desktop screens of about 1000 x 680 or larger. On narrow windows (under about 1120 px)
  the right-hand status panel is hidden; the score is still shown in the dashboard.
- Animations are simple (pulsing indicators, blinking cursor) so the app stays responsive.
- PDF export is not included; the report exports as plain text.
- Only one save slot is used.

## Educational purpose
Teaches phishing awareness, basic cryptography, log analysis, timeline reconstruction and basic
incident response. Every name, address, log and event is fictional (example domains and reserved
documentation IP addresses). The program never touches real systems or the network.
