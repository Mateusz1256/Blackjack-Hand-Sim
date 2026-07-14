from decimal import Decimal

from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import SimulationConfig, run_simulation
from blackjack_simulator.hand import Hand
from blackjack_simulator.output.console import render_console_report
from blackjack_simulator.output.csv_output import report_to_csv
from blackjack_simulator.output.json_output import report_to_json
from blackjack_simulator.round import FixedActionStrategy, RoundResult
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.settlement import Outcome, SettlementResult
from blackjack_simulator.statistics.collector import StatisticsCollector
from blackjack_simulator.statistics.metrics import RunningVariance


def hand_with_bet(bet: Decimal) -> Hand:
    return Hand(
        cards=[Card(Rank.TEN), Card(Rank.SEVEN)],
        original_bet=bet,
        current_bet=bet,
    )


def round_result(net: Decimal, bet: Decimal, outcome: Outcome) -> RoundResult:
    return RoundResult(
        player_hands=[hand_with_bet(bet)],
        dealer_hand=Hand(cards=[Card(Rank.TEN), Card(Rank.SIX)]),
        settlements=[SettlementResult(outcome=outcome, net_result=net)],
    )


class ScriptedShoe:
    def __init__(self, *ranks: Rank) -> None:
        self._cards = [Card(rank) for rank in ranks]

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def needs_shuffle(self) -> bool:
        return False

    def reset(self) -> None:
        raise AssertionError("scripted shoe should not reset")


def test_running_variance_uses_welford_algorithm() -> None:
    variance = RunningVariance()

    variance.add(Decimal("10"))
    variance.add(Decimal("-10"))
    variance.add(Decimal("0"))

    assert variance.count == 3
    assert variance.mean == Decimal("0")
    assert variance.sample_variance == Decimal("100")
    assert variance.population_variance == Decimal("66.66666666666666666666666667")


def test_statistics_collector_aggregates_round_metrics() -> None:
    collector = StatisticsCollector(initial_bankroll=Decimal("100"))

    collector.record_round(
        round_result(Decimal("10"), Decimal("10"), Outcome.PLAYER_WIN),
    )
    collector.record_round(
        round_result(Decimal("-10"), Decimal("10"), Outcome.DEALER_WIN),
    )
    collector.record_round(round_result(Decimal("0"), Decimal("10"), Outcome.PUSH))

    report = collector.to_report()

    assert report.rounds == 3
    assert report.hands == 3
    assert report.net_result == Decimal("0")
    assert report.final_bankroll == Decimal("100")
    assert report.average_net_result == Decimal("0")
    assert report.sample_variance == Decimal("100")
    assert report.house_edge_initial_bet == Decimal("0")
    assert report.house_edge_total_action == Decimal("0")
    assert report.rtp == Decimal("1")
    assert report.max_drawdown == Decimal("10")
    assert report.longest_win_streak == 1
    assert report.longest_loss_streak == 1
    assert report.longest_push_streak == 1


def test_house_edge_uses_initial_bet_and_total_action_denominators() -> None:
    collector = StatisticsCollector(initial_bankroll=Decimal("100"))
    hand = Hand(
        cards=[Card(Rank.TEN), Card(Rank.SEVEN)],
        original_bet=Decimal("10"),
        current_bet=Decimal("20"),
        doubled=True,
    )
    result = RoundResult(
        player_hands=[hand],
        dealer_hand=Hand(cards=[Card(Rank.TEN), Card(Rank.SIX)]),
        settlements=[
            SettlementResult(outcome=Outcome.DEALER_WIN, net_result=Decimal("-20"))
        ],
    )

    collector.record_round(result)
    report = collector.to_report()

    assert report.house_edge_initial_bet == Decimal("2")
    assert report.house_edge_total_action == Decimal("1")


def test_json_output_shape() -> None:
    collector = StatisticsCollector(initial_bankroll=Decimal("100"))
    collector.record_round(
        round_result(Decimal("10"), Decimal("10"), Outcome.PLAYER_WIN),
    )

    payload = report_to_json(collector.to_report())

    assert '"rounds": 1' in payload
    assert '"net_result": "10"' in payload


def test_csv_output_shape() -> None:
    collector = StatisticsCollector(initial_bankroll=Decimal("100"))
    collector.record_round(
        round_result(Decimal("10"), Decimal("10"), Outcome.PLAYER_WIN),
    )

    payload = report_to_csv(collector.to_report())

    assert payload.splitlines()[0].startswith("rounds,hands,net_result")
    assert "1,1,10" in payload


def test_console_report_contains_key_metrics() -> None:
    collector = StatisticsCollector(initial_bankroll=Decimal("100"))
    collector.record_round(
        round_result(Decimal("10"), Decimal("10"), Outcome.PLAYER_WIN),
    )

    payload = render_console_report(collector.to_report())

    assert "Rounds: 1" in payload
    assert "Net result: 10" in payload


def test_engine_can_populate_statistics_report() -> None:
    collector = StatisticsCollector(initial_bankroll=Decimal("100"))
    shoe = ScriptedShoe(Rank.TEN, Rank.NINE, Rank.EIGHT, Rank.SEVEN, Rank.KING)

    result = run_simulation(
        shoe=shoe,
        config=SimulationConfig(
            rounds=1,
            initial_bankroll=Decimal("100"),
            betting_amount=Decimal("10"),
            dealer_rules=DealerRules(),
        ),
        player_strategy=FixedActionStrategy(),
        statistics_collector=collector,
    )

    assert result.statistics is not None
    assert result.statistics.rounds == 1
    assert result.statistics.net_result == result.final_bankroll - Decimal("100")
