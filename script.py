import json
import re
import subprocess
import sys
from typing import List
from data_classes import Violation, Category


def get_violations(*file_paths: str) -> List[Violation]:
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
        violations.append(Violation(**groups))

    return violations


def print_with_numbers(violations: List[Violation]):
    for index, violation in enumerate(violations, 1):
        print(f"{index}\t{violation}")


def print_grouped(violations: List[Violation]):
    with open("categories.json") as input_file:
        categories: List[Category] = json.load(input_file, object_hook=lambda dct: Category(**dct))

    remaining: List[Violation] = violations

    current_index = 1
    for category in categories:
        filtered_violations = list(
            filter(
                lambda violation: violation.code_prefix == category.code_prefix
                and int(violation.code) in range(*category.code_boundaries),
                remaining,
            )
        )
        remaining = [elem for elem in remaining if elem not in filtered_violations]

        print_category(category.name, filtered_violations, current_index)
        current_index += len(filtered_violations)

    print_category("Others", remaining, current_index)


def print_category(category_name: str, violations: List[Violation], start_index: int):
    if violations:
        print(category_name)
        for index, violation in enumerate(violations, start_index):
            print(f"{index}\t{violation}")
        print()


def main(*file_paths: str):
    violations = get_violations(*file_paths)
    # print_with_numbers(violations)
    print_grouped(violations)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(*sys.argv[1:])
    else:
        print("Error: specify the path to the files.")
