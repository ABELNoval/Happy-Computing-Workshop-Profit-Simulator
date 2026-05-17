from dataclasses import dataclass
from typing import Optional


@dataclass
class Client:
    id: int
    arrival_time: float
    service_type: int

    # vendedor
    seller_start_time: Optional[float] = None
    seller_end_time: Optional[float] = None

    # técnico
    technician_start_time: Optional[float] = None
    technician_end_time: Optional[float] = None

    # especialista
    specialist_start_time: Optional[float] = None
    specialist_end_time: Optional[float] = None

    # salida del sistema
    exit_time: Optional[float] = None
