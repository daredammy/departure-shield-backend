from enum import Enum
from typing import Dict


class FileTransferRiskInfluencer(Enum):
    """Enumeration of factors that influence the file transfer risk assessment."""
    DATA_EXFILTRATION = "data_exfiltration"
    UNAUTHORIZED_SHARING = "unauthorized_sharing"
    SENSITIVE_INFORMATION_EXPOSURE = "sensitive_information_exposure"
    COMPLIANCE_VIOLATION = "compliance_violation"
    INTELLECTUAL_PROPERTY_LOSS = "intellectual_property_loss"
    ACTIVITY_TYPE = "activity_type"
    FILE_SIZE = "file_size"


class FileTransferMitigationStatus(Enum):
    PRESENT = "present"
    PARTIAL = "partial"
    ABSENT = "absent"


class FileTransferRiskLevel(Enum):
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


class FileTransferRiskFactor(Enum):
    """Enumeration of risk factors considered in the file transfer assessment."""
    DATA_EXFILTRATION = "data_exfiltration"


FILE_TRANSFER_RISK_MITIGATION_STRATEGIES: Dict[FileTransferRiskFactor, Dict[FileTransferRiskLevel, str]] = {
    FileTransferRiskFactor.DATA_EXFILTRATION: {
        FileTransferRiskLevel.HIGH: "Contact legal department and contact employee to ask for justification",
        FileTransferRiskLevel.MEDIUM: "Contact employee and ask for justification",
        FileTransferRiskLevel.LOW: "No action required"
    },
}


# Constants for risk assessment thresholds
HIGH_RISK_FILE_SIZE_MB = 100
MEDIUM_RISK_FILE_SIZE_MB = 10

DAYS_SINCE_HIGH_TRANSFER_RISK = 1
DAYS_SINCE_MEDIUM_TRANSFER_RISK = 7

HIGH_RISK_ACTIVITIES = ['Bulk Transfer', 'Data Export']
MEDIUM_RISK_ACTIVITIES = ['File Sharing']


def string_to_file_transfer_risk_level(level_str: str) -> FileTransferRiskLevel:
    level_map = {
        "LOW": FileTransferRiskLevel.LOW,
        "MEDIUM": FileTransferRiskLevel.MEDIUM,
        "HIGH": FileTransferRiskLevel.HIGH
    }
    # Default to LOW if unknown
    return level_map.get(level_str.upper(), FileTransferRiskLevel.LOW)
