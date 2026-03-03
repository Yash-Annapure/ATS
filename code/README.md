# HushHush Recruiter

A simple recruitment platform that automates the process of identifying, shortlisting, and interviewing top developer talent from GitHub, LeetCode, and StackOverflow.

# Project Run Guide: HushHush Recruiter
Follow these steps to set up and run the recruitment platform locally.

### 1. Prerequisites
Python 3.10+
``uv`` (recommended) or ``pip``

### 2. Environment Setup
# Clone the repository
```
git clone <repo-url>
cd bdp-oct25-exam-bdp_oct25_group7
```

# Create and activate a virtual environment and install dependencies
```
uv sync
```
in root dir
``.venv\scripts\activate.bat``

# Create virtual environment and install dependencies (pip)
```
python -m venv .venv
```
source .venv\scripts\activate.bat
```
pip install .
```
### 3. Data & Database Initialisation
```
# Optional: Fetch fresh data (requires GITHUB_TOKEN in .env)
python code\Data_Collectors\simple_github_collector.py
# Initialise the SQLite database from CSVs
python code\database\database.py
# Setup users and assignments tables
python code\backend\setup_db.py
```
4. Launch the Application
You will need two terminal windows open:

## Terminal 1: Backend (FastAPI) (From root Dir)
```
cd code\backend
python main.py
```
## Terminal 2: Frontend (Streamlit)
```
streamlit run code\UI\app.py
```
### 5. Access
```
Frontend: http://localhost:8501
Backend API Docs: http://localhost:8000/docs
Default Credentials:
Recruiter: recruiter1 / admin123
Candidate: student1 / password123
```

## Code Structure & Functionality

The project code is organised into modular components that handle specific stages of the recruitment pipeline:

### 1. Data Collection (`Data_Collectors/`)
Scripts in this directory fetch developer profiles from external platforms to build a talent pool.
*   **Collectors**: Python scripts query APIs for GitHub, LeetCode, and StackOverflow to gather metrics like stars, followers, and problem-solving scores.
*   **Output**: The raw profile data is stored as CSV files in the `Profile_Data/` directory.

### 2. Smart Selection model (`ML/`)
Machine Learning algorithms analyze the collected data to surface the best candidates automatically.
*   **Selection Algorithms**: Scripts in `ML/Selection_Algorithms/` use **K-Means Clustering** to categorize candidates into "Good" or "Bad" groups based on their stats.
*   **Prediction**: Classifiers (like Random Forest and XGBoost) are trained to predict the quality of candidates.
*   **Shortlisting**: The top 10 candidates from each platform are identified and saved to `ML/Shortlisted_candidates/`.

### 3. Database (`database/`)
A central SQLite database (`database.db`) powers the application.
*   **Data Loading**: `database/database.py` reads the CSV files (profiles and shortlisted candidates) and populates the database tables.
*   **Schema**: managed by `backend/setup_db.py`, which sets up tables for Users (recruiters/candidates) and Assignments (interviews).

### 4. Application Layer
The user-facing application consists of a backend API and a frontend dashboard.

*   **Backend (`backend/`)**: Built with **FastAPI**.
    *   `main.py`: Handles API requests, user authentication, and database queries.
    *   **Features**: Manages candidate login, sends email invitations for interviews, and runs candidate code submissions against test cases.

*   **User Interface (`UI/`)**: Built with **Streamlit**.
    *   `app.py`: The main entry point for the web app.
    *   **Recruiter View**: Allows recruiters to browse top candidates and assign coding questions.
    *   **Candidate View**: a simplified IDE where candidates log in, view their assigned question, write code, and submit it for evaluation.

---

# Dependencies
The project relies on the following Python packages:
*   `aiohttp>=3.13.3`
*   `dotenv>=0.9.9`
*   `fastapi>=0.128.0`
*   `httpx>=0.28.1`
*   `imblearn>=0.0`
*   `openpyxl>=3.1.5`
*   `pandas>=2.0.0`
*   `pydantic>=2.12.5`
*   `python-dotenv>=1.2.1`
*   `requests>=2.32.5`
*   `scikit-learn>=1.8.0`
*   `seaborn>=0.13.2`
*   `streamlit>=1.42.0`
*   `streamlit-code-editor>=0.1.0`
*   `uvicorn>=0.40.0`
*   `xgboost>=3.2.0`




