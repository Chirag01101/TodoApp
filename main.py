import streamlit as st
import pandas as pd
import os
from datetime import date

# --- File to store tasks ---
TASKS_FILE = "tasks.csv"

# --- Load tasks from CSV ---
def load_tasks():
    if os.path.exists(TASKS_FILE):
        return pd.read_csv(TASKS_FILE)
    return pd.DataFrame(columns=["Task", "Done", "Category", "Due Date", "Priority"])

# --- Save tasks to CSV ---
def save_tasks(tasks_df):
    tasks_df.to_csv(TASKS_FILE, index=False)

# --- Initialize ---
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()

st.title("🚀 Ultimate To-Do List App")

# --- Add new task ---
with st.form("task_form", clear_on_submit=True):
    task = st.text_input("Enter a task:")
    category = st.selectbox("Category", ["Work", "Personal", "Shopping", "Other"])
    due_date = st.date_input("Due Date", value=date.today())
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Add Task")
    
    if submitted and task:
        new_task = {
            "Task": task,
            "Done": False,
            "Category": category,
            "Due Date": due_date,
            "Priority": priority
        }
        st.session_state.tasks = pd.concat(
            [st.session_state.tasks, pd.DataFrame([new_task])],
            ignore_index=True
        )
        save_tasks(st.session_state.tasks)

# --- Search / Filter ---
st.sidebar.header("🔎 Filters")
search_text = st.sidebar.text_input("Search by task")
filter_category = st.sidebar.multiselect("Filter by Category", st.session_state.tasks["Category"].unique())
filter_priority = st.sidebar.multiselect("Filter by Priority", st.session_state.tasks["Priority"].unique())

tasks_df = st.session_state.tasks.copy()

if search_text:
    tasks_df = tasks_df[tasks_df["Task"].str.contains(search_text, case=False, na=False)]
if filter_category:
    tasks_df = tasks_df[tasks_df["Category"].isin(filter_category)]
if filter_priority:
    tasks_df = tasks_df[tasks_df["Priority"].isin(filter_priority)]

# --- Show tasks ---
st.subheader("📋 Your Tasks")

if not tasks_df.empty:
    for i, row in tasks_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([5,2,2,1,1])
        with col1:
            if row["Done"]:
                st.write(f"✅ ~~{row['Task']}~~")
            else:
                st.write(f"🔹 {row['Task']}")
        with col2:
            st.write(f"📂 {row['Category']}")
        with col3:
            st.write(f"📅 {row['Due Date']}")
        with col4:
            if st.button("✔", key=f"done_{i}"):
                st.session_state.tasks.at[i, "Done"] = not row["Done"]
                save_tasks(st.session_state.tasks)
                st.rerun()
        with col5:
            if st.button("❌", key=f"delete_{i}"):
                st.session_state.tasks = st.session_state.tasks.drop(i)
                save_tasks(st.session_state.tasks)
                st.rerun()
else:
    st.info("No tasks found. Add some above! 🎯")

# --- Export options ---
st.sidebar.header("⬇ Export Tasks")
export_format = st.sidebar.radio("Choose format", ["CSV", "Excel"])
if st.sidebar.button("Download"):
    if export_format == "CSV":
        st.sidebar.download_button(
            label="Download CSV",
            data=st.session_state.tasks.to_csv(index=False),
            file_name="tasks.csv",
            mime="text/csv"
        )
    else:
        st.sidebar.download_button(
            label="Download Excel",
            data=st.session_state.tasks.to_excel(index=False, engine="openpyxl"),
            file_name="tasks.xlsx",
            mime="application/vnd.ms-excel"
        )
