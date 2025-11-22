import json
import re
from collections import defaultdict
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


class BusLine:
    """A bus line with multiple stops.

    Keeps track of stops and validates if stops are correctly defined.
    Holds a collection of BusStop objects.
    """

    def __init__(self, line_id: int):
        self.line_id = line_id  # corresponds to bus_id
        self.stops = []

    def get_number_of_stops(self) -> int:
        """Return the number of stops in the bus line."""
        return len(self.stops)

    def is_line_valid(self) -> bool:
        """Check if the bus line is valid based on its stops.
        Line is valid if it has exactly one start stop ('S') and one finish stop ('F').
        """
        start_stops = 0
        finish_stops = 0
        for stop in self.stops:
            start_stops = sum(1 for s in self.stops if s.stop_type == 'S')
            finish_stops = sum(1 for s in self.stops if s.stop_type == 'F')

        return start_stops == 1 and finish_stops == 1


class BusStop:
    """A bus stop with specific attributes."""

    def __init__(self, bus_id: int, stop_id: int, stop_name: str, next_stop: int,
                 stop_type: str, a_time: str):
        self.bus_id = bus_id
        self.stop_id = stop_id
        self.stop_name = stop_name
        self.next_stop = next_stop
        self.stop_type = stop_type
        self.a_time = a_time


class BusCompany:
    """A bus company managing multiple bus lines and stops.

    It is collecting data from input and creating bus lines.
    Holds a collection of BusLine objects.
    """

    def __init__(self, data: List[Dict]):
        self.bus_lines: List[BusLine] = []
        self.data = data

        for item in data:
            bus_id = item.get('bus_id')
            stop = BusStop(
                bus_id=item.get('bus_id'),
                stop_id=item.get('stop_id'),
                stop_name=item.get('stop_name'),
                next_stop=item.get('next_stop'),
                stop_type=item.get('stop_type'),
                a_time=item.get('a_time')
            )
            line = self._get_or_create_line(stop)
            line.stops.append(stop)

    def _get_or_create_line(self, stop: BusStop) -> BusLine:
        """Get existing BusLine by bus_id or create a new one."""
        # check if line already in bus_lines
        for line in self.bus_lines:
            if line.stops and line.line_id == stop.bus_id:
                return line
        # create new line and add to bus lines tracked by bus company
        new_line = BusLine(stop.bus_id)
        self.bus_lines.append(new_line)
        return new_line

    def print_line_info(self):
        for line in self.bus_lines:
            if not line.is_line_valid():
                print(f'There is no start or end stop for the line: {line.line_id}.')
                break
            else:
                print(f'bus_id: {line.line_id} stops: {line.get_number_of_stops()}')

    def print_stops_info(self):
        all_stops = set()
        start_stops = set()
        finish_stops = set()

        for line in self.bus_lines:
            for stop in line.stops:
                all_stops.add(stop.stop_name)
                if stop.stop_type == 'S':
                    start_stops.add(stop.stop_name)
                elif stop.stop_type == 'F':
                    finish_stops.add(stop.stop_name)

        print(f'Start stops: {len(start_stops)} {sorted(start_stops)}')
        print(f'Finish stops: {len(finish_stops)} {sorted(finish_stops)}')
        middle_stops = all_stops - start_stops - finish_stops
        print(f'Middle stops: {len(middle_stops)} {sorted(middle_stops)}')


def validate_item(item: Dict, result: ValidationResult) -> None:
    """Validate a single item and update the validation result

    Validation rules:
    * bus_id: must be an integer
    * stop_id: must be an integer
    * stop_name: must be a non-empty string,
        must start with a capital letter and end with 'Street', 'Avenue', 'Boulevard', or 'Road'
    * next_stop: must be an integer
    * stop_type: must be one of the following characters: 'S', 'O', 'F' or an empty string
    * a_time: string, must be in the format 'HH:MM' (24-hour format)

    :param item: The item to validate
    :param result: The ValidationResult object to update
    """

    if not isinstance(item.get('bus_id'), int):
        result.bus_id_errors += 1

    if not isinstance(item.get('stop_id'), int):
        result.stop_id_errors += 1

    stop_name = item.get('stop_name')
    if not (isinstance(stop_name, str) and stop_name
            and re.match(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)* (Road|Avenue|Boulevard|Street)$', stop_name)):
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


def validate_data(data: List[Dict]) -> ValidationResult:
    """Validate the input data and return the validation results.

    :param data: List of input data dictionaries
    :return: ValidationResult object containing error counts
    """
    result = ValidationResult()

    for item in data:
        validate_item(item, result)

    return result


def count_bus_stops(data: List[Dict]) -> Dict[int, int]:
    """ Count the number of stops for each bus_id.

    :param data: List of data from input
    :return: Dictionary of bus stop counts
    """

    bus_stops = defaultdict(int)

    for item in data:
        bus_id = item.get('bus_id')
        bus_stops[bus_id] += 1
    return bus_stops


def print_bus_stops(bus_stops: Dict[int, int]) -> None:
    """ Print the number of stops for each bus_id.

    :param bus_stops: Dictionary of bus stop counts
    """
    print('Line names and number of stops:')
    for bus_id in sorted(bus_stops.keys()):
        print(f'Bus {bus_id}: stops: {bus_stops[bus_id]}')


def main():
    data = json.loads(input())

    # data validation
    validation_result = validate_data(data)
    print(validation_result)
    print()

    bus_stops_count = count_bus_stops(data)
    print_bus_stops(bus_stops_count)
    print()

    # business logic validation
    bus_company = BusCompany(data)
    bus_company.print_line_info()
    bus_company.print_stops_info()


if __name__ == '__main__':
    main()
