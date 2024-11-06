# Unit Test Generator

## Overview

The **Unit Test Generator** is a web application designed for IU students to generate practice unit test papers based on course materials in PDF format. By simply uploading a PDF of a course unit, students can generate multiple-choice questions (MCQs), six-mark questions, and ten-mark questions, all with varying difficulty levels. The app also tracks usage metrics such as the time taken and tokens used, logging them to a Google Sheet for analysis.

## Features

- Upload a PDF file containing course material.
- Extract text from the first 20 pages of the PDF for question generation.
- Generate five multiple-choice questions (MCQs), two six-mark questions, and two ten-mark questions.
- Display the generated questions in a well-structured format.
- Track the time taken for generating questions and the number of tokens used by the OpenAI API.
- Log usage data (time and tokens) to a Google Sheet for record-keeping.
- Limited to 50,000 tokens per session to minimize costs.

## Prerequisites

- Python 3.7+
- Streamlit
- OpenAI API key
- Google Cloud credentials (service account key) for Google Sheets API
- PyPDF2

## Installation

1. **Clone this repository:**

   ```bash
   git clone https://github.com/yourusername/unit-test-generator.git
   cd unit-test-generator
   ```

2. **Install dependencies:**

   Create a virtual environment and install the required Python libraries:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud Credentials:**

   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project.
   - Enable the Google Sheets and Google Drive APIs.
   - Download the service account JSON key and store it as `service_account_key.json`.
   - Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of this key.

4. **Set up OpenAI API key:**

   - Go to the [OpenAI API](https://platform.openai.com/signup).
   - Get your API key and add it to `secrets.toml` or use Streamlit secrets management.

5. **Run the app:**

   ```bash
   streamlit run app.py
   ```

## Usage

1. **Upload a PDF**: The app accepts PDFs of course units. After uploading, the app will extract text from the first 20 pages of the PDF.
   
2. **Generate Questions**: Click the "Generate Questions" button to create five multiple-choice questions, two six-mark questions, and two ten-mark questions based on the extracted content.
   
3. **View Metrics**: The app will display the total tokens used and the time taken to generate the questions. This data is also logged to a Google Sheet for tracking.

4. **Download Sample PDFs**: Sample PDFs are available for download to try the app.

## File Structure

```
unit-test-generator/
│
├── app.py                      # Streamlit application file
├── requirements.txt            # List of dependencies
├── sample_pdfs/                # Folder containing sample PDFs
│   ├── Software Engineering Unit 1.pdf
│   ├── Advanced Mathematics Unit 1.pdf
│   └── International Financial Accounting Unit 1.pdf
├── service_account_key.json    # Google Cloud service account credentials
└── README.md                   # This file
```

## Google Sheets Integration

The app logs the time taken and the number of tokens used to a Google Sheet named `IU Unit Test Generator Logs`. To enable this feature:

- Ensure your Google Cloud service account has access to the Google Sheets API.
- The sheet must have a worksheet named `Logs` for recording the metrics.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Streamlit** for creating an amazing framework for building web apps.
- **OpenAI** for providing powerful APIs to generate questions based on course content.
- **Google Cloud** for providing the Sheets API to log user data.
  
## Contributing

If you have suggestions, improvements, or bug fixes, feel free to submit a pull request or open an issue. Contributions are welcome!
