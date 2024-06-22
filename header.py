from dataclasses import dataclass, asdict
"""A C style header file to contain all of my dataclasses used in this project"""

@dataclass
class Transcript:
	file: str
	text: str

@dataclass
class Match:
	confidenceLevel: int
	text: str
	file: str
	location: int