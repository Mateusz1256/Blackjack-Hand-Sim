from decimal import Decimal
from functools import partial

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import (
    SimulationConfig,
    WorkerShoeConfig,
    derive_worker_seed,
    run_worker_simulations,
    split_worker_rounds,
)
from blackjack_simulator.hand import Hand
from blackjack_simulator.round import FixedActionStrategy, RoundResult
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.settlement import Outcome, SettlementResult
from blackjack_simulator.statistics.collector import StatisticsCollector


def hand_with_bet(bet: Decimal) -> Hand:
    return Hand(
        cards=[Card(Rank.TEN), Card(Rank.SEVEN)],
        original_bet=bet,
        current_bet=bet,
    )


def round_result(net: Decimal) -> RoundResult:
    return RoundResult(
        player_hands=[hand_with_bet(Decimal("10"))],
        dealer_hand=Hand(cards=[Card(Rank.TEN), Card(Rank.SIX)]),
        settlements=[SettlementResult(outcome=Outcome.PUSH, net_result=net)],
    )


def test_worker_seed_derivation_is_deterministic() -> None:
    first = [derive_worker_seed(123, worker_index) for worker_index in range(4)]
    second = [derive_worker_seed(123, worker_index) for worker_index in range(4)]

    assert first == second
    assert len(set(first)) == len(first)
    assert first != [derive_worker_seed(124, worker_index) for worker_index in range(4)]


def test_split_worker_rounds_distributes_remainder_to_lowest_workers() -> None:
    assert split_worker_rounds(rounds=10, worker_count=3) == (4, 3, 3)
    assert split_worker_rounds(rounds=2, worker_count=4) == (1, 1, 0, 0)


def test_statistics_merge_matches_sequential_collection() -> None:
    sequence = [
        Decimal("10"),
        Decimal("10"),
        Decimal("-10"),
        Decimal("-10"),
        Decimal("0"),
        Decimal("0"),
        Decimal("10"),
    ]
    sequential = StatisticsCollector(initial_bankroll=Decimal("100"))
    for net_result in sequence:
        sequential.record_round(round_result(net_result))

    merged = StatisticsCollector(initial_bankroll=Decimal("100"))
    for chunk in (sequence[:2], sequence[2:5], sequence[5:]):
        worker_collector = StatisticsCollector(initial_bankroll=Decimal("100"))
        for net_result in chunk:
            worker_collector.record_round(round_result(net_result))
        merged.merge(worker_collector)

    merged_report = merged.to_report()
    sequential_report = sequential.to_report()

    assert merged_report.rounds == sequential_report.rounds
    assert merged_report.hands == sequential_report.hands
    assert merged_report.final_bankroll == sequential_report.final_bankroll
    assert merged_report.net_result == sequential_report.net_result
    assert merged_report.total_initial_bet == sequential_report.total_initial_bet
    assert merged_report.total_action == sequential_report.total_action
    assert merged_report.max_drawdown == sequential_report.max_drawdown
    assert merged_report.longest_win_streak == sequential_report.longest_win_streak
    assert merged_report.longest_loss_streak == sequential_report.longest_loss_streak
    assert merged_report.longest_push_streak == sequential_report.longest_push_streak
    assert abs(
        merged_report.sample_variance - sequential_report.sample_variance
    ) < Decimal("1e-24")
    assert abs(
        merged_report.population_variance - sequential_report.population_variance
    ) < Decimal("1e-24")


def test_worker_simulations_are_deterministic_and_aggregate_rounds() -> None:
    config = SimulationConfig(
        rounds=6,
        initial_bankroll=Decimal("100"),
        betting_amount=Decimal("10"),
        dealer_rules=DealerRules(),
    )
    shoe_config = WorkerShoeConfig(decks=1, penetration=0.75)
    strategy_factory = partial(FixedActionStrategy, Action.STAND)

    first = run_worker_simulations(
        config=config,
        shoe_config=shoe_config,
        top_level_seed=123,
        worker_count=3,
        player_strategy_factory=strategy_factory,
        use_processes=False,
    )
    second = run_worker_simulations(
        config=config,
        shoe_config=shoe_config,
        top_level_seed=123,
        worker_count=3,
        player_strategy_factory=strategy_factory,
        use_processes=False,
    )

    assert first.statistics is not None
    assert second.statistics is not None
    assert first.statistics == second.statistics
    assert first.statistics.rounds == 6
    assert first.final_bankroll == first.initial_bankroll + first.statistics.net_result
