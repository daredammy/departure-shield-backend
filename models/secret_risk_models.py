# risk_definitions.py

from enum import IntEnum
from enum import Enum, auto
from typing import Dict


class RiskInfluencer(Enum):
    """Enumeration of factors that influence the primary risk factors."""
    DATA_EXFILTRATION = "data_exfiltration"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SYSTEM_COMPROMISE = "system_compromise"
    COMPLIANCE_VIOLATION = "compliance_violation"
    INTELLECTUAL_PROPERTY_THEFT = "intellectual_property_theft"
    SERVICE_CRITICALITY = "service_criticality"
    DATA_SENSITIVITY = "data_sensitivity"


class MitigationStatus(Enum):
    PRESENT = "present"
    PARTIAL = "partial"
    ABSENT = "absent"


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented


class RiskFactor(Enum):
    """Enumeration of risk factors considered in the assessment."""
    PERSISTENT_ACCESS_RISK = "rotation_risk"
    DATA_EXFILTRATION = "recent_access_risk"
    SERVICE_CRITICALITY = "service_criticality"
    DATA_SENSITIVITY = "data_sensitivity"


RISK_MITIGATION_STRATEGIES: Dict[RiskFactor, Dict[RiskLevel, str]] = {
    RiskFactor.PERSISTENT_ACCESS_RISK: {
        RiskLevel.HIGH: "Rotate key within the next 7 days",
        RiskLevel.MEDIUM: "Rotate key within the next 30 days",
        RiskLevel.LOW: "Track any anomalous actions"
    }
}


def string_to_risk_level(level_str: str) -> RiskLevel:
    level_map = {
        "LOW": RiskLevel.LOW,
        "MEDIUM": RiskLevel.MEDIUM,
        "HIGH": RiskLevel.HIGH
    }
    # Default to LOW if unknown
    return level_map.get(level_str.upper(), RiskLevel.LOW)
