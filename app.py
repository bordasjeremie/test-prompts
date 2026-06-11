"""Running Coach — Prompt Scenario Lab.

A testing harness for the modular prompt system. Assemble a scenario from:
    prompt family (feature)  +  tone (personality)  +  audience add-on  +  user profile
then run it against OpenAI and inspect the assembled prompt and the model output.
"""

import json
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from openai import OpenAI

import scenarios

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "prompts_modular"))
from prompt_builder import (  # noqa: E402  (path injected above)
    build_prompt,
    tools_for,
    FEATURES,
    PERSONALITIES,
    AUDIENCES,
    DEFAULT_PERSONALITY,
)

load_dotenv()

import os  # noqa: E402


def default_api_key() -> str:
    """Resolve the OpenAI key from Streamlit secrets (cloud) or the env (.env, local)."""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:  # noqa: BLE001 — no secrets.toml present (e.g. local run)
        pass
    return os.getenv("OPENAI_API_KEY", "")


def _expected_password() -> str:
    """The gate password, from Streamlit secrets (cloud) or the env (local). Empty = no gate."""
    try:
        if "APP_PASSWORD" in st.secrets:
            return st.secrets["APP_PASSWORD"]
    except Exception:  # noqa: BLE001 — no secrets.toml present (e.g. local run)
        pass
    return os.getenv("APP_PASSWORD", "")


def check_password() -> bool:
    """Render a password gate. Returns True once the correct password is entered.

    If no APP_PASSWORD is configured (secrets or env), the gate is disabled and
    the app is open — handy for local development.
    """
    expected = _expected_password()
    if not expected:
        return True
    if st.session_state.get("password_ok"):
        return True

    st.title("🔒 Running Coach — Prompt Lab")
    entered = st.text_input("Password", type="password", key="password_input")
    if entered:
        if entered == expected:
            st.session_state.password_ok = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


# --- UI labels ---------------------------------------------------------------

FEATURE_LABELS = {
    "casual_conversation": "💬 Casual conversation (chat)",
    "run_analysis": "📊 Run analysis",
    "plan_generation": "🗓️ Training plan generation",
    "coach_tips": "💡 Coach tips",
}

PERSONALITY_LABELS = {
    "tough": "Tough — drill sergeant (Premium)",
    "motivating": "Motivating — mentor (Free, default)",
    "gentle": "Gentle — encourager (Free)",
    "friendly": "Friendly — running buddy (Premium)",
}

AUDIENCE_LABELS = {
    "general": "General (no add-on)",
    "beginner": "Beginner",
    "woman": "Woman",
    "trailer": "Trail runner",
}

# Which message role the built prompt is sent as, and whether a chat user turn applies.
TEXT_FEATURES = {"casual_conversation", "run_analysis"}
USER_ROLE_FEATURES = {"plan_generation"}  # whole prompt sent as a user message


# --- OpenAI helpers ----------------------------------------------------------

def call_openai(client, model, messages, *, response_format=None, max_tokens=None, tools=None):
    kwargs = {"model": model, "messages": messages}
    if response_format:
        kwargs["response_format"] = response_format
    if max_tokens:
        kwargs["max_completion_tokens"] = max_tokens
    if tools:
        kwargs["tools"] = tools
    return client.chat.completions.create(**kwargs)


def update_token_usage(usage):
    if usage:
        tu = st.session_state.token_usage
        tu["prompt"] += usage.prompt_tokens
        tu["completion"] += usage.completion_tokens
        tu["total"] += usage.total_tokens


# --- Output renderers --------------------------------------------------------

def render_plan(plan: dict):
    st.subheader(plan.get("title", "Training plan"))
    st.caption(f"{plan.get('total_weeks', '?')} weeks · starts {plan.get('start_date', '?')}")
    if plan.get("summary"):
        st.markdown(plan["summary"])
    if plan.get("key_principles"):
        st.markdown("**Key principles**")
        for p in plan["key_principles"]:
            st.markdown(f"- {p}")
    for w in plan.get("warnings", []):
        st.warning(w)
    for week in plan.get("weeks", []):
        with st.expander(f"Week {week.get('week_number', '?')} — starts {week.get('start_date', '?')}"):
            for s in week.get("sessions", []):
                st.markdown(
                    f"**{s.get('session_name', 'Session')}** "
                    f"({s.get('date', '?')}) · {s.get('session_type', '?')} · "
                    f"{s.get('duration_minutes', '?')} min"
                )
                rows = [
                    {
                        "From (min)": step.get("start_minutes"),
                        "To (min)": step.get("end_minutes"),
                        "Activity": step.get("activity"),
                        "Details": step.get("description"),
                    }
                    for step in s.get("steps", [])
                ]
                if rows:
                    st.table(rows)
    with st.expander("Raw JSON"):
        st.json(plan)


def render_tips(tips: dict):
    sections = [("home", "🏠 Home"), ("program", "🗓️ Program"), ("run", "🏃 Run"), ("stats", "📈 Stats")]
    cols = st.columns(4)
    for col, (key, title) in zip(cols, sections):
        with col:
            st.markdown(f"**{title}**")
            for m in tips.get(key, []):
                st.info(m)
    with st.expander("Raw JSON"):
        st.json(tips)


# --- Scenario execution ------------------------------------------------------

def run_scenario(client, model, feature, system_prompt, user_message):
    """Execute one scenario and render the output. Returns nothing; renders inline."""
    cfg = FEATURES[feature]
    response_format = cfg.get("response_format")
    max_tokens = cfg.get("max_tokens")
    tools = tools_for(feature)

    if feature in USER_ROLE_FEATURES:
        messages = [{"role": "user", "content": system_prompt}]
    elif feature == "coach_tips":
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate the JSON object now."},
        ]
    else:  # text chat features
        turn = user_message.strip() or "Please analyze my recent running and training."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": turn},
        ]

    completion = call_openai(
        client, model, messages,
        response_format=response_format,
        max_tokens=max_tokens,
        tools=tools or None,
    )
    update_token_usage(completion.usage)
    msg = completion.choices[0].message

    # Tool call (casual_conversation -> start_program_creation)
    if getattr(msg, "tool_calls", None):
        names = ", ".join(tc.function.name for tc in msg.tool_calls)
        st.success(f"🛠️ Model called tool(s): **{names}** → the app would open the program creation flow.")
        if msg.content:
            st.markdown(msg.content)
        return

    content = msg.content or ""

    if response_format and response_format.get("type") == "json_object":
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            st.error(f"Model did not return valid JSON: {e}")
            st.code(content)
            return
        if feature == "plan_generation":
            render_plan(data)
            (ROOT / "program.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            st.caption("Saved to program.json")
        elif feature == "coach_tips":
            render_tips(data)
        else:
            st.json(data)
    else:
        st.markdown(content)


# --- App ---------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Running Coach — Prompt Lab", page_icon="🏃", layout="wide")

    if not check_password():
        return

    if "token_usage" not in st.session_state:
        st.session_state.token_usage = {"prompt": 0, "completion": 0, "total": 0}

    profiles = scenarios.load_profiles()

    # --- Sidebar: Configuration ---
    with st.sidebar:
        st.header("Configuration")

        api_key = st.text_input(
            "OpenAI API Key",
            value=default_api_key(),
            type="password",
        )

        st.divider()
        st.header("Token Usage")
        tu = st.session_state.token_usage
        st.metric("Prompt tokens", tu["prompt"])
        st.metric("Completion tokens", tu["completion"])
        st.metric("Total tokens", tu["total"])
        if st.button("Reset token counter"):
            st.session_state.token_usage = {"prompt": 0, "completion": 0, "total": 0}
            st.rerun()

    # --- Main: Scenario builder ---
    st.title("🏃 Running Coach — Prompt Scenario Lab")
    st.caption("Assemble a scenario: **prompt family + tone + audience + profile**, then run it.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        feature = st.selectbox(
            "Prompt family (feature)",
            list(FEATURES.keys()),
            format_func=lambda f: FEATURE_LABELS.get(f, f),
        )
    cfg = FEATURES[feature]
    uses_personality = "personality" in cfg["layers"]
    uses_audience = "audience" in cfg["layers"]

    with c2:
        personality = st.selectbox(
            "Tone (personality)",
            list(PERSONALITIES.keys()),
            index=list(PERSONALITIES.keys()).index(DEFAULT_PERSONALITY),
            format_func=lambda p: PERSONALITY_LABELS.get(p, p),
            disabled=not uses_personality,
            help=None if uses_personality else "plan_generation does not use a personality layer.",
        )
    with c3:
        audience = st.selectbox(
            "Audience add-on",
            ["general"] + list(AUDIENCES),
            format_func=lambda a: AUDIENCE_LABELS.get(a, a),
            disabled=not uses_audience,
        )
    with c4:
        profile_label = st.selectbox("User profile", list(profiles.keys()))

    profile = profiles[profile_label]

    # Model comes from the feature definition; language comes from the profile.
    model = cfg["model"]
    language = profile.get("language", "en")

    # Scenario summary line
    rf = cfg.get("response_format")
    rf_str = rf["type"] if rf else "text"
    tool_names = ", ".join(cfg.get("tools", [])) or "—"
    st.markdown(
        f"**Scenario:** `{feature}` · tone `{personality if uses_personality else '—'}` · "
        f"audience `{audience if uses_audience else '—'}` · profile **{profile_label}** "
        f"({language})  \n"
        f"**Call:** model `{model}` · format `{rf_str}` · "
        f"max_tokens `{cfg.get('max_tokens') or 'default'}` · tools `{tool_names}`"
    )

    # User message (chat features only)
    user_message = ""
    if feature in TEXT_FEATURES:
        user_message = st.text_area(
            "User message",
            value=profile.get("default_user_message", ""),
            height=110,
            help="The runner's chat message. For run analysis this is optional.",
        )

    # Build the prompt
    variables = scenarios.derive_variables(feature, profile, language=language, user_message=user_message)
    system_prompt = build_prompt(
        feature,
        personality=personality,
        audience=audience if uses_audience else None,
        variables=variables,
    )

    with st.expander("🔍 Assembled prompt", expanded=False):
        st.code(system_prompt, language="markdown")
    with st.expander("🧩 Filled variables", expanded=False):
        st.json({k: v for k, v in variables.items()})

    # Run
    run = st.button("▶ Run scenario", type="primary")

    st.divider()
    st.subheader("Output")

    if run:
        if not api_key:
            st.warning("Enter your OpenAI API key in the sidebar to run.")
            return
        client = OpenAI(api_key=api_key)
        try:
            with st.spinner(f"Running {feature} on {model}…"):
                run_scenario(client, model, feature, system_prompt, user_message)
        except Exception as e:  # noqa: BLE001 — surface any API error in the UI
            st.error(f"Run failed: {e}")
    else:
        st.caption("Configure a scenario above and press **Run scenario**.")


if __name__ == "__main__":
    main()
