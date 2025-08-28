from enum import Enum

class Region(Enum):
    EUROPE = "Europe"
    AFRICA = "Africa"
    EAST_ASIA = "East Asia" # asian
    SOUTH_ASIA = "South Asia" # middle eastern
    SOUTHEAST_ASIA = "Southeast Asia" # asian
    WEST_ASIA = "West Asia" # middle eastern
    CENTRAL_ASIA = "Central Asia" # asian
    NORTH_AMERICA = "North America"
    SOUTH_AMERICA = "South America"
    AUSTRALIA = "Australia"
    ANTARCTICA = "Antarctica"
    PACIFIC_ISLANDS = "Pacific Islands"

class Ethnicity(Enum):
    MIDDLE_EAST = "M"
    EAST_ASIA = "A"
    SOUTH_ASIA = "AS"
    SOUTHEAST_ASIA = "A"
    CENTRAL_ASIA = "A"
    WEST_ASIA = "M"
    EUROPE = "C"
    AFRICA = "B"
    NORTH_AMERICA = "H"
    SOUTH_AMERICA = "H"
    AUSTRALIA = "C"
    ANTARCTICA = "C"
    PACIFIC_ISLANDS = "AP"

class Sex(Enum):
    MALE = "Male"
    FEMALE = "Female" 