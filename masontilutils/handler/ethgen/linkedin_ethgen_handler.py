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
        print(f"   >> Building multiple executives note...")
        queries = []
        multiple_executives = ""
        for executive in response.executives:
            multiple_executives += f"{executive.name} ({executive.role}), "
        multiple_executives = multiple_executives[:-2]
        print(f"   >> Executive list: {multiple_executives}")

        note_query = f"UPDATE {self.table_name} SET ethgen_note = 'multiple owners found: {self.escape(multiple_executives)}' WHERE MTAuID = '{mta_uid}'"
        queries.append(note_query)
        print(f"   >> Generated ethgen_note query")
        
        print(f"   >> Processing ethnicity...")
        if query := self.handle_ethnicity(response, mta_uid):
            queries.append(query)
            print(f"   >> Added ethnicity query: {response.ethnicity}")
        else:
            print(f"   >> No ethnicity data to process")
            
        print(f"   >> Processing gender...")
        if query := self.handle_gender(response, mta_uid):
            queries.append(query)
            print(f"   >> Added gender query: {response.gender}")
        else:
            print(f"   >> No gender data to process")
            
        print(f"   >> Processing sources...")
        if query := self.handle_sources(response, mta_uid):
            queries.append(query)
            print(f"   >> Added sources query")
        else:
            print(f"   >> No sources data to process")
        
        return queries
    
    def handle_one_executive(self, response: LinkedInEthGenResponse, mta_uid: str) -> list[str]:
        queries = []
        
        print(f"   >> Processing executive name...")
        if query := self.handle_name(response, mta_uid):
            queries.append(query)
            print(f"   >> Added name query: {response.executives[0].name if response.executives else 'N/A'}")
        else:
            print(f"   >> No name data to process")
            
        print(f"   >> Processing ethnicity...")
        if query := self.handle_ethnicity(response, mta_uid):
            queries.append(query)
            print(f"   >> Added ethnicity query: {response.ethnicity}")
        else:
            print(f"   >> No ethnicity data to process")
            
        print(f"   >> Processing gender...")
        if query := self.handle_gender(response, mta_uid):
            queries.append(query)
            print(f"   >> Added gender query: {response.gender}")
        else:
            print(f"   >> No gender data to process")

        print(f"   >> Processing LinkedIn URL...")
        # build linkedin_url field
        if query := self.handle_linkedin_url(response, mta_uid):
            queries.append(query)
            linkedin_status = "Found" if (response.executives and response.executives[0].linkedin_url) else "Not found - using default note"
            print(f"   >> Added LinkedIn URL query: {linkedin_status}")

        print(f"   >> Processing picture URL...")
        if query := self.handle_picture_url(response, mta_uid):
            queries.append(query)
            picture_status = "Found" if (response.executives and response.executives[0].picture_url) else "Not found - using default note"
            print(f"   >> Added picture URL query: {picture_status}")

        print(f"   >> Processing sources...")
        # build sources field
        if query := self.handle_sources(response, mta_uid):
            queries.append(query)
            print(f"   >> Added sources query")
        else:
            print(f"   >> No sources data to process")

        return queries

    
    def handle_gender(self, response: LinkedInEthGenResponse, mta_uid: str) -> str | None:
        gender = response.gender


        if gender:
            return f"UPDATE {self.table_name} SET gender = '{gender.upper()[0]}' WHERE MTAuID = '{mta_uid}'"
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
        print(f"========== LinkedIn EthGen Handler Started ==========")
        print(f"Table: {self.table_name}")
        print(f"MTAuID: {mta_uid}")
        print(f"Company: {response.company_name}")
        
        queries = []
        
        print(f"\n--- Handler Input Analysis ---")
        print(f"Is Publicly Traded: {response.is_publicly_traded}")
        print(f"Executive Found: {response.executive_found}")
        print(f"Multiple Executives: {response.multiple_executives}")
        print(f"Number of Executives: {len(response.executives)}")
        print(f"Final Ethnicity: {response.ethnicity}")
        print(f"Final Gender: {response.gender}")
        print(f"Multiple Ethnicities: {response.multiple_ethnicities}")
        print(f"Multiple Genders: {response.multiple_genders}")
        
        # Publicly Traded
        if response.is_publicly_traded:
            print(f"\n--- Processing Publicly Traded Company ---")
            print(f"Setting ethgen_note to: {EthGenNote.PUBLICLY_TRADED.value}")
            # set ethgen_note field to "Publicly traded" where MTAuID = mta_uid
            query = f"UPDATE {self.table_name} SET ethgen_note = '{EthGenNote.PUBLICLY_TRADED.value}' WHERE MTAuID = '{mta_uid}'"
            queries.append(query)
            print(f"Generated Query: {query}")
            print(f"Processing complete for publicly traded company")
            print(f"========== LinkedIn EthGen Handler Completed ==========\n")
            return queries

        # No Executive Found
        if not response.executive_found:
            print(f"\n--- Processing No Executive Found ---")
            print(f"Setting ethgen_note to: {EthGenNote.NO_EXECUTIVE_FOUND.value}")
            query = f"UPDATE {self.table_name} SET ethgen_note = '{EthGenNote.NO_EXECUTIVE_FOUND.value}' WHERE MTAuID = '{mta_uid}'"
            queries.append(query)
            print(f"Generated Query: {query}")
            print(f"Processing complete for no executive found")
            print(f"========== LinkedIn EthGen Handler Completed ==========\n")
            return queries
        
        # Multiple Executives Found
        if response.multiple_executives:
            print(f"\n--- Processing Multiple Executives ---")
            print(f"Calling handle_multiple_executives for {len(response.executives)} executives")
            for i, exec in enumerate(response.executives, 1):
                print(f"Executive {i}: {exec.name} ({exec.role})")
            queries = self.handle_multiple_executives(response, mta_uid)
            print(f"Generated {len(queries)} queries for multiple executives")
        else:
            print(f"\n--- Processing Single Executive ---")
            if response.executives:
                exec = response.executives[0]
                print(f"Executive: {exec.name} ({exec.role})")
                print(f"LinkedIn URL: {exec.linkedin_url or 'Not found'}")
                print(f"Picture URL: {exec.picture_url or 'Not found'}")
                print(f"Individual Ethnicity: {exec.ethnicity or 'Not found'}")
                print(f"Individual Gender: {exec.gender or 'Not found'}")
            print(f"Calling handle_one_executive")
            queries = self.handle_one_executive(response, mta_uid)
            print(f"Generated {len(queries)} queries for single executive")
        
        print(f"\n--- Final Query Summary ---")
        print(f"Total Queries Generated: {len(queries)}")
        for i, query in enumerate(queries, 1):
            print(f"Query {i}: {query}")
        
        print(f"Processing complete!")
        print(f"========== LinkedIn EthGen Handler Completed ==========\n")
        return queries
    