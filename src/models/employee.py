from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    id: int
    role: str

    busy: bool = False
    current_client_id: Optional[int] = None
