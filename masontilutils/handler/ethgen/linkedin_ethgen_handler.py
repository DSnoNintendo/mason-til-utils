from masontilutils.service.ethgen.linkedin_ethgen_service import LinkedInEthGenResponse
import enum


class EthGenNote(enum.Enum):
    NO_EXECUTIVE_FOUND = "No Executive Found"
    PUBLICLY_TRADED = "Publicly Traded"
    NO_ETHNICITY_FOUND = "No Ethnicity Found"
    NO_GENDER_FOUND = "No Gender Found"
    NO_LINKEDIN_URL_FOUND = "No LinkedIn Found"
    NO_IMAGE_FOUND = "No Image Found"
    MULTIPLE_EXECUTIVES_FOUND = "Multiple Executives Found"

class LinkedInEthGenResponseHandler:
    def __init__(self, table_name: str):
        self.table_name = table_name
        pass

    def escape(self, value: str) -> str:
        """Escape single quotes in SQL string values"""
        return value.replace("'", "''") if value else value

    def handle_multiple_executives(self, response: LinkedInEthGenResponse, mta_uid: str) -> list[str]:
        queries = []
        multiple_executives = ""
        for executive in response.executives:
            multiple_executives += f"{executive.name} ({executive.role}), "
        multiple_executives = multiple_executives[:-2]

        queries.append(
            f"UPDATE {self.table_name} SET ethgen_note = 'multiple owners found: {self.escape(multiple_executives)}' WHERE MTAuID = '{mta_uid}'"
        )
        if query := self.handle_ethnicity(response, mta_uid):
            queries.append(query)
        if query := self.handle_gender(response, mta_uid):
            queries.append(query)
        if query := self.handle_sources(response, mta_uid):
            queries.append(query)
        
        return queries
    
    def handle_one_executive(self, response: LinkedInEthGenResponse, mta_uid: str) -> list[str]:
        queries = []
        if query := self.handle_name(response, mta_uid):
            queries.append(query)
        if query := self.handle_ethnicity(response, mta_uid):
            queries.append(query)
        if query := self.handle_gender(response, mta_uid):
            queries.append(query)

        # build linkedin_url field
        if query := self.handle_linkedin_url(response, mta_uid):
            queries.append(query)

        if query := self.handle_picture_url(response, mta_uid):
            queries.append(query)

        # build sources field
        if query := self.handle_sources(response, mta_uid):
            queries.append(query)

        return queries

    
    def handle_gender(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        if response.gender:
            return f"UPDATE {self.table_name} SET gender = '{self.escape(response.gender)}' WHERE MTAuID = '{mta_uid}'"
        else: 
            return None
        
    def handle_ethnicity(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        if response.ethnicity:
            return f"UPDATE {self.table_name} SET ethnicity = '{self.escape(response.ethnicity)}' WHERE MTAuID = '{mta_uid}'"
        else: 
            return None
        
    def handle_sources(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        sources = ""
        for executive in response.executives:
            if executive.sources:
                for source in executive.sources:
                    sources += f"{source} , "
        
        sources = sources[:-3] # remove the last comma
        if len(sources) > 0:
            return f"UPDATE {self.table_name} SET sources = '{self.escape(sources)}' WHERE MTAuID = '{mta_uid}'"
        else:
            return None
 
    
        
    def handle_linkedin_url(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        if len(response.executives) > 0 and response.executives[0].linkedin_url:
            return f"UPDATE {self.table_name} SET linkedin_url = '{self.escape(response.executives[0].linkedin_url)}' WHERE MTAuID = '{mta_uid}'"
        else:
            return f"UPDATE {self.table_name} SET linkedin_url = '{EthGenNote.NO_LINKEDIN_URL_FOUND.value}' WHERE MTAuID = '{mta_uid}'"

        
    def handle_picture_url(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        if len(response.executives) > 0 and response.executives[0].picture_url:
            return f"UPDATE {self.table_name} SET picture_url = '{self.escape(response.executives[0].picture_url)}' WHERE MTAuID = '{mta_uid}'"
        else:
            return f"UPDATE {self.table_name} SET picture_url = '{EthGenNote.NO_IMAGE_FOUND.value}' WHERE MTAuID = '{mta_uid}'"
        
    def handle_name(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        if len(response.executives) > 0:
            return f"UPDATE { self.table_name} SET contact = '{self.escape(response.executives[0].name)}' WHERE MTAuID = '{mta_uid}'"
        else:
            return None


    # returns SQL query
    def handle(self, response: LinkedInEthGenResponse, mta_uid: str) -> list[str]:
        queries = []
        
        # Publicly Traded
        if response.is_publicly_traded:
            # set ethgen_note field to "Publicly traded" where MTAuID = mta_uid
            queries.append(
                f"UPDATE {self.table_name} SET ethgen_note = '{EthGenNote.PUBLICLY_TRADED.value}' WHERE MTAuID = '{mta_uid}'"
            )
            return queries

        # No Executive Found
        if not response.executive_found:
            queries.append(
                f"UPDATE {self.table_name} SET ethgen_note = '{EthGenNote.NO_EXECUTIVE_FOUND.value}' WHERE MTAuID = '{mta_uid}'"
            )
            return queries
        
        # Multiple Executives Found
        if response.multiple_executives:
            return self.handle_multiple_executives(response, mta_uid)
        else:
            return self.handle_one_executive(response, mta_uid)
    