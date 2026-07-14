"""Streaming simulation statistics collector."""

from dataclasses import dataclass, field
from decimal import Decimal

from blackjack_simulator.round import RoundResult
from blackjack_simulator.statistics.metrics import RunningVariance
from blackjack_simulator.statistics.report import SimulationReport


@dataclass(slots=True)
class StatisticsCollector:
    initial_bankroll: Decimal
    rounds: int = 0
    hands: int = 0
    net_result: Decimal = Decimal("0")
    total_initial_bet: Decimal = Decimal("0")
    total_action: Decimal = Decimal("0")
    final_bankroll: Decimal = field(init=False)
    max_bankroll: Decimal = field(init=False)
    max_drawdown: Decimal = Decimal("0")
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    longest_push_streak: int = 0
    _current_win_streak: int = 0
    _current_loss_streak: int = 0
    _current_push_streak: int = 0
    _variance: RunningVariance = field(default_factory=RunningVariance)

    def __post_init__(self) -> None:
        self.final_bankroll = self.initial_bankroll
        self.max_bankroll = self.initial_bankroll

    def record_round(self, result: RoundResult) -> None:
        self.rounds += 1
        self.hands += len(result.player_hands)
        self.net_result += result.net_result
        self.final_bankroll += result.net_result
        self._variance.add(result.net_result)

        for hand in result.player_hands:
            self.total_initial_bet += hand.original_bet
            self.total_action += hand.current_bet
        if result.insurance_settlement is not None:
            self.total_action += result.insurance_settlement.bet

        self.max_bankroll = max(self.max_bankroll, self.final_bankroll)
        self.max_drawdown = max(
            self.max_drawdown,
            self.max_bankroll - self.final_bankroll,
        )
        self._update_streaks(result.net_result)

    def to_report(self) -> SimulationReport:
        return SimulationReport(
            rounds=self.rounds,
            hands=self.hands,
            initial_bankroll=self.initial_bankroll,
            final_bankroll=self.final_bankroll,
            net_result=self.net_result,
            total_initial_bet=self.total_initial_bet,
            total_action=self.total_action,
            average_net_result=self._variance.mean,
            sample_variance=self._variance.sample_variance,
            population_variance=self._variance.population_variance,
            house_edge_initial_bet=self._ratio(
                -self.net_result,
                self.total_initial_bet,
            ),
            house_edge_total_action=self._ratio(-self.net_result, self.total_action),
            rtp=self._rtp(),
            max_drawdown=self.max_drawdown,
            longest_win_streak=self.longest_win_streak,
            longest_loss_streak=self.longest_loss_streak,
            longest_push_streak=self.longest_push_streak,
        )

    def _update_streaks(self, net_result: Decimal) -> None:
        if net_result > 0:
            self._current_win_streak += 1
            self._current_loss_streak = 0
            self._current_push_streak = 0
            self.longest_win_streak = max(
                self.longest_win_streak,
                self._current_win_streak,
            )
        elif net_result < 0:
            self._current_loss_streak += 1
            self._current_win_streak = 0
            self._current_push_streak = 0
            self.longest_loss_streak = max(
                self.longest_loss_streak,
                self._current_loss_streak,
            )
        else:
            self._current_push_streak += 1
            self._current_win_streak = 0
            self._current_loss_streak = 0
            self.longest_push_streak = max(
                self.longest_push_streak,
                self._current_push_streak,
            )

    def _rtp(self) -> Decimal:
        if self.total_action == 0:
            return Decimal("0")

        return (self.total_action + self.net_result) / self.total_action

    @staticmethod
    def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")

        return numerator / denominator
