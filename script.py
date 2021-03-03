import json
import re
import subprocess
import sys

from data_classes import *


def parse(*file_paths: str) -> List[Violation]:
    output = subprocess.run(["flake8", *file_paths], capture_output=True, text=True)

    violations = []

    for line in map(str, output.stdout.splitlines()):
        violation_pattern = re.compile(
            r"""
        (?P<file_path>.*) # До первой ":" находится путь к файлу
        [:]
        (?P<line>\d+) # После первой ":" идет номер строки
        [:]
        (?P<column>\d+) # Далее, номер столбца
        [:]
        \s 
        (?P<code_prefix>\w+) # Код (включая префикс) нарушения отделён пробелами
        (?P<code>\d{3}) # Код нарушения содержит ровно 3 цифры
        \s
        (?P<description>.*) # Всё что идёт после кода нарушения является описанием ошибки
        """,
            re.VERBOSE,
        )

        if not violation_pattern.search(line):
            break

        groups = violation_pattern.search(line).groupdict()
        violation = Violation(**groups)
        violations.append(violation)

    return violations


def print_with_numbers(violations: List[Violation]):
    for i, violation in enumerate(violations, 1):
        print(f"{i}\t{violation}")


def print_category(category_name: str, violations: List[Violation], start_index: int):
    current_index = start_index
    if violations:
        print(category_name)
        for elem in violations:
            print(f"{current_index}\t{elem}")
            current_index += 1
        print()


def print_grouped(violations: List[Violation]):
    with open("categories.json") as f:
        categories: List[Category] = json.load(f, object_hook=lambda items: Category(**items))

    remaining: List[Violation] = violations

    current_index: int = 1
    for category in categories:
        code_prefix: str = category.code_prefix
        code_boundaries: List[int] = category.code_boundaries
        filtered_violations = list(
            filter(
                lambda violation: violation.code_prefix == code_prefix and violation.code in range(*code_boundaries),
                remaining,
            )
        )
        remaining = [x for x in remaining if x not in filtered_violations]

        print_category(category.name, filtered_violations, current_index)
        current_index += len(filtered_violations)

    print_category("Others", remaining, current_index)


def script(*file_paths: str):
    violations = parse(*file_paths)
    # print_with_numbers(violations)
    print_grouped(violations)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        script(*sys.argv[1:])
    else:
        print("Error: specify the path to the files.")
