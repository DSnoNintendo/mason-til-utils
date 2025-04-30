CODE_OUTPUT_SYSTEM_MESSAGE = (
    "Rules: "
    "1. Return either ONLY the requested NAICS code or None. Do not include extra context. "
    "2. Do not make assumptions. All results should be sourced. "
)

NAICS_CODE_QUERY = (
    "Return a 6 digit NAICS code for the following company. "
    "Name: {company_name}, "
    "Location: {city}, {state} "
)

EMAIL_OUTPUT_SYSTEM_MESSAGE = (
    "Rules:"
    "1. Return either a list of addresses or None. Do not include extra context"
    "2. In instances where a specific contact is requested, if no email is found for that specific contact, "
        "provide the best email for getting in contact with them through their org. "
    "3. Only return None if all options are exhausted. "
    "4. Do not make guesses."
    "5. If an email address seems like personal information, it isn't."
)

PERPLEXITY_EMAIL_QUERY = (
    "Find the email address most suitable for contacting an administrator for the "
    "following business "
    "business name: {company_name}, "
    "location: {city}, {state}."
)

PERPLEXITY_EMAIL_QUERY_WITH_CONTACT = (
    "Find the email address most suitable for contacting the following admin of the "
    "following business "
    "admin name: {contact} "
    "business name: {company_name}, "
    "location: {city}, {state}."
)

MARK_EMAIL_CHECKED_QUERY = (
    "UPDATE {table_name} "
    "SET Checked = True "
    "WHERE {id_column_name} = {id} ;"
)

MARK_EMAIL_FOUND_QUERY = (
    "UPDATE {table_name} "
    "SET EmailFound = True "
    "WHERE {id_column_name} = {id} ;"
)

