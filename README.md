# SmartHire-AI

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Choose your license and add a LICENSE file -->
[![Powered by CrewAI](https://img.shields.io/badge/Powered%20by-CrewAI-blueviolet)](https://crewai.com/)

SmartHire-AI is an intelligent recruitment assistant powered by [CrewAI](https://crewai.com). It leverages a team of specialized AI agents to automate and streamline the initial stages of the hiring process, from analyzing job descriptions and parsing CVs to matching candidates and scheduling interviews.

## Overview

Finding the right talent can be time-consuming. SmartHire-AI aims to accelerate this by:

1.  **Analyzing Job Descriptions:** Extracting key requirements, skills, and responsibilities.
2.  **Parsing Resumes/CVs:** Structuring candidate information for easy comparison.
3.  **Performing Market Research:** Providing context like salary benchmarks for the role.
4.  **Matching Candidates:** Scoring candidates based on their fit with the job description.
5.  **Automating Initial Outreach:** Scheduling interviews with shortlisted candidates.

This project uses a multi-agent system built with CrewAI, where each agent has a specific role and collaborates to achieve the overall hiring goals.

## Workflow

The core process involves the following steps orchestrated by the CrewAI framework:

1.  **Job Analysis:** The `jd_analyzer` agent reads the job description file (`.csv` in the example) and extracts key criteria.
2.  **CV Parsing:** The `cv_parser` agent reads the candidate's CV file (`.pdf` in the example) and extracts structured information.
3.  **Market Research:** The `market_researcher` agent uses the JD analysis to research salary benchmarks and industry trends using search tools.
4.  **Matching:** The `matching_agent` compares the structured data from the JD and CV, calculating a match score and providing justification.
5.  **Scheduling:** If the match score meets a threshold, the `scheduler_agent` drafts an interview request email (sending requires tool setup).



![smarthire ai](https://github.com/user-attachments/assets/9af187cc-0aa4-46c4-a01a-c7f5c039471c)

## Technology Stack

*   **Python:** >=3.10, <3.13
*   **CrewAI:** Framework for orchestrating autonomous AI agents.
*   **CrewAI Tools:** Pre-built tools like `FileReadTool`, `SerperDevTool`.
*   **UV:** Fast Python package installer and resolver (used by `crewai install`).
*   **LLMs:** Designed to work with models like OpenAI's GPT series or local models via Ollama (e.g., Mistral 7B as configured in `crew.py`).
*   **YAML:** For configuring agents and tasks.
*   **SQLite:** For storing execution results (`main.py` implementation).

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/BalajiMittapalli/SmartHire-AI.git
    cd SmartHire-AI
    ```

2.  **Install UV (if you don't have it):**
    ```bash
    pip install uv
    ```

3.  **Install Dependencies:** Navigate to the `hireai` sub-directory and use the `crewai` command (which utilizes UV):
    ```bash
    cd hireai
    crewai install
    # Or alternatively, directly using uv:
    # uv pip sync pyproject.toml
    ```

4.  **Configure Environment Variables:**
    *   Create a `.env` file inside the `hireai` directory (`hireai/.env`).
    *   Add your API keys:
        ```dotenv
        # Required by CrewAI core or specific tools, even if using local LLM primarily
        OPENAI_API_KEY="sk-..."

        # Required for the Market Researcher agent's SerperDevTool
        SERPER_API_KEY="your_serper_api_key"

        # Add other keys if needed for different LLMs or tools (e.g., email)
        ```

5.  **(Optional) Local LLM Setup:** The current configuration in `hireai/src/hireai/crew.py` points to `ollama/mistral:7b`. If you intend to use this, ensure you have [Ollama](https://ollama.ai/) installed and running with the `mistral:7b` model pulled (`ollama pull mistral:7b`). You can change the `llm` parameter in `crew.py` to use different local or cloud models supported by CrewAI.

## Running the Crew

1.  Make sure you are in the `hireai` directory:
    ```bash
    # If you are in the root SmartHire-AI directory:
    cd hireai
    ```

2.  Execute the crew:
    ```bash
    crewai run
    ```

*   This command runs the process defined in `hireai/src/hireai/main.py`.
*   By default, it uses the sample job descriptions in `hireai/data/job_description.csv` and a sample CV (e.g., `hireai/data/CVs1/C1627.pdf` as per the `main.py` code). You can modify `main.py` to change the default input files.
*   The output logs the agent actions and final results to the console.
*   The `main.py` script also saves results to `output.txt` and `results.db` within the `hireai` directory.

