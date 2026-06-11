"""Scenario data layer for the prompt lab.

Loads runner profiles and derives the feature-specific {variables} that
prompt_builder.build_prompt() expects. Keeping this separate from app.py keeps
the UI thin and the variable mapping testable.
"""

import json
from datetime import date, timedelta
from pathlib import Path

PROFILES_DIR = Path(__file__).parent / "profiles"

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_profiles() -> dict[str, dict]:
    """Return {label: profile_dict} for every profile JSON, sorted by label."""
    profiles = {}
    for f in sorted(PROFILES_DIR.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        data["_file"] = f.name
        profiles[data.get("label", f.stem)] = data
    return profiles


def format_training_data(healthkit: dict) -> str:
    """Turn recent_workouts into the formatted block features expect, else N/A."""
    workouts = healthkit.get("recent_workouts", [])
    if not workouts:
        return "N/A"
    lines = []
    for w in workouts:
        parts = [f"{w.get('date', '?')}: {w.get('distance_km', '?')} km"]
        if w.get("duration_minutes") is not None:
            parts.append(f"{w['duration_minutes']} min")
        if w.get("average_pace_min_per_km") is not None:
            parts.append(f"pace {w['average_pace_min_per_km']} min/km")
        if w.get("average_heart_rate_bpm") is not None:
            parts.append(f"avg HR {w['average_heart_rate_bpm']} bpm")
        if w.get("elevation_gain_m") is not None:
            parts.append(f"+{w['elevation_gain_m']} m D+")
        lines.append(" | ".join(parts))
    total_km = sum(w.get("distance_km", 0) for w in workouts)
    lines.append(f"Total: {total_km:.1f} km over {len(workouts)} runs (last 8 weeks)")
    return "\n".join(lines)


def physical_profile_block(physical: dict) -> str:
    """Age / Sex / Weight (kg) / Height (cm) lines, N/A where unknown."""
    rows = [
        ("Age", physical.get("age")),
        ("Sex", physical.get("sex")),
        ("Weight (kg)", physical.get("weight_kg")),
        ("Height (cm)", physical.get("height_cm")),
    ]
    return "\n".join(f"{label}: {value if value is not None else 'N/A'}" for label, value in rows)


def build_scheduling_rule(preferred_days: list[str], tomorrow: date) -> str:
    """Reproduce the Notion {schedulingRule}, or '' if the AI picks the days."""
    if not preferred_days:
        return ""
    ordered = [d for d in WEEKDAYS if d in preferred_days]
    days_str = ", ".join(ordered)
    # First occurrence of each preferred weekday on/after tomorrow.
    first_week = []
    for day in ordered:
        target = WEEKDAYS.index(day)
        delta = (target - tomorrow.weekday()) % 7
        first_week.append((day, tomorrow + timedelta(days=delta)))
    first_week.sort(key=lambda x: x[1])
    seq = ", then ".join(f"{name} {d.isoformat()}" for name, d in first_week)
    return (
        f"\nCRITICAL SCHEDULING RULE (overrides all other date logic): Sessions MUST only "
        f"fall on: {days_str}. No other days allowed. Week 1: {seq}. Every subsequent week "
        f"follows the same {days_str} pattern. A session on any other day = INVALID JSON.\n"
    )


def previous_analysis_block(profile: dict) -> str:
    """Format the prior-analysis snapshot for the evolution section, or note its absence."""
    prev = profile.get("previous_analysis")
    if not prev:
        return "No previous analysis available — this is the first analysis."
    rows = [
        ("Date of previous analysis", prev.get("date")),
        ("Runs per week", prev.get("runs_per_week")),
        ("Longest run (km)", prev.get("longest_run_km")),
        ("Average pace (min/km)", prev.get("average_pace_min_per_km")),
    ]
    return "\n".join(f"{label}: {value}" for label, value in rows if value is not None)


def following_program_text(profile: dict, *, boolean: bool = False) -> str:
    """followingProgram value. coach_tips wants 'true'/'false'; chat wants a sentence."""
    active = bool(profile.get("following_program"))
    if boolean:
        return "true" if active else "false"
    if active and profile.get("program"):
        first_line = profile["program"].splitlines()[0]
        return f"Active program: {first_line}"
    return "Active program" if active else "No active program"


def derive_variables(feature: str, profile: dict, *, language: str,
                     user_message: str = "", today: date | None = None) -> dict:
    """Map a profile onto the {placeholders} a given feature needs."""
    today = today or date.today()
    tomorrow = today + timedelta(days=1)
    healthkit = profile.get("healthkit", {})
    training_data = format_training_data(healthkit)

    common = {"language": language}

    if feature in ("casual_conversation", "run_analysis"):
        return {
            **common,
            "followingProgram": following_program_text(profile),
            "athleteProfile": profile.get("athlete_profile", "N/A"),
            "healthkitData": json.dumps(healthkit, indent=2, ensure_ascii=False),
            "trainingData": training_data,
            "user_message": user_message,
        }

    if feature == "plan_generation":
        n = profile.get("sessions_per_week", 3)
        plan_context = (
            f"Level: {profile.get('level', 'N/A')}\n"
            f"Terrain: {profile.get('terrain', 'N/A')}\n"
            f"Weekly frequency: EXACTLY {n} sessions per week, no more, no less."
        )
        return {
            **common,
            "tomorrow": tomorrow.isoformat(),
            "schedulingRule": build_scheduling_rule(profile.get("preferred_days", []), tomorrow),
            "physicalProfile": physical_profile_block(profile.get("physical", {})),
            "goal": profile.get("goal", "N/A"),
            "planContext": plan_context,
            "trainingData": training_data,
            "sessionsPerWeek": n,
        }

    if feature == "profile_analysis":
        return {
            **common,
            "today": today.isoformat(),
            "followingProgram": following_program_text(profile),
            "athleteProfile": profile.get("athlete_profile", "N/A"),
            "healthkitData": json.dumps(healthkit, indent=2, ensure_ascii=False),
            "trainingData": training_data,
            "previousAnalysis": previous_analysis_block(profile),
        }

    if feature == "coach_tips":
        runner_context = f"Experience: {profile.get('level', 'N/A')}, Goal: {profile.get('goal', 'N/A')}"
        return {
            **common,
            "followingProgram": following_program_text(profile, boolean=True),
            "runnerContext": runner_context,
            "programContext": profile.get("program") or "No active program",
            "trainingData": training_data,
        }

    raise ValueError(f"Unknown feature {feature!r}")
