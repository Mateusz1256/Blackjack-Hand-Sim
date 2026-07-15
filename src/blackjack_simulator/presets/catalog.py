"""Built-in preset catalog.

The names describe generic rule shapes, not verified rules from a specific
venue.
"""

from typing import Any

from blackjack_simulator.presets.model import Preset, PresetMetadata


def builtin_presets() -> tuple[Preset, ...]:
    return (
        _preset(
            preset_id="standard-6d-s17",
            name="Standard 6 Deck S17",
            description="Generic six-deck S17 table with 3:2 blackjack payout.",
            category="standard",
            tags=("6-deck", "s17", "3-to-2", "das", "late-surrender"),
            config=_config(decks=6, hits_soft_17=False, surrender="late"),
        ),
        _preset(
            preset_id="standard-6d-h17",
            name="Standard 6 Deck H17",
            description="Generic six-deck H17 table with 3:2 blackjack payout.",
            category="standard",
            tags=("6-deck", "h17", "3-to-2", "das"),
            config=_config(decks=6, hits_soft_17=True, surrender="none"),
        ),
        _preset(
            preset_id="eight-deck-h17",
            name="8 Deck H17",
            description="Generic eight-deck H17 table for shoe-game analysis.",
            category="standard",
            tags=("8-deck", "h17", "3-to-2", "das"),
            config=_config(decks=8, hits_soft_17=True, surrender="none"),
        ),
        _preset(
            preset_id="six-deck-six-to-five",
            name="6 Deck 6:5",
            description="Six-deck H17 variant with 6:5 blackjack payout.",
            category="variant",
            tags=("6-deck", "h17", "6-to-5"),
            config=_config(
                decks=6,
                hits_soft_17=True,
                blackjack_payout="1.2",
                surrender="none",
            ),
        ),
        _preset(
            preset_id="single-deck-three-to-two",
            name="Single Deck 3:2",
            description="Single-deck S17 table with 3:2 blackjack payout.",
            category="single-deck",
            tags=("single-deck", "s17", "3-to-2"),
            config=_config(
                decks=1,
                hits_soft_17=False,
                penetration=0.65,
                double_after_split=False,
            ),
        ),
        _preset(
            preset_id="single-deck-six-to-five",
            name="Single Deck 6:5",
            description="Single-deck H17 table with 6:5 blackjack payout.",
            category="single-deck",
            tags=("single-deck", "h17", "6-to-5"),
            config=_config(
                decks=1,
                hits_soft_17=True,
                blackjack_payout="1.2",
                penetration=0.65,
                surrender="none",
                double_after_split=False,
            ),
        ),
        _preset(
            preset_id="european-no-hole-card",
            name="European No Hole Card",
            description="Generic ENHC table without dealer peek.",
            category="regional",
            tags=("6-deck", "s17", "enhc", "no-peek"),
            config=_config(
                decks=6,
                hits_soft_17=False,
                peeks_for_blackjack=False,
                insurance_offered=False,
                surrender="none",
                hole_card_mode="european_no_hole_card",
                enhc_loss_rule="original_bet_only",
            ),
        ),
        _preset(
            preset_id="atlantic-city-style",
            name="Atlantic City Style",
            description=(
                "Generic rules inspired by common multi-deck public examples; "
                "not a claim about a specific table."
            ),
            category="regional",
            tags=("8-deck", "s17", "3-to-2", "das", "late-surrender"),
            config=_config(decks=8, hits_soft_17=False, surrender="late"),
        ),
        _preset(
            preset_id="player-friendly-table",
            name="Player-Friendly Table",
            description="Analysis preset combining favorable supported options.",
            category="analysis",
            tags=("6-deck", "s17", "3-to-2", "das", "late-surrender"),
            config=_config(
                decks=6,
                hits_soft_17=False,
                penetration=0.8,
                surrender="late",
                allowed_totals=None,
                resplit_aces=True,
                hit_split_aces=True,
            ),
        ),
        _preset(
            preset_id="casino-friendly-table",
            name="Casino-Friendly Table",
            description="Analysis preset combining less favorable supported options.",
            category="analysis",
            tags=("8-deck", "h17", "6-to-5", "no-surrender"),
            config=_config(
                decks=8,
                hits_soft_17=True,
                blackjack_payout="1.2",
                penetration=0.65,
                surrender="none",
                double_allowed=False,
                split_max_hands=2,
            ),
        ),
    )


def _preset(
    *,
    preset_id: str,
    name: str,
    description: str,
    category: str,
    tags: tuple[str, ...],
    config: dict[str, Any],
) -> Preset:
    return Preset(
        metadata=PresetMetadata(
            id=preset_id,
            name=name,
            description=description,
            category=category,
            tags=tags,
            source="built-in",
            version=1,
            read_only=True,
        ),
        configuration=config,
    )


def _config(
    *,
    decks: int,
    hits_soft_17: bool,
    blackjack_payout: str = "1.5",
    penetration: float = 0.75,
    peeks_for_blackjack: bool = True,
    surrender: str = "late",
    double_allowed: bool = True,
    double_after_split: bool = True,
    allowed_totals: list[int] | None = None,
    split_max_hands: int = 4,
    resplit_aces: bool = False,
    hit_split_aces: bool = False,
    insurance_offered: bool = True,
    hole_card_mode: str = "american",
    enhc_loss_rule: str = "all_bets",
) -> dict[str, Any]:
    return {
        "simulation": {
            "rounds": 1000,
            "seed": 123456,
            "workers": 1,
        },
        "bankroll": {
            "initial": 10000,
        },
        "rules": {
            "decks": decks,
            "penetration": penetration,
            "shuffle_after_each_round": False,
            "blackjack_payout": blackjack_payout,
            "dealer": {
                "hits_soft_17": hits_soft_17,
                "peeks_for_blackjack": peeks_for_blackjack,
            },
            "double": {
                "allowed": double_allowed,
                "after_split": double_after_split,
                "allowed_totals": allowed_totals or [9, 10, 11],
            },
            "surrender": {
                "type": surrender,
            },
            "split": {
                "allowed": True,
                "max_hands": split_max_hands,
                "require_same_rank": True,
                "resplit_aces": resplit_aces,
                "hit_split_aces": hit_split_aces,
                "double_after_split_aces": False,
                "blackjack_after_split_counts_as_blackjack": False,
            },
            "insurance": {
                "offered": insurance_offered,
                "payout": 2,
                "max_bet_fraction": 0.5,
            },
            "hole_card": {
                "mode": hole_card_mode,
                "enhc_loss_rule": enhc_loss_rule,
            },
        },
        "player": {
            "playing_strategy": {
                "type": "basic_strategy",
            },
            "insurance_strategy": {
                "type": "never",
            },
            "betting_strategy": {
                "type": "flat",
                "amount": 10,
            },
        },
        "output": {
            "console": True,
            "json_file": None,
            "csv_file": None,
        },
    }
