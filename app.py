import streamlit as st
from review_core import review_code_string, issues_to_markdown, filter_issues_to_changed_lines

st.set_page_config(page_title= "CodeAssist", layout = "wide")
st.title("CodeAssist - Code Review")
tab1, tab2 = st.tabs(["Review a code snippet", "Review a diff"])

with tab1:
    code = st.text_area("Paste Python Code", height = 240, value = "def add(a,b): return a+b/n")
    filename = st.text_input("Filename (for display)",  value = "snippet.py")
    if st.button("Review code"):
        with st.spinner("Analyzing…"):
            issues = review_code_string(code, filename_hint=filename)  # <- get Issue list
        st.markdown(issues_to_markdown(issues))

with tab2:
    diff_file = st.file_uploader("Upload unified diff (.patch/.diff)", type=["diff", "patch", "txt"])
    new_code = st.text_area("Paste the NEW file version referenced in the diff", height = 240)
    fname2 = st.text_input("Filename in diff", value = "src/app.py")
    
    if st.button("Review diff"):
        if diff_file and new_code:
            diff_text = diff_file.read().decode("utf-8", errors="ignore")
            issues = review_code_string(new_code, filename_hint=fname2)  # Issue list
            issues = filter_issues_to_changed_lines(issues, diff_text)
            st.markdown(issues_to_markdown(issues))
    else:
        st.warning("Please upload a diff and paste the new code.")


