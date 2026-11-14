# Lecture Notes Assistant AI Agent

## 1. Project Overview

The Lecture Notes Assistant is an AI-powered study assistant that converts lecture materials into structured study notes.

It uses an intelligent agent workflow to plan tasks, select and execute tools, extract important concepts, check information against the original lecture, and generate notes based on the student's preferred detail level.

The application also uses student feedback to adjust the level of detail in future notes.

## 2. Problem Statement

Students often spend considerable time organising lecture materials and identifying important concepts. Manually creating study notes can also make it difficult to maintain consistency and avoid including information that was not covered in the lecture.

This project addresses these problems by developing an AI agent that helps automate the note-making process while checking generated information against the original lecture material.

## 3. Main Features

- **Task planning:** Creates a sequence of steps based on the student's goal.
- **Topic segmentation:** Divides lecture material into meaningful sections.
- **Concept extraction:** Identifies important terms and definitions.
- **Grounding checks:** Checks whether generated claims are supported by the lecture.
- **Reflection:** Reviews extracted concepts and their supporting information.
- **Structured note generation:** Produces notes at different detail levels.
- **Student memory:** Stores feedback and adapts the preferred detail level.
- **File upload:** Supports PDF, DOCX and TXT lecture materials in the local application.
- **Execution trace:** Records agent steps, status, processing time and details.
- **Feedback:** Allows students to provide feedback about the generated notes.

## 4. Agent Workflow

1. The student uploads lecture material and selects a goal.
2. The application extracts the lecture text.
3. The planner creates a sequence of tasks.
4. The agent segments the lecture into topics.
5. The agent extracts important concepts.
6. The grounding tool checks extracted concepts against the source lecture.
7. The reflection stage reviews the results.
8. The agent generates structured notes for each section.
9. Generated claims are checked, and unsupported claims are marked `[unverified]`.
10. The student provides feedback, allowing the memory component to adjust the preferred detail level.

### Planning and Memory

The planner uses the language model to select available tools and arrange them in an execution sequence. If the generated plan is invalid, the system uses a predefined fallback plan.

The student memory component stores the preferred note detail level and feedback history in a JSON file.

It supports three detail levels:

- Brief
- Normal
- Detailed

When a student says the notes are too short, the system increases the detail level. When the notes are too long, it decreases the detail level. Positive feedback keeps the current level unchanged.

## 5. Technologies Used

- Python
- Streamlit
- Ollama
- Qwen 2.5 (1.5B)
- PyPDF
- Python-docx
- JSON
- Pytest

## 6. Project Structure

```text
studynotes-agent/
│
├── app.py
├── local_app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── sample_lecture.txt
│   └── student_memory.json
│
├── eval/
│   ├── grounding_cases.json
│   ├── results_quote-check-v1.json
│   ├── results_yesno-v0.json
│   └── run_grounding_eval.py
│
├── src/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── llm.py
│   │   ├── notes.py
│   │   └── planner.py
│   │
│   ├── memory/
│   │   └── student_memory.py
│   │
│   └── tools/
│       ├── concepts.py
│       ├── grounding.py
│       ├── registry.py
│       └── segmenter.py
│
└── tests/
    └── test_notes.py
```

## 7. Installation and Setup

### Prerequisites

- Python 3.10 or later
- Ollama installed
- Qwen 2.5 (1.5B) model downloaded

### Steps

Clone the repository:

```bash
git clone https://github.com/Tashipelden11/studynotes-agent.git
cd studynotes-agent
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Download the language model:

```bash
ollama pull qwen2.5:1.5b
```

Make sure the Ollama service is running before starting the application.

## 8. Running the Application

### Actual AI Application (Local)

Run:

```bash
streamlit run local_app.py
```

Open the local URL displayed in the terminal.

Upload a PDF, DOCX or TXT lecture file. The agent will process the lecture and generate structured study notes, key concepts and an execution trace.

This version uses the locally installed Ollama model.

### Public Demonstration

The public demonstration is available at:

https://studynotes-agent-huusw2azl5adokkdjbf62q.streamlit.app/

It displays prepared example results to demonstrate the application's interface and workflow. It does not perform live AI processing.

## 9. Testing

Run the tests:

```bash
python -m pytest -v
```

The tests check selected note-generation and grounding-related functions.

## 10. Grounding Evaluation

The project includes two grounding-checking approaches:

- `yesno-v0`: Uses a simple supported/not-supported response.
- `quote-check-v1`: Requires supporting evidence quoted from the lecture.

Evaluation on 16 test cases produced:

| Checker | Accuracy | Average time |
|---|---:|---:|
| yesno-v0 | 87.5% | 1.3 seconds |
| quote-check-v1 | 93.75% | 3.0 seconds |

The quote-based checker achieved higher accuracy in this test, but it was slower.

Run the evaluation:

```bash
python -m eval.run_grounding_eval
```

**Note:** The current main agent's tool registry uses `yesno-v0`. The quote-based checker is evaluated separately and has not yet replaced the main agent's checker.

## 11. Limitations

- The quality of generated notes depends on the language model.
- Processing time depends on the computer's hardware and the size of the lecture.
- Grounding checks may sometimes accept unsupported claims or reject supported claims.
- Exact-match reflection checks do not guarantee that every extracted concept is semantically correct.
- Evaluation currently uses a small sample of 16 claims.
- The actual AI application currently runs locally using Ollama. The public version is a demonstration rather than a live AI service.

## 12. Future Improvements

- Improve concept extraction and note consistency.
- Improve semantic grounding verification.
- Expand the grounding evaluation dataset.
- Improve processing speed.
- Develop a hosted version that supports live AI processing.

## 13. Author

Developed as an individual academic project for the DAT404 AI Agent assignment.
