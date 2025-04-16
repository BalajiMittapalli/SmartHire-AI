#!/usr/bin/env python
import sys
import sqlite3
import os
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

def run(cv_file_path=None):
    """
    Run the crew.
    """
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # TODO: Replace with actual paths to your JD and CV files
    inputs = {
        'jd_file_path': 'hireai/data/job_description.csv',
        'cv_file_path': cv_file_path or 'hireai/data/CVs1/C1061.pdf'
    }
    
    try:
        print(f"Running crew with inputs: {inputs}")
        crew = Hireai().crew()
        result1 = crew.kickoff(inputs=inputs)
        # Store result in SQLite database
        conn = sqlite3.connect('results.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS results
                          (task TEXT, input TEXT, result TEXT)''')
        cursor.execute("INSERT INTO results VALUES (?, ?, ?)",
                       ("kickoff1", str(inputs), str(result1)))
        conn.commit()
        conn.close()
        # Write result to output.txt
        with open('output.txt', 'a', encoding='utf-8') as f:
            f.write(f"kickoff1 result: {str(result1)}\n")
        print(f"kickoff1 result: {str(result1)}")

        result2 = crew.kickoff(inputs=inputs)
        # Store result in SQLite database
        conn = sqlite3.connect('results.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO results VALUES (?, ?, ?)",
                       ("kickoff2", str(inputs), str(result2)))
        conn.commit()
        conn.close()
        # Write result to output.txt
        with open('output.txt', 'a', encoding='utf-8') as f:
            f.write(f"kickoff2 result: {str(result2)}\n")
        print(f"kickoff2 result: {str(result2)}")
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
        if sys.argv[1] == "train":
            train()
        elif sys.argv[1] == "replay":
            replay()
        elif sys.argv[1] == "test":
            test()
        else:
            print("Invalid argument. Use 'train', 'replay', or 'test'.")
    else:
        run(cv_file_path='hireai/data/CVs1/C1627.pdf')
