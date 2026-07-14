"""Basic multi-round simulation orchestration."""

from dataclasses import dataclass, field
from decimal import Decimal

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


def run_simulation(
    *,
    shoe: RoundShoe,
    config: SimulationConfig,
    player_strategy: PlayerStrategy,
    insurance_strategy: InsuranceStrategy | None = None,
    betting_strategy: BettingStrategy | None = None,
    card_counter: CardCounter | None = None,
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
        round_results.append(result)

    return SimulationResult(
        rounds=round_results,
        initial_bankroll=config.initial_bankroll,
        final_bankroll=bankroll,
    )
