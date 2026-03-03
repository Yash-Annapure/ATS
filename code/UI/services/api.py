import requests
import os
import streamlit as st

# Backend URL (default to localhost for local dev, overridden by env var in prod)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def check_backend_status():
    try:
        response = requests.get(BACKEND_URL, timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def login_user(username, password, endpoint):
    try:
        response = requests.post(
            f"{BACKEND_URL}{endpoint}",
            json={"username": username, "password": password}
        )
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError:
        st.error("Backend unavailable.")
        return None

def fetch_candidates(platform):
    """Helper to fetch candidate lists from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/candidates/{platform}")
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        st.error(f"Failed to fetch {platform} data.")
        return []

def fetch_top_candidates(platform):
    """Fetch top candidates list for a specific platform."""
    try:
        response = requests.get(f"{BACKEND_URL}/top_candidates/{platform}")
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        st.error(f"Failed to fetch top candidates for {platform}.")
        return []

def fetch_questions():
    """Fetch sample questions."""
    try:
        return requests.get(f"{BACKEND_URL}/questions").json()
    except:
        return []

def assign_question(recruiter, candidate, question_dict, email, password):
    """Call backend to assign question."""
    payload = {
        "recruiter_username": recruiter,
        "candidate_username": str(candidate),
        "question_id": question_dict['id'],
        "question_title": question_dict['title'],
        "email": email,
        "candidate_password": password
    }
    try:
        res = requests.post(f"{BACKEND_URL}/assign_question", json=payload)
        return res.status_code == 200
    except:
        return False

def fetch_stats():
    try:
        stats = requests.get(f"{BACKEND_URL}/stats").json()
        return stats
    except:
        return None

def fetch_my_assignments(username):
    try:
        return requests.get(f"{BACKEND_URL}/my_assignments/{username}").json()
    except:
        return None

def fetch_recruiter_assignments(username):
    try:
        return requests.get(f"{BACKEND_URL}/recruiter_assignments/{username}").json()
    except:
        return None

def run_code_mock(code, question_id):
    """
    Mock execution of code.
    In real world: this would send code to backend, which runs it in a sandbox.
    """
    try:
        # We will implement this endpoint in the backend shortly.
        payload = {"code": code, "question_id": question_id}
        res = requests.post(f"{BACKEND_URL}/run_code", json=payload)
        if res.status_code == 200:
            return res.json()
        else:
            return {"status": "error", "output": "Failed to communicate with execution server."}
    except Exception as e:
        return {"status": "error", "output": str(e)}

def submit_solution(username, question_id, assignment_id, code):
    try:
        payload = {"username": username, "question_id": question_id, "assignment_id": assignment_id, "code": code}
        res = requests.post(f"{BACKEND_URL}/submit_solution", json=payload)
        
        if res.status_code != 200:
            st.error(f"Backend Error ({res.status_code}): {res.text}")
            return {"status": "error", "message": res.text}
            
        return res.json()
    except Exception as e:
        st.error(f"Request Failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def trigger_workflow(token, owner, repo, workflow_id, inputs):
    """
    Triggers a GitHub Actions workflow dispatch event.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Targeting main branch as requested
    data = {"ref": "main", "inputs": inputs}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 204:
            return True, "Workflow triggered successfully!"
        else:
            return False, f"Failed: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"
