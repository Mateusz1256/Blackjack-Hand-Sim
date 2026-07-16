"""Task queue service around simulation jobs."""

from dataclasses import dataclass

from blackjack_api.repositories import RunRepository
from blackjack_api.workers import (
    Job,
    LocalTaskQueue,
    batch_task,
    comparison_task,
    simulation_task,
)
from blackjack_simulator.comparison import ComparisonMode
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

    def enqueue_comparison(
        self,
        configs: list[str],
        *,
        names: list[str] | None = None,
        mode: ComparisonMode = ComparisonMode.INDEPENDENT_SEEDS,
        overrides: dict[str, int] | None = None,
    ) -> Job:
        if len(configs) < 2:
            msg = "at least two configurations are required for comparison"
            raise ValueError(msg)
        for config_text in configs:
            parse_app_config(config_text, overrides=overrides)
        if self.run_repository is not None:
            self.run_repository.create(
                run_type="comparison",
                status="queued",
                config_snapshot="\n---\n".join(configs),
            )
        return self.queue.enqueue(
            comparison_task(
                configs,
                names=names,
                mode=mode,
                overrides=overrides,
            ),
        )

    def enqueue_batch(
        self,
        config_text: str,
        *,
        sessions: int,
        rounds_per_session: int,
        base_seed: int | None = None,
        configuration_id: str | None = None,
    ) -> Job:
        app_config = parse_app_config(config_text)
        if self.run_repository is not None:
            self.run_repository.create(
                configuration_id=configuration_id,
                run_type="batch",
                status="queued",
                seed=base_seed if base_seed is not None else app_config.simulation.seed,
                rounds=rounds_per_session,
                config_snapshot=config_text,
            )
        return self.queue.enqueue(
            batch_task(
                config_text,
                sessions=sessions,
                rounds_per_session=rounds_per_session,
                base_seed=base_seed,
            ),
        )

    def get_job(self, job_id: str) -> Job | None:
        return self.queue.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        return self.queue.cancel(job_id)
