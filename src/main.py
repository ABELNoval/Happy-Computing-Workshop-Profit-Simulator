import json
from pathlib import Path

from statistics import mean, stdev
from math import sqrt

from simulation.simulator import HappyComputingSimulator


def main():
    project_root = Path(__file__).resolve().parent
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    number_of_runs = 100
    simulation_time = 480
    base_seed = 42

    run_results = []

    for run_index in range(number_of_runs):
        sim = HappyComputingSimulator(
            simulation_time=simulation_time, seed=base_seed + run_index
        )

        summary = sim.run()
        summary["run"] = run_index + 1
        summary["seed"] = base_seed + run_index
        run_results.append(summary)

    aggregate = {
        "number_of_runs": number_of_runs,
        "simulation_time": simulation_time,
        "seed_start": base_seed,
        "seed_end": base_seed + number_of_runs - 1,
        "confidence_intervals_95": {},
        "parameters": {
            "arrivals": {
                "distribution": "Poisson process interarrival times",
                "mean_minutes": 20,
            },
            "service_type_probabilities": {"1": 0.45, "2": 0.25, "3": 0.10, "4": 0.20},
            "vendor_service": {
                "distribution": "Normal",
                "mean_minutes": 5,
                "std_dev_minutes": 2,
            },
            "technician_service": {"distribution": "Exponential", "mean_minutes": 20},
            "specialist_service": {"distribution": "Exponential", "mean_minutes": 15},
            "employees": {"sellers": 2, "technicians": 3, "specialists": 1},
            "prices": {"1": 0, "2": 350, "3": 500, "4": 750},
        },
        "means": {},
        "std_devs": {},
        "mins": {},
        "maxs": {},
    }

    metric_keys = [
        "clients_created",
        "arrivals_in_horizon",
        "clients_completed",
        "money_total",
        "average_wait_seller",
        "average_wait_technician",
        "average_wait_specialist",
        "average_time_in_system",
        "max_seller_queue",
        "max_technician_queue",
        "max_specialist_queue",
    ]

    for metric in metric_keys:
        values = [run[metric] for run in run_results]
        std = stdev(values) if len(values) > 1 else 0.0
        avg = mean(values)

        margin = 1.96 * std / sqrt(len(values))

        aggregate["confidence_intervals_95"][metric] = {
            "lower": avg - margin,
            "upper": avg + margin,
        }
        aggregate["means"][metric] = mean(values)
        aggregate["std_devs"][metric] = stdev(values) if len(values) > 1 else 0.0
        aggregate["mins"][metric] = min(values)
        aggregate["maxs"][metric] = max(values)

    with (results_dir / "simulation_runs.json").open("w", encoding="utf-8") as file:
        json.dump(run_results, file, indent=2, ensure_ascii=False)

    with (results_dir / "simulation_summary.json").open("w", encoding="utf-8") as file:
        json.dump(aggregate, file, indent=2, ensure_ascii=False)

    print("\n========== RESULTADOS ==========")
    print(f"Corridas ejecutadas: {number_of_runs}")
    print(f"Resultados guardados en: {results_dir}")
    print(f"Promedio de dinero: {aggregate['means']['money_total']:.2f}")
    print(
        f"Promedio de tiempo en sistema: {aggregate['means']['average_time_in_system']:.2f}"
    )


if __name__ == "__main__":
    main()
