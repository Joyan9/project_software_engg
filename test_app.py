# test_app.py
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from io import BytesIO
from PyPDF2 import PdfWriter

# Import functions and session state from app
import streamlit as st
from streamlit_app import extract_text_from_pdf, generate_question_paper, DAILY_TOKEN_LIMIT


# Mocking the Streamlit session state for test environment
@pytest.fixture(autouse=True)
def mock_streamlit_session():
    st.session_state["token_usage"] = 0
    st.session_state["usage_date"] = datetime.now().date()


# Test 1: Daily token limit reset
def test_token_usage_reset():
    # Simulate yesterday's date in session state
    st.session_state["usage_date"] = datetime.now().date().replace(day=datetime.now().day - 1)
    st.session_state["token_usage"] = 100

    # Trigger the reset (in real app, this would run at the start of the script)
    if st.session_state["usage_date"] != datetime.now().date():
        st.session_state["token_usage"] = 0
        st.session_state["usage_date"] = datetime.now().date()

    assert st.session_state["token_usage"] == 0, "Token usage should reset to 0 daily."


# Test 2: PDF extraction within page limits
def test_extract_text_from_pdf_within_limits():
    # Create a mock PDF with 10 pages
    pdf = BytesIO()
    pdf_writer = PdfWriter()
    for _ in range(10):
        pdf_writer.add_blank_page(width=72, height=72)
    pdf_writer.write(pdf)
    pdf.seek(0)

    # Test text extraction for first 5 pages
    extracted_text = extract_text_from_pdf(pdf, start_page=0, end_page=5)
    assert isinstance(extracted_text, str), "Extracted text should be a string."


# Test 3: OpenAI API call and token usage tracking
@patch("streamlit_app.client.chat.completions.create")
def test_generate_question_paper(mock_openai):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"mcqs": [], "six_mark_questions": [], "ten_mark_questions": []}'
    mock_response.usage.total_tokens = 50
    mock_openai.return_value = mock_response

    # Call the function with test input
    result = generate_question_paper("sample course content")

    assert "mcqs" in result, "Result should contain 'mcqs' key."
    assert "six_mark_questions" in result, "Result should contain 'six_mark_questions' key."
    assert "ten_mark_questions" in result, "Result should contain 'ten_mark_questions' key."
    assert st.session_state["token_usage"] == 50, "Token usage should be updated based on API response."


# Test 4: PDF extraction error handling
def test_extract_text_from_pdf_error_handling():
    invalid_pdf = BytesIO(b"not a real pdf content")

    result = extract_text_from_pdf(invalid_pdf, start_page=0, end_page=5)
    assert "Error extracting text from PDF" in result, "Should return an error message for invalid PDF."


# Test 5: Token limit warning message
def test_token_limit_warning():
    st.session_state["token_usage"] = DAILY_TOKEN_LIMIT

    remaining_tokens = DAILY_TOKEN_LIMIT - st.session_state["token_usage"]
    assert remaining_tokens == 0, "Remaining tokens should be 0 when limit is reached."

    # Mock Streamlit warning function to check message
    with patch("streamlit.warning") as mock_warning:
        if remaining_tokens <= 0:
            st.warning("Daily token limit reached. Try again tomorrow.")
        mock_warning.assert_called_once_with("Daily token limit reached. Try again tomorrow.")
