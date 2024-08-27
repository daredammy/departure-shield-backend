import json
from core.secret_evaluation import evaluate_overall_secret_risk
from core.file_transfer_evaluation import evaluate_overall_file_transfer_risk


def evaluate_departure_risk(user_id: str) -> dict:
    """
    Evaluate the overall departure risk for a given user by assessing both
    secret access and file transfer risks.

    Args:
        user_id (str): The ID of the user being evaluated.

    Returns:
        dict: A dictionary containing the combined risk assessment results.
    """
    secret_risk = evaluate_overall_secret_risk(user_id)
    file_transfer_risk = evaluate_overall_file_transfer_risk(user_id)

    combined_risk = {
        "user_id": user_id,
        "secret_risk": secret_risk,
        "file_transfer_risk": file_transfer_risk,
        "overall_risk_level": calculate_overall_risk_level(secret_risk, file_transfer_risk)
    }

    return combined_risk


def calculate_overall_risk_level(secret_risk: dict, file_transfer_risk: dict) -> str:
    """
    Calculate the overall risk level based on secret and file transfer risks.

    Args:
        secret_risk (dict): The secret risk assessment results.
        file_transfer_risk (dict): The file transfer risk assessment results.

    Returns:
        str: The overall risk level (LOW, MEDIUM, or HIGH).
    """
    risk_levels = ['low', 'medium', 'high']
    highest_secret_risk = max(
        risk_levels, key=lambda x: len(secret_risk.get(x, [])))
    highest_file_transfer_risk = max(
        risk_levels, key=lambda x: len(file_transfer_risk.get(x, [])))

    if 'high' in [highest_secret_risk, highest_file_transfer_risk]:
        return 'HIGH'
    elif 'medium' in [highest_secret_risk, highest_file_transfer_risk]:
        return 'MEDIUM'
    else:
        return 'LOW'


def generate_risk_summary(risk_assessment: dict) -> str:
    """
    Generate a human-readable summary of the risk assessment.

    Args:
        risk_assessment (dict): The combined risk assessment results.

    Returns:
        str: A formatted summary of the risk assessment.
    """
    summary = f"Departure Risk Summary for User ID: {risk_assessment['user_id']}\n"
    summary += f"Overall Risk Level: {risk_assessment['overall_risk_level']}\n\n"

    summary += "Secret Risk Assessment:\n"
    for level in ['high', 'medium', 'low']:
        secrets = risk_assessment['secret_risk'].get(level, [])
        summary += f"  {level.upper()} Risk Secrets: {len(secrets)}\n"
        for secret in secrets[:3]:  # List up to 3 secrets for each risk level
            summary += f"    - {secret['name']}: {', '.join(secret['risk_factors'].values())}\n"
        if len(secrets) > 3:
            summary += f"    ... and {len(secrets) - 3} more\n"

    summary += "\nFile Transfer Risk Assessment:\n"
    for level in ['high', 'medium', 'low']:
        transfers = risk_assessment['file_transfer_risk'].get(level, [])
        summary += f"  {level.upper()} Risk Transfers: {len(transfers)}\n"
        # List up to 3 transfers for each risk level
        for transfer in transfers[:3]:
            summary += f"    - {transfer['name']}: {', '.join(transfer['risk_factors'].values())}\n"
        if len(transfers) > 3:
            summary += f"    ... and {len(transfers) - 3} more\n"

    return summary


if __name__ == "__main__":
    # Add or modify user IDs as needed
    user_ids = ["emp12345", "emp67890", "emp24680"]
    risk_assessments = []

    for user_id in user_ids:
        risk_assessment = evaluate_departure_risk(user_id)
        risk_assessments.append(risk_assessment)
        print(generate_risk_summary(risk_assessment))
        print("\n" + "-"*50 + "\n")  # Separator between summaries

    # Save the full risk assessments to a JSON file
    with open("departure_risks.json", "w") as f:
        json.dump(risk_assessments, f, indent=2)
    print(f"\nFull risk assessments saved to departure_risks.json")
