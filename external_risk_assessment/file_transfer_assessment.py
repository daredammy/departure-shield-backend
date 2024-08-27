import json
from enum import Enum
from typing import Dict, Any

from utils.ai_service import get_perplexity_response
from models.file_transfer_risk_models import FileTransferRiskInfluencer, FileTransferRiskLevel


def assess_file_transfer_heightened_risk(file_transfer: Dict[str, Any]) -> Dict[FileTransferRiskInfluencer, FileTransferRiskLevel]:
    prompt = f"""
    Analyze the following file transfer activity for potential heightened risks:
    Activity Type: {file_transfer['activity_type']}
    File Description: {file_transfer['description']}
    Source: {file_transfer['location']['source']}
    Destination: {file_transfer['location']['destination']}
    Size: {file_transfer['size_mb']} MB
    Sharing Status: {file_transfer['sharing_status']}

    Consider the following risk vectors:
    1. Data Exfiltration
    2. Unauthorized Sharing
    3. Sensitive Information Exposure
    4. Compliance Violation
    5. Intellectual Property Loss

    For each risk vector, assess the risk level as LOW, MEDIUM, or HIGH. 
    Respond with a JSON object in the following format:
    {{
        "data_exfiltration": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "unauthorized_sharing": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "sensitive_information_exposure": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "compliance_violation": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }},
        "intellectual_property_loss": {{ "level": "LOW" | "MEDIUM" | "HIGH", "explanation": "Brief explanation" }}
    }}
    """
    try:
        response = get_perplexity_response(prompt)
    except Exception as e:
        print(f"Error assessing heightened risk from  perplexity: {e}")
        return {
            FileTransferRiskInfluencer.DATA_EXFILTRATION: FileTransferRiskLevel.LOW,
            FileTransferRiskInfluencer.UNAUTHORIZED_SHARING: FileTransferRiskLevel.LOW,
            FileTransferRiskInfluencer.SENSITIVE_INFORMATION_EXPOSURE: FileTransferRiskLevel.LOW,
            FileTransferRiskInfluencer.COMPLIANCE_VIOLATION: FileTransferRiskLevel.LOW,
            FileTransferRiskInfluencer.INTELLECTUAL_PROPERTY_LOSS: FileTransferRiskLevel.LOW
        }

    risk_assessment = {}
    for risk_vector in FileTransferRiskInfluencer:
        if risk_vector.value in response:
            level_str = response[risk_vector.value]["level"]
            risk_assessment[risk_vector] = FileTransferRiskLevel[level_str.upper()]
        else:
            risk_assessment[risk_vector] = FileTransferRiskLevel.LOW

    return risk_assessment


def get_file_transfer_additional_context(file_transfer: Dict[str, Any]) -> Dict[str, Any]:
    heightened_risks = assess_file_transfer_heightened_risk(file_transfer)

    return {
        "heightened_risks": heightened_risks
    }


# Helper function to convert enums to strings for JSON serialization
def enum_to_str(obj):
    if isinstance(obj, Enum):
        return obj.name
    elif isinstance(obj, dict):
        return {k: enum_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [enum_to_str(v) for v in obj]
    return obj
