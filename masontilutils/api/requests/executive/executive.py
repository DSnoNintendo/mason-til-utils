from dataclasses import dataclass
import json
from typing import List, Dict, Any

from masontilutils.api.queries.ethgen import (
    EXECUTIVE_QUERY,
)

@dataclass
class ExecutiveRequest:
    company_name: str
    city: str
    state: str
    address: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the request to a dictionary."""
        return {
            "company_name": self.company_name,
            "city": self.city,
            "state": self.state,
            "address": self.address
        }


def build_executive_messages(system_message: Dict[str, Any], request: ExecutiveRequest) -> List[Dict[str, Any]]:
    """
    Build Chat Completions messages for Executive search.
    """
    
    return [
        system_message,
        {"role": "user", "content": json.dumps(request.to_dict())},
    ]


def build_executive_payload(
    system_message: Dict[str, Any],
    request: ExecutiveRequest,
    *,
    model: str = "sonar-deep-research",
    max_tokens: int = 2500,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """
    Build a ready-to-send payload dict for Perplexity Chat Completions for Executive search.
    """
    return {
        "model": model,
        "messages": build_executive_messages(system_message, request),
        "max_tokens": max_tokens,
        "temperature": temperature,
    } 