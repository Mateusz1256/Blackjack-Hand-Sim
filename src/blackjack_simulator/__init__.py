"""Blackjack simulation package."""

from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.engine import (
    SimulationConfig,
    SimulationResult,
    run_simulation,
)
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import (
    DealerRules,
    DoubleRules,
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
    "DealerRules",
    "DoubleRules",
    "EvenMoneyInsuranceStrategy",
    "Hand",
    "InsuranceRules",
    "NeverInsuranceStrategy",
    "Rank",
    "Shoe",
    "SimulationConfig",
    "SimulationResult",
    "SplitRules",
    "SurrenderRules",
    "SurrenderType",
    "__version__",
    "basic_strategy_for_rules",
    "run_simulation",
]

__version__ = "0.1.0"
