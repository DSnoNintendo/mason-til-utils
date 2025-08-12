from dataclasses import dataclass
import json
from typing import Optional, List, Dict, Any


@dataclass
class EthGenRequest:
    image_path: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_path": self.image_path,
            "name": self.name,
        }


@dataclass
class GenderRequest:
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
        }



def build_ethgen_messages(system_message: Dict[str, Any], request: EthGenRequest, image_url: str) -> List[Dict[str, Any]]:
    """
    Build Chat Completions messages for EthGen (image + optional name).
    The `image_url` should already be prepared (either direct URL or data URI).
    """

    return [
        system_message,
        {
            "role": "user",
            "content": [
                {"type": "text", "text": json.dumps(request.to_dict())},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        },
    ]


def build_gender_messages(system_message: Dict[str, Any], request: GenderRequest) -> List[Dict[str, Any]]:
    """
    Build Chat Completions messages for Gender (text only).
    """

    return [
        system_message,
        {
            "role": "user",
            "content": [{"type": "text", "text": json.dumps(request.to_dict())}],
        },
    ]


def build_ethgen_payload(
    system_message: Dict[str, Any],
    request: EthGenRequest,
    image_url: str,
    *,
    model: str,
    max_tokens: int = 100,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """
    Build a ready-to-send payload dict for OpenAI Chat Completions for EthGen.
    """
    payload = {
        "model": model,
        "messages": build_ethgen_messages(system_message, request, image_url),

        "temperature": temperature,
        "response_format": {"type": "text"},
    }
    if model == "gpt-5":
        print("gpt-5")
        payload["max_completion_tokens"] = max_tokens
    else:
        print("gpt-4.1")
        payload["max_tokens"] = max_tokens

    return payload


def build_gender_payload(
    system_message: Dict[str, Any],
    request: GenderRequest,
    *,
    model: str = "gpt-4.1",
    max_tokens: int = 100,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """
    Build a ready-to-send payload dict for OpenAI Chat Completions for Gender.
    """
    payload = {
        "model": model,
        "messages": build_gender_messages(system_message, request),
        "temperature": temperature,
        "response_format": {"type": "text"},
    }
    if model == "gpt-5":
        print("gpt-5")
        payload["max_completion_tokens"] = max_tokens
    else:
        print("gpt-4.1")
        payload["max_tokens"] = max_tokens

    return payload