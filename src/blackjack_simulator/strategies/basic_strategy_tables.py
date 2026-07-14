"""Table data for basic strategy profiles."""

from dataclasses import dataclass
from enum import StrEnum

from blackjack_simulator.cards import Rank

DEALER_UPCARDS: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
HARD_TOTALS: tuple[int, ...] = tuple(range(4, 22))
SOFT_TOTALS: tuple[int, ...] = tuple(range(13, 22))
PAIR_RANKS: tuple[Rank, ...] = tuple(Rank)


class StrategyDecision(StrEnum):
    HIT = "H"
    STAND = "S"
    DOUBLE_HIT = "Dh"
    DOUBLE_STAND = "Ds"
    SPLIT = "P"
    SURRENDER_HIT = "Rh"
    SURRENDER_STAND = "Rs"


StrategyRow = dict[int, StrategyDecision]


@dataclass(frozen=True, slots=True)
class BasicStrategyTables:
    hard: dict[int, StrategyRow]
    soft: dict[int, StrategyRow]
    pairs: dict[Rank, StrategyRow]


def get_tables(profile: object) -> BasicStrategyTables:
    profile_name = getattr(profile, "value", str(profile))
    tables = _build_s17_tables()
    if profile_name == "h17":
        tables.hard[11][11] = StrategyDecision.DOUBLE_HIT

    _validate_tables(tables)
    return tables


def _row(default: StrategyDecision, **overrides: StrategyDecision) -> StrategyRow:
    row = {upcard: default for upcard in DEALER_UPCARDS}
    for key, value in overrides.items():
        row[_parse_upcard_key(key)] = value

    return row


def _parse_upcard_key(key: str) -> int:
    if key == "ace":
        return 11

    return int(key.removeprefix("up_"))


def _build_s17_tables() -> BasicStrategyTables:
    hit = StrategyDecision.HIT
    stand = StrategyDecision.STAND
    double_hit = StrategyDecision.DOUBLE_HIT
    double_stand = StrategyDecision.DOUBLE_STAND
    split = StrategyDecision.SPLIT

    hard = {total: _row(hit) for total in HARD_TOTALS}
    for total in range(17, 22):
        hard[total] = _row(stand)
    for total in range(13, 17):
        hard[total] = _row(
            hit,
            up_2=stand,
            up_3=stand,
            up_4=stand,
            up_5=stand,
            up_6=stand,
        )
    hard[12] = _row(hit, up_4=stand, up_5=stand, up_6=stand)
    hard[9] = _row(
        hit,
        up_3=double_hit,
        up_4=double_hit,
        up_5=double_hit,
        up_6=double_hit,
    )
    hard[10] = _row(
        hit,
        up_2=double_hit,
        up_3=double_hit,
        up_4=double_hit,
        up_5=double_hit,
        up_6=double_hit,
        up_7=double_hit,
        up_8=double_hit,
        up_9=double_hit,
    )
    hard[11] = _row(
        hit,
        up_2=double_hit,
        up_3=double_hit,
        up_4=double_hit,
        up_5=double_hit,
        up_6=double_hit,
        up_7=double_hit,
        up_8=double_hit,
        up_9=double_hit,
        up_10=double_hit,
    )

    soft = {total: _row(hit) for total in SOFT_TOTALS}
    soft[13] = _row(hit, up_5=double_hit, up_6=double_hit)
    soft[14] = _row(hit, up_5=double_hit, up_6=double_hit)
    soft[15] = _row(hit, up_4=double_hit, up_5=double_hit, up_6=double_hit)
    soft[16] = _row(hit, up_4=double_hit, up_5=double_hit, up_6=double_hit)
    soft[17] = _row(
        hit,
        up_3=double_hit,
        up_4=double_hit,
        up_5=double_hit,
        up_6=double_hit,
    )
    soft[18] = _row(
        hit,
        up_2=stand,
        up_3=double_stand,
        up_4=double_stand,
        up_5=double_stand,
        up_6=double_stand,
        up_7=stand,
        up_8=stand,
    )
    soft[19] = _row(stand, up_6=double_stand)
    soft[20] = _row(stand)
    soft[21] = _row(stand)

    pairs = {rank: _row(hit) for rank in PAIR_RANKS}
    pairs[Rank.ACE] = _row(split)
    pairs[Rank.TEN] = _row(stand)
    pairs[Rank.JACK] = _row(stand)
    pairs[Rank.QUEEN] = _row(stand)
    pairs[Rank.KING] = _row(stand)
    pairs[Rank.NINE] = _row(
        stand,
        up_2=split,
        up_3=split,
        up_4=split,
        up_5=split,
        up_6=split,
        up_8=split,
        up_9=split,
    )
    pairs[Rank.EIGHT] = _row(split)
    pairs[Rank.SEVEN] = _row(
        hit,
        up_2=split,
        up_3=split,
        up_4=split,
        up_5=split,
        up_6=split,
        up_7=split,
    )
    pairs[Rank.SIX] = _row(
        hit,
        up_2=split,
        up_3=split,
        up_4=split,
        up_5=split,
        up_6=split,
    )
    pairs[Rank.FIVE] = hard[10].copy()
    pairs[Rank.FOUR] = _row(hit, up_5=split, up_6=split)
    pairs[Rank.THREE] = _row(
        hit,
        up_2=split,
        up_3=split,
        up_4=split,
        up_5=split,
        up_6=split,
        up_7=split,
    )
    pairs[Rank.TWO] = pairs[Rank.THREE].copy()

    return BasicStrategyTables(hard=hard, soft=soft, pairs=pairs)


def _validate_tables(tables: BasicStrategyTables) -> None:
    if set(tables.hard) != set(HARD_TOTALS):
        msg = "hard strategy table is incomplete"
        raise ValueError(msg)
    if set(tables.soft) != set(SOFT_TOTALS):
        msg = "soft strategy table is incomplete"
        raise ValueError(msg)
    if set(tables.pairs) != set(PAIR_RANKS):
        msg = "pair strategy table is incomplete"
        raise ValueError(msg)

    for table_name, table in (
        ("hard", tables.hard),
        ("soft", tables.soft),
        ("pairs", tables.pairs),
    ):
        for key, row in table.items():
            if set(row) != set(DEALER_UPCARDS):
                msg = f"{table_name} strategy row {key!r} is incomplete"
                raise ValueError(msg)
