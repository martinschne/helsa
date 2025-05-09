from app.models.consultation import Prompt, PatientReport, ResponseTone


def _get_configured_temperature(tone: ResponseTone) -> float:
    if tone == ResponseTone.FUNNY or tone == ResponseTone.FRIENDLY:
        return 0.3
    return 0.1


def build_diagnose_prompt(patient_report: PatientReport) -> Prompt:
    """
    May raise validation error.
    :param patient_report:
    :return:
    """
    system_instruction = f"You are a {patient_report.response_tone} doctor."
    prompt = f"""
    The patient describes following symptoms: '{patient_report.symptoms}'
    The patient says about the duration of the symptoms: '{patient_report.duration if patient_report.duration else "N/A"}'
    If patient provided images, please take them in the account when finding appropriate diagnoses.
    Briefly describe what you see on the images and how it supports/disapproves the diagnoses of your choice.
    If patient provided images that do not display symptoms of a medical condition or unrelated images, e.g. images
    of objects instead of body parts, do NOT take them into account and inform the patient about it.
    Answer shortly, and use {patient_report.response_tone} tone.
    Address the person directly using 'you' in the answer.
    Use {patient_report.language_style} language in the answer, as if you were speaking to an average person aged: 
    {patient_report.age_years if patient_report.age_years else "N/A"}.
    What would be the possible diagnosis and what are the recommended steps for the patient to do?
    Please provide at least one possible diagnose, with considering all other possible diagnoses.
    """

    return Prompt(
        system_instruction=system_instruction,
        query=prompt,
        temperature=_get_configured_temperature(patient_report.response_tone)
    )
