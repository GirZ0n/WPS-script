from dataclasses import dataclass
from typing import List


@dataclass
class Category:
    name: str
    code_prefix: str
    code_boundaries: List[int]


@dataclass
class Violation:
    file_path: str
    line: int
    column: int
    code_prefix: str
    code: str
    description: str

    def __str__(self):
        return f"{self.file_path}:{self.line}:{self.column}: {self.code_prefix}{self.code} {self.description}"

    def __post_init__(self):
        self.line = int(self.line)
        self.column = int(self.column)
