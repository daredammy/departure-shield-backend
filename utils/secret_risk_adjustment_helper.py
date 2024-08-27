from typing import Any, Dict
from models.secret_risk_models import MitigationStatus, RiskFactor, RiskInfluencer, RiskLevel


def adjust_risk_factors(risk_factors: Dict[RiskFactor, RiskLevel], additional_context: Dict[str, Any]):
    external_mitigation = additional_context['external_mitigation']
    heightened_risks = additional_context['heightened_risks']

    # Reduce risk if external mitigation is present
    if external_mitigation == MitigationStatus.PRESENT:
        for factor in risk_factors:
            if risk_factors[factor] != RiskLevel.LOW:
                risk_factors[factor] = RiskLevel(
                    risk_factors[factor].value - 1)

    # Elevate risks based on heightened risks
    for influencer, level in heightened_risks.items():
        if level == RiskLevel.HIGH:
            if influencer == RiskInfluencer.SYSTEM_COMPROMISE:
                risk_factors[RiskFactor.PERSISTENT_ACCESS_RISK] = RiskLevel.HIGH
            elif influencer in [RiskInfluencer.COMPLIANCE_VIOLATION, RiskInfluencer.INTELLECTUAL_PROPERTY_THEFT]:
                # These could potentially affect both primary risk factors
                risk_factors[RiskFactor.PERSISTENT_ACCESS_RISK] = RiskLevel.HIGH

    # Ensure no risk level exceeds HIGH
    for factor in risk_factors:
        risk_factors[factor] = min(risk_factors[factor], RiskLevel.HIGH)


def adjust_risk_factors_by_additional_context(risk_factors: Dict[RiskFactor, RiskLevel], additional_context: Dict[str, Any]):
    external_mitigation = additional_context['external_mitigation']
    heightened_risks = additional_context['heightened_risks']

    # Reduce risk if external mitigation is present
    if external_mitigation == MitigationStatus.PRESENT:
        for factor in risk_factors:
            if risk_factors[factor] != RiskLevel.LOW:
                risk_factors[factor] = RiskLevel(
                    risk_factors[factor].value - 1)

    # Elevate risks based on heightened risks
    for influencer, level in heightened_risks.items():
        if level == RiskLevel.HIGH:
            if influencer == RiskInfluencer.SYSTEM_COMPROMISE:
                risk_factors[RiskFactor.PERSISTENT_ACCESS_RISK] = RiskLevel.HIGH
            elif influencer in [RiskInfluencer.COMPLIANCE_VIOLATION, RiskInfluencer.INTELLECTUAL_PROPERTY_THEFT]:
                # These could potentially affect both primary risk factors
                risk_factors[RiskFactor.PERSISTENT_ACCESS_RISK] = RiskLevel.HIGH

    # Ensure no risk level exceeds HIGH
    for factor in risk_factors:
        risk_factors[factor] = min(risk_factors[factor], RiskLevel.HIGH)


def adjust_risk_factors_by_influencers(risk_factors: Dict[RiskFactor, RiskLevel], service_criticality: RiskLevel, data_sensitivity: RiskLevel):
    # Adjust for service criticality
    if service_criticality == RiskLevel.LOW:
        for factor in risk_factors:
            if risk_factors[factor] != RiskLevel.LOW:
                risk_factors[factor] = RiskLevel(
                    risk_factors[factor].value - 1)

    # Adjust for data sensitivity
    if data_sensitivity in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
        for factor in risk_factors:
            if risk_factors[factor] != RiskLevel.HIGH:
                risk_factors[factor] = RiskLevel(
                    risk_factors[factor].value + 1)

    # Ensure no risk level goes below LOW or above HIGH
    for factor in risk_factors:
        risk_factors[factor] = max(
            min(risk_factors[factor], RiskLevel.HIGH), RiskLevel.LOW)
