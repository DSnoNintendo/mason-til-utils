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
        
    
    def call(self, company_name: str, city: str, state: str, address: str) -> LinkedInEthGenResponse | None:
        request = ServiceRequest(company_name, city, state, address)

        # Get executive information
        executive_response: ExecutiveResponse = self.executive_api.call(
            company_name=company_name,
            city=city, 
            state=state,
            address=address
        )

        if not executive_response or executive_response.is_none:
            return None

        # if company is publicly traded, set ethnicity to C
        if executive_response.is_publicly_traded:
            request.response.is_publicly_traded = True
            request.response.ethnicity = "C"
            return request.response 
        
        # Convert API response executives to service executives
        if len(executive_response.executives) > 0:
            request.response.executive_found = True
            if len(executive_response.executives) > 1:
                request.response.multiple_executives = True
            for api_exec in executive_response.executives:
                request.response.executives.append(self.create_executive_info(api_exec))
        else:
            return request.response


        for executive in request.response.executives:
            # get linkedin url
            linkedin_url = self.get_linkedin(executive.name, company_name)
            if linkedin_url:
                executive.linkedin_url = linkedin_url
                # get profile picture
                if profile_picture := self.browser.get_profile_picture_from_url(linkedin_url):
                    executive.picture_url = profile_picture

                    # get ethnicity and gender
                    ethgen_response: EthGenResponse | None = self.ethgen_api.call(profile_picture)
                    if ethgen_response:
                        executive.ethnicity = ethgen_response.ethnicity
                        executive.gender = ethgen_response.sex
                    else:
                        # get gender from name
                        print(f"No ethnicity or gender found for {executive.name}")
                        gender_response: GenderResponse | None = self.gender_api.call(executive.name)
                        if gender_response:
                            executive.gender = gender_response.sex
                        else:
                            print(f"No gender found for {executive.name}")
                else:
                    print(f"No profile picture found for {executive.name}")

        # if multiple executives, check if ethnicity and gender are the same
        if request.response.multiple_executives:
            if any(executive.ethnicity != request.response.executives[0].ethnicity for executive in request.response.executives):
                request.response.multiple_ethnicities = True
            else:
                request.response.ethnicity = request.response.executives[0].ethnicity
            if any(executive.gender != request.response.executives[0].gender for executive in request.response.executives):
                request.response.multiple_genders = True
                request.response.gender = "Z"
            else:
                request.response.gender = request.response.executives[0].gender
        else:
            request.response.ethnicity = request.response.executives[0].ethnicity
            request.response.gender = request.response.executives[0].gender

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