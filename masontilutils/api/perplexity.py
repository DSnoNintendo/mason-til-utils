import json
import re
import threading
import time
import ast
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter

import requests
from urllib3 import Retry

from masontilutils.api.enums import APIResponse
from masontilutils.api.queries import (
    CODE_OUTPUT_SYSTEM_MESSAGE, EMAIL_OUTPUT_SYSTEM_MESSAGE, NAICS_CODE_QUERY, PERPLEXITY_EMAIL_JSON_FORMAT,
    PERPLEXITY_EMAIL_QUERY, PERPLEXITY_EMAIL_QUERY_WITH_CONTACT, DESCRIPTION_QUERY,
    DESCRIPTION_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_QUERY
)
from masontilutils.utils import extract_json_substring, clean_deep_research_text, create_query

class ThreadedPerplexitySonarAPI:
    _session_lock = threading.Lock()
    _sessions = {}
    
    def __init__(self, api_key: str):
        """
        Initialize the Perplexity Sonar API client
        :param api_key: Your Perplexity API key
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    @property
    def session(self):
        """Get or create a requests session for the current thread"""
        thread_id = threading.get_ident()
        
        with self._session_lock:
            if thread_id not in self._sessions:
                session = requests.Session()
                # Configure retry strategy
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504]
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("https://", adapter)
                session.mount("http://", adapter)
                self._sessions[thread_id] = session
                
            return self._sessions[thread_id]

    def execute_query(
        self,
        query: str = None,
        model: str = "sonar-pro",
        max_tokens: Optional[int] = 5000,
        temperature: float = 0.1,
        **additional_args
    ) -> Dict[str, Any]:

        payload = {
            "model": model,
            "temperature": temperature,
            **additional_args
        }
        
        if query is not None:
            payload["messages"] = [{"role": "user", "content": query}]
        elif "messages" not in payload and "messages" not in additional_args:
            payload["messages"] = []
            
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        max_retries = 5
        base_delay = 5  # Base delay in seconds
        current_retry = 0

        while current_retry < max_retries:
            try:
                response = self.session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=500
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                print(f"API request failed: {str(e)}")
                if e.response.status_code == 429:
                    # Get rate limit information from headers
                    retry_after = int(e.response.headers.get('Retry-After', base_delay * (2 ** current_retry)))
                    reset_time = e.response.headers.get('X-RateLimit-Reset')
                    
                    print(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                    if reset_time:
                        print(f"Rate limit resets at: {reset_time}")
                    
                    # Sleep for the specified time
                    time.sleep(retry_after)
                    current_retry += 1
                    continue
                else:
                    print(f"API request failed: {str(e)}",
                        f"Status code: {e.response.status_code if hasattr(e, 'response') and e.response else None}")
                    return {
                        "error": f"API request failed: {str(e)}",
                        "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
                    }

            except requests.exceptions.RequestException as e:
                print(f"API request failed: {str(e)}",
                    f"Status code: {e.response.status_code if hasattr(e, 'response') and e.response else None}")
                return {
                    "error": f"API request failed: {str(e)}",
                    "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
                }

        # If we've exhausted all retries
        return {
            "error": "Max retries exceeded for rate limit",
            "status_code": 429
        }
        
class PerplexityNAICSCodeAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def extract_code(self, str):
        """Extract the NAICS code from the response"""
        match = re.search(r"\d{6}", str)
        return match.group(0) if match else None

    def call(self,
             company_name: str,
             city: str,
             state: str,
        ) -> str | None:

        system_role = {"role": "system", "content": CODE_OUTPUT_SYSTEM_MESSAGE}

        query = NAICS_CODE_QUERY.format(
            company_name=company_name,
            city=city,
            state=state
        )

        response = super().execute_query(
            messages=[system_role, {"role": "user", "content": query}]
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            print(answer)
            return self.extract_code(answer)
        else:
            print(f"Error: {response['error']}")
            return None


class PerplexityEmailAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        self.email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        super().__init__(api_key)

    def email_valid(self, email: str) -> bool:
        """Check if an email is valid"""
        return re.match(self.email_regex, email) is not None
    
    def build_response(self, results) -> List[dict]:
        res = list()
        if results:
            json_string = extract_json_substring(results)
            # Ensure the JSON string has proper string keys
            json_string = re.sub(r'(\d+)\s*:', r'"\1":', json_string)
            loaded_json = ast.literal_eval(json_string)
            for key, value in loaded_json.items():
                email_dict = dict()
                if self.email_valid(key):
                    email_dict["email"] = key
                    email_dict["sources"] = value["sources"]
                    res.append(email_dict)
        else:
            return res

        return res

    def call(self,
             company_name: str,
             city: str,
             state: str,
             contact: str | None = None,
        ) -> dict:

        system_role = {"role": "system", "content": EMAIL_OUTPUT_SYSTEM_MESSAGE}


        if contact:
            query = create_query(query=PERPLEXITY_EMAIL_QUERY_WITH_CONTACT, 
                                 company_name=company_name, 
                                 city=city, 
                                 state=state,
                                 contact=contact,
                                 FORMAT=PERPLEXITY_EMAIL_JSON_FORMAT)
        else:
            query = create_query(query=PERPLEXITY_EMAIL_QUERY, 
                                 company_name=company_name, 
                                 city=city, 
                                 state=state,
                                 FORMAT=PERPLEXITY_EMAIL_JSON_FORMAT)

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )

        answer = response["choices"][0]["message"]["content"]

        if "error" not in response:
            reply = clean_deep_research_text(answer)
            if "None" in reply:
                return None
            return self.build_response(results=reply)
        else:
            print(f"Error: {response['error']}")
            return None

class PerplexityBusinessDescAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def call(self,
             company_name: str,
             city: str,
             state: str,
        ) -> str | None:

        system_role = {"role": "system", "content": DESCRIPTION_OUTPUT_SYSTEM_MESSAGE}

        query = DESCRIPTION_QUERY.format(
            company_name=company_name,
            city=city,
            state=state
        )

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[system_role, {"role": "user", "content": query}]
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            if "None" in answer:
                return None
            return clean_deep_research_text(answer)
        else:
            print(f"Error: {response['error']}")
            return None

class PerplexityExecutiveAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.publically_traded_identifier = "comapny_publically_traded"

    def build_response(self, results) -> List[dict]:
        res = list()
        if results:
            try:
                json_string = clean_deep_research_text(results)
                json_string = extract_json_substring(json_string)
                # Ensure the JSON string has proper string keys
                json_string = re.sub(r'(\d+)\s*:', r'"\1":', json_string)
                loaded_json = ast.literal_eval(json_string)
                print(loaded_json)
                for key, value in loaded_json.items():
                    res.append(value)
            except Exception as e:
                print(f"Error: {e}")
                return json_string
        else:
            res = list()

        return res

    def extract_executive(self, text: str) -> List[dict] | None:
        """Extract executive information from the response"""
        # Look for patterns like "Name: John Smith" or "Title: CEO"
        name_match = re.search(r"Name:\s*([^\n]+)", text, re.IGNORECASE)
        title_match = re.search(r"Title:\s*([^\n]+)", text, re.IGNORECASE)
        
        if name_match and title_match:
            return {
                "name": name_match.group(1).strip(),
                "title": title_match.group(1).strip()
            }
        return None

    def call(self,
             company_name: str,
             city: str,
             state: str,
        ) -> dict:

        print(EXECUTIVE_OUTPUT_SYSTEM_MESSAGE.format(
            publically_traded_identifier=self.publically_traded_identifier))

        system_role = {
            "role": "system", "content": EXECUTIVE_OUTPUT_SYSTEM_MESSAGE.format(
            publically_traded_identifier=self.publically_traded_identifier)
        }

        query = EXECUTIVE_QUERY.format(
            company_name=company_name,
            city=city,
            state=state
        )

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            if self.publically_traded_identifier in clean_deep_research_text(answer):
                return "C"
            elif "None" in clean_deep_research_text(answer):
                return None
            
            res =  self.build_response(results=answer)
            return res
        else:
            print(f"Error: {response['error']}")
            return None


def build_response(results) -> List[dict]:
        res = list()
        if results:
            try:
                json_string = clean_deep_research_text(results)
                json_string = extract_json_substring(json_string)
                # Ensure the JSON string has proper string keys
                json_string = re.sub(r'(\d+)\s*:', r'"\1":', json_string)
                loaded_json = ast.literal_eval(json_string)
                for key, value in loaded_json.items():
                    res.append(value)
            except Exception as e:
                print(f"Error: {e}")
                return json_string
        else:
            res = list()

        return res

test = """
<think>
We are given a query to find the name, title, and email of an executive or administrator at 3SIXTY INNOVATION INC in SAN DIEGO, CA, focusing on the CEO, President, Owner, or highest-ranking executive.

We have multiple search results. Let's analyze each one:

[1] This result is about Mike Muhsin, who is the Chief Executive Officer at Success.ai and also President & CEO at KLTS LIMOUSINE since 2008. It also mentions he is the Chief Executive Officer at 3SIXTY INNOVATION INC since 2003. The email is masked: mi****@kl****.com. This suggests that Mike Muhsin is the CEO of 3SIXTY INNOVATION INC.

[2] This is a company overview of 3Sixty Innovation Inc. as a general contractor. It doesn't provide executive information.

[3] This page lists contacts for 3Sixty Innovation Inc. Among the contacts are:
   - Mohamad Muhsin
   - Mike Muhsin
   - Angela Watts
   - Bill Abdelfattah
   - Bill Abdel
The email addresses are masked (e.g., @3sixtyinnovation.com). This confirms that Mike Muhsin is associated with the company.

[4] This ZoomInfo page for 3Sixty Innovation lists the company's headquarters and phone number, but no specific executives.

[5] This page is about 3Sixty Integrated, which is a different company (a division of The Cook & Boardman Group). Not relevant.

[6] This is a real estate agent listing. Not relevant.

[7] This page about 3Sixty Innovation Inc. lists two addresses but no executive names.

[8] This is a PDF of a tax return. It doesn't mention 3Sixty Innovation Inc.

[9] This is a directory of associate members. Not relevant.

[10] This is a tax return for The American Society for the Prevention of Cruelty to Animals. Not relevant.

[11] This is a tax return for The Nature Conservancy. Not relevant.

[12] This page is about the leadership team of 3Sixty Insights, Inc. (a different company). Not relevant.

[13] This page is about Robyn Joliat, CTO of 3Sixty (a relocation company). Not relevant.

[14] This Buzzfile page states: "Mohamad Muhsin is the Chief Executive Officer at 3sixty Innovation." and provides the phone number (858) 304-1093.

[15] This PDF from a community college district lists registered contractors. It includes:
   - 3SIXTY INNOVATION INC.
   - Contact: MOHAMAD MUHSIN
   - Email: ESTIMATING@3SIXTYINNOVATION.COM
   - Phone: 858-304-1093

From the above, we have two names: Mike Muhsin and Mohamad Muhsin. Both are associated with 3Sixty Innovation Inc.

In [1], Mike Muhsin is listed as the Chief Executive Officer of 3SIXTY INNOVATION INC. since 2003.

In [14] and [15], Mohamad Muhsin is listed as the CEO.

However, note that in [3], both Mohamad Muhsin and Mike Muhsin are listed as contacts. This suggests that both are involved in the company.

But the query asks for the CEO, President, Owner, or highest-ranking executive. We need to determine who holds the top position.

Looking at [1]: Mike Muhsin is the Chief Executive Officer at 3SIXTY INNOVATION INC. and has been since 2003.

In [15], the contact for the company is Mohamad Muhsin, but the title is not specified. The email is for estimating, which might be a department.

Given that [1] explicitly states Mike Muhsin as CEO and [14] states Mohamad Muhsin as CEO, there might be a discrepancy.

But note that [1] is from a professional profile (Success.ai) and [14] is from Buzzfile. We should consider the recency and reliability.

Also, in [3] (from a construction projects site), both names are listed as contacts. This suggests that both are executives, but we are looking for the highest-ranking.

Given that Mike Muhsin is listed as CEO in [1] and has been with the company since 2003, and Mohamad Muhsin is also listed as CEO in [14], it is possible that there are two executives. However, the query asks for one executive (the highest-ranking).

Alternatively, it is possible that Mike and Mohamad are the same person? But the names are different.

Looking at the email pattern: in [3], the email domain is @3sixtyinnovation.com. We don't have the full email for either.

In [15], the email for Mohamad Muhsin is estimating@3sixtyinnovation.com, which is likely a departmental email.

We need to find the email of the CEO.

From [1], the email for Mike Muhsin is masked: mi****@kl****.com. This is from his profile at KLTS LIMOUSINE, not necessarily his email at 3Sixty.

We don't have a direct email for Mike Muhsin at 3Sixty.

But in [3], we have a list of contacts with the domain @3sixtyinnovation.com. We can infer that the email for Mike Muhsin would be in the pattern: first initial + last name or similar. However, without more information, we cannot be sure.

Given the query, we are to return the executive information in a specific JSON format.

We have two candidates:

1. Mike Muhsin, CEO (from [1])
2. Mohamad Muhsin, CEO (from [14])

But note that in [15], the contact for the company in a contractor list is Mohamad Muhsin, but that doesn't specify his title.

We must choose the one that is the highest-ranking. Since both are called CEO, we need to see if there is more recent information.

The search results have different dates. [1] is from 2008, but it says Mike has been CEO since 2003 and still present. [14] is from 2023, which is more recent.

[14] explicitly states: "Mohamad Muhsin is the Chief Executive Officer at 3sixty Innovation."

Therefore, we can conclude that as of 2023, Mohamad Muhsin is the CEO.

But wait, in [3] (which is from 2023-09-11) both names are listed. So both are currently associated.

However, the query asks for the highest-ranking executive. We must choose one.

Given that [14] (from 2023) and [15] (from 2023) both point to Mohamad Muhsin as the CEO, and [1] is older and might be outdated, we should go with Mohamad Muhsin.

But note: [1] is a profile of Mike Muhsin and he lists his current position as CEO of 3SIXTY INNOVATION INC. until the present (2008-present). So it's possible he is still the CEO.

Alternatively, it's possible that Mike and Mohamad are the same person? The names are different: Mike vs Mohamad. But in some cultures, Mike can be a nickname for Mohamad? Not typically.

Looking at the phone numbers:
- In [1], Mike Muhsin's phone number is +1858304**** (masked).
- In [3], both Mike and Mohamad have the same area code (858) and the same prefix (304). The last four digits are masked for Mike in [1] and not provided for Mohamad in [3]. But the company phone in [4] is (858) 304-1093.

In [15], the phone number for Mohamad Muhsin is 858-304-1093.

In [3], the phone number for both Mike and Mohamad is (858) (without the rest). But the company phone in [4] is (858) 304-1093.

So it's the same phone number.

This suggests that Mike Muhsin and Mohamad Muhsin might be the same person? Or they share the same phone number.

But in [3], they are listed as two separate contacts.

Given the confusion, we must rely on the most direct evidence.

The query is for 3SIXTY INNOVATION INC in SAN DIEGO, CA.

In [15] (a PDF from a community college district), the company 3SIXTY INNOVATION INC. is registered with contact MOHAMAD MUHSIN and email estimating@3sixtyinnovation.com.

But that email is for estimating, not necessarily the CEO.

In [14] (Buzzfile), it explicitly says Mohamad Muhsin is the CEO.

In [1], Mike Muhsin is the CEO.

We have two sources claiming two different people as CEO.

But note that [1] is a profile that might not have been updated, while [14] and [15] are from 2023.

Moreover, in [3] (a construction projects site from 2023), both are listed, but without titles.

Given the recency of [14] and [15], we will go with Mohamad Muhsin as the CEO.

However, we must also consider the possibility that the company has two executives. But the query asks for the highest-ranking, so we should pick one.

Alternatively, we can return both? But the query says "an executive", meaning one.

But the personalization says: "format the executive information in a json string" and then shows an example with multiple executives. So we can return multiple.

The example has:
{
    1: { ... },
    2: { ... }
}

So we can have multiple entries.

But the query says: "Find the name, title, and email of an executive or administrator" (singular). However, the example format allows multiple.

Given that we have two candidates, we can return both.

But we must verify their titles.

For Mohamad Muhsin:
- [14] says he is the Chief Executive Officer.
- [15] lists him as the contact, but without a title.

For Mike Muhsin:
- [1] says he is the Chief Executive Officer.

So both are claimed as CEO.

This is conflicting.

Alternatively, it's possible that Mike Muhsin is the CEO and Mohamad Muhsin is also an executive but with a different title? In [3], they are both listed without titles.

We need to resolve this.

Looking at the company website? But we don't have it in the search results.

Given the information, we can return both and note the sources.

But the personalization says: "If you cannot find an executive, respond with 'None'." We have found executives.

We'll return both, with the titles we have.

For Mike Muhsin:
- Title: Chief Executive Officer (from [1])
- Sources: [1], [3]
- Email: We don't have a direct email. In [3], the email is masked. We can try to infer: mike.muhsin@3sixtyinnovation.com? But we don't have confirmation.

For Mohamad Muhsin:
- Title: Chief Executive Officer (from [14])
- Sources: [14], [15]
- Email: In [15], the email is estimating@3sixtyinnovation.com, which is not personal. We don't have a personal email.

The personalization requires email as a dictionary with contact and sources.

We don't have personal emails for either.

But in [3], we have the domain, so we can construct? But without the full email, we cannot be sure.

Alternatively, we can leave the email as unknown? But the format requires an email dictionary.

The example has:
"email": {
    "email1@example.com": {
        "contact": "...",
        "sources": ["link", "link"]
    }
}

We don't have any email addresses for these individuals.

Therefore, we cannot provide an email.

But the query asks for email.

We must do our best.

In [15], we have an email for Mohamad Muhsin: estimating@3sixtyinnovation.com. But this is likely a departmental email, not personal.

Similarly, we don't have any email for Mike.

We can use the company email domain and make an educated guess? But that might be inaccurate.

Alternatively, we can omit the email if we don't have it? But the format requires it.

The personalization says: "If you cannot find an executive, respond with 'None'." We have found executives, but without email.

We must return the information we have.

We'll return the names and titles, and for email, we'll use the company email domain and the common pattern: firstname.lastname@3sixtyinnovation.com.

But without confirmation, this is speculative.

Alternatively, we can use the email from [15] for Mohamad, but it's for estimating.

Given the constraints, we will return:

For Mohamad Muhsin:
- Name: Mohamad Muhsin
- Title: Chief Executive Officer (from [14])
- Sources: [14], [15]
- Email: We don't have a personal email, but we have estimating@3sixtyinnovation.com from [15]. We can use that, noting it's the estimating department.

But the example format has multiple emails per person. We can include that one.

Similarly, for Mike Muhsin, we don't have any email.

We can skip Mike and only return Mohamad? But we have two sources for Mike as CEO.

Alternatively, we can return both and for email, use the company domain and a pattern.

But without confirmation, we cannot be sure.

Given the above, we decide to return:

1. Mohamad Muhsin as CEO, with the email from [15] (estimating@3sixtyinnovation.com) and note that it's the estimating department.

But the personalization says: "email" should be a dictionary of email addresses with contact and sources.

We can do:

For Mohamad Muhsin:
"email": {
    "estimating@3sixtyinnovation.com": {
        "contact": "Estimating Department",
        "sources": ["https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"]
    }
}

But that email is not his personal email.

Alternatively, we can leave the email field empty? But the format requires it.

We must provide what we have.

We'll use the email we have, even if it's not personal.

Similarly, for Mike, we have no email, so we cannot include an email for him.

But the example format has the email as a required part.

We'll return only Mohamad Muhsin, because we have a more recent source (2023) and an email (even if it's not personal).

But note: [14] (Buzzfile) is from 2023 and says Mohamad is the CEO, and [15] (a PDF) also lists him as the contact.

So we return:

{
    1: {
        "name": "Mohamad Muhsin",
        "role": "Chief Executive Officer",
        "sources": [
            "https://www.buzzfile.com/business/3sixty-Innovation,-Inc.-858-304-1093",
            "https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"
        ],
        "email": {
            "estimating@3sixtyinnovation.com": {
                "contact": "Estimating Department",
                "sources": ["https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"]
            }
        }
    }
}

But wait, the query asks for the highest-ranking executive. We are returning one.

Alternatively, we can also return Mike Muhsin as CEO from the older source? But we have a conflict.

Given the recency, we go with Mohamad.

But note: in [1], Mike is still listed as CEO until present. So it's possible he is still the CEO.

We must decide.

Another approach: in [3], the contacts are listed, and Mike Muhsin is listed first? Actually, the order is:
1. Mohamad Muhsin
2. Mike Muhsin
3. Angela Watts
4. Bill Abdelfattah
5. Bill Abdel

So Mohamad is listed first, which might indicate he is the primary contact.

Therefore, we return Mohamad Muhsin as the CEO.

Final decision: return Mohamad Muhsin.

But note: the query says "in SAN DIEGO, CA". The company is in San Diego, and both are in San Diego.

We'll return the JSON for Mohamad Muhsin.

However, the personalization says: "If the given company is publically traded, though, simply respond with 'comapny_publically_traded'." We don't have information that 3SIXTY INNOVATION INC is publicly traded. It appears to be a private company.

So we proceed.

The JSON:

{
    1: {
        "name": "Mohamad Muhsin",
        "role": "Chief Executive Officer",
        "sources": [
            "https://www.buzzfile.com/business/3sixty-Innovation,-Inc.-858-304-1093",
            "https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"
        ],
        "email": {
            "estimating@3sixtyinnovation.com": {
                "contact": "Estimating Department",
                "sources": ["https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"]
            }
        }
    }
}

But note: the email is not a personal email. We are using the email from the contractor registration, which is for the estimating department.

We have no other email.

Alternatively, we can try to find an email in the search results.

In [3], the emails are masked. We cannot see them.

In [4], the website is www.3sixtyinnovation.com, but we don't have a contact page.

We have to use what we have.

So we return the above.

But note: the example in the personalization has multiple emails per person. We have only one.

We'll do that.

But wait, the personalization says: "Do not include any additional text or explanation."

So we output the JSON.

However, we have two sources for the role: [14] for the role and [15] for the email.

We must cite the sources correctly.

Now, writing the JSON.
</think>
{
    1: {
        "name": "Mohamad Muhsin",
        "role": "Chief Executive Officer",
        "sources": [
            "https://www.buzzfile.com/business/3sixty-Innovation,-Inc.-858-304-1093",
            "https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"
        ],
        "email": {
            "estimating@3sixtyinnovation.com": {
                "contact": "Estimating Department",
                "sources": ["https://www.gcccd.edu/purchasing-contracts/contractors/registered-contractors.pdf"]
            }
        }
    }
}
"""

print(build_response(test))