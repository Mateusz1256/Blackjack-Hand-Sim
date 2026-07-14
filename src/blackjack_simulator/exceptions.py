"""Domain exceptions for blackjack simulator."""


class BlackjackSimulatorError(Exception):
    """Base exception for simulator errors."""


class InsufficientBankrollError(BlackjackSimulatorError):
    """Raised when bankroll cannot satisfy table limits or the requested bet."""
