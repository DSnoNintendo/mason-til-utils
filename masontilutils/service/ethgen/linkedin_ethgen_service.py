from dataclasses import dataclass, field
from typing import List
import uuid
from linkedin_selenium import LinkedInBrowser
from masontilutils.api.responses.ethgen.ethgen import EthGenResponse, GenderResponse
from masontilutils.api.chatgpt import ChatGPTEthGenAPI, ChatGPTGenderAPI
from masontilutils.api.perplexity import PerplexityExecutiveAPI
from masontilutils.api.duckduckgo import DuckDuckGoLinkedInAPI
import os

from masontilutils.api.responses.executive.executive import ExecutiveResponse, ExecutiveInfo


@dataclass
class ServiceExecutiveInfo:
    name: str
    role: str
    linkedin_url: str | None = None
    picture_url: str | None = None
    ethnicity: str | None = None
    gender: str | None = None
    sources: List[str] = field(default_factory=list)

@dataclass
class LinkedInEthGenResponse:
    company_name: str
    executives: List[ServiceExecutiveInfo] = field(default_factory=list)
    ethnicity: str | None = None
    gender: str | None = None
    executive_found: bool = False # if true, at least one executive was found
    multiple_executives: bool = False # if true, there are multiple executives
    multiple_ethnicities: bool = False # if true ethnicity is non-minority
    multiple_genders: bool = False # if true gender is Z
    is_family_owned: bool = False # if true, the company is family owned
    is_publicly_traded: bool = False # if true, the company is publicly traded


class ServiceRequest:
    def __init__(self, company_name: str, city: str, state: str, address: str):
        self.id = str(uuid.uuid4())

        self.company_name = company_name
        self.city = city
        self.state = state
        self.address = address

        self.response = LinkedInEthGenResponse(company_name=company_name)


class LinkedInEthGenService:
    def __init__(self):
        # Initialize Perplexity Executive API
        perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        if not perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")
        
        # Initialize ChatGPT APIs
        chatgpt_key = os.getenv('CHATGPT_API_KEY')
        if not chatgpt_key:
            raise ValueError("CHATGPT_API_KEY environment variable not set")
        
        self.executive_api = PerplexityExecutiveAPI(perplexity_key)
        self.ethgen_api = ChatGPTEthGenAPI(chatgpt_key)
        self.gender_api = ChatGPTGenderAPI(chatgpt_key)
        self.ddg_api = DuckDuckGoLinkedInAPI()
        self.browser = None

    def create_executive_info(self, executive: ExecutiveInfo) -> ServiceExecutiveInfo:
        return ServiceExecutiveInfo(
            name=executive.name,
            role=executive.role,
            linkedin_url="",
            ethnicity="",
            picture_url="",
            gender="",  
            sources=executive.sources
        )

    def start(self):
        # Login to LinkedIn
        self.browser = LinkedInBrowser()
        self.browser.login()

    def stop(self):
        if self.browser:
            self.browser.close()

    def is_family_owned(self, executives: List[ServiceExecutiveInfo]) -> bool:
        # check if family owned by finding multiple executives with the same last name
        last_names = []
        for exec in executives:
            # Extract last name (assuming it's the last word in the name)
            name_parts = exec.name.strip().split()
            if name_parts:
                last_names.append(name_parts[-1])
        
        # Count occurrences of each last name using dictionary
        last_name_counts = {}
        for last_name in last_names:
            last_name_counts[last_name] = last_name_counts.get(last_name, 0) + 1
        
        # Check if any last name appears more than once
        for last_name, count in last_name_counts.items():
            if count > 1:
                print(f"   Multiple executives ({count}) share the last name '{last_name}' - marking as family owned")
                return True
        
        print(f"   No shared last names among executives - not family owned")
        return False
    
    def call(self, company_name: str, city: str, state: str, address: str) -> LinkedInEthGenResponse | None:
        print(f"========== LinkedIn EthGen Service Call Started ==========")
        print(f"Company: {company_name}")
        print(f"Location: {city}, {state}")
        print(f"Address: {address}")
        
        request = ServiceRequest(company_name, city, state, address)
        print(f"Service Request ID: {request.id}")

        # Get executive information
        print(f"\n--- Step 1: Fetching Executive Information ---")
        print(f"Calling Perplexity Executive API...")
        
        executive_response: ExecutiveResponse = self.executive_api.call(
            company_name=company_name,
            city=city, 
            state=state,
            address=address
        )

        if not executive_response or executive_response.is_none:
            print(f"No executive response received or response is empty")
            print(f"Returning None - no data to process")
            return None

        print(f"Executive API response received")
        print(f"Is Publicly Traded: {executive_response.is_publicly_traded}")
        print(f"Number of Executives Found: {len(executive_response.executives)}")

        # if company is publicly traded, set ethnicity to C
        if executive_response.is_publicly_traded:
            print(f"\n--- Publicly Traded Company Detected ---")
            print(f"Setting ethnicity to 'C' (Corporate/Publicly Traded)")
            request.response.is_publicly_traded = True
            request.response.ethnicity = "C"
            print(f"Processing complete for publicly traded company")
            print(f"========== LinkedIn EthGen Service Call Completed ==========\n")
            return request.response 
        
        # Convert API response executives to service executives
        if len(executive_response.executives) > 0:
            print(f"\n--- Step 2: Processing {len(executive_response.executives)} Executive(s) ---")
            request.response.executive_found = True
            
            if len(executive_response.executives) > 1:
                request.response.multiple_executives = True
                print(f"Multiple executives detected - will process all and consolidate results")
            else:
                print(f"Single executive detected")
                
            for i, api_exec in enumerate(executive_response.executives, 1):
                print(f"Executive {i}: {api_exec.name} ({api_exec.role})")
                request.response.executives.append(self.create_executive_info(api_exec))
        else:
            print(f"No executives found in response - returning basic response")
            print(f"========== LinkedIn EthGen Service Call Completed ==========\n")
            return request.response

        print(f"\n--- Step 3: LinkedIn Profile and Image Analysis ---")
        for i, executive in enumerate(request.response.executives, 1):
            print(f"\n>> Processing Executive {i}: {executive.name}")
            
            # get linkedin url
            print(f"   Searching for LinkedIn profile...")
            linkedin_url = self.get_linkedin(executive.name, company_name)
            
            if linkedin_url:
                print(f"   LinkedIn profile found: {linkedin_url}")
                executive.linkedin_url = linkedin_url
                
                # get profile picture
                print(f"   Attempting to extract profile picture...")
                if profile_picture := self.browser.get_profile_picture_from_url(linkedin_url):
                    print(f"   Profile picture extracted successfully")
                    executive.picture_url = profile_picture

                    # get ethnicity and gender
                    print(f"   Analyzing ethnicity and gender from image...")
                    ethgen_response: EthGenResponse | None = self.ethgen_api.call(profile_picture)
                    if ethgen_response:
                        executive.ethnicity = ethgen_response.ethnicity
                        executive.gender = ethgen_response.sex
                        print(f"   Image analysis complete - Ethnicity: {executive.ethnicity}, Gender: {executive.gender}")
                    else:
                        # get gender from name
                        print(f"   No ethnicity or gender found from image for {executive.name}")
                        print(f"   Falling back to name-based gender detection...")
                        gender_response: GenderResponse | None = self.gender_api.call(executive.name)
                        if gender_response:
                            executive.gender = gender_response.sex
                            print(f"   Gender detected from name: {executive.gender}")
                        else:
                            print(f"   No gender found for {executive.name}")
                else:
                    print(f"   No profile picture found for {executive.name}")
                    print(f"   Attempting name-based gender detection...")
                    gender_response: GenderResponse | None = self.gender_api.call(executive.name)
                    if gender_response:
                        executive.gender = gender_response.sex
                        print(f"   Gender detected from name: {executive.gender}")
                    else:
                        print(f"   No gender found for {executive.name}")
            else:
                print(f"   No LinkedIn profile found for {executive.name}")
                print(f"   Attempting name-based gender detection...")
                gender_response: GenderResponse | None = self.gender_api.call(executive.name)
                if gender_response:
                    executive.gender = gender_response.sex
                    print(f"   Gender detected from name: {executive.gender}")
                else:
                    print(f"   No gender found for {executive.name}")

        print(f"\n--- Step 4: Consolidating Results ---")
        # if multiple executives, check if ethnicity and gender are the same
        if request.response.multiple_executives:
            print(f"Processing multiple executives for consistency...")

            # check if ethnicity is the same
            ethnicities = [exec.ethnicity for exec in request.response.executives if exec.ethnicity]
            unique_ethnicities = set(ethnicities)

            # check if family owned
            if self.is_family_owned(request.response.executives):
                request.response.is_family_owned = True
                
            if len(unique_ethnicities) > 1:
                request.response.multiple_ethnicities = True
                request.response.ethnicity = "Non-Minority"
                print(f"   Multiple ethnicities detected: {unique_ethnicities}")
                print(f"   Setting consolidated ethnicity to: Non-Minority")
            elif len(unique_ethnicities) == 1:
                request.response.ethnicity = list(unique_ethnicities)[0]
                print(f"   Consistent ethnicity across executives: {request.response.ethnicity}")
            else:
                print(f"   No ethnicity data available for any executive")
                
            # Check gender consistency  
            genders = [exec.gender for exec in request.response.executives if exec.gender]
            unique_genders = set(genders)
            
            if len(unique_genders) > 1:
                request.response.multiple_genders = True
                request.response.gender = "Z"
                print(f"   Multiple genders detected: {unique_genders}")
                print(f"   Setting consolidated gender to: Z")
            elif len(unique_genders) == 1:
                request.response.gender = list(unique_genders)[0]
                print(f"   Consistent gender across executives: {request.response.gender}")
            else:
                print(f"   No gender data available for any executive")
        else:
            print(f"Single executive - using individual results")
            if request.response.executives:
                request.response.ethnicity = request.response.executives[0].ethnicity
                request.response.gender = request.response.executives[0].gender
                print(f"   Final ethnicity: {request.response.ethnicity}")
                print(f"   Final gender: {request.response.gender}")

        print(f"\n--- Final Results Summary ---")
        print(f"Company: {company_name}")
        print(f"Executives Found: {len(request.response.executives)}")
        print(f"Multiple Executives: {request.response.multiple_executives}")
        print(f"Multiple Ethnicities: {request.response.multiple_ethnicities}")
        print(f"Multiple Genders: {request.response.multiple_genders}")
        print(f"Family Owned: {request.response.is_family_owned}")
        print(f"Final Ethnicity: {request.response.ethnicity}")
        print(f"Final Gender: {request.response.gender}")
        
        for i, exec in enumerate(request.response.executives, 1):
            print(f"Executive {i}: {exec.name} ({exec.role}) - LinkedIn: {'Yes' if exec.linkedin_url else 'No'}, Image: {'Yes' if exec.picture_url else 'No'}, Ethnicity: {exec.ethnicity or 'N/A'}, Gender: {exec.gender or 'N/A'}")

        print(f"Processing complete!")
        print(f"========== LinkedIn EthGen Service Call Completed ==========\n")
        return request.response
    
    def get_linkedin(self, name: str, company_name: str) -> str | None:
        """
        Search for LinkedIn profile URL using DuckDuckGo
        
        Args:
            name: Executive name
            company_name: Company name
            
        Returns:
            LinkedIn profile URL or None if not found
        """
        linkedin_url = self.ddg_api.call(name=name, company_name=company_name)
        return linkedin_url
     
    def close(self):
        if self.browser:
            self.browser.quit() 