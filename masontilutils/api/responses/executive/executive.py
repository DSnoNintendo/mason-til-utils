from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json

from masontilutils.api.queries.ethgen import (
    EXECUTIVE_NONE_IDENTIFIER,
    PUBLICALLY_TRADED_IDENTIFIER
)
from masontilutils.utils import extract_json_substring, clean_deep_research_text

@dataclass
class ExecutiveInfo:
    name: str
    role: str
    sources: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the executive info to a dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "sources": self.sources
        }

@dataclass
class ExecutiveResponse:
    executives: List[ExecutiveInfo]
    is_publicly_traded: bool = False
    is_none: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response to a dictionary."""
        return {
            "executives": [exec_info.to_dict() for exec_info in self.executives],
            "is_publicly_traded": self.is_publicly_traded,
            "is_none": self.is_none
        }


def build_executive_response(answer: str) -> ExecutiveResponse:
    """
    Convert raw API response text into a normalized ExecutiveResponse object.
    Handles special cases for publicly traded companies and no executives found.
    """

    api_response = extract_json_substring(clean_deep_research_text(answer))

    # Check for special identifiers first
    if EXECUTIVE_NONE_IDENTIFIER in api_response:
        return ExecutiveResponse(executives=[], is_none=True)
    
    if PUBLICALLY_TRADED_IDENTIFIER in api_response:
        return ExecutiveResponse(executives=[], is_publicly_traded=True)
    
    # Try to extract and parse JSON
    try:
        if not api_response:
            return ExecutiveResponse(executives=[], is_none=True)
            
        api_json = json.loads(api_response)
        
        executives = []
        for key, data in api_json.items():
            if isinstance(data, dict) and "name" in data and "role" in data:
                executives.append(ExecutiveInfo(
                    name=data["name"],
                    role=data["role"],
                    sources=data.get("sources", [])
                ))
        
        return ExecutiveResponse(executives=executives)
        
    except Exception as e:
        print(f"Error parsing executive data: {e}")
        import traceback
        traceback.print_exc()
        return ExecutiveResponse(executives=[], is_none=True) 