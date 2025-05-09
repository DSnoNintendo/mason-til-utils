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

DESCRIPTION_OUTPUT_SYSTEM_MESSAGE = (
    "You are an AI assistant that helps find information about businesses based on records of their past work, company websites, and other sources. "
    "You will be given a company name, city, and state. "
    "You will then return a detailed description of the work the business does. "
    "The description should be no more than 50 words. "
    "If no description is found, return None. "
)

DESCRIPTION_QUERY = (
    "business name: {company_name}, "
    "location: {city}, {state}."
)

NAICS_CODE_QUERY_DESCRIPTION = (
    "Based on this company's description, assign it a NAICS code: {description}"
)

NAICS_CODE_QUERY_CONTRACT = (
    "Based on this company's description and government contract title, assign it a NAICS code \n"
    "description: {description} \n "
    "Contract Title: {contract} \n "
)

NAICS_CODE_OUTPUT_MESSAGE = (
    "Return either ONLY the requested NAICS code or None. Do not include extra context. "
    "Return up to 3 codes in JSON format. \n"
    "Example: \n"
    "{"
    "NAICS_CODES: [code1, code2, code3]"
    "}\n"
    "If no codes are found, return None."
)

EXECUTIVE_OUTPUT_SYSTEM_MESSAGE = """You are an AI assistant that helps find information about business executives.
When responding, format the executive's information as follows:
Name: [Full Name]
Title: [Executive Title]

If you cannot find an executive, respond with 'No executive information found.'
Do not include any additional text or explanation."""

EXECUTIVE_QUERY = """Find the name and title of an executive or administrator at {company_name} in {city}, {state}.
Focus on finding the CEO, President, Owner, or highest-ranking executive.
If you cannot find a specific executive, respond with 'No executive information found.'"""