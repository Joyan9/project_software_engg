import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import json
from datetime import datetime, timedelta
import csv
import os
import pandas as pd

# Define the CSV file path
CSV_FILE_PATH = "user_metrics.csv"


open_ai_key = st.secrets["open_ai_key"]["key"]
client = OpenAI(api_key=open_ai_key)


# Token limit and reset configurations
DAILY_TOKEN_LIMIT = 50000

# Initialize or retrieve token usage and date
if "token_usage" not in st.session_state or "usage_date" not in st.session_state:
    st.session_state["token_usage"] = 0
    st.session_state["usage_date"] = datetime.now().date()

# Reset token count if the day has changed
if st.session_state["usage_date"] != datetime.now().date():
    st.session_state["token_usage"] = 0
    st.session_state["usage_date"] = datetime.now().date()


# Check if "start_time" exists in session state, initialize if not
if "start_time" not in st.session_state:
    st.session_state["start_time"] = None


# Function to initialize the CSV file with headers if it doesn't exist
def initialize_csv():
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "time_taken_seconds", "tokens_used"])

# Initialize DataFrame in session state
if "metrics_df" not in st.session_state:
    st.session_state["metrics_df"] = pd.DataFrame(columns=["timestamp", 
                                                           "time_taken_seconds", 
                                                           "tokens_used"])

# Function to log metrics in-memory
def log_metrics_in_memory(time_taken_seconds, tokens_used):
    new_row = {
        "timestamp": datetime.now().isoformat(),
        "time_taken_seconds": time_taken_seconds,
        "tokens_used": tokens_used
    }
    st.session_state["metrics_df"] = pd.concat([st.session_state["metrics_df"], 
                                                pd.DataFrame([new_row])], 
                                                ignore_index=True)

# Function to save the in-memory DataFrame to CSV
def save_metrics_to_csv():
    if os.path.exists(CSV_FILE_PATH):
        # Append without headers if CSV already exists
        st.session_state["metrics_df"].to_csv(CSV_FILE_PATH, mode="a", header=False, index=False)
    else:
        # Write with headers if CSV doesn't exist
        st.session_state["metrics_df"].to_csv(CSV_FILE_PATH, mode="w", header=True, index=False)
    
    # Clear in-memory DataFrame after saving to avoid duplication
    st.session_state["metrics_df"] = st.session_state["metrics_df"].iloc[0:0]


# Function to extract text from specific pages in a PDF
def extract_text_from_pdf(pdf, start_page, end_page):
    try:
        reader = PdfReader(pdf)
        total_pages = len(reader.pages)

        # Ensure the end_page does not exceed the total number of pages
        if end_page > total_pages:
            end_page = total_pages

        text = ""
        for page_num in range(start_page, end_page):
            # Add a default if no text is found
            text += reader.pages[page_num].extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


# Function to generate questions and track token usage
def generate_question_paper(course_content):
    prompt = (
        f"You are a subject matter expert for the following course content.\n"
        f"Generate questions based on this course content: {course_content}\n\n"
        f"Instructions:\n"
        f"1. Create five multiple-choice questions (MCQs) with a range of difficulty levels.\n"
        f"2. Create two six-mark questions, ensuring a variety of difficulty levels.\n"
        f"3. Create two ten-mark questions, also with varied difficulty.\n"
        f"4. Include numerical questions if suitable for the course content.\n\n"
        f"Output Format:\n"
        f"Return a JSON object only, structured as follows:\n"
        f"{{\n"
        f"  'mcqs': [\n"
        f"    {{ 'question': 'Lorem ipsum dolor sit amet?',\n"
        f"       'options': ['A) Lorem', 'B) Ipsum', 'C) Dolor', 'D) Sit'] }},\n"
        f"    {{ 'question': 'Consectetur adipiscing elit?',\n"
        f"       'options': ['A) Amet', 'B) Consectetur', 'C) Adipiscing', 'D) Elit'] }}\n"
        f"  ],\n"
        f"  'six_mark_questions': [\n"
        f"    {{ 'question': 'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',\n"
        f"       'mark': 6 }}\n"
        f"  ],\n"
        f"  'ten_mark_questions': [\n"
        f"    {{ 'question': 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip.',\n"
        f"       'mark': 10 }}\n"
        f"  ]\n"
        f"}}\n\n"
        f"Instructions:\n"
        f"- ONLY respond with the JSON object.\n"
        f"- Do not include any introductory text or explanations.\n"
    )


    try:
        # Check token usage limit before making a request
        if st.session_state["token_usage"] >= DAILY_TOKEN_LIMIT:
            st.warning("Daily token limit reached. Try again tomorrow.")
            return None

        # Using OpenAI to generate the response and track token usage
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Get the response and token count
        generated_questions = chat_completion.choices[0].message.content
        tokens_used = chat_completion.usage.total_tokens
        
        # Update session token count
        st.session_state["token_usage"] += tokens_used

        # Parse the response as a JSON
        question_data = json.loads(generated_questions)
        
        return {
            "raw_output": generated_questions,
            "mcqs": question_data['mcqs'],
            "six_mark_questions": question_data['six_mark_questions'],
            "ten_mark_questions": question_data['ten_mark_questions'],
            "tokens_used": tokens_used
        }

    except Exception as e:
        st.error(f"Error generating question: {str(e)}")
        return None


# Streamlit App UI
# CSS for centering the image and caption
st.markdown(
    """
    <style>
    .centered-content {
        text-align: center;
    }
    .centered-image {
        width: 35%; /* Adjust the width as needed */
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Use st.markdown to add both the image and caption, centered
st.markdown(
    """
    <div class="centered-content">
        <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQQk0Nid6exA02gz9SatDfmITvW0PF5oXmzT8olISA3U1mckTEe6loG3GMXwVqMWnKsYpA&usqp=CAU" class="centered-image" alt="IU Logo">
        <p>Welcome to the Unit Test Generator for IU</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Add vertical space
st.write("\n" * 10)
# Some introductory content
st.write("""
As an IU student, I noticed that the unit tests available on myCampus often don't challenge students enough. This tool is designed to help IU students push themselves further and better prepare for their final exams.

The user simply uploads a PDF of one of their units and clicks the 'Generate Questions' button. 
The web app will then generate 5 multiple-choice questions, 2 six-mark questions, and 2 ten-mark questions all with varying difficulty levels.
         
Each user gets a maximum of 50,000 tokens per session (100 tokens ≈ 75 words, read more [here](https://platform.openai.com/tokenizer)).

Please note that this web app was developed solely for academic purposes and is not intended for production use. Additionally, no data is stored on the servers.
""")

# Add vertical space
st.write("\n" * 10)

# Sample PDF download buttons
st.markdown("### Sample PDFs")

with open("/workspaces/project_software_engg/sample_pdfs/Software Engineering Unit 1.pdf", "rb") as file1:
    st.download_button(label="Download Software Engineering Unit 1 PDF", 
                       data=file1, file_name="Software Engineering Unit 1.pdf")

with open("/workspaces/project_software_engg/sample_pdfs/Advanced Mathematics Unit 1.pdf", "rb") as file2:
    st.download_button(label="Download Advanced Mathematics Unit 1 PDF", 
                       data=file2, file_name="Advanced Mathematics Unit 1.pdf")

with open("/workspaces/project_software_engg/sample_pdfs/International Financial Accounting Unit 1.pdf", "rb") as file3:
    st.download_button(label="Download International Financial Accounting Unit 1 PDF", 
                       data=file3, file_name="International_Financial_Accounting_Unit_1.pdf")

# Add vertical space
st.write("\n" * 10)

# remaining tokens
remaining_tokens = DAILY_TOKEN_LIMIT - st.session_state["token_usage"]

# Check if remaining tokens have gone below 1000
if remaining_tokens < 1000:
    st.error("Daily token limit reached, you do not sufficient tokens to generate questions! Please try again tomorrow.")
else:

    # File Upload for PDF
    uploaded_pdf = st.file_uploader("Upload a PDF for one of your course units", type="pdf")

    # Show token count
    st.write(f"Remaining Tokens Today: {remaining_tokens}")

    if uploaded_pdf:
        # Load the uploaded PDF using PdfReader
        num_of_pages = len(PdfReader(uploaded_pdf).pages)
        st.write(f"The uploaded PDF contains {num_of_pages} pages.")
        st.markdown("""
        <span style="color:darkorange;">
        Note: For this academic project, only the first 20 pages of the uploaded PDF will be processed. 
        This limitation helps reduce token usage and minimize costs.
        </span>
        """, unsafe_allow_html=True)

        # Add vertical space
        st.write("\n" * 5)

        # On button click, set start_time to current time
        if st.button("Generate Questions"):
            st.session_state["start_time"] = datetime.now()
            course_text = extract_text_from_pdf(uploaded_pdf, 0, 20)
            
            if "Error" in course_text:
                st.error("There was an error in parsing the uploaded PDF, please try again or with another PDF.")
            else:
                question_paper = generate_question_paper(course_text)
                
                # Fail-safe: check if the output is a valid JSON structure
                if question_paper:
                    try:
                        # Validate that the expected keys are present
                        if all(key in question_paper for key in ["mcqs", 
                                                                 "six_mark_questions", 
                                                                 "ten_mark_questions"]):
                            # Calculate time taken to view questions
                            time_to_view = datetime.now() - st.session_state["start_time"]
                            time_taken_seconds = time_to_view.total_seconds()

                            # Initialize CSV and log time and tokens used
                            initialize_csv()
                            log_metrics_in_memory(time_taken_seconds, question_paper["tokens_used"])

                            # Display Tokens Used
                            st.subheader("Total Tokens Used")
                            st.write(question_paper["tokens_used"])

                            # Save immediately after logging each metric
                            save_metrics_to_csv()

                            st.success("Question generation completed!")

                            # Display the generated questions in a structured format
                            st.subheader("Multiple Choice Questions")
                            for i, mcq in enumerate(question_paper["mcqs"], 1):
                                st.markdown(f"**Q{i}:** {mcq['question']}")
                                for option in mcq["options"]:
                                    st.write(option)
                                st.write("---")

                            st.subheader("Six-Mark Questions")
                            for i, question in enumerate(question_paper["six_mark_questions"], 1):
                                st.markdown(f"**Q{i}:** {question['question']}")
                                st.write("---")

                            st.subheader("Ten-Mark Questions")
                            for i, question in enumerate(question_paper["ten_mark_questions"], 1):
                                st.markdown(f"**Q{i}:** {question['question']}")
                                st.write("---")

                            
                        else:
                            raise ValueError("Invalid JSON structure")

                    except (ValueError, KeyError, TypeError) as e:
                        st.error("The generated output was not in the expected format. Please click 'Generate Questions' again.")
                else:
                    st.error("Failed to generate questions. Please try again.")
