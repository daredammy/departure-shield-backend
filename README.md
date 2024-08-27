# Departure Shield Backend

## Overview

Departure Shield Backend is a Python-based service designed to assess and manage risks associated with departing employees. It provides APIs for evaluating secret access risks and file transfer risks, integrating with AI services for enhanced risk analysis.

## Features

- Evaluate overall secret access risks for employees
- Assess file transfer risks based on recent activities
- Integrate with AI services (OpenAI, Google AI, Anthropic, Perplexity) for advanced risk analysis
- Modular structure for easy expansion and maintenance
- JSON-based data storage for employee secrets and file transfers

## Technologies Used

- Python 3.8+
- Flask (for API endpoints)
- OpenAI API
- Google AI API
- Anthropic API
- Perplexity API

## Project Structure

```
departure_shield_backend/
├── external_risk_assessment/
│   ├── secret_risk_assessment.py
│   └── file_transfer_assessment.py
├── models/
│   ├── secret_risk_models.py
│   └── file_transfer_risk_models.py
├── utils/
│   ├── ai_service.py
│   ├── secret_risk_adjustment_helper.py
│   └── file_transfer_risk_adjustment_helper.py
├── mock_data/
│   ├── secret_metadata.json
│   └── file_transfer_metadata.json
├── secret_evaluation.py
├── file_transfer_evaluation.py
├── departure_risk.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-organization/departure-shield-backend.git
   ```

2. Navigate to the project directory:
   ```
   cd departure-shield-backend
   ```

3. Create a virtual environment:
   ```
   python -m venv venv
   ```

4. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_AI_API_KEY=your_google_ai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   PERPLEXITY_API_KEY=your_perplexity_api_key
   ```

## Usage

Please ensure the neeeded environment variables are set up before running the scripts.
- `OPENAI_API_KEY`: OpenAI API key
- `GOOGLE_AI_API_KEY`: Google AI API key
- `ANTHROPIC_API_KEY`: Anthropic API
- `PERPLEXITY_API_KEY`: Perplexity API

To run the main risk assessment:

```
python departure_risk.py
```

This will evaluate risks for all employees in the mock data and output the results.

## API Endpoints

(Note: API endpoints are not implemented in the current version. This section is a placeholder for future development.)

- `/evaluate_departure_risk/<user_id>` (GET): Evaluate overall departure risk for a specific user
- `/evaluate_secret_risk/<user_id>` (GET): Evaluate secret access risk for a specific user
- `/evaluate_file_transfer_risk/<user_id>` (GET): Evaluate file transfer risk for a specific user


## Acknowledgments

- This project was created as part of a hackathon event for Afrotech 2024. Thanks to the organizers for the opportunity.
