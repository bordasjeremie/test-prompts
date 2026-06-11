# Modular prompts

Prompts are built by concatenating layers, so each piece can be edited and
recombined independently:

```
final prompt  =  context  +  personality  +  audience add-on  +  feature  (+ variables)
```

```
prompts_modular/
├── context/          # 1. base coach identity (shared by all features)
│   └── base.md
├── personality/      # 2. tone of voice (pick one)
│   ├── tough.md          (Premium)
│   ├── motivating.md     (Free — default)
│   ├── gentle.md         (Free)
│   └── friendly.md       (Premium)
├── audience/         # 3. add-on for app versions targeting a public (optional)
│   ├── beginner.md       [DRAFT]
│   ├── woman.md          [DRAFT]
│   └── trailer.md        [DRAFT]
├── features/         # 4. the task being performed (pick one)
│   ├── casual_conversation.md
│   ├── run_analysis.md   [DRAFT]
│   ├── plan_generation.md
│   └── coach_tips.md
├── prompt_builder.py # build_prompt() concatenates layers + fills variables
└── README.md
```

## Which layers each feature uses

Not every feature uses every layer — this is encoded in `FEATURES` in
`prompt_builder.py`.

| Feature | context | personality | audience | Model | response_format | max_tokens | tools |
|---|:--:|:--:|:--:|---|---|---|---|
| `casual_conversation` | ✅ | ✅ | ✅ | `gpt-4o-mini` | text | default | `start_program_creation` |
| `run_analysis` *(draft)* | ✅ | ✅ | ✅ | `gpt-4o-mini` | text | default | — |
| `plan_generation` | — | — | ✅ | `gpt-4o` | `json_object` | 16000 | — |
| `coach_tips` | ✅ | ✅ | ✅ | `gpt-4o-mini` | `json_object` | 4000 | — |

`plan_generation` is a self-contained JSON generator: in Notion it is a single
`user` message with no personality. We keep it verbatim and only allow the
**audience** add-on (beginner vs trailer changes the plan substantially).

## Usage

```python
from prompt_builder import build_prompt, tools_for

system = build_prompt(
    "casual_conversation",
    personality="motivating",
    audience="beginner",          # or None / "general" for no add-on
    variables={
        "language": "fr",
        "followingProgram": "No active program",
        "athleteProfile": athlete_profile_str,
        "healthkitData": healthkit_str,
        "trainingData": training_str,
    },
)
tools = tools_for("casual_conversation")   # -> [start_program_creation]
```

## Variables (placeholders)

Filled at build time by `build_prompt(..., variables=...)`. Names match the
Notion README exactly.

| Placeholder | Used by | Source |
|---|---|---|
| `{language}` | all | `fr` or `en` |
| `{personality}` | (injected by the personality layer itself) | — |
| `{followingProgram}` | chat, coach_tips | `"Active program: ..."` / `"No active program"` (chat); `true`/`false` (tips) |
| `{athleteProfile}` | chat, run_analysis | Full athlete profile |
| `{healthkitData}` | chat, run_analysis | Subset of the profile |
| `{trainingData}` | all features | Last 8 weeks of runs, formatted, else `N/A` |
| `{tomorrow}` | plan_generation | Next day `YYYY-MM-DD` — the 1st session must land here |
| `{schedulingRule}` | plan_generation | Hard day-of-week rule if the user picked days, else empty |
| `{physicalProfile}` | plan_generation | `Age` / `Sex` / `Weight (kg)` / `Height (cm)` lines, `N/A` if unknown |
| `{goal}` | plan_generation | Chosen goal (preset or free text), else `N/A` |
| `{planContext}` | plan_generation | `Level` / `Terrain` / `Weekly frequency: EXACTLY N...` |
| `{sessionsPerWeek}` | plan_generation | Exact sessions/week (default 3) |
| `{runnerContext}` | coach_tips | `"Experience: <level>, Goal: <goal>"` or `N/A` |
| `{programContext}` | coach_tips | Active-plan block (prev/current/next week), or `No active program` |

### `{schedulingRule}` example (specific days chosen)

```
CRITICAL SCHEDULING RULE (overrides all other date logic): Sessions MUST only fall on: Monday, Wednesday, Friday. No other days allowed. Week 1: Monday 2026-05-28, then Wednesday 2026-05-30, then Friday 2026-06-01. Every subsequent week follows the same Monday, Wednesday, Friday pattern. A session on any other day = INVALID JSON.
```

If the user lets the AI decide, this string is empty.

## Provenance (Notion → files)

| Notion section | File(s) |
|---|---|
| *Prompt — Génération de plan* | `features/plan_generation.md` (verbatim) |
| *Prompt — AI Chat (text)* | `features/casual_conversation.md` + shared parts hoisted to `context/base.md`; tool → `START_PROGRAM_CREATION_TOOL` |
| *Prompt — Coach tips* | `features/coach_tips.md` (verbatim; identity hoisted to `context/base.md`) |
| *Personnalités du coach* | `personality/*.md` (verbatim snippets) |

## Not in Notion yet (drafts — need review)

- **`audience/*` (beginner / woman / trailer)** — the add-on layer for the
  different app versions. Drafted from scratch; review wording and policy
  (especially `woman.md`, which touches cycle/RED-S topics) before shipping.
- **`features/run_analysis.md`** — Notion folds run analysis into the single
  chat prompt. Split here as a dedicated feature; review whether you want it
  separate or merged back into `casual_conversation`.

## Known source conflict

The `friendly` personality says *"Use humor and emoji"*, while the chat /
analysis / coach_tips features say *"No emoji / Never use emojis"*. This
contradiction exists in the Notion source — decide which wins (current feature
text would suppress emojis even for the friendly coach).
