
import streamlit as st
from io import BytesIO

from pypdf import PdfReader
from docx import Document

from src.agent.agent import LectureAgent
from src.tools.segmenter import segment_topics


# --------------------------------------------------
# 1. PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Lecture Notes Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Lecture Notes Assistant")

st.write(
    "Upload your lecture and let the AI agent "
    "generate structured study notes."
)


# --------------------------------------------------
# 2. CREATE THE AI AGENT
# --------------------------------------------------

if "agent" not in st.session_state:
    st.session_state.agent = LectureAgent()


# --------------------------------------------------
# 3. EXTRACT TEXT FROM UPLOADED FILES
# --------------------------------------------------

def extract_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        reader = PdfReader(BytesIO(uploaded_file.getvalue()))

        text = ""

        for page in reader.pages:
            text += (page.extract_text() or "") + "\n\n"

        return text

    elif file_name.endswith(".docx"):
        document = Document(BytesIO(uploaded_file.getvalue()))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
        ]

        return "\n\n".join(paragraphs)

    elif file_name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8-sig")

    else:
        raise ValueError("Unsupported file format.")


# --------------------------------------------------
# 4. UPLOAD LECTURE
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload your lecture",
    type=["pdf", "docx", "txt"]
)


# --------------------------------------------------
# 5. GENERATE STUDY NOTES
# --------------------------------------------------

if uploaded_file is not None:

    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Generate Study Notes", type="primary"):

        st.session_state.pop("result", None)
        st.session_state.pop("trace", None)

        try:
            with st.spinner("Reading your lecture file..."):
                lecture_text = extract_text(uploaded_file)

            if not lecture_text.strip():
                st.error(
                    "No readable text was found in this file. "
                    "The PDF may contain scanned images."
                )

            else:
                sections = segment_topics(lecture_text)

                st.write(
                    f"Lecture extracted successfully: "
                    f"{len(lecture_text.split())} words, "
                    f"{len(sections)} sections."
                )

                st.header("Agent Progress")

                progress_bar = st.progress(0)

                progress_message = st.empty()

                def update_progress(
                    completed,
                    total,
                    title,
                    status
                ):
                    """Update the progress bar after each section."""

                    progress_value = (
                        completed / total if total else 0
                    )

                    progress_bar.progress(
                        min(progress_value, 1.0)
                    )

                    if status == "processing":
                        progress_message.info(
                            f"Processing {title} "
                            f"({completed + 1} of {total}). "
                            "This may take a few minutes."
                        )

                    elif status == "completed":
                        progress_message.success(
                            f"Completed {title} "
                            f"({completed} of {total})."
                        )

                    elif status == "failed":
                        progress_message.warning(
                            f"{title} could not be processed. "
                            f"Continuing with the remaining sections."
                        )

                state, trace = st.session_state.agent.run(
                    "Turn this lecture into structured study notes",
                    lecture_text,
                    progress_callback=update_progress
                )

                st.session_state.result = state
                st.session_state.trace = trace

                analysis_step = next(
                    (
                        step for step in trace
                        if step["step"] == "analyze_sections"
                    ),
                    None
                )

                if analysis_step and analysis_step["status"] == "partial":
                    st.warning(
                        "Processing finished, but some sections "
                        "could not be analyzed. Check the execution "
                        "trace below."
                    )

                elif not state["notes"]:
                    st.error(
                        "The agent could not generate study notes. "
                        "Please check the execution trace."
                    )

                else:
                    st.success(
                        "Study notes generated successfully!"
                    )

        except Exception as error:
            st.error(
                f"An error occurred: {type(error).__name__}: {error}"
            )


# --------------------------------------------------
# 6. DISPLAY STUDY NOTES
# --------------------------------------------------

if "result" in st.session_state:

    state = st.session_state.result

    st.header("📝 Study Notes")

    for section in state["notes"]:

        with st.expander(section["title"], expanded=True):
            st.markdown(section["notes"])


    # --------------------------------------------------
    # 7. DISPLAY KEY CONCEPTS
    # --------------------------------------------------

    st.header("🔑 Key Concepts")

    if not state["final_notes"]:
        st.info("No key concepts were extracted.")

    for concept in state["final_notes"]:

        if concept["status"] == "verified":
            st.write(
                f"✅ **{concept['term']}**: "
                f"{concept['definition']}"
            )

        elif concept["status"] == "mentioned":
            st.write(
                f"ℹ️ **{concept['term']}**: "
                f"{concept['definition']}"
            )

        else:
            st.write(
                f"⚠️ **{concept['term']}**: "
                "Not supported by the lecture."
            )


    # --------------------------------------------------
    # 8. DISPLAY EXECUTION TRACE
    # --------------------------------------------------

    st.header("⚙️ Agent Execution Trace")

    for step in st.session_state.trace:

        st.write(
            f"**{step['step']}** | "
            f"Status: {step['status']} | "
            f"Time: {step['seconds']} seconds"
        )

        if step["detail"]:
            st.caption(step["detail"])


    # --------------------------------------------------
    # 9. STUDENT FEEDBACK
    # --------------------------------------------------

    st.header("💬 Student Feedback")

    rating = st.radio(
        "How was the level of detail in the notes?",
        ["too_short", "good", "too_long"],
        format_func=lambda x: x.replace("_", " ").title()
    )

    if st.button("Submit Feedback"):

        st.session_state.agent.give_feedback(rating)

        st.success(
            "Feedback saved! Your agent's detail preference "
            "has been updated."
        )
