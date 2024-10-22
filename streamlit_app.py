import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
import random

open_ai_key = st.secrets["open_ai_key"]["key"]

client = OpenAI(api_key=open_ai_key)

# Function to extract text from specific pages in a PDF
def extract_text_from_pdf(pdf, start_page, end_page):
    try:
        reader = PdfReader(pdf)
        text = ""
        for page_num in range(start_page - 1, end_page):
            text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


# Function to generate a question using OpenAI API with LaTeX formatting
def generate_question(course_content, question_type="mcq", difficulty="medium"):
    prompt = (
        f"Generate a {difficulty} {question_type} question in LaTeX format "
        f"based on this course content: {course_content}. "
        f"Do not include the answer or any explanation. "
        f"Format the question using LaTeX syntax."
    )
    try:
        # Using the correct method for chat completion
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return chat_completion.choices[0].message['content']
    except Exception as e:
        return f"Error generating question: {str(e)}"


# Function to generate the question paper
def generate_question_paper(course_text):
    # Shuffle difficulties
    difficulties = ['easy', 'medium', 'hard']
    tokens_used = []
    
    # Generate 5 MCQs
    mcqs = []
    for _ in range(5):
        difficulty = random.choice(difficulties)
        mcq = generate_question(course_text, question_type="mcq", difficulty=difficulty)
        mcqs.append(mcq)
        tokens_used.append(mcq.usage.total_tokens)  # Adjust based on response format

    # Generate 2 six-mark questions
    six_mark_questions = []
    for _ in range(2):
        difficulty = random.choice(difficulties)
        six_mark_question = generate_question(course_text, question_type="long", difficulty=difficulty)
        six_mark_questions.append(six_mark_question)
        tokens_used.append(six_mark_question.usage.total_tokens)

    # Generate 2 ten-mark questions
    ten_mark_questions = []
    for _ in range(2):
        difficulty = random.choice(difficulties)
        ten_mark_question = generate_question(course_text, question_type="long", difficulty=difficulty)
        ten_mark_questions.append(ten_mark_question)
        tokens_used.append(ten_mark_question.usage.total_tokens)

    # Return questions and token usage
    return {
        "mcqs": mcqs,
        "six_mark_questions": six_mark_questions,
        "ten_mark_questions": ten_mark_questions,
        "tokens_used": tokens_used
    }
    

# Streamlit App UI
# Set page layout to wide mode for a more immersive hero image
st.set_page_config(layout="wide")

# Add CSS to style the hero image
st.markdown("""
    <style>
    .hero-image {
        width: 100%;
        height: 300px; /* Set the height of the hero image */
        object-fit: cover; /* Cover the area and keep aspect ratio */
        margin-bottom: 20px; /* Add some space below the image */
    }
    </style>
""", unsafe_allow_html=True)

# Display the hero image
st.image("iu_logo.jpg", caption="Welcome to the Unit Test Generator", use_column_width=True)

# Or use st.markdown with HTML if you want more control
st.markdown("""
    <img src="your_hero_image.jpg" class="hero-image" alt="Hero Image">
""", unsafe_allow_html=True)

# Add some vertical space
st.write("\n" * 10)  # This will add 5 new lines as space
# Some introductory content
st.write("""
Welcome to the Unit Test Generator.

As an IU student, I noticed that the unit tests available on myCampus often don't challenge students enough. This tool is designed to help IU students push themselves further and better prepare for their final exams.

The user simply uploads a PDF of one of their units and clicks the 'Generate Questions' button. The web app will then generate 3 multiple-choice questions, 2 six-mark questions, and 2 ten-mark questions.

Please note that this web app was developed solely for academic purposes and is not intended for production use. Additionally, no data is stored on the servers.
""")


# Add some vertical space
st.write("\n" * 10) 

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
        course_text = extract_text_from_pdf(uploaded_pdf, 1, 20)

        if "Error" in course_text:
            st.error(course_text)  # Show the error if there's an issue with the extraction
        else:
            # Generate question paper (assuming `generate_question_paper` is implemented)
            question_paper = generate_question_paper(course_text)

            # Display Tokens Used
            st.subheader("Total Tokens Used")
            st.write(sum(question_paper['tokens_used']))

            # Function to render LaTeX or text
            def display_question(question):
                if "$" in question:  # Simple check for LaTeX math mode
                    st.latex(question)  # Render as LaTeX if detected
                else:
                    st.write(question)  # Render as plain text if no LaTeX

            # Display MCQs
            st.subheader("Multiple Choice Questions (5):")
            for i, mcq in enumerate(question_paper['mcqs'], 1):
                st.write(f"{i}. ")
                display_question(mcq)

            # Display Six-Mark Questions
            st.subheader("Six-Mark Questions (2):")
            for i, question in enumerate(question_paper['six_mark_questions'], 1):
                st.write(f"{i}. ")
                display_question(question)

        # Display Ten-Mark Questions
        st.subheader("Ten-Mark Questions (2):")
        for i, question in enumerate(question_paper['eighteen_mark_questions'], 1):
            st.write(f"{i}. ")
            display_question(question)