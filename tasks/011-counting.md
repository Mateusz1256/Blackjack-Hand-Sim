# Task 011: Card Counting

## Goal

Add Hi-Lo counting support.

## Scope

- Running count.
- True count.
- Reset on shuffle.
- Count-based insurance.
- True-count betting spread.

## Out of Scope

- New non-Hi-Lo systems.

## Functional Requirements

- Hole card affects count only when revealed.
- Count resets on shuffle.

## Technical Requirements

- Counting must observe dealt/revealed cards without owning shoe state.

## Tests

- Count values by rank.
- True count calculation.
- Shuffle reset.
- Hole-card reveal timing.

## Acceptance Criteria

- Counting is deterministic and aligned with visible cards.

## Likely Files

- `src/blackjack_simulator/counting/`
- `src/blackjack_simulator/betting/count_spread.py`

## Risks

- Counting hidden cards too early.
