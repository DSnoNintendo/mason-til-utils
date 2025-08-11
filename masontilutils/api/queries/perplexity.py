# NAICS Code Queries
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





# Business Description Queries
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
        address: string
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
    "address: {address}"
) 