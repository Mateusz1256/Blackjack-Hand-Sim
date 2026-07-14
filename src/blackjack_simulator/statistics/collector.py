"""Streaming simulation statistics collector."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum

from blackjack_simulator.round import RoundResult
from blackjack_simulator.statistics.metrics import RunningVariance
from blackjack_simulator.statistics.report import SimulationReport


class _StreakKind(StrEnum):
    WIN = "win"
    LOSS = "loss"
    PUSH = "push"


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
    min_bankroll: Decimal = field(init=False)
    max_drawdown: Decimal = Decimal("0")
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    longest_push_streak: int = 0
    leading_streak_kind: _StreakKind | None = None
    leading_streak_length: int = 0
    trailing_streak_kind: _StreakKind | None = None
    trailing_streak_length: int = 0
    _current_win_streak: int = 0
    _current_loss_streak: int = 0
    _current_push_streak: int = 0
    _variance: RunningVariance = field(default_factory=RunningVariance)

    def __post_init__(self) -> None:
        self.final_bankroll = self.initial_bankroll
        self.max_bankroll = self.initial_bankroll
        self.min_bankroll = self.initial_bankroll

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
        self.min_bankroll = min(self.min_bankroll, self.final_bankroll)
        self.max_drawdown = max(
            self.max_drawdown,
            self.max_bankroll - self.final_bankroll,
        )
        self._update_streaks(result.net_result)

    def merge(self, other: "StatisticsCollector") -> None:
        if other.rounds == 0:
            return
        if self.rounds == 0:
            self._copy_from(other)
            return

        self._merge_streaks(other)
        original_final_bankroll = self.final_bankroll
        original_max_bankroll = self.max_bankroll
        other_bankroll_offset = original_final_bankroll - other.initial_bankroll

        self.rounds += other.rounds
        self.hands += other.hands
        self.net_result += other.net_result
        self.total_initial_bet += other.total_initial_bet
        self.total_action += other.total_action
        self.final_bankroll += other.net_result
        self._variance.merge(other._variance)

        shifted_other_max = other.max_bankroll + other_bankroll_offset
        shifted_other_min = other.min_bankroll + other_bankroll_offset
        self.max_bankroll = max(self.max_bankroll, shifted_other_max)
        self.min_bankroll = min(self.min_bankroll, shifted_other_min)
        cross_drawdown = original_max_bankroll - shifted_other_min
        self.max_drawdown = max(
            self.max_drawdown,
            other.max_drawdown,
            cross_drawdown,
        )

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
        kind = _streak_kind(net_result)
        self._update_edge_streaks(kind)
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

    def _copy_from(self, other: "StatisticsCollector") -> None:
        self.rounds = other.rounds
        self.hands = other.hands
        self.net_result = other.net_result
        self.total_initial_bet = other.total_initial_bet
        self.total_action = other.total_action
        self.final_bankroll = other.final_bankroll
        self.max_bankroll = other.max_bankroll
        self.min_bankroll = other.min_bankroll
        self.max_drawdown = other.max_drawdown
        self.longest_win_streak = other.longest_win_streak
        self.longest_loss_streak = other.longest_loss_streak
        self.longest_push_streak = other.longest_push_streak
        self.leading_streak_kind = other.leading_streak_kind
        self.leading_streak_length = other.leading_streak_length
        self.trailing_streak_kind = other.trailing_streak_kind
        self.trailing_streak_length = other.trailing_streak_length
        self._current_win_streak = other._current_win_streak
        self._current_loss_streak = other._current_loss_streak
        self._current_push_streak = other._current_push_streak
        self._variance = RunningVariance(
            count=other._variance.count,
            mean=other._variance.mean,
            _m2=other._variance._m2,
        )

    def _update_edge_streaks(self, kind: _StreakKind) -> None:
        if self.rounds == 1:
            self.leading_streak_kind = kind
            self.leading_streak_length = 1
            self.trailing_streak_kind = kind
            self.trailing_streak_length = 1
            return

        if (
            self.leading_streak_kind is kind
            and self.leading_streak_length == self.rounds - 1
        ):
            self.leading_streak_length += 1

        if self.trailing_streak_kind is kind:
            self.trailing_streak_length += 1
        else:
            self.trailing_streak_kind = kind
            self.trailing_streak_length = 1

    def _merge_streaks(self, other: "StatisticsCollector") -> None:
        self.longest_win_streak = max(
            self.longest_win_streak,
            other.longest_win_streak,
        )
        self.longest_loss_streak = max(
            self.longest_loss_streak,
            other.longest_loss_streak,
        )
        self.longest_push_streak = max(
            self.longest_push_streak,
            other.longest_push_streak,
        )

        if (
            self.trailing_streak_kind is not None
            and self.trailing_streak_kind is other.leading_streak_kind
        ):
            boundary_streak = self.trailing_streak_length + other.leading_streak_length
            if self.trailing_streak_kind is _StreakKind.WIN:
                self.longest_win_streak = max(
                    self.longest_win_streak,
                    boundary_streak,
                )
            elif self.trailing_streak_kind is _StreakKind.LOSS:
                self.longest_loss_streak = max(
                    self.longest_loss_streak,
                    boundary_streak,
                )
            else:
                self.longest_push_streak = max(
                    self.longest_push_streak,
                    boundary_streak,
                )

        if (
            self.leading_streak_kind is other.leading_streak_kind
            and self.leading_streak_length == self.rounds
        ):
            self.leading_streak_length += other.leading_streak_length

        if self.trailing_streak_kind is other.trailing_streak_kind:
            self.trailing_streak_length += other.trailing_streak_length
        else:
            self.trailing_streak_kind = other.trailing_streak_kind
            self.trailing_streak_length = other.trailing_streak_length

        self._current_win_streak = 0
        self._current_loss_streak = 0
        self._current_push_streak = 0
        if self.trailing_streak_kind is _StreakKind.WIN:
            self._current_win_streak = self.trailing_streak_length
        elif self.trailing_streak_kind is _StreakKind.LOSS:
            self._current_loss_streak = self.trailing_streak_length
        else:
            self._current_push_streak = self.trailing_streak_length

    def _rtp(self) -> Decimal:
        if self.total_action == 0:
            return Decimal("0")

        return (self.total_action + self.net_result) / self.total_action

    @staticmethod
    def _ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")

        return numerator / denominator


def _streak_kind(net_result: Decimal) -> _StreakKind:
    if net_result > 0:
        return _StreakKind.WIN
    if net_result < 0:
        return _StreakKind.LOSS
    return _StreakKind.PUSH
