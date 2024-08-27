"""
Departure Shield: Risk Assessment Module

This module provides functionality to assess the risk associated with an employee's departure,
focusing on their access to sensitive information and secrets.
"""

import datetime
from enum import Enum
import json
import os
from typing import Dict, Any

from utils.ai_service import get_ai_chat_response
from external_risk_assessment.secret_risk_assessment import assess_external_mitigation, assess_heightened_risk
from models.secret_risk_models import RISK_MITIGATION_STRATEGIES, MitigationStatus, RiskFactor, RiskLevel
from utils.secret_risk_adjustment_helper import adjust_risk_factors_by_additional_context, adjust_risk_factors_by_influencers


# Constants for risk assessment thresholds
HIGH_ROTATION_THRESHOLD = 90
MID_ROTATION_THRESHOLD = 30
DAYS_SINCE_HIGH_ACCESS_RISK = 7
DAYS_SINCE_MEDIUM_ACCESS_RISK = 30


def load_secrets(user_id: str) -> Dict[str, Any]:
    """
    Load secrets associated with a given user ID from a JSON file.

    Args:
        user_id (str): The ID of the user whose secrets are to be loaded.

    Returns:
        Dict[str, Any]: A dictionary containing the user's secrets, or None if the user is not found.
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the mock_data directory
    mock_data_dir = os.path.join(current_dir, '..', 'mock_data')

    # Load the secret metadata for all employees
    with open(os.path.join(mock_data_dir, 'secret_metadata.json'), 'r') as f:
        all_data = json.load(f)

    # Find the specific employee's data
    for employee in all_data['employees']:
        if employee['user_id'] == user_id:
            return employee

    # Return None if the user is not found
    return None


def calculate_days_until_rotation(next_rotation_date: str) -> int:
    """
    Calculate the number of days until the next rotation date for a secret.

    Args:
        next_rotation_date (str): The next rotation date in 'YYYY-MM-DD' format.

    Returns:
        int: The number of days until rotation, or infinity if no rotation is scheduled.
    """
    if not next_rotation_date:
        return 365 * 5  # 5 years (arbitrary large value for no rotation)
    today = datetime.date.today()
    rotation_date = datetime.datetime.strptime(
        next_rotation_date, "%Y-%m-%d").date()
    return (rotation_date - today).days


def get_additional_context_from_perplexity(secret: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get additional context for risk assessment using Perplexity AI.

    This function integrates with Perplexity AI to assess external mitigation measures
    and potential heightened risks associated with the given secret.

    Args:
        secret (Dict[str, Any]): A dictionary containing secret metadata.

    Returns:
        Dict[str, Any]: A dictionary containing external mitigation status and heightened risks.
    """
    # Assess external mitigation
    mitigation_status = assess_external_mitigation(secret)

    # Assess heightened risks
    heightened_risks = assess_heightened_risk(secret)

    # Convert heightened risks to a more usable format
    processed_risks = {
        risk_vector.name: risk_level
        for risk_vector, risk_level in heightened_risks.items()
    }

    return {
        "external_mitigation": mitigation_status,
        "heightened_risks": processed_risks
    }


def evaluate_secret_risk(secret: Dict[str, Any]) -> Dict[str, Any]:
    # Calculate time-based metrics
    days_until_rotation = calculate_days_until_rotation(
        secret['next_rotation_date'])
    days_since_last_access = (datetime.date.today(
    ) - datetime.datetime.strptime(secret['last_accessed'], "%Y-%m-%d").date()).days

    # Assess base risk levels
    persistent_access_risk = assess_base_persistent_access_risk(
        days_until_rotation, days_since_last_access)

    risk_factors = {
        RiskFactor.PERSISTENT_ACCESS_RISK: persistent_access_risk,
    }

    # Assess influencing factors
    service_criticality = assess_service_criticality(secret['service'])
    data_sensitivity = assess_data_sensitivity(secret['description'])

    # Store initial risk factors for justification
    initial_risk_factors = risk_factors.copy()

    # Adjust risk factors
    adjust_risk_factors_by_influencers(
        risk_factors, service_criticality, data_sensitivity)

    # Get additional context and further adjust risk factors
    additional_context = get_additional_context_from_perplexity(secret)
    adjust_risk_factors_by_additional_context(risk_factors, additional_context)

    justifications = {}
    mitigation_strategies = {}

    for factor, level in risk_factors.items():
        initial_level = initial_risk_factors[factor]
        justification = f"{factor.name}: {level.name}\n"

        if factor == RiskFactor.PERSISTENT_ACCESS_RISK:
            days_until_rotation = calculate_days_until_rotation(
                secret['next_rotation_date'])
            days_since_last_access = (datetime.date.today(
            ) - datetime.datetime.strptime(secret['last_accessed'], "%Y-%m-%d").date()).days

            justification += f"This secret was last accessed {days_since_last_access} days ago"
            if days_until_rotation == 365 * 5:  # If it's our arbitrary large value
                justification += " and is not scheduled for rotation."
            else:
                justification += f" and is due for rotation in {days_until_rotation} days."

            if level == RiskLevel.HIGH:
                justification += " This represents a high risk due to recent access and distant rotation date."
            elif level == RiskLevel.MEDIUM:
                justification += " This represents a medium risk due to either recent access or a somewhat distant rotation date."

        if level != initial_level:
            justification += "\nRisk level was adjusted due to:"
            if service_criticality != RiskLevel.LOW:
                justification += f"\n- The service '{secret['service']}' is considered critical."
            if data_sensitivity != RiskLevel.LOW:
                justification += f"\n- The data accessed is considered sensitive."

            external_mitigation = additional_context['external_mitigation']
            if external_mitigation != MitigationStatus.ABSENT:
                justification += f"\n- There are some external mitigation measures in place."

            heightened_risks = additional_context['heightened_risks']
            high_risks = [risk for risk, risk_level in heightened_risks.items(
            ) if risk_level == RiskLevel.HIGH]
            if high_risks:
                justification += f"\n- There are heightened risks in the following areas: {', '.join(high_risks)}."

        justifications[factor.name] = justification.strip()
        mitigation_strategies[factor.name] = RISK_MITIGATION_STRATEGIES[factor][level]

    return {
        "risk_levels": risk_factors,
        "justifications": justifications,
        "mitigation_strategies": mitigation_strategies,
        "additional_context": additional_context
    }


def assess_base_persistent_access_risk(days_until_rotation: int, days_since_last_access: int) -> RiskLevel:
    return (
        RiskLevel.HIGH if days_until_rotation > HIGH_ROTATION_THRESHOLD and days_since_last_access < DAYS_SINCE_HIGH_ACCESS_RISK
        else RiskLevel.MEDIUM if days_until_rotation > MID_ROTATION_THRESHOLD or days_since_last_access < DAYS_SINCE_MEDIUM_ACCESS_RISK
        else RiskLevel.LOW
    )


def assess_service_criticality(service: str) -> RiskLevel:
    return RiskLevel.HIGH if 'production' in service.lower() else RiskLevel.MEDIUM


def assess_data_sensitivity(description: str) -> RiskLevel:
    prompt = f"""
    Analyze the following description of a secret or sensitive information and assess its data sensitivity level. 
    Consider factors such as the type of data, potential impact if exposed, and regulatory implications.

    Description: "{description}"

    Provide your assessment as a JSON object with the following structure:
    {{
        "risk_level": "LOW" | "MEDIUM" | "HIGH",
        "explanation": "Brief explanation for the assessment"
    }}

    Base your assessment on these guidelines:
    - HIGH: Highly sensitive data (e.g., customer personal information, payment details, trade secrets)
    - MEDIUM: Moderately sensitive data (e.g., internal business processes, proprietary but non-critical information)
    - LOW: Low sensitivity data (e.g., publicly available information, non-confidential internal data)

    Respond only with the JSON object, no additional text.
    """

    try:
        response = get_ai_chat_response(
            prompt, ai_engine='openAI', response_format="json_object")
        if response and isinstance(response, list) and len(response) > 0:
            assessment = response[0]
            return RiskLevel[assessment['risk_level'].upper()]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error processing AI response: {e}")

    # Fallback to MEDIUM if AI assessment fails
    return RiskLevel.MEDIUM


def evaluate_overall_secret_risk(user_id: str) -> Dict[str, Any]:
    user_secrets = load_secrets(user_id)
    if not user_secrets:
        return {"error": "User not found"}

    overall_risk = {level: [] for level in RiskLevel}

    for secret in user_secrets['secrets']:
        risk_evaluation = evaluate_secret_risk(secret)
        risk_level = max(
            risk_evaluation['risk_levels'].values(), key=lambda x: x.value)

        overall_risk[risk_level].append({
            'secret_id': secret['secret_id'],
            'name': secret['name'],
            'description': secret['description'],  # Add this line
            'risk_factors': {factor.name: level.name for factor, level in risk_evaluation['risk_levels'].items()},
            'justifications': risk_evaluation['justifications'],
            'mitigation_strategies': risk_evaluation['mitigation_strategies'],
            'additional_context': risk_evaluation['additional_context']
        })

    result = {level.name.lower(): secrets for level,
              secrets in overall_risk.items()}
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
    # Example usage of the risk assessment system
    user_risk = evaluate_overall_secret_risk("emp12345")
    print(json.dumps(user_risk, indent=2))
