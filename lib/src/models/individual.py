from typing import Dict


class Individual:
    def __init__(self, timetable: Dict[str, Dict[str, str]]):
        self.timetable = timetable

    def get_slot(self, day: str, time: str) -> str:
        return self.timetable[day][time]

    def set_slot(self, day: str, time: str, subject: str):
        self.timetable[day][time] = subject
