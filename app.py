import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set web page configuration
st.set_page_config(page_title="UAT Test Management Portal", layout="wide", page_icon="🧪")

# Title and Description
st.title("🧪 User Acceptance Testing (UAT) Dashboard")
st.caption("Document test suites, select item severity, view execution breakdown metrics, and sync deployment updates.")

# Initialize global session state arrays
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []
if "current_mode" not in st.session_state:
    st.session_state.current_mode = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# Sidebar Configuration
st.sidebar.header("⚙️ Data Settings")
data_option = st.sidebar.radio(
    "Choose your data source:",
    ("Option A: Use Synthetic Data", "Option B: Upload Custom CSV Data")
)

# Option A: Handle Synthetic Data Generation
if data_option == "Option A: Use Synthetic Data":
    if st.session_state.current_mode != "synthetic":
        st.session_state.test_cases = [
            {
                "id": "TC-001", "module": "Authentication",
                "scenario": "Verify user can log in with valid credentials.",
                "steps": "1. Navigate to /login\n2. Enter valid email and password\n3. Click Login button.",
                "expected": "User is redirected to the home dashboard and a success toast appears.",
                "status": "Untested", "severity": "Medium", "notes": "", "tester": "", "last_updated": "Never"
            },
            {
                "id": "TC-002", "module": "Checkout",
                "scenario": "Apply a valid 10% discount promo code.",
                "steps": "1. Add item to cart\n2. Navigate to /checkout\n3. Enter code 'SAVE10' and click Apply.",
                "expected": "Total price decreases by 10% instantly. Success message displayed.",
                "status": "Untested", "severity": "Low", "notes": "", "tester": "", "last_updated": "Never"
            },
            {
                "id": "TC-003", "module": "User Profile",
                "scenario": "Attempt uploading an unsupported file format (.exe) as avatar picture.",
                "steps": "1. Go to Profile Settings\n2. Click 'Change Avatar'\n3. Select a system executable (.exe file) and hit upload.",
                "expected": "A validation warning banner states 'Invalid file format. Please upload JPG or PNG.' File block prevents execution.",
                "status": "Untested", "severity": "Critical", "notes": "", "tester": "", "last_updated": "Never"
            }
        ]
        st.session_state.current_mode = "synthetic"
        st.session_state.uploaded_file_name = None  # Reset upload lock tracker
        st.sidebar.success("🤖 AI-generated mock test suite loaded successfully!")

# Option B: Handle Uploading Custom CSV Data with Persistent Storage Lock
elif data_option == "Option B: Upload Custom CSV Data":
    if st.session_state.current_mode != "uploaded":
        st.session_state.test_cases = []  # Reset workspace state when toggling
        st.session_state.current_mode = "uploaded"
        st.session_state.uploaded_file_name = None
        
    uploaded_file = st.sidebar.file_uploader("Upload your own corporate UAT file (CSV)", type=["csv"])
    
    # FIXED LOGIC: Only parse the file if it's new. Stops Streamlit from overwriting updates on click.
    if uploaded_file is not None:
        if st.session_state.uploaded_file_name != uploaded_file.name:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                required_cols = ["id", "module", "scenario", "steps", "expected", "status", "severity", "notes", "tester", "last_updated"]
                
                # Match schema structure configurations and add defaults if missing
                for col in required_cols:
                    if col not in uploaded_df.columns:
                        if col == "status":
                            uploaded_df[col] = "Untested"
                        elif col == "severity":
                            uploaded_df[col] = "Medium"
                        elif col == "last_updated":
                            uploaded_df[col] = "Never"
                        else:
                            uploaded_df[col] = ""
                
                st.session_state.test_cases = uploaded_df[required_cols].to_dict(orient="records")
                st.session_state.uploaded_file_name = uploaded_file.name  # Lock file name into memory
                st.sidebar.success("📁 Your custom data file loaded successfully!")
            except Exception as e:
                st.sidebar.error(f"Error parsing file: {e}")
            
    elif not st.session_state.test_cases:
        st.info("ℹ️ Please use the sidebar on the left to upload your custom company CSV testing file.")
        template_df = pd.DataFrame(columns=["id", "module", "scenario", "steps", "expected", "status", "severity", "notes", "tester", "last_updated"])
        template_csv = template_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Empty CSV Template Schema", data=template_csv, file_name="uat_template.csv", mime="text/csv")
# Main Interface Layout
if st.session_state.test_cases:
    st.header("🏃‍♂️ Test Suite Execution Run")
    st.info("💡 Instructions for your Tester: Open your business website, follow the steps inside each item below, click 'Save Updates' after changing an outcome status, and export the file when finished.")
    
    for idx, tc in enumerate(st.session_state.test_cases):
        with st.expander(f"**[{tc['id']}]** {tc['module']} - {tc['scenario']} | Status: **{tc['status']}** | Severity: **{tc['severity']}** | Updated: *{tc['last_updated']}*"):
            st.markdown(f"**Steps to Reproduce:**\n{tc['steps']}")
            st.markdown(f"**Expected Behavior:**\n{tc['expected']}")
            st.divider()
            
            c1, c2, c3 = st.columns(3)
            with c1:
                current_status = ["Untested", "Passed", "Failed", "Blocked"]
                default_status_idx = current_status.index(tc['status']) if tc['status'] in current_status else 0
                status_input = st.selectbox(f"Outcome ({tc['id']})", current_status, index=default_status_idx, key=f"status_{tc['id']}")
            with c2:
                current_severities = ["Low", "Medium", "Critical"]
                default_sev_idx = current_severities.index(tc['severity']) if tc['severity'] in current_severities else 1
                severity_input = st.selectbox(f"Bug Severity ({tc['id']})", current_severities, index=default_sev_idx, key=f"severity_{tc['id']}")
            with c3:
                tester_name = st.text_input("Tester Name/ID", value=tc['tester'], key=f"tester_{tc['id']}")
                
            notes_input = st.text_area("Execution Notes / Documentation Log", value=tc['notes'], key=f"notes_{tc['id']}", placeholder="Type what broke or went wrong here...")
            
            if st.button("Save Updates", key=f"save_{tc['id']}"):
                st.session_state.test_cases[idx]['status'] = status_input
                st.session_state.test_cases[idx]['severity'] = severity_input
                st.session_state.test_cases[idx]['notes'] = notes_input
                st.session_state.test_cases[idx]['tester'] = tester_name
                st.session_state.test_cases[idx]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.success(f"Saved updates for {tc['id']}!")
                st.rerun()

    # Metrics Headings & Reset Action Bar Area
    st.divider()
    metrics_title_col, reset_btn_col = st.columns(2)
    
    with metrics_title_col:
        st.header("📊 Sign-Off Report & Breakout Metrics")
        
    with reset_btn_col:
        if st.button("♻️ Reset Workspace", use_container_width=True, help="Wipe all execution records back to Untested baseline variables"):
            for case in st.session_state.test_cases:
                case['status'] = 'Untested'
                case['notes'] = ''
                case['tester'] = ''
                case['last_updated'] = 'Never'
            st.success("Workspace fields cleared back to default properties.")
            st.rerun()

    df = pd.DataFrame(st.session_state.test_cases)
    
    # Text Metrics Calculation variables
    total_count = len(df)
    passed_count = len(df[df['status'] == 'Passed'])
    failed_count = len(df[df['status'] == 'Failed'])
    untested_count = len(df[df['status'] == 'Untested'])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cases Registered", total_count)
    m2.metric("Passed ✅", passed_count)
    m3.metric("Failed 🚨", failed_count)
    m4.metric("Untested", untested_count)
    
    # Automated Sign-off Email Generator Trigger
    if passed_count == total_count and total_count > 0:
        st.success("🎉 All tests have successfully passed! The Sign-Off email template has been generated below.")
        
        email_body = f"""Subject: OFFICIAL SIGN-OFF: UAT Testing Complete & Successful for [Project Name]

Hi Team,

I am incredibly excited to announce that User Acceptance Testing (UAT) for [Project/Product Name] has officially concluded successfully as of August 2026.

Our QA and business testing teams have completed a rigorous run-through of our core customer journeys, including critical modules across Authentication, Profile Systems, and the Checkout Workflow.

Key Performance Highlights:
- Total Test Cases Executed: {total_count}
- Total Passing Scenarios: {passed_count} (100% Pass Rate)
- Unresolved Critical / Blocking Bugs: {failed_count}

Based on these spotless results, we are officially granting UAT sign-off. The software is confirmed to be highly stable, intuitive, and compliant with all core corporate requirements. We are clear to move forward into production deployment.

A massive thank you to our UAT contract testers and development leads for getting this across the finish line smoothly. 

I have attached the comprehensive UAT log report sheet to this email for your permanent stakeholder review records. Let’s get ready for a fantastic launch!

Best regards,

[Your Name]  
[Your Title / Business Owner]  
[Your Company Name]"""
        
        with st.expander("📋 VIEW AUTOMATIC COMPLIANCE SIGN-OFF EMAIL", expanded=True):
            st.text_area("Copy and send this block to your company team mailing lists:", value=email_body, height=450)

    # Graphic Layout Partition
    graph_col_left, graph_col_right = st.columns(2)
    
    with graph_col_left:
        st.subheader("Tabular Overview Data")
        st.dataframe(df, use_container_width=True)
    
    with graph_col_right:
        st.subheader("Plotly Interactive Status Breakdown")
        if not df.empty and 'status' in df.columns:
            status_df = df['status'].value_counts().reset_index()
            status_df.columns = ['Test Status', 'Count']
            
            color_discrete_map = {'Passed': '#2ecc71', 'Failed': '#e74c3c', 'Untested': '#95a5a6', 'Blocked': '#f39c12'}
            
            fig = px.pie(
                status_df, 
                values='Count', 
                names='Test Status', 
                color='Test Status',
                color_discrete_map=color_discrete_map,
                hole=0.4
            )
            
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=True,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data rows available to render plot breakdown graphics.")

    # Export Feature
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Finalized UAT Report (CSV)",
        data=csv_data,
        file_name=f"uat_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv'
    )
