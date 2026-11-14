# Lecture Notes Assistant AI Agent

## 1. Project Overview

The Lecture Notes Assistant is an AI-powered study assistant that converts lecture materials into structured study notes.

It uses an intelligent agent workflow to plan tasks, select and execute tools, extract important concepts, check information against the original lecture, and generate notes based on the student's preferred detail level.

The system also uses student feedback to adjust the level of detail in future notes.

## 2. Problem Statement

Students often spend considerable time organising lecture materials and identifying important concepts. Manually creating study notes can also make it difficult to maintain consistency and avoid including information that was not covered in the lecture.

This project addresses these problems by developing an AI agent that automates parts of the note-making process while checking generated information against the original lecture material.

## 3. Main Features

- **Task planning:** Creates a sequence of steps based on the student's goal.
- **Topic segmentation:** Divides lecture material into meaningful sections.
- **Concept extraction:** Identifies important terms and definitions.
- **Grounding checks:** Checks whether claims are supported by the lecture.
- **Reflection:** Keeps verified concepts, preserves mentioned concepts without inventing definitions, and drops unsupported concepts.
- **Structured note generation:** Produces notes at different detail levels.
- **Student memory:** Stores feedback and adapts the preferred detail level.
- **Execution trace:** Records agent steps, status, time taken, and details.

## 4. Agent Workflow

1. The student provides a goal and lecture text.
2. The planner creates a sequence of tasks.
3. The agent segments the lecture into topics.
4. The agent extracts important concepts.
5. The grounding tool checks extracted concepts against the source lecture.
6. The reflection stage reviews the results.
7. The agent generates structured notes for each section.
8. Generated claims are checked, and unsupported claims are marked `[unverified]`.
9. The student provides feedback, allowing the memory component to adjust the detail level.
### Planning and Memory

The planner uses the language model to select available tools and arrange them in an execution sequence. If the generated plan is invalid, the system uses a predefined fallback plan.

The student memory component stores the preferred note detail level and feedback history in a JSON file. It supports three detail levels:

- Brief
- Normal
- Detailed

When a student says the notes are too short, the system increases the detail level. When the notes are too long, it decreases the detail level. Positive feedback keeps the current level unchanged.

## 5. Technologies Used

- Python
- Ollama
- Llama 3.2 (3B)
- JSON
- Pytest

## 6. Project Structure

```text
studynotes-agent/
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
- Llama 3.2 (3B) model downloaded

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
pip install ollama pytest
```

Download the language model:

```bash
ollama pull llama3.2:3b
```

Make sure the Ollama service is running.

## 8. Running the Agent

Run the following command from the project root:

```bash
python -m src.agent.agent
```

The agent will process the sample lecture, generate structured study notes, display key concepts, and show its execution trace.

At the end, the student can provide feedback about the note detail level.

## 9. Testing

Run the note-generation tests:

```bash
python -m pytest tests/test_notes.py -v
```

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
- Grounding checks may sometimes accept unsupported claims or reject supported claims.
- The quote-based checker takes longer than the yes/no checker.
- Evaluation currently uses a small sample of 16 claims.
- The current system processes lecture text rather than providing a complete file-upload interface.
The planner can select tools dynamically, but the agent currently supports only a fixed set of execution handlers.
## 12. Future Improvements

- Integrate the quote-based grounding checker into the main agent.
- Expand the evaluation dataset.
- Improve concept extraction and note consistency.
- Add support for PDF lecture uploads.
- Develop a simple user interface.

## 13. Author

Developed as an individual academic project for the DAT404 AI Agent assignment.