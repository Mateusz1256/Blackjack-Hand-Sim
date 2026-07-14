from blackjack_simulator.actions import Action
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.hand import Hand
from blackjack_simulator.rules import DealerRules
from blackjack_simulator.strategies.basic_strategy import (
    BasicStrategy,
    BasicStrategyProfile,
    basic_strategy_for_rules,
)
from blackjack_simulator.strategies.basic_strategy_tables import (
    DEALER_UPCARDS,
    HARD_TOTALS,
    PAIR_RANKS,
    SOFT_TOTALS,
    StrategyDecision,
    get_tables,
)


def hand_with(*ranks: Rank) -> Hand:
    return Hand(cards=[Card(rank) for rank in ranks])


def upcard(rank: Rank) -> Card:
    return Card(rank)


def test_tables_are_complete_for_supported_profiles() -> None:
    for profile in BasicStrategyProfile:
        tables = get_tables(profile)

        assert set(tables.hard) == set(HARD_TOTALS)
        assert set(tables.soft) == set(SOFT_TOTALS)
        assert set(tables.pairs) == set(PAIR_RANKS)

        for row in tables.hard.values():
            assert set(row) == set(DEALER_UPCARDS)
        for row in tables.soft.values():
            assert set(row) == set(DEALER_UPCARDS)
        for row in tables.pairs.values():
            assert set(row) == set(DEALER_UPCARDS)


def test_hard_total_decisions_use_table_and_fallback_double_to_hit() -> None:
    strategy = BasicStrategy(BasicStrategyProfile.S17)

    assert (
        strategy.choose_action(hand_with(Rank.TEN, Rank.SIX), upcard(Rank.TEN))
        is Action.HIT
    )
    assert (
        strategy.choose_action(hand_with(Rank.TEN, Rank.TWO), upcard(Rank.FOUR))
        is Action.STAND
    )
    assert (
        strategy.choose_action(hand_with(Rank.FIVE, Rank.FOUR), upcard(Rank.THREE))
        is Action.HIT
    )


def test_soft_total_decisions_use_table_and_fallback_double_to_stand() -> None:
    strategy = BasicStrategy(BasicStrategyProfile.S17)

    assert (
        strategy.choose_action(hand_with(Rank.ACE, Rank.SEVEN), upcard(Rank.NINE))
        is Action.HIT
    )
    assert (
        strategy.choose_action(hand_with(Rank.ACE, Rank.SEVEN), upcard(Rank.SIX))
        is Action.STAND
    )
    assert (
        strategy.choose_action(hand_with(Rank.ACE, Rank.EIGHT), upcard(Rank.SIX))
        is Action.STAND
    )


def test_pair_decisions_fallback_when_split_is_not_legal() -> None:
    strategy = BasicStrategy(BasicStrategyProfile.S17)

    assert (
        strategy.choose_action(hand_with(Rank.ACE, Rank.ACE), upcard(Rank.SIX))
        is Action.HIT
    )
    assert (
        strategy.choose_action(hand_with(Rank.EIGHT, Rank.EIGHT), upcard(Rank.TEN))
        is Action.HIT
    )
    assert (
        strategy.choose_action(hand_with(Rank.TEN, Rank.TEN), upcard(Rank.SIX))
        is Action.STAND
    )


def test_pair_decision_returns_split_when_split_is_legal() -> None:
    strategy = BasicStrategy(
        BasicStrategyProfile.S17,
        legal_actions={Action.HIT, Action.STAND, Action.SPLIT},
    )

    assert (
        strategy.choose_action(hand_with(Rank.EIGHT, Rank.EIGHT), upcard(Rank.TEN))
        is Action.SPLIT
    )


def test_double_decision_returns_double_when_double_is_legal() -> None:
    strategy = BasicStrategy(
        BasicStrategyProfile.S17,
        legal_actions={Action.HIT, Action.STAND, Action.DOUBLE},
    )

    assert (
        strategy.choose_action(hand_with(Rank.FIVE, Rank.FOUR), upcard(Rank.THREE))
        is Action.DOUBLE
    )


def test_s17_and_h17_profiles_can_differ() -> None:
    s17 = BasicStrategy(BasicStrategyProfile.S17)
    h17 = BasicStrategy(BasicStrategyProfile.H17)
    hand = hand_with(Rank.SIX, Rank.FIVE)
    dealer_ace = upcard(Rank.ACE)

    assert s17.preferred_decision(hand, dealer_ace) is StrategyDecision.HIT
    assert h17.preferred_decision(hand, dealer_ace) is StrategyDecision.DOUBLE_HIT
    assert h17.choose_action(hand, dealer_ace) is Action.HIT


def test_factory_selects_profile_from_dealer_rules() -> None:
    s17 = basic_strategy_for_rules(DealerRules(hits_soft_17=False))
    h17 = basic_strategy_for_rules(DealerRules(hits_soft_17=True))

    assert s17.profile is BasicStrategyProfile.S17
    assert h17.profile is BasicStrategyProfile.H17
