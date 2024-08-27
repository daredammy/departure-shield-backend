from typing import Any, Dict
from models.file_transfer_risk_models import FileTransferRiskFactor, FileTransferRiskLevel, FileTransferRiskInfluencer, FileTransferMitigationStatus


def adjust_file_transfer_risk_factors(risk_factors: Dict[FileTransferRiskFactor, FileTransferRiskLevel], additional_context: Dict[str, Any]):
    external_mitigation = additional_context['external_mitigation']
    heightened_risks = additional_context['heightened_risks']

    # Reduce risk if external mitigation is present
    if external_mitigation == FileTransferMitigationStatus.PRESENT:
        for factor in risk_factors:
            if risk_factors[factor] != FileTransferRiskLevel.LOW:
                risk_factors[factor] = FileTransferRiskLevel(
                    risk_factors[factor].value - 1)

    # Elevate risks based on heightened risks
    for influencer, level in heightened_risks.items():
        if level == FileTransferRiskLevel.HIGH:
            if influencer in [FileTransferRiskInfluencer.DATA_EXFILTRATION, FileTransferRiskInfluencer.SENSITIVE_INFORMATION_EXPOSURE]:
                risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.HIGH
            elif influencer in [FileTransferRiskInfluencer.UNAUTHORIZED_SHARING, FileTransferRiskInfluencer.INTELLECTUAL_PROPERTY_LOSS]:
                risk_factors[FileTransferRiskFactor.UNAUTHORIZED_SHARING] = FileTransferRiskLevel.HIGH
            elif influencer == FileTransferRiskInfluencer.COMPLIANCE_VIOLATION:
                # Compliance violations could affect both primary risk factors
                risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.HIGH
                risk_factors[FileTransferRiskFactor.UNAUTHORIZED_SHARING] = FileTransferRiskLevel.HIGH

    # Ensure no risk level exceeds HIGH
    for factor in risk_factors:
        risk_factors[factor] = min(
            risk_factors[factor], FileTransferRiskLevel.HIGH)


def adjust_file_transfer_risk_factors_by_additional_context(risk_factors: Dict[FileTransferRiskFactor, FileTransferRiskLevel], additional_context: Dict[str, Any]):
    heightened_risks = additional_context['heightened_risks']

    # Elevate risks based on heightened risks
    for influencer, level in heightened_risks.items():
        if level == FileTransferRiskLevel.HIGH:
            if influencer in [FileTransferRiskInfluencer.DATA_EXFILTRATION, FileTransferRiskInfluencer.SENSITIVE_INFORMATION_EXPOSURE]:
                risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.HIGH
            elif influencer in [FileTransferRiskInfluencer.UNAUTHORIZED_SHARING, FileTransferRiskInfluencer.INTELLECTUAL_PROPERTY_LOSS]:
                risk_factors[FileTransferRiskFactor.UNAUTHORIZED_SHARING] = FileTransferRiskLevel.HIGH
            elif influencer == FileTransferRiskInfluencer.COMPLIANCE_VIOLATION:
                risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.HIGH
                risk_factors[FileTransferRiskFactor.UNAUTHORIZED_SHARING] = FileTransferRiskLevel.HIGH

    # Ensure no risk level exceeds HIGH or goes below LOW
    for factor in risk_factors:
        risk_factors[factor] = max(
            min(risk_factors[factor], FileTransferRiskLevel.HIGH), FileTransferRiskLevel.LOW)


def adjust_file_transfer_risk_factors_by_influencers(risk_factors: Dict[FileTransferRiskFactor, FileTransferRiskLevel], data_sensitivity: FileTransferRiskLevel, activity_type_risk: FileTransferRiskLevel):
    # Adjust for data sensitivity
    if data_sensitivity == FileTransferRiskLevel.HIGH:
        for factor in risk_factors:
            risk_factors[factor] = FileTransferRiskLevel.HIGH
    elif data_sensitivity == FileTransferRiskLevel.MEDIUM:
        for factor in risk_factors:
            if risk_factors[factor] == FileTransferRiskLevel.LOW:
                risk_factors[factor] = FileTransferRiskLevel.MEDIUM

    # Adjust for activity type risk
    if activity_type_risk == FileTransferRiskLevel.HIGH:
        risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.HIGH
    elif activity_type_risk == FileTransferRiskLevel.MEDIUM:
        if risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] == FileTransferRiskLevel.LOW:
            risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.MEDIUM

    # Ensure no risk level goes below LOW or above HIGH
    for factor in risk_factors:
        risk_factors[factor] = max(
            min(risk_factors[factor], FileTransferRiskLevel.HIGH), FileTransferRiskLevel.LOW)


def adjust_file_transfer_risk_by_file_size(risk_factors: Dict[FileTransferRiskFactor, FileTransferRiskLevel], file_size_mb: float):
    from file_transfer_risk_definitions import HIGH_RISK_FILE_SIZE_MB, MEDIUM_RISK_FILE_SIZE_MB

    if file_size_mb >= HIGH_RISK_FILE_SIZE_MB:
        risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.HIGH
    elif file_size_mb >= MEDIUM_RISK_FILE_SIZE_MB:
        if risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] == FileTransferRiskLevel.LOW:
            risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = FileTransferRiskLevel.MEDIUM

    # Ensure no risk level exceeds HIGH
    risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION] = min(
        risk_factors[FileTransferRiskFactor.DATA_EXFILTRATION], FileTransferRiskLevel.HIGH)
