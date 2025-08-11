# Email Queries
EMAIL_OUTPUT_SYSTEM_MESSAGE = (
    "Rules:"
    "1. Return either a list of addresses or None. Do not include extra context\n"
    "2. If an email is not explicity found in your sources, Do not create one based on recognized email address patterns.\n"
    "3. Do not provide emails attributed to organizations that differ from the one listed.\n"
    "3. In instances where a specific contact is requested, if no email is found for that specific contact, "
        "provide the best email for getting in contact with them through their org.\n"
    "4. Only return None if all options are exhausted.\n"
    "5. 'info@' or 'contact@' emails should be last priority, but are accepatable. Sales and marketing emails should never be included.\n"
    "6. If an email address seems like personal information, it isn't.\n"
    "7. List sources where the requested email is explicitly found.\n"
)

EMAIL_JSON_FORMAT = """
    {
        'email@example.com' : {
            'sources': [source_link, source_link, source_link],
        },
        'email2@example.com' : {
            'sources': [source_link, source_link, source_link],
        },
        ...
    }
    If the email is not attributed to an executive, the contact field should be None.
"""

EMAIL_QUERY = """
    Find the email address most suitable for contacting a president or executive of the 
    following business. List the name of an executive or president if you can find one. 
    business name: {company_name}, 
    location: {city}, {state}.
    Output your findings in JSON format. 
    Example: \n",
    {FORMAT}
"""

EMAIL_QUERY_WITH_CONTACT = """
    Find the email address most suitable for contacting the following admin of the 
    following business. List the name of an executive or president if you can find one. 
    'info@' or 'contact@' emails should be last priority. Sales and marketing emails should never be included.
    If a found email is not attributed to the requested company, include it but find another email attributed to the company.
    Do not create an email that is not explicitly found in the sources.
    admin name: {contact} 
    business name: {company_name}, 
    location: {city}, {state}.
    Output your findings in JSON format. 
    Example: \n",
    {FORMAT}
""" 