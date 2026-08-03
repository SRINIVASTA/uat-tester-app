import streamlit as st
import pandas as pd
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

# Sidebar Configuration
st.sidebar.header("⚙️ Data Settings")
data_option = st.sidebar.radio(
    "Choose your data source:",
    ("Option A: Use Synthetic Data", "Option B: Upload Custom CSV Data")
)

# Option A: Handle Synthetic Data Generation (Updated with Severity and Timestamp placeholders)
if data_option == "Option A: Use Synthetic Data":
    if st.session_state.current_mode != "synthetic" or not st.session_state.test_cases:
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
                "expected": "An validation warning banner states 'Invalid file format. Please upload JPG or PNG.' File block prevents execution.",
                "status": "Untested", "severity": "Critical", "notes": "", "tester": "", "last_updated": "Never"
            }
        ]
        st.session_state.current_mode = "synthetic"
        st.sidebar.success("🤖 AI-generated mock test suite loaded successfully!")

# Option B: Handle Uploading Custom CSV Data
elif data_option == "Option B: Upload Custom CSV Data":
    if st.session_state.current_mode != "uploaded":
        st.session_state.test_cases = []  # Reset workspace state when toggling
        st.session_state.current_mode = "uploaded"
        
    uploaded_file = st.sidebar.file_uploader("Upload your own corporate UAT file (CSV)", type=["csv"])
    
    if uploaded_file is not None:
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
        # Displays the status, severity, and the automated timestamp inside the header block line
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
                # AUTOMATIC TIMESTAMP LOGGING
                st.session_state.test_cases[idx]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.success(f"Saved updates for {tc['id']}!")
                st.rerun()

    # Metrics & Native Progress Tracking Bar
    st.divider()
    st.header("📊 Sign-Off Report & Breakout Metrics")
    df = pd.DataFrame(st.session_state.test_cases)
    
    # Text Metrics Cards
    total_cases = len(df)
    passed_cases = len(df[df['status'] == 'Passed'])
    failed_cases = len(df[df['status'] == 'Failed'])
    untested_cases = len(df[df['status'] == 'Untested'])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cases Registered", total_cases)
    m2.metric("Passed ✅", passed_cases)
    m3.metric("Failed 🚨", failed_cases)
    m4.metric("Untested", untested_cases)
    
    # NEW FEATURE: Visual progress calculation bar
    st.subheader("🏁 Overall Testing Completion Progress")
    completed_cases = total_cases - untested_cases
    progress_percentage = int((completed_cases / total_cases) * 100) if total_cases > 0 else 0
    
    # Renders the clean loading progress bar
    st.progress(progress_percentage / 100)
    st.caption(f"**{progress_percentage}% Completed** ({completed_cases} out of {total_cases} test actions finalized)")

    # Data Table Overview
    st.subheader("Tabular Overview Data")
    st.dataframe(df, use_container_width=True)

    # Export Feature
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Finalized UAT Report (CSV)",
        data=csv_data,
        file_name=f"uat_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv'
    )
