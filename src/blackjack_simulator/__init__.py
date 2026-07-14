"""Blackjack simulation package."""

from blackjack_simulator.actions import Action
from blackjack_simulator.betting import (
    DAlembertBettingStrategy,
    FibonacciBettingStrategy,
    FlatBettingStrategy,
    MartingaleBettingStrategy,
    ParoliBettingStrategy,
    TableLimits,
    TrueCountSpreadBettingStrategy,
)
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.counting import HiLoCounter
from blackjack_simulator.engine import (
    SimulationConfig,
    SimulationResult,
    run_simulation,
)
from blackjack_simulator.exceptions import InsufficientBankrollError
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
    EnhcLossRule,
    HoleCardMode,
    HoleCardRules,
    InsuranceRules,
    SplitRules,
    SurrenderRules,
    SurrenderType,
)
from blackjack_simulator.shoe import Shoe
from blackjack_simulator.strategies import (
    AlwaysInsuranceStrategy,
    BasicStrategy,
    BasicStrategyProfile,
    CountBasedInsuranceStrategy,
    EvenMoneyInsuranceStrategy,
    NeverInsuranceStrategy,
    basic_strategy_for_rules,
)

__all__ = [
    "Action",
    "AlwaysInsuranceStrategy",
    "BasicStrategy",
    "BasicStrategyProfile",
    "Card",
    "CountBasedInsuranceStrategy",
    "DAlembertBettingStrategy",
    "DealerRules",
    "DoubleRules",
    "EnhcLossRule",
    "EvenMoneyInsuranceStrategy",
    "FibonacciBettingStrategy",
    "FlatBettingStrategy",
    "Hand",
    "HiLoCounter",
    "HoleCardMode",
    "HoleCardRules",
    "InsufficientBankrollError",
    "InsuranceRules",
    "MartingaleBettingStrategy",
    "NeverInsuranceStrategy",
    "ParoliBettingStrategy",
    "Rank",
    "Shoe",
    "SimulationConfig",
    "SimulationResult",
    "SplitRules",
    "SurrenderRules",
    "SurrenderType",
    "TableLimits",
    "TrueCountSpreadBettingStrategy",
    "__version__",
    "basic_strategy_for_rules",
    "run_simulation",
]

__version__ = "0.1.0"
