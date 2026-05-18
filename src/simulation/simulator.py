from collections import deque
from statistics import mean

from generators.random_variables import RandomVariables

from models.client import Client
from models.employee import Employee
from models.event import Event, EventType

from simulation.event_queue import EventQueue


class HappyComputingSimulator:
    def __init__(self, simulation_time=480, seed=None):

        # reloj de simulación
        self.clock = 0.0

        # duración (8 horas)
        self.simulation_time = simulation_time

        # generador aleatorio
        self.random = RandomVariables(seed=seed)

        # agenda de eventos
        self.event_queue = EventQueue()

        self.reset_state()

    def reset_state(self):
        self.event_queue = EventQueue()
        self.clients = {}

        self.next_client_id = 1
        self.money = 0

        self.sellers = [Employee(1, "seller"), Employee(2, "seller")]
        self.technicians = [
            Employee(1, "technician"),
            Employee(2, "technician"),
            Employee(3, "technician"),
        ]
        self.specialist = Employee(1, "specialist")

        self.seller_queue = deque()
        self.technician_queue = deque()
        self.specialist_queue = deque()

        self.max_seller_queue = 0
        self.max_technician_queue = 0
        self.max_specialist_queue = 0

        self.money_by_service = {1: 0, 2: 0, 3: 0, 4: 0}
        self.completed_by_service = {1: 0, 2: 0, 3: 0, 4: 0}

        self.wait_times = {"seller": [], "technician": [], "specialist": []}
        self.system_times = []

        self.arrivals_in_horizon = 0
        self.completed_clients = 0

    def record_queue_lengths(self):
        self.max_seller_queue = max(self.max_seller_queue, len(self.seller_queue))
        self.max_technician_queue = max(
            self.max_technician_queue, len(self.technician_queue)
        )
        self.max_specialist_queue = max(
            self.max_specialist_queue, len(self.specialist_queue)
        )

    def add_revenue(self, service_type, amount):
        self.money += amount
        self.money_by_service[service_type] += amount

    def average_or_zero(self, values):
        return mean(values) if values else 0.0

    def build_summary(self):
        return {
            "simulation_time": self.simulation_time,
            "clients_created": len(self.clients),
            "arrivals_in_horizon": self.arrivals_in_horizon,
            "clients_completed": self.completed_clients,
            "money_total": self.money,
            "money_by_service": self.money_by_service,
            "completed_by_service": self.completed_by_service,
            "average_wait_seller": self.average_or_zero(self.wait_times["seller"]),
            "average_wait_technician": self.average_or_zero(
                self.wait_times["technician"]
            ),
            "average_wait_specialist": self.average_or_zero(
                self.wait_times["specialist"]
            ),
            "average_time_in_system": self.average_or_zero(self.system_times),
            "max_seller_queue": self.max_seller_queue,
            "max_technician_queue": self.max_technician_queue,
            "max_specialist_queue": self.max_specialist_queue,
            "remaining_seller_queue": len(self.seller_queue),
            "remaining_technician_queue": len(self.technician_queue),
            "remaining_specialist_queue": len(self.specialist_queue),
        }

    def initialize(self):

        first_arrival = self.random.tiempo_entre_llegadas()

        if first_arrival <= self.simulation_time:
            self.event_queue.push(
                Event(time=first_arrival, event_type=EventType.CLIENT_ARRIVAL)
            )

    def run(self):

        self.reset_state()
        self.initialize()

        while not self.event_queue.is_empty():
            event = self.event_queue.pop()
            self.clock = event.time

            match event.event_type:
                case EventType.CLIENT_ARRIVAL:
                    self.handle_client_arrival(event)

                case EventType.SELLER_FINISH:
                    self.handle_seller_finish(event)

                case EventType.TECHNICIAN_FINISH:
                    self.handle_technician_finish(event)

                case EventType.SPECIALIST_FINISH:
                    self.handle_specialist_finish(event)
        return self.build_summary()

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
        self.arrivals_in_horizon += 1

        print(
            f"[{self.clock:.2f}] Cliente {client.id} llegó (tipo {client.service_type})"
        )

        # -------------------------
        # Programar siguiente llegada
        # -------------------------

        next_arrival = self.clock + self.random.tiempo_entre_llegadas()

        if next_arrival <= self.simulation_time:
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
            self.wait_times["seller"].append(
                client.seller_start_time - client.arrival_time
            )

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
            self.record_queue_lengths()

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
                self.record_queue_lengths()

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

            if self.clock <= self.simulation_time:
                self.add_revenue(4, 750)

            if self.clock <= self.simulation_time:
                self.completed_clients += 1
                self.completed_by_service[client.service_type] += 1
                self.system_times.append(client.exit_time - client.arrival_time)

            print(f"Cliente {client.id} salió")

        # -------------------------
        # Revisar cola vendedor
        # -------------------------

        if len(self.seller_queue) > 0:
            next_client_id = self.seller_queue.popleft()

            next_client = self.clients[next_client_id]

            seller.busy = True
            seller.current_client_id = next_client.id

            next_client.seller_start_time = self.clock
            self.wait_times["seller"].append(
                next_client.seller_start_time - next_client.arrival_time
            )

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

        if self.clock <= self.simulation_time:
            if client.service_type == 1:
                self.add_revenue(1, 0)
            elif client.service_type == 2:
                self.add_revenue(2, 350)

        if self.clock <= self.simulation_time:
            self.completed_clients += 1
            self.completed_by_service[client.service_type] += 1
            self.system_times.append(client.exit_time - client.arrival_time)

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
            self.wait_times["technician"].append(
                next_client.technician_start_time - next_client.seller_end_time
            )

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

        if self.clock <= self.simulation_time:
            if client.service_type == 3:
                self.add_revenue(3, 500)
            elif client.service_type == 2:
                self.add_revenue(2, 350)

        if self.clock <= self.simulation_time:
            self.completed_clients += 1
            self.completed_by_service[client.service_type] += 1
            self.system_times.append(client.exit_time - client.arrival_time)

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
            self.wait_times["specialist"].append(
                next_client.specialist_start_time - next_client.seller_end_time
            )

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
            self.wait_times["technician"].append(
                next_client.technician_start_time - next_client.seller_end_time
            )

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
