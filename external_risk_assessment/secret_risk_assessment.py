import json
import requests
from enum import Enum
from typing import Dict, Any

from utils.ai_service import get_perplexity_response
from models.secret_risk_models import RiskInfluencer, MitigationStatus, RiskLevel, string_to_risk_level


def assess_external_mitigation(secret: Dict[str, Any]) -> MitigationStatus:
    prompt = f"""
    Analyze the following secret and service for external mitigation measures:
    Secret Description: {secret['description']}
    Service: {secret['service']}

    Considering industry-standard security practices, assess whether this service likely has 
    external mitigation measures in place to protect against unauthorized access or misuse 
    of this secret. Respond with a JSON object in the following format:
    {{
        "mitigation_status": "PRESENT" | "PARTIAL" | "ABSENT",
        "explanation": "Brief explanation for the assessment"
    }}
    """
    try:
        response = get_perplexity_response(prompt)
        return MitigationStatus(response["mitigation_status"].lower())
    except Exception as e:
        return MitigationStatus.ABSENT


def assess_heightened_risk(secret: Dict[str, Any]) -> Dict[RiskInfluencer, RiskLevel]:
    prompt = f"""
    Analyze the following secret and service for potential heightened risks:
    Secret Description: {secret['description']}
    Service: {secret['service']}

    Consider the following risk vectors:
    1. Data Exfiltration
    2. Unauthorized Access
    3. System Compromise
    4. Compliance Violation
    5. Intellectual Property Theft

    For each risk vector, assess the risk level as LOW, MEDIUM, or HIGH. 
    Respond with a JSON object in the following format:
    {{
        "data_exfiltration": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "unauthorized_access": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "system_compromise": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "compliance_violation": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "intellectual_property_theft": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }}
    }}
    """

    response = get_perplexity_response(prompt)

    risk_assessment = {}
    for risk_vector in RiskInfluencer:
        # Ensure the risk vector exists in the response
        if risk_vector.value in response:
            level_str = response[risk_vector.value]["level"]
            risk_assessment[risk_vector] = string_to_risk_level(level_str)
        else:
            # Default to LOW if the risk vector is not in the response
            risk_assessment[risk_vector] = RiskLevel.LOW

    return risk_assessment


def get_additional_context_from_perplexity(secret: Dict[str, Any]) -> Dict[str, Any]:
    mitigation_status = assess_external_mitigation(secret)
    heightened_risks = assess_heightened_risk(secret)

    return {
        "external_mitigation": mitigation_status,
        "heightened_risks": heightened_risks
    }
