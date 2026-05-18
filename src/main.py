import random

from simulation.simulator import HappyComputingSimulator


def main():

    sim = HappyComputingSimulator(simulation_time=60)

    # -------------------------
    # TEST CONTROLADO
    # -------------------------

    # mezcla de tipos
    sim.random.tipo_servicio = lambda: random.choice([1, 2, 3, 4])

    # llega un cliente cada 3 min
    # (más legible)
    sim.random.tiempo_entre_llegadas = lambda: 3

    # vendedor rápido
    sim.random.tiempo_vendedor = lambda: 5

    # técnico
    sim.random.tiempo_tecnico = lambda: 8

    # especialista
    sim.random.tiempo_tecnico_especializado = lambda: 12

    sim.run()

    print("\n========== RESULTADOS ==========")

    print(f"Clientes creados: {len(sim.clients)}")

    print(f"Dinero generado: {sim.money}")


if __name__ == "__main__":
    main()
