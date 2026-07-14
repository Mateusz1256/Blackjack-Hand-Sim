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
    SurrenderRules,
    SurrenderType,
)
from blackjack_simulator.shoe import Shoe
from blackjack_simulator.strategies import (
    BasicStrategy,
    BasicStrategyProfile,
    basic_strategy_for_rules,
)

__all__ = [
    "Action",
    "BasicStrategy",
    "BasicStrategyProfile",
    "Card",
    "DealerRules",
    "DoubleRules",
    "Hand",
    "Rank",
    "Shoe",
    "SimulationConfig",
    "SimulationResult",
    "SurrenderRules",
    "SurrenderType",
    "__version__",
    "basic_strategy_for_rules",
    "run_simulation",
]

__version__ = "0.1.0"
