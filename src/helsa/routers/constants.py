ACCESS_EXC_MSG_INCORRECT_CREDENTIALS = "Incorrect username or password"
ACCESS_EXC_MSG_USERNAME_EXISTS = "User with this email already exists"
ACCESS_SUCCESS_MSG_USER_CREATED = "User was successfully created!"
ACCESS_TOKEN_TYPE = "bearer"

ACCESS_GET_ACCESS_TOKEN_SUMMARY = "Get access token"
ACCESS_GET_ACCESS_TOKEN_DESCRIPTION = "Obtain access token after authenticating with user credentials"

ACCESS_REGISTER_USER_SUMMARY = "Register new user"
ACCESS_REGISTER_USER_DESCRIPTION = "Upon providing valid `username` and `password`, create and save a distinct new user to db."

ADMIN_SUCCESS_MSG_FLAGS_SET = "User have been updated with flags: {flags}"
ADMIN_EXC_MSG_NO_USER_FLAGS_UNSET = "User was not found. Flags unset."

ADMIN_SET_USER_FLAGS_SUMMARY = "Set flags for a user"
ADMIN_SET_USER_FLAGS_DESCRIPTION = "Allow admin to set and save flags for a user found by username"

DIAGNOSE_LOG_REQUEST_NOT_PARSED = "OpenAI API did not parse the response properly."
DIAGNOSE_EXC_MSG_REQUEST_FAILED = "Requesting diagnose failed, please try again later."
DIAGNOSE_EXC_MSG_OPENAI_VALIDATION_ERROR = "Invalid output from AI service. Please try again later."
DIAGNOSE_EXC_MSG_OPENAI_API_ERROR = "AI service is not available. Please try again later."
DIAGNOSE_EXC_MSG_RATE_LIMIT_ERROR = "Too many requests. Please wait and retry later."
DIAGNOSE_EXC_MSG_BAD_REQUEST_ERROR = "Invalid input"
DIAGNOSE_EXC_MSG_AUTHENTICATION_ERROR = "Authentication with AI service failed."
DIAGNOSE_EXC_MSG_UNEXPECTED_ERROR = "Unexpected error occurred during obtaining diagnoses from AI service."

DIAGNOSE_GET_DIAGNOSE_SUMMARY = "Get AI generated diagnostic response"
DIAGNOSE_GET_DIAGNOSE_DESCRIPTION = \
    "Obtain an AI generated diagnostic response from OpenAI API based on provided patient data."