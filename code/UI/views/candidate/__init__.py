import streamlit as st
from .dashboard import render_assignment_list
from .submission import render_code_editor

def render_candidate_dashboard():
    # Initialize session state for candidate view navigation
    if 'candidate_view' not in st.session_state:
        st.session_state['candidate_view'] = 'list'
    if 'time_expired' not in st.session_state:
        st.session_state['time_expired'] = False
    
    st.markdown(f"<h1 class='dashboard-title'>Candidate Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='font-size: 2rem; font-weight: 300;'>Welcome, <span style='color: #FF4B4B;'>{st.session_state['username']}</span>!</h2>", unsafe_allow_html=True)
    st.divider()

    if st.session_state['candidate_view'] == 'list':
        render_assignment_list()
    elif st.session_state['candidate_view'] == 'editor':
        render_code_editor()
