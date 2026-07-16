"""Blackjack simulation package."""

from blackjack_simulator.actions import Action
from blackjack_simulator.betting import (
    BankrollPercentageBettingStrategy,
    BetRoundingMode,
    BetRoundingPolicy,
    DAlembertBettingStrategy,
    FibonacciBettingStrategy,
    FlatBettingStrategy,
    KellyStyleBettingStrategy,
    MartingaleBettingStrategy,
    ParoliBettingStrategy,
    TableLimits,
    TrueCountSpreadBettingStrategy,
)
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.counting import HiLoCounter
from blackjack_simulator.counting.system import (
    ConfigurableCardCounter,
    CountingSystem,
    TrueCountRounding,
    get_counting_system,
)
from blackjack_simulator.engine import (
    FlatBettingStrategyFactory,
    SimulationConfig,
    SimulationResult,
    SimulationStopReason,
    WorkerShoeConfig,
    WorkerSimulationResult,
    derive_worker_seed,
    run_simulation,
    run_worker_simulations,
    split_worker_rounds,
)
from blackjack_simulator.exceptions import InsufficientBankrollError
from blackjack_simulator.hand import Hand
from blackjack_simulator.output import (
    render_console_report,
    report_to_csv,
    report_to_json,
)
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
from blackjack_simulator.statistics import (
    RunningVariance,
    SimulationReport,
    StatisticsCollector,
)
from blackjack_simulator.strategies import (
    AlwaysInsuranceStrategy,
    BasicStrategy,
    BasicStrategyProfile,
    CountBasedInsuranceStrategy,
    DeviatingStrategy,
    DeviationHandType,
    EvenMoneyInsuranceStrategy,
    NeverInsuranceStrategy,
    StrategyDeviation,
    basic_strategy_for_rules,
)
from blackjack_simulator.trace import TraceCollector, TraceEvent, TraceEventType

__all__ = [
    "Action",
    "AlwaysInsuranceStrategy",
    "BankrollPercentageBettingStrategy",
    "BasicStrategy",
    "BasicStrategyProfile",
    "BetRoundingMode",
    "BetRoundingPolicy",
    "Card",
    "ConfigurableCardCounter",
    "CountBasedInsuranceStrategy",
    "CountingSystem",
    "DAlembertBettingStrategy",
    "DealerRules",
    "DeviatingStrategy",
    "DeviationHandType",
    "DoubleRules",
    "EnhcLossRule",
    "EvenMoneyInsuranceStrategy",
    "FibonacciBettingStrategy",
    "FlatBettingStrategy",
    "FlatBettingStrategyFactory",
    "Hand",
    "HiLoCounter",
    "HoleCardMode",
    "HoleCardRules",
    "InsufficientBankrollError",
    "InsuranceRules",
    "KellyStyleBettingStrategy",
    "MartingaleBettingStrategy",
    "NeverInsuranceStrategy",
    "ParoliBettingStrategy",
    "Rank",
    "RunningVariance",
    "Shoe",
    "SimulationConfig",
    "SimulationReport",
    "SimulationResult",
    "SimulationStopReason",
    "SplitRules",
    "StatisticsCollector",
    "StrategyDeviation",
    "SurrenderRules",
    "SurrenderType",
    "TableLimits",
    "TraceCollector",
    "TraceEvent",
    "TraceEventType",
    "TrueCountRounding",
    "TrueCountSpreadBettingStrategy",
    "WorkerShoeConfig",
    "WorkerSimulationResult",
    "__version__",
    "basic_strategy_for_rules",
    "derive_worker_seed",
    "get_counting_system",
    "render_console_report",
    "report_to_csv",
    "report_to_json",
    "run_simulation",
    "run_worker_simulations",
    "split_worker_rounds",
]

__version__ = "1.0.0"
