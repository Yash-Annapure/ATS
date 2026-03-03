import streamlit as st
import os
from services.api import check_backend_status, login_user
from views.candidate import render_candidate_dashboard
from views.recruiter import render_recruiter_dashboard

def attempt_login(role, endpoint):
    st.header(f"{role.capitalize()} Login")
    username = st.text_input("Username", key=f"{role}_user")
    password = st.text_input("Password", type="password", key=f"{role}_pass")
    if st.button(f"Login as {role.capitalize()}"):
        user_data = login_user(username, password, endpoint)
        if user_data:
            st.session_state.update({'logged_in': True, 'role': role, 'username': user_data['username']})
            st.rerun()
        else:
            st.error("Invalid credentials.")

def main():
    st.set_page_config(page_title="HushHush Recruiter", layout="wide")
    
    # Backend Status Indicator
    is_online = check_backend_status()
    status_color = "green" if is_online else "red"
    status_text = "Online" if is_online else "Offline"
    st.sidebar.markdown(f"**Backend Status:** <span style='color:{status_color};'>●</span> {status_text}", unsafe_allow_html=True)
    # Moving Logout to the sidebar
    if st.sidebar.button("Logout", key="logout_btn"):
        st.session_state.clear()
        st.rerun()

    if not st.session_state.get('logged_in'):
        st.title("HushHush Recruiter Portal")
        tab1, tab2 = st.tabs(["Candidate", "Recruiter"])
        with tab1: attempt_login("Candidate", "/login/Candidate")
        with tab2: attempt_login("recruiter", "/login/recruiter")
    else:
        role = st.session_state['role']
        if role == 'Candidate':
            render_candidate_dashboard()
        elif role == 'recruiter':
            render_recruiter_dashboard()
        else:
            st.error("Unknown role")
            if st.button("Reset"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()
