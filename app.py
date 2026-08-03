import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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

# Option A: Handle Synthetic Data Generation (Updated with Severity fields)
if data_option == "Option A: Use Synthetic Data":
    if st.session_state.current_mode != "synthetic" or not st.session_state.test_cases:
        st.session_state.test_cases = [
            {
                "id": "TC-001", "module": "Authentication",
                "scenario": "Verify user can log in with valid credentials.",
                "steps": "1. Navigate to /login\n2. Enter valid email and password\n3. Click Login button.",
                "expected": "User is redirected to the home dashboard and a success toast appears.",
                "status": "Untested", "severity": "Medium", "notes": "", "tester": ""
            },
            {
                "id": "TC-002", "module": "Checkout",
                "scenario": "Apply a valid 10% discount promo code.",
                "steps": "1. Add item to cart\n2. Navigate to /checkout\n3. Enter code 'SAVE10' and click Apply.",
                "expected": "Total price decreases by 10% instantly. Success message displayed.",
                "status": "Untested", "severity": "Low", "notes": "", "tester": ""
            }
        ]
        st.session_state.current_mode = "synthetic"
        st.sidebar.success("Loaded synthetic mock test suite!")

# Option B: Handle Uploading Custom CSV Data
elif data_option == "Option B: Upload Custom CSV Data":
    if st.session_state.current_mode != "uploaded":
        st.session_state.test_cases = []  # Reset workspace state
        st.session_state.current_mode = "uploaded"
        
    uploaded_file = st.sidebar.file_uploader("Upload your UAT template (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            required_cols = ["id", "module", "scenario", "steps", "expected", "status", "severity", "notes", "tester"]
            
            # Match schema structure configurations
            for col in required_cols:
                if col not in uploaded_df.columns:
                    if col == "status":
                        uploaded_df[col] = "Untested"
                    elif col == "severity":
                        uploaded_df[col] = "Medium"
                    else:
                        uploaded_df[col] = ""
            
            st.session_state.test_cases = uploaded_df[required_cols].to_dict(orient="records")
            st.sidebar.success("Successfully loaded your uploaded file!")
        except Exception as e:
            st.sidebar.error(f"Error parsing file: {e}")
            
    elif not st.session_state.test_cases:
        st.info("ℹ️ Please upload a UAT CSV file in the sidebar to populate the workspace.")
        template_df = pd.DataFrame(columns=["id", "module", "scenario", "steps", "expected", "status", "severity", "notes", "tester"])
        template_csv = template_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Empty CSV Template Schema", data=template_csv, file_name="uat_template.csv", mime="text/csv")

# Render interface workflows if elements exist in scope
if st.session_state.test_cases:
    # FIXED: Added integer '2' to explicitly declare the side-by-side workspace split
    col_left, col_right = st.columns(2)

    # Left Column: Add test cases dynamically
    with col_left:
        st.header("📝 Create / Document Test Case")
        with st.form("new_case_form", clear_on_submit=True):
            tc_id = f"TC-00{len(st.session_state.test_cases) + 1}"
            module = st.selectbox("Module/Feature Area", ["Authentication", "Checkout", "User Profile", "Settings"])
            scenario = st.text_input("Test Scenario Summary")
            steps = st.text_area("Step-by-Step Execution Guide")
            expected = st.text_area("Expected Result Detail")
            case_severity = st.selectbox("Initial Target Severity", ["Low", "Medium", "Critical"])
            
            submit = st.form_submit_button("Add to Test Suite")
            if submit:
                if scenario and steps and expected:
                    st.session_state.test_cases.append({
                        "id": tc_id, "module": module, "scenario": scenario,
                        "steps": steps, "expected": expected, "status": "Untested",
                        "severity": case_severity, "notes": "", "tester": ""
                    })
                    st.success(f"Added {tc_id} successfully!")
                    st.rerun()
                else:
                    st.error("Please fill out all fields.")

    # Right Column: Run test parameters and choose severity levels
    with col_right:
        st.header("🏃‍♂️ Test Suite Execution Run")
        for idx, tc in enumerate(st.session_state.test_cases):
            with st.expander(f"**[{tc['id']}]** {tc['module']} - {tc['scenario']} | Status: **{tc['status']}** | Severity: **{tc['severity']}**"):
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
                    
                notes_input = st.text_area("Execution Notes / Documentation Log", value=tc['notes'], key=f"notes_{tc['id']}")
                
                if st.button("Save Updates", key=f"save_{tc['id']}"):
                    st.session_state.test_cases[idx]['status'] = status_input
                    st.session_state.test_cases[idx]['severity'] = severity_input
                    st.session_state.test_cases[idx]['notes'] = notes_input
                    st.session_state.test_cases[idx]['tester'] = tester_name
                    st.success(f"Saved execution adjustments for {tc['id']}!")
                    st.rerun()

    # Dashboard Metrics Section
    st.divider()
    st.header("📊 Sign-Off Report & Breakout Metrics")
    df = pd.DataFrame(st.session_state.test_cases)
    
    # Text Metrics Cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Cases Registered", len(df))
    m2.metric("Passed ✅", len(df[df['status'] == 'Passed']))
    m3.metric("Failed 🚨", len(df[df['status'] == 'Failed']))
    m4.metric("Untested", len(df[df['status'] == 'Untested']))
    
    # Graphic Layout Partition: Table Left, Dynamic Pie Chart Right
    graph_col_left, graph_col_right = st.columns(2)
    
    with graph_col_left:
        st.subheader("Tabular Overview Data")
        st.dataframe(df, use_container_width=True)
    
    with graph_col_right:
        st.subheader("Status Breakout Chart")
        status_counts = df['status'].value_counts()
        
        # Color coding configuration profiles matching UI states
        color_map = {'Passed': '#2ecc71', 'Failed': '#e74c3c', 'Untested': '#95a5a6', 'Blocked': '#f39c12'}
        colors = [color_map.get(status, '#3498db') for status in status_counts.index]
        
        # Render clean matplotlib graphic container objects
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140, colors=colors, textprops={'fontsize': 10})
        ax.axis('equal')
        fig.patch.set_facecolor('none')  # Transparent backdrop configuration integration
        ax.set_facecolor('none')
        st.pyplot(fig)

    # Export Feature
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Finalized UAT Report (CSV)",
        data=csv_data,
        file_name=f"uat_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv'
    )
