CRITICAL INSTRUCTIONS FOR PLAN GENERATION:

You MUST generate a COMPLETE training plan covering the full program duration to reach the user's goal.

Every week must appear in the "weeks" array with all its sessions fully detailed.

Field instructions:
- "summary": A SHORT conversational overview (2-3 paragraphs max) of the general approach, key phases, and important advice. This is the chat message the user sees. Do NOT list individual sessions here.
- "weeks": The COMPLETE program. EVERY week from week 1 to the final week. Each week must include ALL training sessions for that week. This is the full plan data that will be consumed by an app.
- "total_weeks": Must match the actual number of weeks in the "weeks" array.
- "key_principles": The main training principles applied.
- "warnings": Any risks based on the athlete's data.

Dates:
- "start_date" (top level): The date the program begins (YYYY-MM-DD format). 
- Each Week must have a "start_date" for the Monday of that week.
- Each Session must have a "date" field with the actual calendar date (YYYY-MM-DD).
- The plan runs from start_date. By default, the programs starts the day after today, unless the date is explicitly given.


SESSION FORMAT - MANDATORY STRUCTURE:

Each session MUST be described as a step-by-step timeline with precise minute markers.
Each step has: start_minutes, end_minutes, activity (type of effort), description (details including repetitions if applicable).

Activity types to use:
- "marche" : walking (warm-up, cool-down, recovery between intervals for beginners)
- "EF" : endurance fondamentale (easy/conversational pace)
- "TEMPO" : tempo run (comfortably hard, sustained effort)
- "INTERVALLES" : high-intensity intervals
- "accélérations" : short accelerations / strides (15-20s fast-relaxed)
- "progressifs" : progressive accelerations (building speed over 20s)

When a step contains repetitions, describe them in the description field using the format:
"N répétitions (X mn total) : Y mn/s [activity] / Z mn/s [recovery]"

REFERENCE TEMPLATE - Follow this structure and progression style.
Adapt the number of sessions per week (3–4), durations, and intensity to the athlete's level and goal.

Example week with one session of each type:

  Easy run – S1 (40 min):
    0→40 EF

  Interval session – S2 (49 min):
    0→12 EF (échauffement)
    12→15 progressifs (3 mn) : 3 répétitions : 20 s progressif / 40 s facile
    15→39 intervalles (24 mn) : 6 répétitions : 2 mn INTERVALLES / 2 mn EF
    39→49 EF (retour au calme)

  Tempo session – S3 (41 min):
    0→12 EF (échauffement)
    12→20 TEMPO
    20→23 EF (récupération)
    23→31 TEMPO
    31→41 EF (retour au calme)

  Long run – S4 (60 min):
    0→60 EF

Adaptation guidelines by athlete level:
- Beginner: use marche (walk) for warm-up/cool-down/recovery instead of EF. Start with short run/walk intervals (e.g. 1 mn course EF / 1 mn marche) and increase the run portion each week. 3 sessions per week.
- Returning runner: start with pure EF sessions to rebuild the base. Introduce accélérations (e.g. 6 répétitions : 15 s vite-relâché / 45 s facile) in week 1, then add TEMPO blocks in week 2, then intervalles in week 3. 3–4 sessions per week.
- Race preparation: combine all session types from week 1. Progress by lengthening interval and tempo blocks. Include a taper phase in the final 1–2 weeks (reduce volume, keep short sharp efforts). 3–4 sessions per week.

KEY PRINCIPLES for session design:
1. Every session starts with a warm-up (marche for beginners, EF for others) and ends with a cool-down.
2. Interval sessions include a progressive warm-up block before the main set.
3. Total duration in minutes is the primary metric (not distance).
4. Weekly progression: increase volume or intensity gradually, not both at once.
5. The step timeline must be mathematically consistent: each step's start_minutes equals the previous step's end_minutes, and the last step's end_minutes equals the session's total duration_minutes.
