import streamlit as st
import datetime
from services.api import fetch_my_assignments, fetch_questions

def render_assignment_list():
    st.subheader("My Assignments")
    assignments = fetch_my_assignments(st.session_state['username'])
    
    if assignments:
        # Fetch question details to display names and difficulty (mocked)
        questions = fetch_questions()
        
        # Create a table-like structure
        for task in assignments:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{task['question_title']}**")
                # Find desc
                desc = next((q['description'] for q in questions if q['id'] == task['question_id']), "Solve this problem...")
                st.caption(desc[:100] + "...")
            with col2:
                 status = task.get('status', 'Pending')
                 if status == 'Completed':
                     st.write(f"Status: {status} ✅")
                 else:
                     st.write(f"Status: {status}")
            with col3:
                if status == 'Completed':
                    st.button("Completed ✅", key=f"solve_{task['id']}", disabled=True)
                else:
                    if st.button("Solve Challenge", key=f"solve_{task['id']}"):
                        st.session_state['active_assignment'] = task
                        st.session_state['active_question'] = next((q for q in questions if q['id'] == task['question_id']), None)
                        st.session_state['candidate_view'] = 'editor'
                        st.session_state['start_time'] = datetime.datetime.now()
                        st.session_state['end_time'] = st.session_state['start_time'] + datetime.timedelta(minutes=30)
                        st.session_state['time_expired'] = False # Reset timer flag
                        st.rerun()
            st.divider()
    else:
        st.info("You have no pending assignments.")
