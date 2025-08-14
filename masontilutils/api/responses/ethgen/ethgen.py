from dataclasses import dataclass
from typing import Optional, Dict, Any

from masontilutils.api.queries.enums import Region, Ethnicity, Sex

@dataclass
class EthGenResponse:
    ethnicity: Optional[str]
    sex: Optional[str]

@dataclass
class GenderResponse:
    sex: Optional[str]

# Internal mapping from Region to Ethnicity code
_REGION_TO_ETHNICITY: Dict[Region, str] = {
    Region.EUROPE: Ethnicity.EUROPE.value,
    Region.AFRICA: Ethnicity.AFRICA.value,
    Region.NORTH_AMERICA: Ethnicity.NORTH_AMERICA.value,
    Region.SOUTH_AMERICA: Ethnicity.SOUTH_AMERICA.value,
    Region.AUSTRALIA: Ethnicity.AUSTRALIA.value,
    Region.EAST_ASIA: Ethnicity.EAST_ASIA.value,
    Region.SOUTH_ASIA: Ethnicity.SOUTH_ASIA.value,
    Region.SOUTHEAST_ASIA: Ethnicity.EAST_ASIA.value,  # keep parity with existing behavior
    Region.WEST_ASIA: Ethnicity.WEST_ASIA.value,
    Region.CENTRAL_ASIA: Ethnicity.CENTRAL_ASIA.value,
    Region.ANTARCTICA: Ethnicity.ANTARCTICA.value,
    Region.PACIFIC_ISLANDS: Ethnicity.PACIFIC_ISLANDS.value,
}


def _normalize_str(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def build_ethgen_response(api_res: Dict[str, Any]) -> EthGenResponse | None:
    """
    Convert raw API json into a normalized EthGenResponse object.
    Expected api_res keys: `region`, `sex` (case-insensitive content).
    """
    region_text = _normalize_str(api_res.get("region"))
    sex_text = _normalize_str(api_res.get("sex"))

    ethnicity_value: Optional[str] = None

    if region_text:
        # exact value match first
        exact = next((r for r in Region if _normalize_str(r.value) == region_text), None)
        if exact is not None:
            ethnicity_value = _REGION_TO_ETHNICITY.get(exact)
        else:
            # containment heuristic
            matched = next(
                (
                    r for r in Region
                    if _normalize_str(r.value) in region_text or region_text in _normalize_str(r.value)
                ),
                None,
            )
            if matched is not None:
                ethnicity_value = _REGION_TO_ETHNICITY.get(matched)

    sex_value: Optional[str] = None
    if sex_text and sex_text != "none":
        matched_sex = next((s for s in Sex if _normalize_str(s.value) == sex_text), None)
        sex_value = matched_sex.value if matched_sex else None

    res = EthGenResponse(ethnicity=ethnicity_value, sex=sex_value)
    if res.ethnicity is None and res.sex is None:
        return None

    return res



def build_gender_response(api_res: Dict[str, Any]) -> GenderResponse:
    """
    Convert raw API json into a normalized GenderResponse object.
    Expected api_res key: `sex` (case-insensitive content).
    """
    sex_text = _normalize_str(api_res.get("sex"))
    if not sex_text or sex_text == "none":
        return GenderResponse(sex=None)

    matched_sex = next((s for s in Sex if _normalize_str(s.value) == sex_text), None)

    if matched_sex is None:
        return None
    
    return GenderResponse(sex=matched_sex.value) 