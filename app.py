import streamlit as st # type: ignore
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from io import BytesIO
import random

st.title("NSS Shadowing Lottery")
col1, col2 = st.columns(2)
# Uploading files and processing that into data frames
col1.subheader("Upload")
experiences_file = col1.file_uploader("Experiences Template File Upload", type=["xlsx"])
shadowing_preferences_file = col1.file_uploader("Shadowing Preferences File Upload", type=["xlsx"])
if experiences_file is not None:
    experiences = pd.read_excel(experiences_file)
if shadowing_preferences_file is not None:
    shadowing_preferences = pd.read_excel(shadowing_preferences_file)
col2.write("Enter students' names who did not get shadowing last quarter, each on its own line.")
high_preference_names = col2.text_area("High preferences")
if "no_shadowing_list" not in st.session_state:
    st.session_state.no_shadowing_list = []
if st.session_state.no_shadowing_list:
    col2.write("Students without assignments:")
    for name in st.session_state.no_shadowing_list:
        col2.write(name)
# generate results:
if experiences_file is not None and shadowing_preferences_file is not None and st.button("Generate Result"):
    no_shadowing_list = list() # collects names of students who didn't get a provider to shadow
    shadowing_preferences["Your Name"] = shadowing_preferences["Your Name"].str.strip()
    shuffled_list = shadowing_preferences["Your Name"].tolist()
    random.shuffle(shuffled_list)
    # Incorporate the students with high priority due to not getting shadowing in previous terms
    high_preference_list = high_preference_names.split("\n")
    high_preference_list = [name.strip() for name in high_preference_list if name.strip()]
    # Removing duplicates from list
    shuffled_list_no_duplicates = [name for name in shuffled_list if name not in high_preference_list]
    priority_order = shuffled_list_no_duplicates
    if high_preference_list:
        priority_order = high_preference_list + shuffled_list_no_duplicates
    for name in priority_order:
        # Find the row in dataframe corresponding to this student
        name_row = shadowing_preferences[shadowing_preferences["Your Name"]==name]
        # for each of the student's preferences ranked from 1 to 5
        for i in range(1,6):
            preference_col = f"Preference #{i}"
            experience_num = int(name_row[preference_col].values[0])
            experience_row = experiences[experiences["Experience #"].astype(int) == experience_num]
            num_students = int(experience_row.iloc[0]["# Students"])
            idx = experience_row.index[0]
            # Checking if this provider has space to take on another student
            student_done = False
            for j in range(1,num_students+1):
                col_name = f"Student {j}"
                if pd.isna(experience_row[col_name].values[0]):
                    experiences.loc[idx, col_name] = name
                    student_done = True
                    break
            if student_done:
                break
            if not student_done and i == 5:
                no_shadowing_list.append(name)
    # output results file
    result = experiences
    out = BytesIO()
    result.to_excel(out, index=False, engine="openpyxl")
    out.seek(0)
    st.session_state.no_shadowing_list = no_shadowing_list
    if st.session_state.no_shadowing_list:
        col2.write("Students without assignments:")
        for name in st.session_state.no_shadowing_list:
            col2.write(name)
    col2.download_button(
        label="Download Excel",
        data=out,
        file_name="Shadowing_Assignments.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )