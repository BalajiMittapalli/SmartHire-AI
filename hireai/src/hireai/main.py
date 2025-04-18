#!/usr/bin/env python
import sys
import sqlite3
import os
import json 
from dotenv import load_dotenv 

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import sys
import warnings

# from datetime import datetime # No longer needed for default inputs

from src.hireai.crew import Hireai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run(cv_file_path):
    """
    Run the crew with the specified CV file path.
    """
    if not cv_file_path:
        raise ValueError("A CV file path must be provided to the run function.")

    # ensure UTF‑8 output
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    inputs = {
        'jd_file_path': 'hireai/data/job_description.csv',
        'cv_file_path': cv_file_path
    }

    try:
        print(f"Running crew with inputs: {inputs}")
        crew = Hireai().crew()
        result1 = crew.kickoff(inputs=inputs)

        # Store in SQLite (unchanged)
        conn = sqlite3.connect('results.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results
              (task TEXT, input TEXT, result TEXT)
        ''')
        cursor.execute(
            "INSERT INTO results VALUES (?, ?, ?)",
            ("kickoff1", str(inputs), str(result1))
        )
        conn.commit()
        conn.close()

        # --- BEGIN CHANGED: use Pydantic to serialize result1 properly ---
        try:
            # Pydantic v2+
            serial = result1.model_dump()
        except Exception:
            try:
                # Pydantic v1 fallback
                serial = result1.dict()
            except Exception:
                # Last resort: raw text or string
                raw = getattr(result1, 'raw', None)
                serial = {'raw': raw if raw is not None else str(result1)}
        # --- END CHANGED ---

        # Extract CV file name
        cv_file_name = os.path.basename(inputs['cv_file_path'])

        # Extract matching score and email from tasks output
        matching_score = None
        email = None
        for task_output in serial.get('tasks_output', []):
            if task_output.get('name') == 'matching_task':
                raw_output = task_output.get('raw', '')
                if raw_output:
                    try:
                        matching_score = float(raw_output.split(':')[1].split('.')[0])
                    except:
                        matching_score = None
            elif task_output.get('name') == 'schedule_interview_task':
                raw_output = task_output.get('raw', '')
                if raw_output:
                    try:
                        email = raw_output.split(' ')[3].replace('.', '')
                    except:
                        email = None

        output_data = {
            "inputs": inputs,
            "cv_file_name": cv_file_name,
            "matching_score": matching_score,
            "email": email,
            "result": serial  # **CHANGED** renamed from full_result_dump
        }

        # Append to results.json (unchanged)
        OUT = 'results.json'
        if os.path.exists(OUT):
            with open(OUT, 'r+', encoding='utf-8') as f:
                try:
                    all_results = json.load(f)
                except json.JSONDecodeError:
                    all_results = []
                all_results.append(output_data)
                f.seek(0)
                json.dump(all_results, f, indent=2, ensure_ascii=False)
                f.truncate()
        else:
            with open(OUT, 'w', encoding='utf-8') as f:
                json.dump([output_data], f, indent=2, ensure_ascii=False)

        print(f"Result appended to {OUT}")

    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while running the crew: {e}")

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Hireai().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Hireai().crew().replay(task_id=sys.argv[1])

    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    # TODO: Update test inputs if needed
    inputs = {
        'jd_file_path': 'hireai/data/job_description.csv',
        'cv_file_path': 'hireai/data/CVs1/C1061.pdf'
    }
    try:
        Hireai().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {e}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "train":
            # Ensure correct number of arguments for train
            if len(sys.argv) < 4:
                 print("Usage: python main.py train <n_iterations> <filename>")
                 sys.exit(1)
            train()
        elif command == "replay":
             # Ensure correct number of arguments for replay
            if len(sys.argv) < 3:
                 print("Usage: python main.py replay <task_id>")
                 sys.exit(1)
            replay()
        elif command == "test":
             # Ensure correct number of arguments for test
            if len(sys.argv) < 4:
                 print("Usage: python main.py test <n_iterations> <openai_model_name>")
                 sys.exit(1)
            test()
        else:
            print(f"Invalid command: {command}. Use 'train', 'replay', or 'test'.")
            sys.exit(1)
    else:
        # Default behavior: Prompt user to select a CV file
        cv_dir = 'hireai/data/CVs1'
        try:
            cv_files = sorted([f for f in os.listdir(cv_dir) if f.lower().endswith('.pdf')])
        except FileNotFoundError:
            print(f"Error: CV directory not found at '{cv_dir}'")
            sys.exit(1)

        if not cv_files:
            print(f"No PDF CV files found in '{cv_dir}'")
            sys.exit(1)

        print("\nAvailable CV files:")
        for i, filename in enumerate(cv_files):
            print(f"{i + 1}. {filename}")

        selected_cv_path = None
        while not selected_cv_path:
            try:
                choice = input(f"Enter the number of the CV file to process (1-{len(cv_files)}): ")
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(cv_files):
                    selected_cv_filename = cv_files[choice_index]
                    # Construct path using os.path.join and ensure forward slashes for consistency
                    selected_cv_path = os.path.join(cv_dir, selected_cv_filename).replace('\\', '/')
                else:
                    print("Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except EOFError:
                 print("\nOperation cancelled by user.")
                 sys.exit(0)


        print(f"\nProcessing selected CV: {selected_cv_path}")
        run(cv_file_path=selected_cv_path)
