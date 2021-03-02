import re
import subprocess
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class Violation:
    file_path: str
    line: int
    column: int
    type: str
    code: int
    description: str

    def __str__(self):
        return f"{self.file_path}:{self.line}:{self.column} {self.type}{self.code} {self.description}"


def parse(*file_paths: str) -> List[Violation]:
    output = subprocess.run(["flake8", *file_paths], capture_output=True, text=True)

    violations = []

    for line in map(str, output.stdout.splitlines()):
        pattern = re.compile(
            r"(?P<file_path>.*)[:](?P<line>\d+)[:](?P<column>\d+)[:] (?P<type>[^\d\W]+)(?P<code>\d+) (?P<description>.*)"
        )
        if not pattern.search(line):
            break

        result = pattern.search(line).groupdict()
        violation = Violation(**result)
        violations.append(violation)

    return violations


def script(*file_paths: str):
    violations = parse(*file_paths)

    for i, violation in enumerate(violations, 1):
        print(f"{i}\t{violation}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        script(*sys.argv[1:])
    else:
        print("Error: specify the path to the files.")
