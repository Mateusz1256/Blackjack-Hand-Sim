"""Task queue service around simulation jobs."""

from dataclasses import dataclass

from blackjack_api.repositories import RunRepository
from blackjack_api.workers import Job, LocalTaskQueue, simulation_task
from blackjack_simulator.configuration import parse_app_config


@dataclass(slots=True)
class TaskService:
    queue: LocalTaskQueue
    run_repository: RunRepository | None = None

    def enqueue_simulation(
        self,
        config_text: str,
        *,
        configuration_id: str | None = None,
    ) -> Job:
        app_config = parse_app_config(config_text)
        if self.run_repository is not None:
            self.run_repository.create(
                configuration_id=configuration_id,
                run_type="simulation",
                status="queued",
                seed=app_config.simulation.seed,
                rounds=app_config.simulation.rounds,
                config_snapshot=config_text,
            )
        return self.queue.enqueue(simulation_task(config_text))

    def get_job(self, job_id: str) -> Job | None:
        return self.queue.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        return self.queue.cancel(job_id)
