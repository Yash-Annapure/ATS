# Doodle ATS+
 
# Introduction
In the following project, we have built a basic ATS (Applicant Tracking System) that can be used by recruiters to find suitable candidates for a job opening. The ATS is built using Python and uses various API's to collect data from different sources (Github, leetcode, Stackoverflow) and then use machine learning algorithms to find the best candidates for a job opening. The entire CI/CD Pipeline is supplemented by Github Actions and its UI/UX has been created via Streamlit, further complemented by a Robust FastAPI backend to connect our UI/UX to our SQL lite database. Providing a seamless experience for recruiters to find suitable candidates for a job opening while keeping them in the loop.

# Demo Video
Watch the full system demo here: [Demo Video](https://drive.google.com/file/d/1HetH6fcVtkEV6-ELXB0Fpc2kAZBvF476/view?usp=sharing)
 
# Recruiter View

The **Recruiter Dashboard** is the central hub for managing the hiring process. It offers several key functionalities designed to simplify candidate selection.

### 1. Top Candidates Dashboard
*   **What it is**: A smart list of automatically shortlisted candidates.
*   **How it works**: Our system analyzes data from GitHub, LeetCode, and StackOverflow to find high-performing developers. You can select a platform (e.g., "GitHub") to see the top-rated candidates based on metrics like stars, followers, and reputation.
*   **Action**: From this view, you can directly select a candidate and assign them a technical interview by email.
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/097738cd-cf2c-4a7f-b204-423fef5fef5b" />


### 2. Candidate Management
*   **What it is**: A complete database of all potential candidates.
*   **How it works**: Browsable lists of candidates from all supported platforms. You can view key details like usernames and profile scores to make informed decisions.
*   **Action**: Like the dashboard, you can initiate the interview process from here by email.
<img width="1918" height="1078" alt="recruiter_dash" src="https://github.com/user-attachments/assets/fce28c51-a460-4327-b08a-1a210e2389e5" />


### 3. Interview Assignment & Email Automation
*   **What it is**: A streamlined workflow to assign coding tests.
*   **How it works**: 
    1.  Select a candidate and a coding question from our question bank.
    2.  Enter the candidate's email address.
    3.  The system automatically creates a secure account for the candidate and sends them an **email invitation** containing their username, password, and a link to the test portal(currently its a placeholder as localhost).
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/0e01a09e-76c5-42d1-a8d9-346866465014" />


### 4. Submission Review
*   **What it is**: A dedicated interface to evaluate candidate performance.
*   **How it works**: Once a candidate submits their code, you can see:
    *   The code they wrote.
    *   Whether it passed the test cases (Accepted/Rejected).
    *   Their execution score and the runtime metrics.
    *   A detailed execution log.
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/d0e57253-6205-4ab4-9f26-08e2eb2009c8" />


### 5. Pipeline Automation
*   **What it is**: A control panel for data freshness.
*   **How it works**: You can trigger **GitHub Actions** workflows directly from the UI to fetch new data from sources (GitHub/LeetCode/StackOverflow) or retrain the machine learning models.
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/b9f8fcd5-8254-4d1d-b29a-eb36e7cd7fe1" />


---

# Candidate View
 
The **Candidate Portal** provides a mock coding environment for developers to prove their skills.

### 1. Candidate Login
*   Candidates receive unique credentials via email from the recruiter.
*   They use these to log into the assessment portal.
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/f0df7685-eb38-4755-877a-0aab54ff833a" />


### 2. Interview & Coding Interface
*   **Question Display**: Candidates see the problem statement, examples, and constraints clearly displayed.
*   **Code Editor**: A built-in code editor allows them to write their solution in Python.
*   **Mock Execution**: Before submitting, candidates can "run" their code against sample test cases to check for errors and verify logic.
<img width="1916" height="1078" alt="candidate_dashboard" src="https://github.com/user-attachments/assets/c5856698-f9c5-4c6b-b126-a7b1794fa4cc" />


### 3. Submission
*   Once confident, the candidate submits their final solution.
*   The system immediately evaluates the code against hidden test cases and records the result for the recruiter to review.
<img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/9b3fccbd-4b0e-435f-95a6-5579b19f7e33" />


---

# Key Technology Stack
*   **Frontend**: Built with **Streamlit** for a responsive and clean user interface.
*   **Backend**: Powered by **FastAPI** for high-performance data handling.
*   **Database**: Uses **SQLite** for efficient, lightweight data storage.
*   **Data Processing**: **Pandas** is used for all data manipulation and analysis.
*   **Infrastructure**: **GitHub Actions** handles automation, and **uv** enables fast dependency management.

# For in-depth code analysis refer the readme in code folder
Please refer to [code/README.md](https://github.com/Big-Data-Programming/bdp-oct25-exam-bdp_oct25_group7/blob/CICD_Testing/code/README.md) for technical deep-dives and implementation details.



