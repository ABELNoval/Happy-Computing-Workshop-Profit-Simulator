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
        # -------------------------
        # Crear cliente
        # -------------------------
        client_id = self.next_client_id
        self.next_client_id += 1

        client = Client(
            id=client_id,
            arrival_time=self.clock,
            service_type=self.random.tipo_servicio(),
        )

        self.clients[client.id] = client

        print(
            f"[{self.clock:.2f}] Cliente {client.id} llegó (tipo {client.service_type})"
        )

        # -------------------------

        # Programar siguiente llegada
        # -------------------------

        next_arrival = self.clock + self.random.tiempo_entre_llegadas()

        self.event_queue.push(
            Event(time=next_arrival, event_type=EventType.CLIENT_ARRIVAL)
        )

        # -------------------------
        # Buscar vendedor libre
        # -------------------------

        free_seller = None

        for seller in self.sellers:
            if not seller.busy:
                free_seller = seller
                break

        # -------------------------
        # Si hay vendedor
        # -------------------------

        if free_seller:
            free_seller.busy = True
            free_seller.current_client_id = client.id

            client.seller_start_time = self.clock

            finish_time = self.clock + self.random.tiempo_vendedor()

            self.event_queue.push(
                Event(
                    time=finish_time,
                    event_type=(EventType.SELLER_FINISH),
                    client_id=client.id,
                    employee_id=free_seller.id,
                )
            )

        # -------------------------
        # Si no hay vendedor
        # -------------------------

        else:
            self.seller_queue.append(client.id)

            print(f"Cliente {client.id} entra en cola vendedor")

    def handle_seller_finish(self, event):
        pass

    def handle_technician_finish(self, event):
        pass

    def handle_specialist_finish(self, event):
        pass
