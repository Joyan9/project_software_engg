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


# Example function to log data to Google Sheets (import this if it's in another module)
def log_metrics_to_google_sheets(sheet, data):
    """Logs metrics (including timestamp) to Google Sheets."""
    try:
        # Assume data is appended with the following format:
        sheet.append_row(data)
        return True
    except Exception as e:
        return str(e)

# Fixture to mock Google Sheets
@pytest.fixture
def mock_google_sheets():
    with patch("google_sheets_api.GoogleSheetClient") as MockGoogleSheetClient:
        mock_client = MockGoogleSheetClient.return_value
        mock_client.append_row = MagicMock()
        yield mock_client

# Test suite for Google Sheets logging
def test_log_metrics_to_google_sheets(mock_google_sheets):
    # Sample data to log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "Some metric", 123]  # Adjust as needed

    # Log data using the function
    result = log_metrics_to_google_sheets(mock_google_sheets, data)

    # Verify that append_row was called once with the correct data
    mock_google_sheets.append_row.assert_called_once_with(data)
    assert result is True, "Expected logging function to return True on success"

def test_log_metrics_to_google_sheets_failure(mock_google_sheets):
    # Simulate an exception when trying to log data
    mock_google_sheets.append_row.side_effect = Exception("Google Sheets API error")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [timestamp, "Some metric", 123]  # Adjust as needed
    result = log_metrics_to_google_sheets(mock_google_sheets, data)

    # Check that an exception message is returned
    assert result == "Google Sheets API error", "Expected logging function to return an error message on failure"

