from dataclasses import dataclass
from typing import Optional
from enum import Enum


class EventType(Enum):
    CLIENT_ARRIVAL = 1
    SELLER_FINISH = 2
    TECHNICIAN_FINISH = 3
    SPECIALIST_FINISH = 4


@dataclass
class Event:
    time: float
    event_type: EventType

    client_id: Optional[int] = None
    employee_id: Optional[int] = None
