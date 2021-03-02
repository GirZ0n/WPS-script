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
    violation_code: str
    description: str

    def __str__(self):
        return f"{self.file_path}:{self.line}:{self.column} {self.violation_code} {self.description}"


def parse(*file_paths: str) -> List[Violation]:
    output = subprocess.run(["flake8", *file_paths], capture_output=True, text=True)

    violations = []

    for line in map(str, output.stdout.splitlines()):
        pattern = re.compile(r"""
        (?P<file_path>.*) # До первой ":" находится путь к файлу
        [:]
        (?P<line>\d+) # После первой ":" идет номер строки
        [:]
        (?P<column>\d+) # Далее, номер столбца
        [:]
        \s 
        (?P<violation_code>[\w]+) # Код нарушения отделён пробелами 
        \s
        (?P<description>.*) # Всё что идёт после кода нарушения является описанием ошибки
        """, re.VERBOSE)

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
