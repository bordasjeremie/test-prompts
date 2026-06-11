from enum import Enum

from pydantic import BaseModel


class GoalType(str, Enum):
    race = "race"
    fitness = "fitness"
    unknown = "unknown"


class PlanIntake(BaseModel):
    """Result of analyzing the conversation to check if enough info exists to generate a plan."""
    goal_type: GoalType
    race_date: str | None = None
    race_distance: str | None = None
    missing_info: list[str]
    follow_up_question: str | None = None
    ready_to_generate: bool


class SessionStep(BaseModel):
    """A single timed block within a session timeline."""
    start_minutes: int
    end_minutes: int
    activity: str
    description: str


class Session(BaseModel):
    date: str
    day: str
    session_number: str
    workout_type: str
    duration_minutes: float
    steps: list[SessionStep]
    notes: str | None = None


class Week(BaseModel):
    week_number: int
    start_date: str
    phase: str
    focus: str
    sessions: list[Session]
    rest_days: list[str]


class TrainingPlan(BaseModel):
    summary: str
    goal: str
    start_date: str
    total_weeks: int
    weeks: list[Week]
    key_principles: list[str]
    warnings: list[str]
