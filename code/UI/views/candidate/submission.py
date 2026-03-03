import streamlit as st
import datetime
import time
import streamlit.components.v1 as components
from code_editor import code_editor
from services.api import run_code_mock, submit_solution

def render_code_editor():
    task = st.session_state.get('active_assignment')
    question = st.session_state.get('active_question')
    
    if not task or not question:
        st.error("No active assignment found.")
        if st.button("Back to Dashboard"):
            st.session_state['candidate_view'] = 'list'
            st.rerun()
        return

    # Check lockout
    if task.get('status') == 'Completed':
        st.error("This assignment has already been completed.")
        if st.button("Back to Dashboard"):
            st.session_state['candidate_view'] = 'list'
            st.rerun()
        return

    # --- Header with Timer (JS-based) ---
    col_header, col_timer = st.columns([3, 1])
    with col_header:
        if st.button("← Back to List"):
            st.session_state['candidate_view'] = 'list'
            st.rerun()
    
    with col_timer:
        remaining = st.session_state['end_time'] - datetime.datetime.now()
        seconds_left = int(remaining.total_seconds())
        
        if seconds_left <= 0:
             st.error("Time's Up! Submitting implementation...")
             st.session_state['time_expired'] = True
             
             # Attempt to submit current code if available
             # Auto-submit if not already done
             current_code = st.session_state.get(f"code_{task['id']}")
             if current_code:
                 result = submit_solution(st.session_state['username'], question['id'], task['id'], current_code)
                 if result and result.get('status') == 'success':
                     exec_res = result.get('execution_result', {})
                     score = exec_res.get('score', 0)
                     total = exec_res.get('total', 0)
                     
                     st.success(f"Time's Up! Assignment Auto-Submitted. Score: {score}/{total}")
                     time.sleep(3)
                     st.session_state['candidate_view'] = 'list'
                     st.rerun()
        else:
             # JavaScript Real-time Timer
             timer_html = f"""
                <div style="
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-family: 'Source Sans Pro', sans-serif;
                    margin-top: 10px;
                ">
                    <div style="
                        font-size: 1.5rem; 
                        font-weight: 600; 
                        color: #333; 
                        background-color: white;
                        padding: 8px 16px;
                        border-radius: 8px;
                        border: 1px solid #e0e0e0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    ">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF4B4B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        <span id="timer_display" style="color: #31333F; font-feature-settings: 'tnum'; font-variant-numeric: tabular-nums;">Loading...</span>
                    </div>
                </div>
                <script>
                    var timeleft = {seconds_left};
                    
                    function updateTimer() {{
                        var minutes = Math.floor(timeleft / 60);
                        var seconds = timeleft % 60;
                        
                        // Pad with leading zeros
                        minutes = minutes < 10 ? '0' + minutes : minutes;
                        seconds = seconds < 10 ? '0' + seconds : seconds;
                        
                        document.getElementById("timer_display").innerHTML = minutes + ":" + seconds;
                        
                        // Change color when low on time
                        if(timeleft < 300) {{ // less than 5 mins
                             document.getElementById("timer_display").style.color = "#FF4B4B";
                        }}

                        if(timeleft <= 0){{
                            document.getElementById("timer_display").innerHTML = "00:00";
                            // You could verify with backend here if needed
                        }}
                        timeleft -= 1;
                    }}
                    
                    // Run immediately then every second
                    updateTimer();
                    var downloadTimer = setInterval(updateTimer, 1000);
                </script>
             """
             components.html(timer_html, height=80)

    # --- Split View ---
    col_left, col_right = st.columns([4, 6])
    
    with col_left:
        # Problem Description Panel
        st.markdown(f"### {question['title']}")
        st.info(f"Difficulty: Medium") # Mock
        st.markdown("#### Description")
        st.write(question['description'])
        
        st.markdown("#### Examples")
        # Display examples if available, else show generic
        examples = question.get('examples', [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"}
        ])
        
        for i, ex in enumerate(examples):
             st.markdown(f"**Example {i+1}:**")
             st.code(f"Input: {ex['input']}\nOutput: {ex['output']}")
        
        st.markdown("#### Constraints")
        st.markdown("- `2 <= nums.length <= 10^4`")
        st.markdown("- `-10^9 <= nums[i] <= 10^9`")

    with col_right:
        # Code Editor Panel
        st.markdown("#### Code Editor")
        
        default_code = f"# Write your solution for {question['title']} here:\ndef solution():\n    pass"
        current_code = st.session_state.get(f"code_{task['id']}", default_code)
        
        # LeetCode-style configuration
        # Define buttons for the editor bar
        custom_buttons = [
            {"name": "Run", "feather": "Play", "primary": True, "hasText": True, "showWithIcon": True, "commands": ["submit"], "style": {"bottom": "0.44rem", "right": "0.4rem"}}
        ]

        editor_response = code_editor(
            current_code,
            lang="python",
            height="600px", # Fixed height in pixels to avoid vh issues
            theme="monokai", 
            key=f"editor_{task['id']}",
            options={"wrap": True, "fontSize": 14},
            buttons=custom_buttons
        )
        
        # Update code in session state
        if editor_response['text'] != current_code:
             st.session_state[f"code_{task['id']}"] = editor_response['text']
             code = editor_response['text']
        else:
             code = current_code

        evt_type = editor_response.get('type')
        
        if evt_type == "Run" or evt_type == "submit":
            if st.session_state.get('time_expired', False):
                st.warning("Time is up!")
            else:
                with st.spinner("Running..."):
                    result = run_code_mock(code, question['id'])
                    st.session_state['run_output'] = result

        elif evt_type == "Submit":
             st.warning("Please use the 'Submit Solution' button below.")

        # Native Submit Button
        col_fb1, col_fb2 = st.columns([1, 4])
        with col_fb1:
            if st.button("Submit Solution", type="primary"):
                 if st.session_state.get('time_expired', False):
                    st.error("Time is up! Cannot submit.")
                 else:
                    confirm_submission(st.session_state['username'], question['id'], task['id'], code)
        
        # Output Console
        if 'run_output' in st.session_state:
            res = st.session_state['run_output']
            st.markdown("#### Output")
            if res.get('status') == 'success':
                 st.success(res.get('output', 'Passed'))
            else:
                 st.error(res.get('output', 'Error'))

@st.dialog("Confirm Submission")
def confirm_submission(username, question_id, assignment_id, code):
    st.write("Are you sure you want to submit? You cannot attempt this question again after submitting.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel"):
            st.rerun()
    with col2:
        if st.button("Confirm Submit", type="primary"):
            result = submit_solution(username, question_id, assignment_id, code)
            if result and result.get('status') == 'success':
                exec_res = result.get('execution_result', {})
                score = exec_res.get('score', 0)
                total = exec_res.get('total', 0)
                outcome = result.get('output', 'Submitted') # Fallback
                
                if score == total and total > 0:
                    st.balloons()
                    st.success(f"Assignment Submitted! \n\n**Result: Passed ({score}/{total})**")
                else:
                    st.warning(f"Assignment Submitted. \n\n**Result: Failed ({score}/{total})**")
                
                time.sleep(3)
                st.session_state['candidate_view'] = 'list'
                st.rerun()
            else:
                st.error(f"Submission Failed: {result.get('message', 'Unknown error')}")
