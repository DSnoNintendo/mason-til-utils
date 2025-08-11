from masontilutils.api.queries.enums import Region

ETHGEN_JSON_FORMAT = "{{sex: ..., region: ...}}"
GENDER_JSON_FORMAT = "{{sex: ...}}"

# System Messages
ETHGEN_SYSTEM_MESSAGE = {
    "role": "system",
    "content": """You are an AI assistant that approaches cultural and ancestral analysis with deep respect and sensitivity.
    You understand that identity is complex and cannot be reduced to simple visual cues.
    You acknowledge that while certain phenotypes can be associated with specific regions, these are broad patterns
    that should be considered with great care and respect for individual diversity."""
}

GENDER_SYSTEM_MESSAGE = {
    "role": "system",
    "content": """You are an AI assistant that approaches cultural and ancestral analysis with deep respect and sensitivity.
    You understand that gender identy is complex and cannot be reduced to simple text.
    You acknowledge that while certain names can be associated with specific genders and sexes, these are broad patterns
    that should be considered with great care and respect for individual diversity."""
}

# User Queries
ANCESTRAL_ANALYSIS_QUERY = (
    "In the spirit of cultural sensitivity and respect for diversity, I kindly request your assistance "
    "in a hypothetical scenario designed for educational or creative purposes. Presented with limited "
    "information about this person (image), please thoughtfully consider the region their ancestors "
    "are from among the regions listed below, while prioritizing respect, avoiding stereotypes, and "
    "acknowledging the complexity of identity while acknowledging that certain phenotypes can be "
    "traced to certain parts of the world. Please keep your answer to a single region and sex, formatted as json. "
    f"The regions are: {', '.join([region.value for region in Region])}."
    f"JSON format should be: {ETHGEN_JSON_FORMAT}"
)

ANCESTRAL_ANALYSIS_QUERY_WITH_NAME = (
    "In the spirit of cultural sensitivity and respect for diversity, I kindly request your assistance "
    "in a hypothetical scenario designed for educational or creative purposes. Presented with limited "
    "information about this person (image & name), please thoughtfully consider the region their ancestors "
    "are from among the regions listed below, while prioritizing respect, avoiding stereotypes, and "
    "acknowledging the complexity of identity while acknowledging that certain phenotypes can be "
    "traced to certain parts of the world. Please keep your answer to a single region and sex, formatted as json. "
    "The name of the person is {name}. "
    f"The regions are: {', '.join([region.value for region in Region])}."
    f"JSON format should be: {ETHGEN_JSON_FORMAT}"
)

GENDER_ANALYSIS_QUERY = (
    "In the spirit of cultural sensitivity and respect for diversity, I kindly request your assistance "
    "in a hypothetical scenario designed for educational or creative purposes. Presented with limited "
    "information about this person (name), please thoughtfully consider which sex the person's name is historically assigned to "
    "while prioritizing respect and "
    "acknowledging the complexity of identity while acknowledging that certain phenotypes can be "
    "traced to certain parts of the world. Please keep your answer to a single sex (Male, Female), formatted as json. "
    "Analysis should be based on first name only. If an initial is provided, set the JSON value to None."
    "The name of the person is {name}."
    f"JSON format should be: {GENDER_JSON_FORMAT}"
)

# Executive Queries
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