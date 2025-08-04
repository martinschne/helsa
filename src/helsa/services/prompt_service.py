from src.helsa.models.consultation import Prompt, PatientReport, ResponseTone


def _get_configured_temperature(tone: ResponseTone) -> float:
    """
    Helper for getting the prompt temperature value based on requested response tone.

    Returns higher temperature for `funny` or `friendly` response tone, allowing for slightly
    more creative AI responses. Returns low temperature value for `professional` response tone
    as more deterministic and exact output is needed.

    :param tone: requested response tone
    :return: set temperature value
    """
    if tone == ResponseTone.FUNNY or tone == ResponseTone.FRIENDLY:
        return 0.3
    return 0.1


def build_diagnose_prompt(patient_report: PatientReport) -> Prompt:
    """
    Create and return `Prompt` based on data from `PatientReport`.

    :param patient_report: model for holding the data about the patient
    :return: `Prompt` instance constructed from dynamically created system instructions, prompt and temperature.
    """
    system_instruction = f"You are a {patient_report.response_tone} doctor."
    prompt = f"""
    The patient provided following information:
    Age in years: {patient_report.age_years if patient_report.age_years else "N/A"}. 
    Sex assigned at birth is: {patient_report.saab if patient_report.saab else "N/A"}. 
    Symptoms: '{patient_report.symptoms}'
    Duration of the symptoms: '{patient_report.duration if patient_report.duration else "N/A"}'
    If patient provided images, please take them in the account when finding appropriate diagnoses.
    Briefly describe what you see on the images and how it supports/disapproves the diagnoses of your choice.
    If patient provided images that do not display symptoms of a medical condition or unrelated images, e.g. images
    of objects instead of body parts, do NOT take them into account and inform the patient about it.
    Answer shortly, and use {patient_report.response_tone} tone.
    Answer using the same subject and framing as the input. 
    For example, if the input uses 'I' pronoun, respond with using 'you'. 
    If the input indirectly mentions symptoms of 'the patient', respond indirectly too using 'the patient' in the answer.
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
