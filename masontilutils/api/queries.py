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

PERPLEXITY_EMAIL_JSON_FORMAT = """
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


PERPLEXITY_EMAIL_QUERY = """
    Find the email address most suitable for contacting a president or executive of the 
    following business. List the name of an executive or president if you can find one. 
    business name: {company_name}, 
    location: {city}, {state}.
    Output your findings in JSON format. 
    Example: \n",
    {FORMAT}
"""

PERPLEXITY_EMAIL_QUERY_WITH_CONTACT = """
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

DESCRIPTION_OUTPUT_JSON = """
{{
    "description": string or null
}}
"""

DESCRIPTION_OUTPUT_SYSTEM_MESSAGE = f"""
    <role>
        You are an AI assistant that provides descriptions of businesses
    </role>

    <request_format>
        business name: string
        state: string
        city: string
    </request_format>

    <response_json>
        {DESCRIPTION_OUTPUT_JSON}
    </response_json>

    <rules>
        1. Keep descriptions to 60 words at most
        2. Do not include company name or location in descriptions
        3. Do not include any details unrelated to the specific work the business does
        4. If no description is found, return None.
    </rules>
"""
    

DESCRIPTION_QUERY = (
    "business name: {company_name}"
    "state: {state}"
    "city: {city}"
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
    "Return either ONLY the requested NAICS code and industry classification or None. Do not include extra context. "
    "Return up to 3 codes in JSON format."
    "{"
    "1: code1 (or None if no code is found), "
    "2: code2 (or None if no code is found), "
    "3: code3 (or None if no code is found)"
    "}"
    "Emphasize correct JSON formatting."
)

EXECUTIVE_RESPONSE_JSON_FORMAT = """
    {{
        1 :
            {{ 
                name: string,
                role: string,
                sources: [https://link, https://link]
                }}
            }},
            ...
    }}
""" 

EXECUTIVE_NONE_IDENTIFIER = "None"

PUBLICALLY_TRADED_IDENTIFIER = "company_publically_traded"

EXECUTIVE_OUTPUT_SYSTEM_MESSAGE = f"""
<role>
You are an AI assistant that helps find information about business owners & executives using information on the company like name and location.
</role>

<rules> 
    1. If the company is publically traded, respond with {PUBLICALLY_TRADED_IDENTIFIER}.
    2. If the company is not publically traded, respond with {EXECUTIVE_RESPONSE_JSON_FORMAT}.
    3. If you cannot find an executive, respond with {EXECUTIVE_NONE_IDENTIFIER}.
    4. Only include owners and executives. Do not include employees.
    5. Do not include any additional text or explanation.
</rules>

<request_format>
    <json>
        company_name: string,
        city: string,
        state: string
        address:
    </json>
</request_format>
"""

EXECUTIVE_QUERY = """
<json>
    company_name: {company_name},
    city: {city},
    state: {state}
    address: {address}
</json>
"""

INDUSTRY_CLASSIFICATION_JSON_FORMAT = """
    {{
        "1" : {{
                "NAICS": string - naics_code or null,
                "NAICS_Definition: string - meaning of naics code,
                "industry_code": string - industry_code or null
        }},
        "2" : {{
                "NAICS": string - naics_code or null,
                "NAICS_Definition: string - meaning of naics code,
                "industry_code": string - industry_code or null
        }},
        "3" : {{
                "NAICS": string - naics_code or null,
                "NAICS_Definition: string - meaning of naics code,
                "industry_code": string - industry_code or null
        }},
    }}
""" 

INDUSTRY_CLASSIFICATION_SYSTEM_MESSAGE = f"""
<role>
    You are an AI assistant that processes business descriptions and assigns them to a maximum of 3 NAICS codes and given industry codes. 
</role>

<industry_codes>
    A - Architecture
    C - Construction
    G - Goods
    S - Services
    I - IT Goods & Services
    P - Professional Services
    O - Other
</industry_codes>

<request_format> 
    String: Description of company
</request_format>

<response_json>
    {INDUSTRY_CLASSIFICATION_JSON_FORMAT}
</response_json>

<rules>
    1. Ensure differentiation between goods, services, IT goods & services, and professional services based on standard industry classification definitions
    2. Each NAICS code should she be mapped to one of the above industry codes. 
    2. Prioritize accuracy. Given descriptions do not necessarily need to correspond with given industry codes.
    4. Only assign other, if no industry codes have been assigned
    6. If an industry code has already been assigned in an earlier JSON item, similar naics codes (first 4 digits) should be left out of the final output
    7. Trades are not professional services. Do not assign NAICS codes in these instances.
    8. Goods and/or services imply a company sells to an end-user. Manufacturers may not always be goods or services.
</rules>

"""


