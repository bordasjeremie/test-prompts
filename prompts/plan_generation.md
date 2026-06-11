Output COMPLETE running plan as valid JSON only. All text in {language}.

Schema:
{"summary":"2-3 para overview","total_weeks":N,"start_date":"YYYY-MM-DD","key_principles":["..."],"warnings":["..."],"weeks":[{"week_number":1,"start_date":"YYYY-MM-DD (Mon)","sessions":[{"date":"YYYY-MM-DD","session_name":"...","session_type":"easy_run|intervals|tempo|long_run|recovery|run_walk","duration_minutes":N,"steps":[{"start_minutes":0,"end_minutes":N,"activity":"MARCHE|EF|TEMPO|INTERVALLES|ACCELERATIONS|PROGRESSIFS","description":"..."}]}]}]}

Activities: MARCHE=walk, EF=easy, TEMPO=sustained hard, INTERVALLES=hard intervals, ACCELERATIONS=strides, PROGRESSIFS=progressive.

Steps: first starts at 0, each start=prev end, last end=duration. No gaps/overlaps. Reps format: "6x 2min INTERVALLES / 2min EF"

Dates: default start=tomorrow, week start=Monday, real YYYY-MM-DD, chronological. 8 weeks maximum. No race date=8-week program.

Templates: Easy(40m):0-40 EF | Intervals(49m):0-12 EF,12-15 PROGRESSIFS,15-39 INTERVALLES,39-49 EF | Tempo(41m):0-12 EF,12-20 TEMPO,20-23 EF,23-31 TEMPO,31-41 EF | Long(60m):0-60 EF

Coaching: warm-up+cool-down always (MARCHE for beginners, EF others). Progress volume OR intensity, not both. Beginner=run/walk, short, conservative. Returning=EF→accelerations→tempo→intervals. Race=all types, taper 1-2 weeks.

Athlete onboarding: {profile_summary}
{goal_summary}

PROFILE: {athlete_profile}
GOAL: {goal}
PLAN: {plan_context}
HEALTH: {healthkit_data}
TRAINING: {training_data}
CONTEXT: {additional_context}
