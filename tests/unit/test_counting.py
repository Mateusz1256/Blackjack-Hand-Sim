from decimal import Decimal

from blackjack_simulator.actions import Action
from blackjack_simulator.betting.count_spread import TrueCountSpreadBettingStrategy
from blackjack_simulator.cards import Card, Rank
from blackjack_simulator.counting.hi_lo import HiLoCounter
from blackjack_simulator.counting.system import (
    ConfigurableCardCounter,
    TrueCountRounding,
    get_counting_system,
)
from blackjack_simulator.round import FixedActionStrategy, play_round
from blackjack_simulator.rules import DealerRules, InsuranceRules
from blackjack_simulator.strategies.insurance import CountBasedInsuranceStrategy


class StubShoe:
    def __init__(self, *ranks: Rank, needs_shuffle: bool = False) -> None:
        self._cards = [Card(rank) for rank in ranks]
        self._needs_shuffle = needs_shuffle
        self.reset_count = 0

    def draw(self) -> Card:
        return self._cards.pop(0)

    @property
    def needs_shuffle(self) -> bool:
        return self._needs_shuffle

    def reset(self) -> None:
        self.reset_count += 1


def test_hi_lo_count_values_by_rank() -> None:
    counter = HiLoCounter()

    counter.observe(Card(Rank.TWO))
    counter.observe(Card(Rank.SIX))
    counter.observe(Card(Rank.SEVEN))
    counter.observe(Card(Rank.TEN))
    counter.observe(Card(Rank.ACE))

    assert counter.running_count == 0


def test_supported_counting_system_rank_values() -> None:
    expectations = {
        "hi_lo": {Rank.TWO: 1, Rank.SEVEN: 0, Rank.TEN: -1, Rank.ACE: -1},
        "ko": {Rank.TWO: 1, Rank.SEVEN: 1, Rank.TEN: -1, Rank.ACE: -1},
        "hi_opt_i": {Rank.TWO: 0, Rank.FIVE: 1, Rank.TEN: -1, Rank.ACE: 0},
        "hi_opt_ii": {Rank.FOUR: 2, Rank.SEVEN: 1, Rank.TEN: -2, Rank.ACE: 0},
        "omega_ii": {Rank.FIVE: 2, Rank.NINE: -1, Rank.TEN: -2, Rank.ACE: 0},
    }

    for system_name, values in expectations.items():
        system = get_counting_system(system_name)
        for rank, expected_value in values.items():
            assert system.value_for(rank) == expected_value


def test_true_count_uses_remaining_decks() -> None:
    counter = HiLoCounter()
    for _ in range(6):
        counter.observe(Card(Rank.FIVE))

    assert counter.true_count(remaining_cards=156) == Decimal("2")


def test_true_count_rounding_modes() -> None:
    counter = ConfigurableCardCounter(
        system=get_counting_system("hi_lo"),
        true_count_rounding=TrueCountRounding.NONE,
    )
    for _ in range(5):
        counter.observe(Card(Rank.FIVE))

    assert counter.true_count(remaining_cards=156) == Decimal(
        "1.666666666666666666666666667",
    )

    counter.true_count_rounding = TrueCountRounding.FLOOR
    assert counter.true_count(remaining_cards=156) == Decimal("1")

    counter.true_count_rounding = TrueCountRounding.TRUNCATE
    assert counter.true_count(remaining_cards=156) == Decimal("1")

    counter.true_count_rounding = TrueCountRounding.NEAREST
    assert counter.true_count(remaining_cards=156) == Decimal("2")


def test_minimum_remaining_decks_denominator() -> None:
    counter = ConfigurableCardCounter(
        system=get_counting_system("hi_lo"),
        min_remaining_decks=Decimal("1"),
    )
    for _ in range(4):
        counter.observe(Card(Rank.FIVE))

    assert counter.true_count(remaining_cards=26) == Decimal("4")


def test_initial_running_count_applies_to_reset() -> None:
    counter = ConfigurableCardCounter(
        system=get_counting_system("ko"),
        initial_running_count=-20,
    )
    counter.observe(Card(Rank.FIVE))

    assert counter.running_count == -19

    counter.reset()

    assert counter.running_count == -20
    assert counter.cards_seen == 0


def test_count_resets_explicitly() -> None:
    counter = HiLoCounter()
    counter.observe(Card(Rank.FIVE))

    counter.reset()

    assert counter.running_count == 0
    assert counter.cards_seen == 0


def test_american_hole_card_counts_only_when_revealed_by_dealer_play() -> None:
    shoe = StubShoe(Rank.TEN, Rank.SIX, Rank.SEVEN, Rank.FIVE, Rank.TEN)
    counter = HiLoCounter()

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
        card_counter=counter,
    )

    assert result.dealer_hand.cards == [Card(Rank.SIX), Card(Rank.FIVE), Card(Rank.TEN)]
    assert counter.running_count == 0
    assert counter.cards_seen == 5


def test_american_hole_card_not_counted_when_player_busts_before_reveal() -> None:
    shoe = StubShoe(Rank.TEN, Rank.SIX, Rank.NINE, Rank.FIVE, Rank.KING)
    counter = HiLoCounter()

    result = play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=False),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
        card_counter=counter,
    )

    assert result.player_hand.is_bust
    assert counter.cards_seen == 4
    assert counter.running_count == -1


def test_hole_card_counts_when_peek_reveals_dealer_blackjack() -> None:
    shoe = StubShoe(Rank.NINE, Rank.TEN, Rank.SEVEN, Rank.ACE)
    counter = HiLoCounter()

    play_round(
        shoe=shoe,
        dealer_rules=DealerRules(peeks_for_blackjack=True),
        player_strategy=FixedActionStrategy(Action.HIT),
        bet=Decimal("10"),
        card_counter=counter,
    )

    assert counter.cards_seen == 4
    assert counter.running_count == -2


def test_counter_resets_after_shuffle() -> None:
    shoe = StubShoe(
        Rank.TEN,
        Rank.NINE,
        Rank.EIGHT,
        Rank.SEVEN,
        Rank.KING,
        needs_shuffle=True,
    )
    counter = HiLoCounter()

    play_round(
        shoe=shoe,
        dealer_rules=DealerRules(),
        player_strategy=FixedActionStrategy(Action.STAND),
        bet=Decimal("10"),
        card_counter=counter,
    )

    assert shoe.reset_count == 1
    assert counter.running_count == 0


def test_count_based_insurance_uses_true_count_threshold() -> None:
    counter = HiLoCounter()
    for _ in range(9):
        counter.observe(Card(Rank.FIVE))
    strategy = CountBasedInsuranceStrategy(counter=counter, threshold=Decimal("3"))

    assert strategy.insurance_bet(
        player=type("Player", (), {"current_bet": Decimal("10")})(),
        rules=InsuranceRules(offered=True),
        remaining_cards=156,
    ) == Decimal("5.0")


def test_true_count_spread_chooses_bet_from_thresholds() -> None:
    counter = HiLoCounter()
    for _ in range(6):
        counter.observe(Card(Rank.FIVE))
    strategy = TrueCountSpreadBettingStrategy(
        counter=counter,
        base_amount=Decimal("10"),
        spread={Decimal("1"): Decimal("2"), Decimal("3"): Decimal("4")},
        remaining_cards_provider=lambda: 104,
    )

    assert strategy.next_bet(Decimal("100")) == Decimal("40")
