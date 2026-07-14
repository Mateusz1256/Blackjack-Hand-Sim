"""Basic multi-round simulation orchestration."""

from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha256
from random import Random

from blackjack_simulator.betting import FlatBettingStrategy
from blackjack_simulator.betting.base import BettingStrategy, outcome_from_net_result
from blackjack_simulator.counting.base import CardCounter
from blackjack_simulator.round import PlayerStrategy, RoundResult, RoundShoe, play_round
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
    HoleCardRules,
    InsuranceRules,
    SplitRules,
    SurrenderRules,
)
from blackjack_simulator.shoe import Shoe
from blackjack_simulator.statistics.collector import StatisticsCollector
from blackjack_simulator.statistics.report import SimulationReport
from blackjack_simulator.strategies.insurance import (
    InsuranceStrategy,
    NeverInsuranceStrategy,
)


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    rounds: int
    initial_bankroll: Decimal
    betting_amount: Decimal
    blackjack_payout: Decimal = Decimal("1.5")
    dealer_rules: DealerRules = field(default_factory=DealerRules)
    double_rules: DoubleRules = field(default_factory=DoubleRules)
    surrender_rules: SurrenderRules = field(default_factory=SurrenderRules)
    split_rules: SplitRules = field(default_factory=SplitRules)
    insurance_rules: InsuranceRules = field(default_factory=InsuranceRules)
    hole_card_rules: HoleCardRules = field(default_factory=HoleCardRules)

    def __post_init__(self) -> None:
        if self.rounds < 0:
            msg = "rounds must not be negative"
            raise ValueError(msg)
        if self.initial_bankroll < 0:
            msg = "initial bankroll must not be negative"
            raise ValueError(msg)
        if self.blackjack_payout <= 0:
            msg = "blackjack payout must be positive"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class SimulationResult:
    rounds: list[RoundResult]
    initial_bankroll: Decimal
    final_bankroll: Decimal
    statistics: SimulationReport | None = None


@dataclass(frozen=True, slots=True)
class WorkerShoeConfig:
    decks: int
    penetration: float
    shuffle_after_each_round: bool = False


@dataclass(frozen=True, slots=True)
class WorkerSimulationResult:
    worker_index: int
    rounds: int
    seed: int
    final_bankroll: Decimal
    statistics_collector: StatisticsCollector


@dataclass(frozen=True, slots=True)
class FlatBettingStrategyFactory:
    amount: Decimal

    def __call__(
        self,
        shoe: Shoe | None = None,
        card_counter: CardCounter | None = None,
    ) -> BettingStrategy:
        del shoe, card_counter
        return FlatBettingStrategy(self.amount)


@dataclass(frozen=True, slots=True)
class _WorkerSimulationJob:
    worker_index: int
    rounds: int
    seed: int
    config: SimulationConfig
    shoe_config: WorkerShoeConfig
    player_strategy_factory: Callable[[], PlayerStrategy]
    insurance_strategy_factory: Callable[[], InsuranceStrategy]
    betting_strategy_factory: Callable[[Shoe, CardCounter | None], BettingStrategy]
    card_counter_factory: Callable[[], CardCounter] | None


def run_simulation(
    *,
    shoe: RoundShoe,
    config: SimulationConfig,
    player_strategy: PlayerStrategy,
    insurance_strategy: InsuranceStrategy | None = None,
    betting_strategy: BettingStrategy | None = None,
    card_counter: CardCounter | None = None,
    statistics_collector: StatisticsCollector | None = None,
    store_rounds: bool = True,
) -> SimulationResult:
    insurance_strategy = insurance_strategy or NeverInsuranceStrategy()
    betting = betting_strategy or FlatBettingStrategy(config.betting_amount)
    bankroll = config.initial_bankroll
    round_results: list[RoundResult] = []

    for _ in range(config.rounds):
        bet = betting.next_bet(bankroll)
        result = play_round(
            shoe=shoe,
            dealer_rules=config.dealer_rules,
            player_strategy=player_strategy,
            bet=bet,
            blackjack_payout=config.blackjack_payout,
            double_rules=config.double_rules,
            surrender_rules=config.surrender_rules,
            split_rules=config.split_rules,
            insurance_rules=config.insurance_rules,
            insurance_strategy=insurance_strategy,
            hole_card_rules=config.hole_card_rules,
            card_counter=card_counter,
        )
        bankroll += result.net_result
        betting.update_after_round(outcome_from_net_result(result.net_result))
        if statistics_collector is not None:
            statistics_collector.record_round(result)
        if store_rounds:
            round_results.append(result)

    return SimulationResult(
        rounds=round_results,
        initial_bankroll=config.initial_bankroll,
        final_bankroll=bankroll,
        statistics=(
            statistics_collector.to_report()
            if statistics_collector is not None
            else None
        ),
    )


def derive_worker_seed(top_level_seed: int, worker_index: int) -> int:
    if worker_index < 0:
        msg = "worker index must not be negative"
        raise ValueError(msg)

    payload = f"{top_level_seed}:{worker_index}".encode("ascii")
    return int.from_bytes(sha256(payload).digest()[:8], byteorder="big")


def split_worker_rounds(rounds: int, worker_count: int) -> tuple[int, ...]:
    if rounds < 0:
        msg = "rounds must not be negative"
        raise ValueError(msg)
    if worker_count <= 0:
        msg = "worker count must be positive"
        raise ValueError(msg)

    base_rounds, remainder = divmod(rounds, worker_count)
    return tuple(
        base_rounds + (1 if worker_index < remainder else 0)
        for worker_index in range(worker_count)
    )


def run_worker_simulations(
    *,
    config: SimulationConfig,
    shoe_config: WorkerShoeConfig,
    top_level_seed: int,
    worker_count: int,
    player_strategy_factory: Callable[[], PlayerStrategy],
    insurance_strategy_factory: Callable[
        [], InsuranceStrategy
    ] = NeverInsuranceStrategy,
    betting_strategy_factory: (
        Callable[[Shoe, CardCounter | None], BettingStrategy] | None
    ) = None,
    card_counter_factory: Callable[[], CardCounter] | None = None,
    use_processes: bool = True,
) -> SimulationResult:
    if betting_strategy_factory is None:
        betting_strategy_factory = FlatBettingStrategyFactory(config.betting_amount)

    jobs = [
        _WorkerSimulationJob(
            worker_index=worker_index,
            rounds=rounds,
            seed=derive_worker_seed(top_level_seed, worker_index),
            config=SimulationConfig(
                rounds=rounds,
                initial_bankroll=config.initial_bankroll,
                betting_amount=config.betting_amount,
                blackjack_payout=config.blackjack_payout,
                dealer_rules=config.dealer_rules,
                double_rules=config.double_rules,
                surrender_rules=config.surrender_rules,
                split_rules=config.split_rules,
                insurance_rules=config.insurance_rules,
                hole_card_rules=config.hole_card_rules,
            ),
            shoe_config=shoe_config,
            player_strategy_factory=player_strategy_factory,
            insurance_strategy_factory=insurance_strategy_factory,
            betting_strategy_factory=betting_strategy_factory,
            card_counter_factory=card_counter_factory,
        )
        for worker_index, rounds in enumerate(
            split_worker_rounds(config.rounds, worker_count),
        )
        if rounds > 0
    ]

    if use_processes and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            worker_results = list(executor.map(_run_worker_simulation_job, jobs))
    else:
        worker_results = [_run_worker_simulation_job(job) for job in jobs]

    worker_results.sort(key=lambda result: result.worker_index)
    collector = StatisticsCollector(initial_bankroll=config.initial_bankroll)
    for worker_result in worker_results:
        collector.merge(worker_result.statistics_collector)

    report = collector.to_report()
    return SimulationResult(
        rounds=[],
        initial_bankroll=config.initial_bankroll,
        final_bankroll=report.final_bankroll,
        statistics=report,
    )


def _run_worker_simulation_job(job: _WorkerSimulationJob) -> WorkerSimulationResult:
    collector = StatisticsCollector(initial_bankroll=job.config.initial_bankroll)
    shoe = Shoe(
        decks=job.shoe_config.decks,
        penetration=job.shoe_config.penetration,
        rng=Random(job.seed),
        shuffle_after_each_round=job.shoe_config.shuffle_after_each_round,
    )
    card_counter = (
        job.card_counter_factory() if job.card_counter_factory is not None else None
    )
    result = run_simulation(
        shoe=shoe,
        config=job.config,
        player_strategy=job.player_strategy_factory(),
        insurance_strategy=job.insurance_strategy_factory(),
        betting_strategy=job.betting_strategy_factory(shoe, card_counter),
        card_counter=card_counter,
        statistics_collector=collector,
        store_rounds=False,
    )
    return WorkerSimulationResult(
        worker_index=job.worker_index,
        rounds=job.rounds,
        seed=job.seed,
        final_bankroll=result.final_bankroll,
        statistics_collector=collector,
    )
