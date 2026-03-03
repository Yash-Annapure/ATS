from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
import os
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS Middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Path
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/database.db')

# Email Configuration
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_NAME = os.getenv('SENDER_NAME')

def send_email_notification(candidate_username, candidate_email, candidate_password):
    subject = "Invitation to Attempt Online Coding Interview Test"
    # Note: Adjust URL port if needed (Streamlit default is 8501)
    email_template = """
Dear {username},

We are pleased to inform you that you are a potential candidate for our company Doodle.
We invite you to attempt an online coding interview test.

Use the username '{username}' to login.
Your password has been set as '{candidate_password}' during assignment.

Please click on the following link to start the test:
Link: http://localhost:8501

Best regards,
The Doodle Team
"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f'{SENDER_NAME} <{SENDER_EMAIL}>'
        msg['To'] = candidate_email
        msg['Subject'] = subject

        body = email_template.format(username=candidate_username, candidate_password=candidate_password)
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp-relay.brevo.com', 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {candidate_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


class UserLogin(BaseModel):
    username: str
    password: str

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"message": "HushHushRecruiter Backend is Running"}

@app.post("/login/Candidate")
def login_Candidate(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = 'Candidate'", (user.username, user.password))
    user_record = cursor.fetchone()
    conn.close()

    if user_record:
        return {"status": "success", "role": "Candidate", "username": user.username}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or incorrect role")

@app.post("/login/recruiter")
def login_recruiter(user: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND role = 'recruiter'", (user.username, user.password))
    user_record = cursor.fetchone()
    conn.close()

    if user_record:
        return {"status": "success", "role": "recruiter", "username": user.username}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials or incorrect role")

# --- Recruiter Features ---

@app.get("/candidates/{platform}")
def get_candidates(platform: str):
    """
    Fetch candidate profiles from the specified platform table.
    Valid platforms: 'GitHub', 'LeetCode', 'StackOverflow'
    """
    # Mapping friendly names to Database Table names
    platform_mapping = {
        'GitHub': 'Git_hub',
        'LeetCode': 'Leet_code',
        'StackOverflow': 'Stack_overflow'
    }
    
    if platform not in platform_mapping:
        raise HTTPException(status_code=400, detail="Invalid platform. Use: GitHub, LeetCode, StackOverflow")

    db_table_name = platform_mapping[platform]

    try:
        conn = get_db_connection()
        # Using pandas to easily read SQL and convert to JSON compatible dict
        df = pd.read_sql(f"SELECT * FROM {db_table_name}", conn)
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/top_candidates/{platform}")
def get_top_candidates(platform: str):
    """
    Fetch top candidate profiles from the specified platform table.
    Valid platforms: 'GitHub', 'LeetCode', 'StackOverflow'
    """
    # Mapping friendly names to Database Table names (Shortlisted)
    platform_mapping = {
        'GitHub': 'top_github',
        'LeetCode': 'top_leetcode',
        'StackOverflow': 'top_stackoverflow'
    }
    
    if platform not in platform_mapping:
        raise HTTPException(status_code=400, detail="Invalid platform. Use: GitHub, LeetCode, StackOverflow")

    db_table_name = platform_mapping[platform]

    try:
        conn = get_db_connection()
        # Using pandas to easily read SQL and convert to JSON compatible dict
        df = pd.read_sql(f"SELECT * FROM {db_table_name}", conn)
        conn.close()
        
        # Handle NaN values
        df = df.astype(object).where(pd.notnull(df), None)
        
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class QuestionPayload(BaseModel):
    candidate_username: str
    question_text: str

@app.post("/send_questions")
def send_questions(payload: QuestionPayload):
    """
    Mock endpoint to simulate sending questions to a candidate.
    In a real app, this would trigger an email or notification.
    """
    # Simulate processing
    print(f"Sending question to {payload.candidate_username}: {payload.question_text}")
    return {"status": "success", "message": f"Question sent to {payload.candidate_username}"}

@app.get("/stats")
def get_stats():
    """
    Returns the count of candidates for each platform.
    """
    stats = {}
    platforms = {
        'GitHub': 'Git_hub',
        'LeetCode': 'Leet_code',
        'StackOverflow': 'Stack_overflow'
    }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for name, table in platforms.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[name] = count
    except Exception as e:
        print(f"Error fetching stats: {e}")
    finally:
        conn.close()
        
    return stats

    return stats

# --- Question Assignment Features ---

SAMPLE_QUESTIONS = [
    {
        "id": 101, 
        "title": "Two Sum", 
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}
        ],
        "test_cases": [
            {"args": [[2,7,11,15], 9], "expected": [0,1]},
            {"args": [[3,2,4], 6], "expected": [1,2]},
            {"args": [[3,3], 6], "expected": [0,1]}
        ]
    },
    {
        "id": 102, 
        "title": "Reverse Linked List", 
        "description": "Given the head of a singly linked list, reverse the list, and return the reversed list. (Note: For this mock, input is just a list)",
        "examples": [
            {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]"}
        ],
        "test_cases": [
            {"args": [[1,2,3,4,5]], "expected": [5,4,3,2,1]},
            {"args": [[1,2]], "expected": [2,1]},
            {"args": [[]], "expected": []}
        ]
    },
    {
        "id": 103, 
        "title": "Valid Parentheses", 
        "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
        "examples": [
            {"input": "s = '()'", "output": "true"},
            {"input": "s = '()[]{}'", "output": "true"},
            {"input": "s = '(]'", "output": "false"}
        ],
        "test_cases": [
            {"args": ["()"], "expected": True},
            {"args": ["()[]{}"], "expected": True},
            {"args": ["(]"], "expected": False}
        ]
    },
    {
        "id": 104, 
        "title": "Merge Intervals", 
        "description": "Given an array of intervals where intervals[i] = [start, end], merge all overlapping intervals.",
        "examples": [
             {"input": "intervals = [[1,3],[2,6],[8,10],[15,18]]", "output": "[[1,6],[8,10],[15,18]]"}
        ],
        "test_cases": [
             {"args": [[[1,3],[2,6],[8,10],[15,18]]], "expected": [[1,6],[8,10],[15,18]]},
             {"args": [[[1,4],[4,5]]], "expected": [[1,5]]}
        ]
    },
    {
        "id": 105, 
        "title": "Maximum Subarray", 
        "description": "Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        "examples": [
            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6"}
        ],
        "test_cases": [
            {"args": [[-2,1,-3,4,-1,2,1,-5,4]], "expected": 6},
            {"args": [[1]], "expected": 1},
            {"args": [[5,4,-1,7,8]], "expected": 23}
        ]
    }
]

@app.get("/questions")
def get_sample_questions():
    """Returns the list of sample questions."""
    return SAMPLE_QUESTIONS

class RunCodePayload(BaseModel):
    code: str
    question_id: int

def execute_code(code: str, question_id: int):
    """
    Helper function to execute code against test cases.
    Returns a dict with status, output, score, total_test_cases.
    """
    import sys
    import io
    import traceback

    # 1. Find the question
    question = next((q for q in SAMPLE_QUESTIONS if q["id"] == question_id), None)
    if not question:
        return {"status": "error", "output": "Question not found.", "score": 0, "total": 0}
    
    # 2. Prepare execution environment
    local_scope = {}
    
    # Capture stdout
    captured_stdout = io.StringIO()
    # We save the original stdout to restore it later, just in case
    original_stdout = sys.stdout
    sys.stdout = captured_stdout

    try:
        # 3. Execute the user's code definition
        exec(code, {}, local_scope)
        
        if "solution" not in local_scope:
             return {"status": "error", "output": "Function 'solution' not found. Please define 'def solution(...):'.", "score": 0, "total": len(question.get("test_cases", []))}
        
        user_func = local_scope["solution"]
        
        # 4. Run against test cases
        test_cases = question.get("test_cases", [])
        total_cases = len(test_cases)
        passed_count = 0
        results = []
        all_passed = True
        
        for i, case in enumerate(test_cases):
            args = case["args"]
            expected = case["expected"]
            
            try:
                # Call function
                result = user_func(*args)
                
                # Check correctness
                if result == expected:
                    results.append(f"Test Case {i+1}: Passed")
                    passed_count += 1
                else:
                    all_passed = False
                    results.append(f"Test Case {i+1}: Failed\n   Input: {args}\n   Expected: {expected}\n   Got: {result}")
                    # Construct detailed error for the first failure
                    return {
                        "status": "error", 
                        "output": f"Wrong Answer on Test Case {i+1}\nInput: {args}\nOutput: {result}\nExpected: {expected}",
                        "score": passed_count,
                        "total": total_cases
                    }
                    
            except Exception as e:
                return {
                    "status": "error", 
                    "output": f"Runtime Error on Test Case {i+1}:\n{str(e)}",
                    "score": passed_count,
                    "total": total_cases
                }

        # If we get here, all passed
        runtime_ms = 35 # Mock runtime for now
        memory_mb = 14.2 # Mock memory
        
        success_msg = f"Accepted\nAll {len(test_cases)} test cases passed!\nRuntime: {runtime_ms}ms\nMemory: {memory_mb}MB"
        return {"status": "success", "output": success_msg, "score": passed_count, "total": total_cases}

    except SyntaxError as e:
        return {"status": "error", "output": f"Syntax Error: {e.msg} at line {e.lineno}", "score": 0, "total": 0}
    except Exception as e:
        return {"status": "error", "output": f"Execution Error: {str(e)}", "score": 0, "total": 0}
    finally:
        sys.stdout = original_stdout # Restore stdout

@app.post("/run_code")
def run_code(payload: RunCodePayload):
    """
    Executes user code against test cases.
    """
    result = execute_code(payload.code, payload.question_id)
    # The endpoint expects just status and output for now, but we can return more if needed
    return result

class AssignmentPayload(BaseModel):
    recruiter_username: str
    candidate_username: str
    question_id: int
    question_title: str
    question_id: int
    question_title: str
    candidate_password: str  # Mandatory now
    email: str # Mandatory now


@app.post("/assign_question")
def assign_question(payload: AssignmentPayload):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Save Assignment
        cursor.execute(
            "INSERT INTO assignments (recruiter_id, candidate_username, question_id, question_title) VALUES (?, ?, ?, ?)",
            (payload.recruiter_username, payload.candidate_username, payload.question_id, payload.question_title)
        )
        
        # 2. Create User (Mandatory now)
        user_created_msg = ""
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (payload.candidate_username, payload.candidate_password, 'Candidate')
            )
            user_created_msg = " and user account created"
        except sqlite3.IntegrityError:
            # Update password if user exists? Or just ignore. Use new password for login.
             cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (payload.candidate_password, payload.candidate_username)
            )
             user_created_msg = " (user account updated)"

        # 3. Send Email
        email_sent = send_email_notification(payload.candidate_username, payload.email, payload.candidate_password)
        email_msg = " | Email sent" if email_sent else " | Email failed"

        conn.commit()
        return {"status": "success", "message": f"Assigned '{payload.question_title}' to {payload.candidate_username}{user_created_msg}{email_msg}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/recruiter_assignments/{username}")
def get_recruiter_assignments(username: str):
    conn = get_db_connection()
    try:
        # Fetch all columns including submitted_code, outcome, score, etc.
        df = pd.read_sql("SELECT * FROM assignments WHERE recruiter_id = ?", conn, params=(username,))
        # Handle NaN values which are not JSON compliant
        df = df.astype(object).where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/my_assignments/{username}")
def get_my_assignments(username: str):
    conn = get_db_connection()
    try:
        # Using pandas to easily get dict list
        df = pd.read_sql("SELECT * FROM assignments WHERE candidate_username = ?", conn, params=(username,))
        # Handle NaN values which are not JSON compliant
        df = df.astype(object).where(pd.notnull(df), None)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

class SubmissionPayload(BaseModel):
    username: str
    question_id: int
    assignment_id: int
    code: str

@app.post("/submit_solution")
def submit_solution_endpoint(payload: SubmissionPayload):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if already completed using assignment_id
        cursor.execute(
            "SELECT status, candidate_username FROM assignments WHERE id = ?",
            (payload.assignment_id,)
        )
        row = cursor.fetchone()
        
        if not row:
             return {"status": "error", "message": "Assignment not found"}
        
        # Verify ownership
        if row['candidate_username'] != payload.username:
             return {"status": "error", "message": "Unauthorized: buffer mismatch"}
             
        if row['status'] == 'Completed':
             return {"status": "error", "message": "Assignment already submitted. You cannot resubmit."}

        # Execute code to get results
        exec_result = execute_code(payload.code, payload.question_id)
        
        outcome = "Passed" if exec_result["status"] == "success" else "Failed"
        if exec_result["status"] == "error" and "Runtime Error" in exec_result["output"]:
            outcome = "Error"
            
        # Update status to 'Completed' and store results
        cursor.execute(
            """
            UPDATE assignments 
            SET status = 'Completed',
                submitted_code = ?,
                outcome = ?,
                score = ?,
                total_test_cases = ?,
                execution_log = ?
            WHERE id = ?
            """,
            (
                payload.code, 
                outcome, 
                exec_result.get("score", 0), 
                exec_result.get("total", 0), 
                exec_result.get("output", ""),
                payload.assignment_id
            )
        )
        conn.commit()
        
        return {
            "status": "success", 
            "message": "Solution submitted", 
            "execution_result": exec_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
