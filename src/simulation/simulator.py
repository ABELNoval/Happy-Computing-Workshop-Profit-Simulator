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
        seller = self.sellers[event.employee_id - 1]

        seller.busy = False
        seller.current_client_id = None

        client = self.clients[event.client_id]

        client.seller_end_time = self.clock

        print(f"[{self.clock:.2f}] Cliente {client.id} terminó vendedor")

        # -------------------------
        # FLUJO CLIENTE
        # -------------------------

        # Tipo 1 y 2 → técnico
        if client.service_type in [1, 2]:
            free_technician = None

            for technician in self.technicians:
                if not technician.busy:
                    free_technician = technician
                    break

            # técnico libre
            if free_technician:
                free_technician.busy = True
                free_technician.current_client_id = client.id

                client.technician_start_time = self.clock

                finish_time = self.clock + self.random.tiempo_tecnico()

                self.event_queue.push(
                    Event(
                        time=finish_time,
                        event_type=(EventType.TECHNICIAN_FINISH),
                        client_id=client.id,
                        employee_id=(free_technician.id),
                    )
                )

                print(f"Cliente {client.id} entra a técnico {free_technician.id}")

            # técnico ocupado
            else:
                self.technician_queue.append(client.id)

                print(f"Cliente {client.id} entra cola técnico")

        # -------------------------
        # Tipo 3 → especialista
        # -------------------------

        elif client.service_type == 3:
            if not self.specialist.busy:
                self.specialist.busy = True
                self.specialist.current_client_id = client.id

                client.specialist_start_time = self.clock

                finish_time = self.clock + self.random.tiempo_tecnico_especializado()

                self.event_queue.push(
                    Event(
                        time=finish_time,
                        event_type=(EventType.SPECIALIST_FINISH),
                        client_id=client.id,
                        employee_id=1,
                    )
                )

                print(f"Cliente {client.id} entra especialista")

            else:
                self.specialist_queue.append(client.id)

                print(f"Cliente {client.id} entra cola especialista")

        # -------------------------
        # Tipo 4 → sale
        # -------------------------
        if client.service_type == 4:
            client.exit_time = self.clock

            self.money += 750

            print(f"Cliente {client.id} salió")
            pass

        # -------------------------
        # Revisar cola vendedor
        # -------------------------

        if len(self.seller_queue) > 0:
            next_client_id = self.seller_queue.popleft()

            next_client = self.clients[next_client_id]

            seller.busy = True
            seller.current_client_id = next_client.id

            next_client.seller_start_time = self.clock

            finish_time = self.clock + self.random.tiempo_vendedor()

            self.event_queue.push(
                Event(
                    time=finish_time,
                    event_type=(EventType.SELLER_FINISH),
                    client_id=next_client.id,
                    employee_id=seller.id,
                )
            )

            print(f"Cliente {next_client.id} sale de cola vendedor")

        # -------------------------
        # Si no hay cola
        # -------------------------

        else:
            seller.busy = False
            seller.current_client_id = None

    def handle_technician_finish(self, event):
        technician = self.technicians[event.employee_id - 1]
        client = self.clients[event.client_id]
        client.technician_end_time = self.clock

        print(f"[{self.clock:.2f}] Cliente {client.id} terminó técnico")

        # -------------------------
        # Cliente sale sistema
        # -------------------------
        client.exit_time = self.clock

        # TODO:
        # reemplazar por valores reales
        if client.service_type == 1:
            self.money += 0

        elif client.service_type == 2:
            self.money += 350

        print(f"Cliente {client.id} salió")

        # -------------------------
        # Revisar cola técnico
        # -------------------------

        if len(self.technician_queue) > 0:
            next_client_id = self.technician_queue.popleft()

            next_client = self.clients[next_client_id]

            technician.busy = True

            technician.current_client_id = next_client.id

            next_client.technician_start_time = self.clock

            finish_time = self.clock + self.random.tiempo_tecnico()

            self.event_queue.push(
                Event(
                    time=finish_time,
                    event_type=(EventType.TECHNICIAN_FINISH),
                    client_id=next_client.id,
                    employee_id=(technician.id),
                )
            )

            print(
                f"Cliente {next_client.id} sale cola técnico → técnico {technician.id}"
            )

        else:
            technician.busy = False
            technician.current_client_id = None

    def handle_specialist_finish(self, event):
        client = self.clients[event.client_id]
        client.specialist_end_time = self.clock

        print(f"[{self.clock:.2f}] Cliente {client.id} terminó especialista")

        # -------------------------
        # Cliente sale sistema
        # -------------------------

        client.exit_time = self.clock

        if client.service_type == 3:
            self.money += 500
        elif client.service_type == 2:
            self.money += 350

        print(f"Cliente {client.id} salió")

        # -------------------------
        # PRIORIDAD 1:
        # cola especialista
        # -------------------------

        if len(self.specialist_queue) > 0:
            next_client_id = self.specialist_queue.popleft()

            next_client = self.clients[next_client_id]

            self.specialist.busy = True

            self.specialist.current_client_id = next_client.id

            next_client.specialist_start_time = self.clock

            finish_time = self.clock + self.random.tiempo_tecnico_especializado()

            self.event_queue.push(
                Event(
                    time=finish_time,
                    event_type=(EventType.SPECIALIST_FINISH),
                    client_id=next_client.id,
                    employee_id=1,
                )
            )

            print(f"Cliente {next_client.id} sale cola especialista")

        # -------------------------
        # PRIORIDAD 2:
        # ayudar técnico
        # -------------------------

        elif len(self.technician_queue) > 0:
            next_client_id = self.technician_queue.popleft()

            next_client = self.clients[next_client_id]

            self.specialist.busy = True

            self.specialist.current_client_id = next_client.id

            # usa tiempo de técnico normal
            next_client.technician_start_time = self.clock

            finish_time = self.clock + self.random.tiempo_tecnico()

            self.event_queue.push(
                Event(
                    time=finish_time,
                    event_type=(EventType.SPECIALIST_FINISH),
                    client_id=next_client.id,
                    employee_id=1,
                )
            )

            print(f"Especialista ayuda a técnico con cliente {next_client.id}")

        # -------------------------
        # Sin trabajo
        # -------------------------

        else:
            self.specialist.busy = False

            self.specialist.current_client_id = None
