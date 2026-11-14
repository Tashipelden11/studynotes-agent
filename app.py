
import streamlit as st
from pathlib import Path


# --------------------------------------------------
# 1. PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Lecture Notes Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Lecture Notes Assistant")

st.write(
    "An AI agent that turns lecture materials into "
    "structured study notes."
)

st.info(
    "Public demonstration version. The results shown below "
    "are prepared examples, not a live AI-generated response."
)


# --------------------------------------------------
# 2. LOAD SAMPLE LECTURE
# --------------------------------------------------

sample_path = Path("data/sample_lecture.txt")

if sample_path.exists():
    sample_lecture = sample_path.read_text(encoding="utf-8")
else:
    sample_lecture = (
        "Today we start with what an intelligent agent is. "
        "An agent perceives its environment through sensors "
        "and acts on it through actuators."
    )


# --------------------------------------------------
# 3. SAMPLE STUDY NOTES
# --------------------------------------------------

sample_notes = [
    {
        "title": "Intelligent Agents",
        "notes": """
An intelligent agent perceives its environment through
sensors and acts on it through actuators.

The main purpose of an agent is to choose actions to
achieve a goal rather than simply produce output.

Examples include a thermostat and a self-driving car.
"""
    },
    {
        "title": "PEAS Framework",
        "notes": """
PEAS stands for Performance measure, Environment,
Actuators and Sensors.

It helps describe the task environment of an agent.

For a taxi driver agent:
- Performance measure: Safety and speed
- Environment: Roads and traffic
- Actuators: Steering and brakes
- Sensors: Cameras and GPS
"""
    },
    {
        "title": "Types of Environments",
        "notes": """
Environments can be classified in different ways:

- Fully or partially observable
- Deterministic or stochastic
- Static or dynamic

Chess is fully observable and deterministic.
Taxi driving is partially observable and stochastic.

The environment affects the choice of agent architecture.
"""
    },
]


# --------------------------------------------------
# 4. SAMPLE KEY CONCEPTS
# --------------------------------------------------

sample_concepts = [
    {
        "term": "Intelligent Agent",
        "definition": (
            "An agent that perceives its environment through "
            "sensors and acts through actuators."
        ),
        "status": "verified",
    },
    {
        "term": "PEAS",
        "definition": (
            "Performance measure, Environment, Actuators "
            "and Sensors."
        ),
        "status": "verified",
    },
    {
        "term": "Deterministic Environment",
        "definition": (
            "A named environment type mentioned in the lecture."
        ),
        "status": "mentioned",
    },
    {
        "term": "Stochastic Environment",
        "definition": (
            "A named environment type mentioned in the lecture."
        ),
        "status": "mentioned",
    },
]


# --------------------------------------------------
# 5. LECTURE INPUT
# --------------------------------------------------

st.header("Your lecture")

goal = st.text_input(
    "What would you like the agent to do?",
    value="Turn this lecture into structured study notes",
)

lecture_text = st.text_area(
    "Lecture text",
    value=sample_lecture,
    height=250,
)

st.caption(
    "The public demo displays prepared sample results. "
    "New lecture text is not processed by the live AI agent."
)

st.caption("The prepared demonstration results are displayed below.")


# --------------------------------------------------
# 6. DISPLAY STUDY NOTES
# --------------------------------------------------

st.divider()
st.header("Study notes")

for section in sample_notes:
    st.subheader(section["title"])
    st.markdown(section["notes"])


# --------------------------------------------------
# 7. DISPLAY KEY CONCEPTS
# --------------------------------------------------

st.divider()
st.header("Key concepts")

for concept in sample_concepts:
    st.markdown(
        f"**{concept['term']}** "
        f"({concept['status']}): {concept['definition']}"
    )


# --------------------------------------------------
# 8. AGENT EXECUTION TRACE
# --------------------------------------------------

st.divider()
st.header("Agent execution trace")

st.caption(
    "Illustrative trace showing the workflow used by the "
    "actual LectureAgent."
)

trace = [
    {
        "step": "plan",
        "status": "ok",
        "seconds": 0.4,
        "detail": "Planning completed (illustrative)",
    },
    {
        "step": "segment_topics",
        "status": "ok",
        "seconds": 0.8,
        "detail": "Lecture divided into three sections",
    },
    {
        "step": "extract_concepts",
        "status": "ok",
        "seconds": 0.7,
        "detail": "Sample concepts prepared",
    },
    {
        "step": "check_grounding",
        "status": "ok",
        "seconds": 1.0,
        "detail": "Example verification results",
    },
    {
        "step": "reflect",
        "status": "ok",
        "seconds": 0.2,
        "detail": "Example reflection completed",
    },
    {
        "step": "write_notes",
        "status": "ok",
        "seconds": 1.1,
        "detail": "Example notes displayed",
    },
]

st.dataframe(
    trace,
    use_container_width=True,
)


# --------------------------------------------------
# 9. STUDENT FEEDBACK DEMONSTRATION
# --------------------------------------------------

st.divider()
st.header("Give feedback")

rating = st.radio(
    "How was the level of detail?",
    ["too_short", "good", "too_long"],
    horizontal=True,
)

if st.button("Submit feedback"):

    if rating == "too_short":
        st.success(
            "Demo feedback received. "
            "The local agent can increase note detail."
        )

    elif rating == "too_long":
        st.success(
            "Demo feedback received. "
            "The local agent can reduce note detail."
        )

    else:
        st.success(
            "Demo feedback received. "
            "The current level of detail is suitable."
        )


# --------------------------------------------------
# 10. PROJECT INFORMATION
# --------------------------------------------------

st.divider()
st.header("About this project")

st.write(
    """
    This project demonstrates an AI agent for helping
    students prepare lecture notes.

    The actual local agent uses:
    - Planning
    - Tool execution
    - Student memory
    - Feedback and adaptation
    - Reflection
    - Grounding verification

    The fully working AI version runs locally using Ollama.
    """
)
