# Unit Test Generator for IU - README

Welcome to the **Unit Test Generator for IU**, a web application built to help IU students better prepare for their final exams by generating custom practice question papers from their course materials.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
- [Usage](#usage)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [License](#license)

## Overview

The **Unit Test Generator for IU** application is designed to generate practice questions in varying levels of difficulty based on user-uploaded PDF content. This tool supports IU students by providing a more challenging study resource, improving preparation for exams.

## Features

- **PDF Processing**: Extracts text from uploaded PDFs to create relevant questions.
- **AI-Powered Question Generation**: Leverages the OpenAI API to generate multiple-choice questions, six-mark, and ten-mark questions based on course content.
- **Token Management**: Manages daily token limits to prevent overuse.
- **Performance Tracking**: Logs metrics including time taken to view generated questions and tokens used per session.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- An OpenAI API Key
- Streamlit
- PyPDF2

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/username/unit-test-generator-iu.git
   cd unit-test-generator-iu
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Setup

1. Set up a secret configuration for the OpenAI API Key in Streamlit:
   - In `.streamlit/secrets.toml`, add:
     ```toml
     [open_ai_key]
     key = "YOUR_OPENAI_API_KEY"
     ```

2. Define the path for storing user metrics:
   - Modify the `CSV_FILE_PATH` variable in the main script to specify the desired location for saving `user_metrics.csv`.

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```

2. Upload a PDF file (course unit), specify the start and end pages, and click the "Generate Questions" button.

3. The application will:
   - Extract text from the first 20 pages of the uploaded PDF.
   - Generate a set of questions based on the text using the OpenAI API.
   - Track time taken and tokens used, logging them in `user_metrics.csv`.

### Token Limits

Each user is allowed a maximum of 50,000 tokens per day (approx. 37,500 words). The token usage is reset daily.

## Technology Stack

- **Python**: Core programming language for the application.
- **Streamlit**: For building the web interface.
- **PyPDF2**: For reading and processing PDF content.
- **OpenAI API**: For generating questions based on extracted content.

## Project Structure

```
unit-test-generator-iu/
├── app.py                   # Main Streamlit application script
├── requirements.txt         # List of dependencies
├── user_metrics.csv         # CSV file for logging metrics
└── .streamlit/
    └── secrets.toml         # Streamlit secrets configuration
```

## License

This project is licensed under the MIT License.
