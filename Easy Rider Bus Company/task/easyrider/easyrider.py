import json
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ValidationResult:
    bus_id_errors: int = 0
    stop_id_errors: int = 0
    stop_name_errors: int = 0
    next_stop_errors: int = 0
    stop_type_errors: int = 0
    a_time_errors: int = 0

    def __repr__(self):
        total_errors = (self.bus_id_errors + self.stop_id_errors + self.stop_name_errors +
                        self.next_stop_errors + self.stop_type_errors + self.a_time_errors)
        return (f'Type and field validation: {total_errors} errors\n'
                f'bus_id: {self.bus_id_errors}\n'
                f'stop_id: {self.stop_id_errors}\n'
                f'stop_name: {self.stop_name_errors}\n'
                f'next_stop: {self.next_stop_errors}\n'
                f'stop_type: {self.stop_type_errors}\n'
                f'a_time: {self.a_time_errors}')


def validate_item(item: Dict, result: ValidationResult) -> None:
    """Validate a single item and update the validation result

    Validation rules:
    * bus_id: must be an integer
    * stop_id: must be an integer
    * stop_name: must be a non-empty string,
        must start with a capital letter and end with 'Street', 'Avenue', 'Boulevard', or 'Drive'
    * next_stop: must be an integer
    * stop_type: must be one of the following characters: 'S', 'O', 'F' or an empty string
    * a_time: string, must be in the format 'HH:MM' (24-hour format)
    pass

    :param item: The item to validate
    :param result: The ValidationResult object to update
    """

    if not isinstance(item.get('bus_id'), int):
        result.bus_id_errors += 1

    if not isinstance(item.get('stop_id'), int):
        result.stop_id_errors += 1

    stop_name = item.get('stop_name')
    if not (isinstance(stop_name, str) and stop_name):
        # and stop_name[0].isupper() ):
        # and stop_name.lower().endswith(('road', 'avenue', 'boulevard', 'street'))):
        result.stop_name_errors += 1

    if not isinstance(item.get('next_stop'), int):
        result.next_stop_errors += 1

    stop_type = item.get('stop_type')
    if stop_type not in ('S', 'O', 'F', ''):
        result.stop_type_errors += 1

    a_time = item.get('a_time')
    if not (isinstance(a_time, str) and len(a_time) == 5 and
            a_time[2] == ':' and
            a_time[:2].isdigit() and 0 <= int(a_time[:2]) < 24 and
            a_time[3:].isdigit() and 0 <= int(a_time[3:]) < 60):
        result.a_time_errors += 1


def validate_data(data: List[Dict]) -> None:
    """Validate the input data and print the validation results."""

    result = ValidationResult()

    for item in data:
        validate_item(item, result)

    print(result)


def main():
    data = json.loads(input())
    validate_data(data)


if __name__ == '__main__':
    main()
