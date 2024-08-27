"""
Departure Shield: File Transfer Risk Assessment Module

This module provides functionality to assess the risk associated with an employee's file transfers and accesses,
focusing on potential data exfiltration and unauthorized sharing.
"""

from utils.file_transfer_risk_adjustment_helper import adjust_file_transfer_risk_factors_by_additional_context, adjust_file_transfer_risk_factors_by_influencers
from utils.file_transfer_risk_adjustment_helper import adjust_file_transfer_risk_factors_by_additional_context, adjust_file_transfer_risk_factors_by_influencers
from models.file_transfer_risk_models import FILE_TRANSFER_RISK_MITIGATION_STRATEGIES, FileTransferRiskFactor, FileTransferRiskLevel
from external_risk_assessment.file_transfer_assessment import assess_file_transfer_heightened_risk
from utils.ai_service import get_ai_chat_response
from typing import Dict, Any
import json
from enum import Enum
import datetime
import os


# Constants for risk assessment thresholds
DAYS_SINCE_HIGH_TRANSFER_RISK = 5
DAYS_SINCE_MEDIUM_TRANSFER_RISK = 7
HIGH_RISK_FILE_SIZE_MB = 100
MEDIUM_RISK_FILE_SIZE_MB = 10


def load_file_transfers(user_id: str) -> Dict[str, Any]:
    """
    Load file transfer and access data associated with a given user ID from a JSON file.

    Args:
        user_id (str): The ID of the user whose file transfer data is to be loaded.

    Returns:
        Dict[str, Any]: A dictionary containing the user's file transfer data, or None if the user is not found.
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the mock_data directory
    mock_data_dir = os.path.join(current_dir, '..', 'mock_data')

    # Load the file transfer metadata for all employees
    with open(os.path.join(mock_data_dir, 'file_transfer_metadata.json'), 'r') as f:
        all_data = json.load(f)

    # Find the specific employee's data
    for employee in all_data['employees']:
        if employee['user_id'] == user_id:
            return employee

    # Return None if the user is not found
    return None


def calculate_days_since_activity(activity_date: str) -> int:
    """
    Calculate the number of days since a file transfer or access activity.

    Args:
        activity_date (str): The date of the activity in 'YYYY-MM-DD' format.

    Returns:
        int: The number of days since the activity.
    """
    today = datetime.date.today()
    activity_date = datetime.datetime.strptime(
        activity_date, "%Y-%m-%dT%H:%M:%SZ").date()
    return (today - activity_date).days


def get_additional_context_from_ai(file_transfer: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get additional context for risk assessment using AI services.

    This function integrates with AI services to assess external mitigation measures
    and potential heightened risks associated with the given file transfer or access.

    Args:
        file_transfer (Dict[str, Any]): A dictionary containing file transfer metadata.

    Returns:
        Dict[str, Any]: A dictionary containing external mitigation status and heightened risks.
    """
    # Assess external mitigation

    # Assess heightened risks
    heightened_risks = assess_file_transfer_heightened_risk(file_transfer)

    # Convert heightened risks to a more usable format
    processed_risks = {
        risk_vector.name: risk_level
        for risk_vector, risk_level in heightened_risks.items()
    }

    return {
        "heightened_risks": processed_risks
    }


def evaluate_file_transfer_risk(file_transfer: Dict[str, Any]) -> Dict[str, Any]:
    # Calculate time-based metrics
    days_since_activity = calculate_days_since_activity(
        file_transfer['timestamp'])

    # Assess base risk levels
    data_exfiltration_risk = assess_base_data_exfiltration_risk(
        days_since_activity, file_transfer['size_mb'], file_transfer)

    risk_factors = {
        FileTransferRiskFactor.DATA_EXFILTRATION: data_exfiltration_risk,
    }

    # Assess influencing factors
    data_sensitivity = assess_data_sensitivity(file_transfer['description'])
    activity_type_risk = assess_activity_type_risk(
        file_transfer['activity_type'])

    # Store initial risk factors for justification
    initial_risk_factors = risk_factors.copy()

    # Adjust risk factors
    adjust_file_transfer_risk_factors_by_influencers(
        risk_factors, data_sensitivity, activity_type_risk)

    # Get additional context and further adjust risk factors
    additional_context = get_additional_context_from_ai(file_transfer)
    adjust_file_transfer_risk_factors_by_additional_context(
        risk_factors, additional_context)

    justifications = {}
    mitigation_strategies = {}

    for factor, level in risk_factors.items():
        initial_level = initial_risk_factors[factor]
        justification = f"{factor.name}: {level.name}\n"

        if factor == FileTransferRiskFactor.DATA_EXFILTRATION:
            justification += f"This file transfer occurred {days_since_activity} days ago. "
            justification += f"The file size is {file_transfer['size_mb']} MB. "
            justification += f"It was transferred from {file_transfer['location']['source']} to {file_transfer['location']['destination']}. "
            justification += f"The sharing status is '{file_transfer['sharing_status']}'.\n"

            if level == FileTransferRiskLevel.HIGH:
                justification += "This represents a high risk due to recent activity, large file size, or sensitive destination/sharing status."
            elif level == FileTransferRiskLevel.MEDIUM:
                justification += "This represents a medium risk due to relatively recent activity, moderate file size, or somewhat sensitive destination/sharing status."

        if level != initial_level:
            justification += "\nRisk level was adjusted due to:"
            if data_sensitivity != FileTransferRiskLevel.LOW:
                justification += "\n- The transferred data is considered sensitive."
            if activity_type_risk != FileTransferRiskLevel.LOW:
                justification += f"\n- The activity type '{file_transfer['activity_type']}' is considered risky."

            heightened_risks = additional_context['heightened_risks']
            high_risks = [risk for risk, risk_level in heightened_risks.items(
            ) if risk_level == FileTransferRiskLevel.HIGH]
            if high_risks:
                justification += f"\n- There are heightened risks in the following areas: {', '.join(high_risks)}."

        justifications[factor.name] = justification.strip()
        mitigation_strategies[factor.name] = FILE_TRANSFER_RISK_MITIGATION_STRATEGIES[factor][level]

    return {
        "risk_levels": risk_factors,
        "justifications": justifications,
        "mitigation_strategies": mitigation_strategies,
        "additional_context": additional_context
    }


def assess_base_data_exfiltration_risk(days_since_activity: int, file_size_mb: float, file_transfer: Dict[str, Any]) -> FileTransferRiskLevel:
    if (days_since_activity <= DAYS_SINCE_HIGH_TRANSFER_RISK or file_size_mb >= HIGH_RISK_FILE_SIZE_MB) and 'personal' in file_transfer['location']['destination'].lower() or 'external' in file_transfer['sharing_status'].lower():
        return FileTransferRiskLevel.HIGH
    elif (days_since_activity <= DAYS_SINCE_MEDIUM_TRANSFER_RISK or file_size_mb >= MEDIUM_RISK_FILE_SIZE_MB) and 'restricted' in file_transfer['sharing_status'].lower():
        return FileTransferRiskLevel.MEDIUM
    else:
        return FileTransferRiskLevel.LOW


def assess_data_sensitivity(description: str) -> FileTransferRiskLevel:
    prompt = f"""
    Analyze the following description of a file or data transfer and assess its data sensitivity level. 
    Consider factors such as the type of data, potential impact if exposed, and regulatory implications.

    Description: "{description}"

    Provide your assessment as a JSON object with the following structure:
    {{
        "risk_level": "LOW" | "MEDIUM" | "HIGH",
        "explanation": "Brief explanation for the assessment"
    }}

    Base your assessment on these guidelines:
    - HIGH: Highly sensitive data (e.g., financial reports, product roadmaps, customer personal information)
    - MEDIUM: Moderately sensitive data (e.g., internal business processes, project plans)
    - LOW: Low sensitivity data (e.g., public information, general communications)

    Respond only with the JSON object, no additional text.
    """

    try:
        response = get_ai_chat_response(
            prompt, ai_engine='openAI', response_format="json_object")
        if response and isinstance(response, list) and len(response) > 0:
            assessment = response[0]
            return FileTransferRiskLevel[assessment['risk_level'].upper()]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error processing AI response: {e}")

    # Fallback to MEDIUM if AI assessment fails
    return FileTransferRiskLevel.MEDIUM


def assess_activity_type_risk(activity_type: str) -> FileTransferRiskLevel:
    high_risk_activities = ['Bulk Transfer', 'Data Export']
    medium_risk_activities = ['File Sharing']

    if activity_type in high_risk_activities:
        return FileTransferRiskLevel.HIGH
    elif activity_type in medium_risk_activities:
        return FileTransferRiskLevel.MEDIUM
    else:
        return FileTransferRiskLevel.LOW


def evaluate_overall_file_transfer_risk(user_id: str) -> Dict[str, Any]:
    user_file_transfers = load_file_transfers(user_id)
    if not user_file_transfers:
        return {"error": "User not found"}

    overall_risk = {level: [] for level in FileTransferRiskLevel}

    for file_transfer in user_file_transfers['files_and_transfers']:
        risk_evaluation = evaluate_file_transfer_risk(file_transfer)
        risk_level = max(
            risk_evaluation['risk_levels'].values(), key=lambda x: x.value)

        overall_risk[risk_level].append({
            'activity_id': file_transfer['activity_id'],
            'name': file_transfer['name'],
            'description': file_transfer['description'],  # Add this line
            'risk_factors': {factor.name: level.name for factor, level in risk_evaluation['risk_levels'].items()},
            'justifications': risk_evaluation['justifications'],
            'mitigation_strategies': risk_evaluation['mitigation_strategies'],
            'additional_context': risk_evaluation['additional_context']
        })

    result = {level.name.lower(): activities for level,
              activities in overall_risk.items()}
    return enum_to_str(result)


def enum_to_str(obj):
    if isinstance(obj, Enum):
        return obj.name
    elif isinstance(obj, dict):
        return {k: enum_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [enum_to_str(v) for v in obj]
    return obj


if __name__ == "__main__":
    # Example usage of the file transfer risk assessment system
    user_risk = evaluate_overall_file_transfer_risk("emp12345")
    print(json.dumps(user_risk, indent=2))
