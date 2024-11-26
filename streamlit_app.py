import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout='wide')
st.title("C10 Labs - C3 analysis ")

# Connect to Google Sheets
conn = st.connection("gsheets_weekly_survey", type=GSheetsConnection)
df = conn.read(worksheet="Form Responses 1")

# conn_weekly_checkin = st.connection("gsheets_weekly_checkin", type=GSheetsConnection)
# df_checkin = conn_weekly_checkin.read(worksheet="Form Responses 1")


df_assi = pd.read_csv('final_df.csv')

# Data Preprocessing for Survey Data
df['Week'] = df['Please select the week in which you are providing feedback']
df['Insights Rating'] = pd.to_numeric(
    df["To what extent did you gain new insights from this week's workshop(s)? "],
    errors='coerce'
)
df['Recommendation Rating'] = pd.to_numeric(
    df["Based on this week's workshop(s), how likely would you recommend the Cohort Program to other founders, entrepreneurs, and innovators."],
    errors='coerce'
)

# Data Preprocessing for Assignment Tracker
df_assi['Timestamp'] = pd.to_datetime(df_assi['Timestamp'])

# Sidebar for both functionalities (Survey Data and Assignment Tracker)
sidebar_option = st.sidebar.radio("Choose View", ["Survey Data", "Assignment Tracker"])

# Survey Data Logic
if sidebar_option == "Survey Data":
    # Group and Aggregate Data for Survey
    aggregated_insights = (
        df.groupby(['Week', "Team's name/ mentor"])['Insights Rating']
        .mean()
        .reset_index()
    )
    aggregated_recommendation = (
        df.groupby(['Week', "Team's name/ mentor"])['Recommendation Rating']
        .mean()
        .reset_index()
    )

    # Sidebar for Team Selection in Survey Data
    teams = df["Team's name/ mentor"].dropna().unique()
    selected_team = st.sidebar.selectbox("Select Team/Mentor for Survey", teams)

    # Filter Data for Selected Team
    team_insights_data = aggregated_insights[aggregated_insights["Team's name/ mentor"] == selected_team]
    team_recommendation_data = aggregated_recommendation[aggregated_recommendation["Team's name/ mentor"] == selected_team]

    # Layout with Columns for Side-by-Side Visualization
    col1, col2 = st.columns(2)

    # Visualization 1: Insights Rating
    with col1:
        st.markdown(f"<h3 style='color:red;'>Insights Gained for {selected_team}</h3>", unsafe_allow_html=True)
        if not team_insights_data.empty:
            plt.figure(figsize=(6, 4))  # Smaller figure size
            sns.lineplot(
                data=team_insights_data, 
                x='Week', 
                y='Insights Rating', 
                marker='o', 
                color='blue'
            )
            plt.title('Weekly Insights Rating', fontsize=12)
            plt.xlabel('Week', fontsize=10)
            plt.ylabel('Average Insights Rating', fontsize=10)
            plt.xticks(rotation=45, fontsize=8)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            st.pyplot(plt)
        else:
            st.warning(f"No data available for the selected team: {selected_team}")

    # Visualization 2: Recommendation Rating
    with col2:
        st.markdown(f"<h3 style='color:red;'>Recommendation Rating for {selected_team}</h3>", unsafe_allow_html=True)
        if not team_recommendation_data.empty:
            plt.figure(figsize=(6, 4))  # Smaller figure size
            sns.lineplot(
                data=team_recommendation_data, 
                x='Week', 
                y='Recommendation Rating', 
                marker='o', 
                color='orange'
            )
            plt.title('Weekly Recommendation Rating', fontsize=12)
            plt.xlabel('Week', fontsize=10)
            plt.ylabel('Average Recommendation Rating', fontsize=10)
            plt.xticks(rotation=45, fontsize=8)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            st.pyplot(plt)
        else:
            st.warning(f"No data available for the selected team: {selected_team}")

# Assignment Tracker Logic
elif sidebar_option == "Assignment Tracker":
    # Sidebar for Company Selection in Assignment Tracker
    companies = df_assi["Company' name "].dropna().unique()
    selected_company = st.sidebar.selectbox("Select Company for Assignment Tracker", companies)

    # Filter the data for the selected company
    company_data = df_assi[df_assi["Company' name "] == selected_company]

    # Group data by Spreadsheet Name to track submission status
    df_assi_grouped = company_data.groupby('Spreadsheet Name', as_index=False).agg({'Timestamp': 'max'})

    # Layout for Assignment Tracker
    st.title(f"Assignment Tracker for {selected_company}")

    # Display the assignment submission status
    st.markdown("<h3 style='color:red;'>Assignment Submission Status</h3>", unsafe_allow_html=True)

    # Iterate over each assignment and display its submission status
    for assignment in df_assi_grouped['Spreadsheet Name'].unique():
        submission_data = df_assi_grouped[df_assi_grouped['Spreadsheet Name'] == assignment]

        submission_date = submission_data['Timestamp'].iloc[0] if not submission_data.empty else None

        if submission_date:
            # If there's a submission, show the date
            st.write(f"**{assignment}** - Submitted on: {submission_date.strftime('%Y-%m-%d %H:%M')}")
        else:
            # If no submission, mark it as not submitted
            st.write(f"**{assignment}** - Not Submitted")

    # Optionally, you can add a visualization of submission timeline for the selected company
    st.markdown("<h3 style='color:red;'>Submission Timeline</h3>", unsafe_allow_html=True)

    # Create a plot to visualize the submission dates
    fig, ax = plt.subplots(figsize=(10, 6))
    for assignment in df_assi_grouped['Spreadsheet Name'].unique():
        assignment_data = df_assi_grouped[df_assi_grouped['Spreadsheet Name'] == assignment]
        if not assignment_data.empty:
            ax.scatter(assignment_data['Timestamp'], [assignment] * len(assignment_data), label=assignment)

    ax.set_xlabel("Submission Date")
    ax.set_ylabel("Assignment")
    ax.set_title(f"Assignments Submitted by {selected_company}")
    ax.legend(title="Assignments", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Display the plot
    st.pyplot(fig)
