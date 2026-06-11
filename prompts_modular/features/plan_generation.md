Generate a COMPLETE running training plan as valid JSON only. No markdown, no explanations.

Output this exact structure:
{
  "title": "Short catchy program name (3-5 words, e.g. 'Programme Semi-Marathon Débutant')",
  "summary": "2-3 paragraph overview of approach and progression",
  "total_weeks": N,
  "start_date": "YYYY-MM-DD",
  "key_principles": ["string"],
  "warnings": ["string"],
  "weeks": [{
    "week_number": 1,
    "start_date": "YYYY-MM-DD",
    "sessions": [{
      "date": "YYYY-MM-DD",
      "session_name": "string",
      "session_type": "easy_run|intervals|tempo|long_run|recovery|run_walk",
      "duration_minutes": N,
      "steps": [{
        "start_minutes": 0,
        "end_minutes": N,
        "activity": "MARCHE|EF|TEMPO|INTERVALLES|ACCELERATIONS|PROGRESSIFS",
        "description": "string"
      }]
    }]
  }]
}

Activity labels: MARCHE=walk, EF=easy run, TEMPO=sustained hard, INTERVALLES=hard intervals, ACCELERATIONS=short strides, PROGRESSIFS=progressive accelerations.

Timeline rules: first step starts at 0, each start_minutes = previous end_minutes, last end_minutes = duration_minutes. No gaps, no overlaps.

CRITICAL DATE RULE: The very first session MUST be on {tomorrow}. The plan start_date MUST be {tomorrow}. Each week's start_date is the date of its first session. All dates real YYYY-MM-DD, chronological. total_weeks = length of weeks array.
{schedulingRule}
Repetitions in description: "6 reps: 2 min INTERVALLES / 2 min EF"

Reference sessions:
- Easy run (40 min): 0-40 EF
- Intervals (49 min): 0-12 EF | 12-15 PROGRESSIFS (3x 20s prog/40s easy) | 15-39 INTERVALLES (6x 2min hard/2min EF) | 39-49 EF
- Tempo (41 min): 0-12 EF | 12-20 TEMPO | 20-23 EF | 23-31 TEMPO | 31-41 EF
- Long run (60 min): 0-60 EF

Coaching:
- Every session: warm-up + cool-down. Beginners use MARCHE for warm-up/recovery, others use EF.
- Progressive load: increase volume or intensity, not both at once.
- Beginner: run/walk, short sessions, conservative start.
- Returning: rebuild with EF, add accelerations then tempo then intervals.
- Race prep: mix all types, race-specific work, taper final 1-2 weeks.

USER PROFILE:
{physicalProfile}

GOAL:
{goal}

PLAN CONTEXT:
{planContext}

TRAINING DATA:
{trainingData}

MANDATORY: Every week MUST contain exactly {sessionsPerWeek} sessions. A week with fewer is INVALID JSON.

Always respond in {language}.

Output valid JSON only.
