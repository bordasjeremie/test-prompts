"""Modular prompt builder.

Final prompt = context  +  personality  +  audience add-on  +  feature  (+ variables).

Each feature declares which layers it uses (see FEATURES). Layers are read from
the sibling sub-folders and concatenated in a fixed order, then {placeholders}
are filled.

    from prompt_builder import build_prompt, FEATURES, START_PROGRAM_CREATION_TOOL

    system = build_prompt(
        "casual_conversation",
        personality="motivating",
        audience="beginner",
        variables={
            "language": "fr",
            "followingProgram": "No active program",
            "athleteProfile": "...",
            "healthkitData": "...",
            "trainingData": "...",
        },
    )
"""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent

# Layers are concatenated in this order.
LAYER_ORDER = ("context", "personality", "audience", "feature")

# Per-feature wiring: which layers apply + the OpenAI call parameters from Notion.
FEATURES = {
    "casual_conversation": {
        "layers": ("context", "personality", "audience", "feature"),
        "context": "base",
        "model": "gpt-4o-mini",
        "response_format": None,                      # plain text
        "max_tokens": None,                           # OpenAI default
        "tools": ["start_program_creation"],
    },
    "run_analysis": {                                  # DRAFT — split out of the chat prompt
        "layers": ("context", "personality", "audience", "feature"),
        "context": "base",
        "model": "gpt-4o-mini",
        "response_format": None,
        "max_tokens": None,
        "tools": [],
    },
    "plan_generation": {
        "layers": ("audience", "feature"),             # self-contained JSON generator; no personality
        "context": "base",
        "model": "gpt-4o",
        "response_format": {"type": "json_object"},
        "max_tokens": 16000,
        "tools": [],
    },
    "coach_tips": {
        "layers": ("context", "personality", "audience", "feature"),
        "context": "base",
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "max_tokens": 4000,
        "tools": [],
    },
}

# Personalities available (id -> tier). 'motivating' is the Free default.
PERSONALITIES = {
    "tough": "premium",
    "motivating": "free",      # default
    "gentle": "free",
    "friendly": "premium",
}
DEFAULT_PERSONALITY = "motivating"

# Audience add-ons. None / "general" means no add-on layer.
AUDIENCES = ("beginner", "woman", "trailer")

# Tool definition (function calling) used by the conversational chat feature.
START_PROGRAM_CREATION_TOOL = {
    "type": "function",
    "function": {
        "name": "start_program_creation",
        "description": "Start the training program creation flow when the user wants to create, plan, or generate a running program.",
        "parameters": {"type": "object", "properties": {}},
    },
}


def _read(*parts: str) -> str:
    return (PROMPTS_DIR.joinpath(*parts).with_suffix(".md")).read_text(encoding="utf-8").strip()


def build_prompt(feature: str, *, personality: str | None = None,
                 audience: str | None = None, variables: dict | None = None) -> str:
    """Concatenate the layers for `feature` and fill {placeholders}."""
    if feature not in FEATURES:
        raise ValueError(f"Unknown feature {feature!r}. Known: {list(FEATURES)}")
    cfg = FEATURES[feature]
    layers = cfg["layers"]

    personality = personality or DEFAULT_PERSONALITY
    if audience in (None, "general"):
        audience = None

    parts: list[str] = []
    if "context" in layers:
        parts.append(_read("context", cfg["context"]))
    if "personality" in layers:
        parts.append(_read("personality", personality))
    if "audience" in layers and audience is not None:
        parts.append(_read("audience", audience))
    if "feature" in layers:
        parts.append(_read("features", feature))

    prompt = "\n\n".join(parts)

    for key, value in (variables or {}).items():
        prompt = prompt.replace(f"{{{key}}}", str(value))
    return prompt


def tools_for(feature: str) -> list[dict]:
    """Return the OpenAI `tools` list for a feature (empty if none)."""
    registry = {"start_program_creation": START_PROGRAM_CREATION_TOOL}
    return [registry[name] for name in FEATURES[feature].get("tools", [])]


if __name__ == "__main__":
    # Quick smoke test: print every feature built with sample layers.
    for feat in FEATURES:
        print("=" * 30, feat, "=" * 30)
        print(build_prompt(
            feat,
            personality="motivating",
            audience="beginner",
            variables={"language": "English"},
        ))
        print()
