from collections import deque

from generators.random_variables import RandomVariables

from models.client import Client
from models.employee import Employee
from models.event import Event, EventType

from simulation.event_queue import EventQueue


class HappyComputingSimulator:
    def __init__(self, simulation_time=480):

        # reloj de simulación
        self.clock = 0.0

        # duración (8 horas)
        self.simulation_time = simulation_time

        # generador aleatorio
        self.random = RandomVariables(seed=42)

        # agenda de eventos
        self.event_queue = EventQueue()

        # clientes creados
        self.clients = {}

        # contador ids
        self.next_client_id = 1

        # dinero ganado
        self.money = 0

        # -------------------
        # EMPLEADOS
        # -------------------

        self.sellers = [Employee(1, "seller"), Employee(2, "seller")]

        self.technicians = [
            Employee(1, "technician"),
            Employee(2, "technician"),
            Employee(3, "technician"),
        ]

        self.specialist = Employee(1, "specialist")

        # -------------------
        # COLAS
        # -------------------

        self.seller_queue = deque()

        self.technician_queue = deque()

        self.specialist_queue = deque()

    def initialize(self):

        first_arrival = self.random.tiempo_entre_llegadas()

        self.event_queue.push(
            Event(time=first_arrival, event_type=EventType.CLIENT_ARRIVAL)
        )

    def run(self):

        self.initialize()

        while not self.event_queue.is_empty():
            event = self.event_queue.pop()
            self.clock = event.time
            if self.clock > self.simulation_time:
                break

            match event.event_type:
                case EventType.CLIENT_ARRIVAL:
                    self.handle_client_arrival(event)

                case EventType.SELLER_FINISH:
                    self.handle_seller_finish(event)

                case EventType.TECHNICIAN_FINISH:
                    self.handle_technician_finish(event)

                case EventType.SPECIALIST_FINISH:
                    self.handle_specialist_finish(event)

    def handle_client_arrival(self, event):
        pass

    def handle_seller_finish(self, event):
        pass

    def handle_technician_finish(self, event):
        pass

    def handle_specialist_finish(self, event):
        pass
