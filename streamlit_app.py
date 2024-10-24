import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import random
import json

open_ai_key = st.secrets["open_ai_key"]["key"]
client = OpenAI(api_key=open_ai_key)

# Initialize token limit
TOKEN_LIMIT = 100_000

# Track total token usage
if 'total_tokens_used' not in st.session_state:
    st.session_state['total_tokens_used'] = 0

# Function to check if the user has enough tokens left to generate questions
def check_token_balance(tokens_required):
    remaining_tokens = TOKEN_LIMIT - st.session_state['total_tokens_used']
    return remaining_tokens >= tokens_required


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


# Combined function to generate all questions with a single OpenAI API call
def generate_question_paper(course_content):
    prompt = (
        f"Generate the following questions based on this course content: {course_content}\n\n"
        f"1. Five multiple-choice questions (MCQs) with varying difficulty levels.\n"
        f"2. Two six-mark long-answer questions with varying difficulty levels.\n"
        f"3. Two ten-mark long-answer questions with varying difficulty levels.\n\n"
        f"Return the result in the following structured format as a direct JSON object:\n"
        f"{{\n"
        f"  'mcqs': [list of 5 MCQs],\n"
        f"  'six_mark_questions': [list of 2 six-mark questions],\n"
        f"  'ten_mark_questions': [list of 2 ten-mark questions]\n"
        f"}}\n\n"
        f"ONLY respond with JSON."
        f"NO preceeding words like json:"
        f"Do not include the answers or any explanations."
    )

    try:
        # Using the correct method for chat completion and capturing token usage
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract the generated questions and token usage
        generated_questions = chat_completion.choices[0].message.content
        total_tokens = chat_completion.usage.total_tokens

        
        # Parse the response as a JSON-like dictionary
        question_data = json.loads(generated_questions)  # Safe JSON parsing

        # Return the questions and total tokens used
        return {
            "raw_output" : generated_questions,
            "mcqs": question_data['mcqs'],
            "six_mark_questions": question_data['six_mark_questions'],
            "ten_mark_questions": question_data['ten_mark_questions'],
            "tokens_used": total_tokens
        }

    except Exception as e:
        return f"Error generating question: {str(e)}", 0



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
         
Each user gets a maximum of 100,000 tokens (100 tokens ~= 75 words, read more here: https://platform.openai.com/tokenizer).

Please note that this web app was developed solely for academic purposes and is not intended for production use. Additionally, no data is stored on the servers.
""")

# Add vertical space
st.write("\n" * 10)

# Display Token Limit
st.write(f"Remaining Tokens: {TOKEN_LIMIT - st.session_state['total_tokens_used']}")

# File Upload for PDF
uploaded_pdf = st.file_uploader("Upload a PDF for one of your course units", type="pdf")

if uploaded_pdf:
    # Load the uploaded PDF using PdfReader
    pdf_reader = PdfReader(uploaded_pdf)
    num_of_pages = len(pdf_reader.pages)

    st.markdown("""
    <span style="color:darkorange;">
    Note: For this academic project, only the first 20 pages of the uploaded PDF will be processed. 
    This limitation helps reduce token usage and minimize costs.
    </span>
    """, unsafe_allow_html=True)

    # Add some vertical space
    st.write("\n" * 2)

    st.write(f"The uploaded PDF contains {num_of_pages} pages.")

    if st.button("Generate Questions"):
        # Extract text from PDF
        course_text = extract_text_from_pdf(uploaded_pdf, 0, 20)

        if "Error" in course_text:
            st.error(course_text)  # Show the error if there's an issue with extraction
        else:
            # Check token limit before generating questions
            if check_token_balance(1000):  # Arbitrary token estimate for the process
                # Generate question paper
                question_paper = generate_question_paper(course_text)

                if "error" in question_paper:
                    st.error(question_paper['error'])  # Display error message if present
                else:
                    # Display Tokens Used
                    st.subheader("Total Tokens Used")
                    st.write(question_paper['tokens_used'])
                    st.session_state['total_tokens_used'] += question_paper['tokens_used']

                    # Display the generated questions
                    st.subheader("Multiple Choice Questions (5):")
                    for i, mcq in enumerate(question_paper["mcqs"], 1):
                        st.write(f"{i}. {mcq}")

                    st.subheader("Six-Mark Questions (2):")
                    for i, question in enumerate(question_paper["six_mark_questions"], 1):
                        st.write(f"{i}. {question}")

                    st.subheader("Ten-Mark Questions (2):")
                    for i, question in enumerate(question_paper["ten_mark_questions"], 1):
                        st.write(f"{i}. {question}")

                st.success("Question generation completed!")
            else:
                st.error("You have reached the token limit and cannot generate more questions.")