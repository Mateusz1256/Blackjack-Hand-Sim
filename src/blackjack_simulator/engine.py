"""Basic multi-round simulation orchestration."""

from dataclasses import dataclass, field
from decimal import Decimal

from blackjack_simulator.betting import FlatBettingStrategy
from blackjack_simulator.round import PlayerStrategy, RoundResult, RoundShoe, play_round
from blackjack_simulator.rules import DealerRules


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    rounds: int
    initial_bankroll: Decimal
    betting_amount: Decimal
    blackjack_payout: Decimal = Decimal("1.5")
    dealer_rules: DealerRules = field(default_factory=DealerRules)

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


def run_simulation(
    *,
    shoe: RoundShoe,
    config: SimulationConfig,
    player_strategy: PlayerStrategy,
) -> SimulationResult:
    betting = FlatBettingStrategy(config.betting_amount)
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
        )
        bankroll += result.settlement.net_result
        round_results.append(result)

    return SimulationResult(
        rounds=round_results,
        initial_bankroll=config.initial_bankroll,
        final_bankroll=bankroll,
    )
