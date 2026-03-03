import streamlit as st
import pandas as pd
import altair as alt
import os
from services.api import fetch_stats, fetch_candidates, fetch_questions, assign_question, fetch_recruiter_assignments, fetch_top_candidates
from dotenv import load_dotenv

load_dotenv()

def render_recruiter_dashboard():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"<h1 style='font-size: 3.5rem;'>Recruiter Dashboard</h1>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='font-size: 2rem; font-weight: 300;'>Welcome, <span style='color: #FF4B4B;'>{st.session_state['username']}</span>!</h2>", unsafe_allow_html=True)
    with col2:
        stats = fetch_stats()
        if stats and any(stats.values()):
            df_stats = pd.DataFrame(list(stats.items()), columns=['Platform', 'Count'])
            
            # Create Donut Chart
            chart = alt.Chart(df_stats).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Platform", type="nominal"),
                tooltip=['Platform', 'Count']
            ).properties(
                title="Candidate Distribution Data"
            )
            st.altair_chart(chart, width="stretch")
        else:
            st.write("Stats unavailable")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Top Shortlisted Candidates", "Manage Candidates", "Review Submissions", "Pipeline Automation"])
    
    with tab1:
        st.markdown(f"<h2 style='font-size: 2.5rem;'><span style='color: #FF4B4B;'>Top Shortlisted Candidates</span></h2>", unsafe_allow_html=True)
        st.write("Candidates shortlisted across all platforms based on performance metrics.")
        
        # 1. Select Platform (Mandatory first step, like Manage Candidates)
        platform_filter = st.selectbox("Select Platform to View", ["GitHub", "LeetCode", "StackOverflow"], key="top_cand_platform")
        
        if platform_filter:
            # Fetch data ONLY for the selected platform
            top_candidates = fetch_top_candidates(platform_filter)
            
            if top_candidates:
                df_top = pd.DataFrame(top_candidates)
                
                # --- Metrics ---
                st.metric(label=f"Total Top Candidates ({platform_filter})", value=len(df_top))
                
                # Dynamic Column Config based on Platform (to avoid nulls)
                # Base config common to all
                col_config = {
                     "username": st.column_config.TextColumn("Username", width="medium"),
                     "selection_probability": st.column_config.NumberColumn("Selection Prob", format="%.4f")
                }
                
                # Add platform specific columns
                if platform_filter == "GitHub":
                    col_config["followers"] = st.column_config.NumberColumn("Followers")
                    col_config["total_stars"] = st.column_config.NumberColumn("Total Stars")
                elif platform_filter == "LeetCode":
                    col_config["ranking"] = st.column_config.NumberColumn("Ranking")
                    col_config["reputation"] = st.column_config.NumberColumn("Reputation")
                elif platform_filter == "StackOverflow":
                    col_config["reputation"] = st.column_config.NumberColumn("Reputation")
                    col_config["gold_badges"] = st.column_config.NumberColumn("Gold Badges")

                st.dataframe(
                    df_top,
                    column_config=col_config,
                    width="stretch",
                    hide_index=True
                )
                
                st.markdown("---")
                
                # --- Assignment Workflow ---
                st.markdown(f"<h2 style='font-size: 2.5rem;'><span style='color: #FFFFFF;'>Assign Interview Question</span></h2>", unsafe_allow_html=True)
                
                assign_container = st.container(border=True)
                with assign_container:
                    col_cand, col_ques = st.columns(2)
                    
                    with col_cand:
                        # Improved user column detection
                        if 'username' in df_top.columns:
                            user_col = 'username'
                        else:
                             user_col = df_top.columns[0]
                             
                        selected_candidate = st.selectbox("Select Candidate", df_top[user_col], key="top_cand_select")
                    
                    with col_ques:
                        questions = fetch_questions()
                        q_titles = [q['title'] for q in questions] if questions else []
                        selected_q_title = st.selectbox("Select Question", q_titles, key="top_cand_q_select")
                        selected_q_obj = next((q for q in questions if q['title'] == selected_q_title), None)

                # Account Creation & Email
                st.markdown("#### Candidate Details (Mandatory)")
                
                # Pre-fill email if available
                row = df_top[df_top[user_col] == selected_candidate].iloc[0]
                # Check for email column variations
                email_val = ''
                if 'email' in row:
                     email_val = row['email'] if pd.notna(row['email']) else ''
                
                candidate_email = st.text_input("Candidate Email", value=email_val, key="top_cand_email")
                new_password = st.text_input("Set Password for Candidate", type="password", key="top_cand_pass")

                if st.button("Assign Question", type="primary", width="stretch", key="top_cand_btn"):
                    if not selected_q_obj:
                        st.error("Please select a question.")
                    elif not candidate_email:
                        st.error("Please enter a valid email.")
                    elif not new_password:
                        st.error("Please set a password for the candidate.")
                    else:
                        if assign_question(st.session_state['username'], selected_candidate, selected_q_obj, candidate_email, new_password):
                            st.success(f"✅ Assigned '{selected_q_title}' to **{selected_candidate}** and sent email to {candidate_email}!")
                        else:
                            st.error("Failed to assign question.")
            else:
                 st.info(f"No top candidates found for {platform_filter}.")

    with tab2:
        st.markdown(f"<h2 style='font-size: 2.5rem;'><span style='color: #FF4B4B;'>Candidate Management</h2><span>", unsafe_allow_html=True)
        
        # 1. Select Platform
        platform = st.selectbox("Select Platform", ["GitHub", "LeetCode", "StackOverflow"])
        
        # 2. View Candidates
        if platform:
            candidates = fetch_candidates(platform)
            if candidates:
                # --- Metrics ---
                st.metric(label=f"Total {platform} Candidates", value=len(candidates))
                
                # --- Candidate Table ---
                df = pd.DataFrame(candidates)
                st.dataframe(df, width="stretch", hide_index=True)

                st.markdown("---")
                
                # --- Assignment Workflow ---
                st.markdown(f"<h2 style='font-size: 2.5rem;'><span style='color: #FFFFFF;'>Assign Interview Question</h2><span>", unsafe_allow_html=True)
                
                assign_container = st.container(border=True)
                with assign_container:
                    col_cand, col_ques = st.columns(2)
                    
                    with col_cand:
                        # Improved user column detection
                        if 'name' in df.columns:
                            user_col = 'name'
                        elif 'username' in df.columns:
                            user_col = 'username'
                        else:
                            user_col = df.columns[0]
                        selected_candidate = st.selectbox("Select Candidate", df[user_col])
                    
                    with col_ques:
                        questions = fetch_questions()
                        q_titles = [q['title'] for q in questions] if questions else []
                        selected_q_title = st.selectbox("Select Question", q_titles)
                        selected_q_obj = next((q for q in questions if q['title'] == selected_q_title), None)
    
                # Account Creation & Email (Mandatory)
                st.markdown("#### Candidate Details (Mandatory)")
                candidate_email = st.text_input("Candidate Email")
                new_password = st.text_input("Set Password for Candidate", type="password")

                if st.button("Assign Question", type="primary", width="stretch"):
                    if not selected_q_obj:
                        st.error("Please select a question.")
                    elif not candidate_email:
                        st.error("Please enter a valid email.")
                    elif not new_password:
                        st.error("Please set a password for the candidate.")
                    else:
                        if assign_question(st.session_state['username'], selected_candidate, selected_q_obj, candidate_email, new_password):
                            st.success(f"✅ Assigned '{selected_q_title}' to **{selected_candidate}** and sent email to {candidate_email}!")
                        else:
                            st.error("Failed to assign question.")
            else:
                st.info(f"No {platform} candidates found. Try running the pipeline to fetch new data.")
                
    with tab3:
        st.markdown(f"<h2 style='font-size: 2.5rem;'><span style='color: #FF4B4B;'>Review Submissions</h2><span>", unsafe_allow_html=True)
        
        # Fetch assignments for this recruiter
        assignments = fetch_recruiter_assignments(st.session_state['username'])
        
        if assignments:
            # Convert to DataFrame for easier viewing
            df_assign = pd.DataFrame(assignments)
            
            # --- Summary Metrics ---
            total_assign = len(df_assign)
            # Count status correctly. Assuming 'completed' is the status for done ones.
            # If status can be 'assigned', 'pending', 'completed', etc.
            completed_assign = len(df_assign[df_assign['status'].str.lower() == 'completed'])
            pending_assign = total_assign - completed_assign
            
            # Display Metrics with custom styling
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Assignments", total_assign)
            m2.metric("Completed", completed_assign)
            m3.metric("Pending", pending_assign)
            
            st.markdown("---")
            
            # --- Selection ---
            st.markdown("### Submission Details")
            
            # Create a label mapping for the selectbox
            submission_options = {row['id']: f"{row['candidate_username']} - {row['question_title']} ({row['status'].capitalize()})" for _, row in df_assign.iterrows()}
            
            selected_submission_id = st.selectbox(
                "Select Submission to Review", 
                options=list(submission_options.keys()),
                format_func=lambda x: submission_options[x]
            )
            
            if selected_submission_id:
                submission = df_assign[df_assign['id'] == selected_submission_id].iloc[0]
                
                # --- Detail View with Columns ---
                col_info, col_result = st.columns([1, 1], gap="medium")
                
                with col_info:
                    st.markdown("#### Candidate Info")
                    st.write(f"**Name:** `{submission['candidate_username']}`")
                    st.write(f"**Question:** {submission['question_title']}")
                    
                    # Status Badge
                    status_val = submission['status'].lower()
                    status_color = "green" if status_val == 'completed' else "orange"
                    st.markdown(f"**Status:** <span style='background-color:{status_color}; color:white; padding: 4px 8px; border-radius: 4px; font-weight:bold;'>{submission['status'].upper()}</span>", unsafe_allow_html=True)

                with col_result:
                    st.markdown("#### Result")
                    # Outcome Badge
                    outcome = submission['outcome'] if submission['outcome'] else "Pending"
                    outcome_color = "green" if outcome == "Accepted" else "red" if outcome == "Wrong Answer" else "gray"
                    
                    st.metric("Score", f"{submission['score']}/{submission['total_test_cases']}")
                    st.markdown(f"**Outcome:** <span style='background-color:{outcome_color}; color:white; padding: 4px 8px; border-radius: 4px; font-weight:bold;'>{outcome}</span>", unsafe_allow_html=True)
                
                st.markdown("---")
                
                # --- Code View in Expander ---
                with st.expander("📝 View Submitted Code", expanded=False):
                    st.code(submission['submitted_code'], language='python')
                
                # --- Execution Log (Enhanced) ---
                st.markdown("#### 🚀 Execution Log")
                if submission['execution_log']:
                    log_container = st.container(border=True)
                    with log_container:
                        for line in submission['execution_log'].split('\n'):
                            stripped_line = line.strip()
                            if "Accepted" in stripped_line or "All Test Cases Passed" in stripped_line:
                                st.markdown(f"<h3 style='color: #28a745; margin: 0;'>{line}</h3>", unsafe_allow_html=True)
                            elif "Runtime:" in stripped_line or "Memory:" in stripped_line:
                                # Highlight specific metrics
                                formatted = line.replace("Runtime:", "<span style='color: #1f77b4; font-weight: bold;'>Runtime:</span>")\
                                                .replace("Memory:", "<span style='color: #9467bd; font-weight: bold;'>Memory:</span>")
                                st.markdown(f"<div style='font-family: monospace;'>{formatted}</div>", unsafe_allow_html=True)
                            elif "Error" in stripped_line or "Exception" in stripped_line:
                                st.markdown(f"<div style='color: #dc3545; font-weight: bold;'>{line}</div>", unsafe_allow_html=True)
                            else:
                                st.text(line)
                else:
                    st.info("No execution log available.")
        else:
            st.info("No assignments found.")

    with tab4:
        st.markdown(f"<h2 style='font-size: 2.5rem;'><span style='color: #FF4B4B;'>Automated Data Pipeline (CI/CD)</span></h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"<h2 style='font-size: 2.5rem; font-weight: 400;'><span style='color: ##FFFFFF;'>Data Configuration</span></h2>", unsafe_allow_html=True)
        st.markdown(
            '<p style="font-size:19px;">Configure and trigger the candidate selection pipeline on GitHub Actions, to Fetch and Filter candidates as per the recruiter\'s requirements via Github Token.</p>',
            unsafe_allow_html=True
        )
        # Repository Details (Hardcoded for Recruiter View)
        repo_owner = "Bloodwingv2"
        repo_name = "ATS"
            
        # Try to load token from env, otherwise ask user
        default_token = os.environ.get("GITHUB_TOKEN", "")
        
        # Authentication in Sidebar
        st.sidebar.markdown("### Configuration:")
        if default_token:
            st.sidebar.success("🟢 GitHub Token Active")
            gh_token = default_token
        else:
            st.sidebar.warning("🔴 Token Missing")
            gh_token = st.sidebar.text_input("Enter GitHub Token", type="password", help="Required for pipeline automation")

        if not gh_token and not default_token:
             st.warning("⚠️ GitHub Token is required to run the pipeline. Please check the sidebar.")

        st.markdown(f"<h2 style='font-size: 2rem; font-weight: 300;'><span style='color: #FFA500;'>Filter Criteria</span></h2>", unsafe_allow_html=True)
        
        # 3. Filters per Platform
        col_gh, col_so, col_lc = st.columns(3)
        
        with col_gh:
            st.markdown("#### GitHub")
            min_gh = st.number_input("Min Followers", value=50, step=10, key="min_gh")
            # Placeholder for potential future GitHub filters
            # st.text_input("Location", key="gh_loc")
            
        with col_so:
            st.markdown("#### StackOverflow")
            min_so = st.number_input("Min Reputation", value=0, step=100, key="min_so")
            
        with col_lc:
            st.markdown("#### LeetCode")
            max_lc = st.number_input("Max Rank", value=1000000, step=1000, key="max_lc")
            
        if st.button("Run Automation Pipeline"):
            if not gh_token:
                st.error("Please provide a GitHub Token.")
            else:
                from services.api import trigger_workflow
                inputs = {
                    "min_github_followers": str(min_gh),
                    "min_stackoverflow_reputation": str(min_so),
                    "max_leetcode_rank": str(max_lc)
                }
                
                with st.spinner("Triggering Pipeline..."):
                    success, msg = trigger_workflow(gh_token, repo_owner, repo_name, "pipeline.yml", inputs)
                    
                if success:
                    st.success(f"{msg} Automation pipeline Initiated! Estimated Time: ~3 mins. Check GitHub Actions for detailed progress!")
                else:
                    st.error(msg)
