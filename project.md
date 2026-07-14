Instrukcja dla agenta AI: implementacja symulatora rozdań blackjacka
1. Cel projektu
Zaprojektuj i zaimplementuj dokładny, konfigurowalny oraz testowalny symulator rozdań blackjacka.
Symulator ma umożliwiać przeprowadzanie od pojedynczych testowych rozdań do wielomilionowych symulacji statystycznych przy różnych:
•	zasadach stołu,
•	strategiach ubezpieczenia,
•	systemach obstawiania,
•	ustawieniach bankrolla,
•	zasadach tasowania shoe,
•	wariantach basic strategy.
Wszystkie ręce gracza mają być rozgrywane automatycznie według odpowiedniej basic strategy dobranej do aktualnych zasad stołu.
Projekt ma być przygotowany jako narzędzie open source, z naciskiem na:
•	poprawność matematyczną,
•	deterministyczne wyniki dla ustalonego seeda,
•	łatwe dodawanie nowych zasad,
•	łatwe dodawanie systemów obstawiania,
•	testowalność,
•	czytelną architekturę,
•	możliwość późniejszego dodania panelu webowego,
•	możliwość uruchamiania dużej liczby symulacji.
Nie implementuj całego projektu w jednym kroku. Pracuj etapami zgodnie z zadaniami opisanymi w dalszej części dokumentu.
________________________________________
2. Wymagany stack technologiczny
2.1. Język
Użyj:
•	Python 3.12 lub nowszy.
2.2. Zarządzanie projektem
Użyj:
•	pyproject.toml,
•	pytest,
•	ruff,
•	mypy,
•	standardowego modułu logging,
•	dataclasses,
•	enum,
•	typing,
•	random.Random lub kompatybilnego generatora przekazywanego przez dependency injection.
Opcjonalnie można zastosować:
•	pydantic do walidacji konfiguracji,
•	PyYAML do odczytu konfiguracji YAML,
•	rich do raportów terminalowych,
•	typer do CLI.
Nie dodawaj frameworka webowego w pierwszej wersji MVP.
Panel webowy będzie osobnym etapem po ukończeniu i przetestowaniu silnika.
2.3. Zależności
Ogranicz liczbę zależności zewnętrznych.
Każda zależność powinna mieć uzasadnienie.
Nie używaj ciężkich bibliotek do prostych rzeczy, które można poprawnie wykonać w standardowej bibliotece Pythona.
________________________________________
3. Główne zasady architektury
Projekt musi być podzielony na niezależne warstwy.
W szczególności należy oddzielić:
1.	model kart i talii,
2.	zasady stołu,
3.	model ręki,
4.	silnik pojedynczej rundy,
5.	strategię rozgrywania ręki,
6.	strategię insurance,
7.	strategię obstawiania,
8.	rozliczanie wyników,
9.	zbieranie statystyk,
10.	konfigurację,
11.	CLI,
12.	eksport wyników.
Silnik blackjacka nie może zależeć od:
•	CLI,
•	panelu webowego,
•	konkretnego formatu konfiguracji,
•	sposobu prezentowania raportu.
Warstwa domenowa ma działać niezależnie.
Niedopuszczalne jest umieszczenie całej logiki w jednym pliku lub jednej klasie.
________________________________________
4. Proponowana struktura projektu
Utwórz strukturę zbliżoną do poniższej:
blackjack-simulator/
├── src/
│   └── blackjack_simulator/
│       ├── __init__.py
│       ├── cards.py
│       ├── shoe.py
│       ├── hand.py
│       ├── rules.py
│       ├── actions.py
│       ├── round.py
│       ├── engine.py
│       ├── settlement.py
│       ├── configuration.py
│       ├── exceptions.py
│       │
│       ├── strategies/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── basic_strategy.py
│       │   ├── basic_strategy_tables.py
│       │   ├── insurance.py
│       │   └── fallback.py
│       │
│       ├── betting/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── flat.py
│       │   ├── martingale.py
│       │   ├── paroli.py
│       │   ├── fibonacci.py
│       │   ├── dalembert.py
│       │   └── count_spread.py
│       │
│       ├── counting/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── hi_lo.py
│       │
│       ├── statistics/
│       │   ├── __init__.py
│       │   ├── collector.py
│       │   ├── metrics.py
│       │   ├── confidence.py
│       │   └── report.py
│       │
│       ├── output/
│       │   ├── __init__.py
│       │   ├── console.py
│       │   ├── json_output.py
│       │   └── csv_output.py
│       │
│       └── cli/
│           ├── __init__.py
│           └── main.py
│
├── configs/
│   ├── standard_6_deck_s17.yaml
│   ├── standard_6_deck_h17.yaml
│   ├── blackjack_6_to_5.yaml
│   └── european_no_hole_card.yaml
│
├── tests/
│   ├── unit/
│   │   ├── test_cards.py
│   │   ├── test_hand.py
│   │   ├── test_shoe.py
│   │   ├── test_dealer.py
│   │   ├── test_settlement.py
│   │   ├── test_splits.py
│   │   ├── test_insurance.py
│   │   ├── test_surrender.py
│   │   ├── test_basic_strategy.py
│   │   ├── test_betting.py
│   │   └── test_statistics.py
│   │
│   ├── integration/
│   │   ├── test_round_flow.py
│   │   ├── test_simulation.py
│   │   └── test_cli.py
│   │
│   └── fixtures/
│
├── tasks/
│   ├── 001-project-foundation.md
│   ├── 002-cards-and-hand.md
│   ├── 003-shoe-and-dealer.md
│   ├── 004-settlement.md
│   ├── 005-basic-strategy.md
│   ├── 006-double-and-surrender.md
│   ├── 007-splits.md
│   ├── 008-insurance.md
│   ├── 009-betting-systems.md
│   ├── 010-statistics.md
│   ├── 011-cli-and-config.md
│   ├── 012-performance.md
│   └── 013-final-validation.md
│
├── docs/
│   ├── architecture.md
│   ├── rules.md
│   ├── statistics.md
│   ├── basic-strategy.md
│   └── contributing.md
│
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml
└── .gitignore
Struktura może zostać nieznacznie zmieniona, jeśli istnieje dobre uzasadnienie architektoniczne. Nie należy jednak łączyć niezależnych odpowiedzialności w jeden wielki moduł.
________________________________________
5. Model kart
5.1. Rangi kart
Obsługuj następujące rangi:
2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A
W podstawowym silniku kolor karty nie wpływa na grę.
Można reprezentować kartę przez rangę, bez przechowywania koloru, ponieważ w blackjacku wszystkie cztery kolory mają taką samą wartość.
Rekomendowana reprezentacja:
from dataclasses import dataclass
from enum import Enum


class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


@dataclass(frozen=True, slots=True)
class Card:
    rank: Rank
Nie zapisuj na stałe wartości asa jako 1 lub 11. Wartość asa zależy od całej ręki.
5.2. Wartości kart
•	karty 2–9 mają wartość zgodną z rangą,
•	10, J, Q, K mają wartość 10,
•	as może mieć wartość 1 albo 11.
________________________________________
6. Model shoe
6.1. Liczba talii
Obsługuj co najmniej:
•	1 talię,
•	2 talie,
•	4 talie,
•	6 talii,
•	8 talii.
Nie zakładaj jednak, że lista jest zamknięta. Konfiguracja powinna pozwalać ustawić dowolną dodatnią liczbę talii w rozsądnym zakresie.
6.2. Zawartość shoe
Dla każdej talii:
•	każda karta 2–9 występuje cztery razy,
•	każda ranga 10, J, Q, K występuje cztery razy,
•	as występuje cztery razy.
W jednej talii istnieje zatem:
•	52 kart,
•	16 kart o wartości 10,
•	4 asy.
6.3. Losowanie
Shoe musi korzystać z przekazanego generatora losowego.
Przykład:
rng = random.Random(seed)
shoe = Shoe(decks=6, penetration=0.75, rng=rng)
Nie używaj bezpośrednio globalnego random.shuffle() wewnątrz logiki domenowej.
Dzięki temu symulacja będzie deterministyczna dla tego samego:
•	seeda,
•	zestawu zasad,
•	systemu obstawiania,
•	liczby rund.
6.4. Penetracja
Obsługuj penetrację shoe, np.:
penetration: 0.75
Wartość 0.75 oznacza, że po wykorzystaniu około 75% kart należy przygotować nowe shoe.
Należy jasno zdefiniować sposób działania cut card.
Preferowane zachowanie:
1.	podczas tasowania wyznacz liczbę kart, które mogą zostać rozdane przed osiągnięciem cut card,
2.	nie przerywaj trwającej rundy,
3.	po zakończeniu rundy sprawdź, czy przekroczono próg,
4.	jeżeli tak, przetasuj shoe przed kolejną rundą.
6.5. Tasowanie po każdej rundzie
Obsługuj opcję:
shuffle_after_each_round: false
Jeżeli ustawiono true, po każdej rundzie generowane jest nowe shoe.
________________________________________
7. Model ręki
Klasa Hand powinna przechowywać co najmniej:
@dataclass
class Hand:
    cards: list[Card]
    original_bet: Decimal
    current_bet: Decimal
    is_split_hand: bool
    split_depth: int
    originated_from_split_aces: bool
    doubled: bool
    surrendered: bool
    stood: bool
    completed: bool
Można zmodyfikować model, ale musi on pozwalać odtworzyć historię i sposób powstania ręki.
7.1. Obliczanie wartości
Algorytm:
1.	zsumuj wszystkie karty, traktując asy początkowo jako 11,
2.	policz liczbę asów,
3.	dopóki suma jest większa od 21 i istnieje as liczony jako 11:
o	odejmij 10,
o	zmniejsz liczbę asów liczonych jako 11,
4.	zwróć ostateczną wartość.
7.2. Soft hand
Ręka jest soft, jeśli po obliczeniu wartości co najmniej jeden as nadal jest liczony jako 11.
Przykłady:
•	A + 6 to soft 17,
•	A + 6 + 10 to hard 17,
•	A + A + 5 to soft 17,
•	A + A + 9 to 21, przy czym jeden as jest liczony jako 11.
7.3. Blackjack
Naturalny blackjack oznacza:
•	dokładnie dwie karty,
•	jedna karta to as,
•	druga karta ma wartość 10,
•	ręka nie powstała w wyniku splitu, chyba że ustawienia stołu jawnie dopuszczają blackjack po splicie.
Domyślnie A + 10 po splicie nie jest blackjackiem. Jest zwykłym 21.
7.4. Bust
Ręka jest bust, jeśli jej wartość przekracza 21.
7.5. Para do splitu
Należy obsługiwać konfigurowalny sposób określania pary:
split_rules:
  require_same_rank: true
Przy true:
•	10 + J nie jest parą,
•	K + Q nie jest parą,
•	10 + 10 jest parą.
Można później obsłużyć tryb, w którym wszystkie karty dziesięciopunktowe są traktowane jako para, ale nie powinien to być domyślny standard.
________________________________________
8. Konfiguracja zasad stołu
Utwórz silnie typowany model konfiguracji.
Przykładowa konfiguracja:
simulation:
  rounds: 1000000
  seed: 123456
  workers: 1

bankroll:
  initial: 10000
  stop_on_ruin: true
  allow_credit: false
  table_minimum: 10
  table_maximum: 1000

rules:
  decks: 6
  blackjack_payout: 1.5

  dealer:
    hits_soft_17: false
    peeks_for_blackjack: true

  european_no_hole_card: false

  double:
    allowed: true
    after_split: true
    allowed_on:
      type: any_two_cards

  surrender:
    type: late

  split:
    allowed: true
    max_hands: 4
    require_same_rank: true
    resplit_aces: false
    hit_split_aces: false
    double_after_split_aces: false
    blackjack_after_split_counts_as_blackjack: false

  insurance:
    offered: true
    payout: 2.0
    max_bet_fraction: 0.5

  penetration: 0.75
  shuffle_after_each_round: false

player:
  playing_strategy:
    type: basic_strategy

  insurance_strategy:
    type: never

  betting_strategy:
    type: flat
    amount: 10

output:
  console: true
  json_file: results/result.json
  csv_file: null
  bankroll_history:
    enabled: true
    sample_every: 100
8.1. Blackjack payout
Obsługuj co najmniej:
•	3:2, czyli mnożnik zysku 1.5,
•	6:5, czyli mnożnik zysku 1.2,
•	1:1, czyli mnożnik zysku 1.0,
•	dowolny dodatni mnożnik z konfiguracji.
Przykład przy stawce 10:
•	blackjack 3:2 daje zysk netto +15,
•	blackjack 6:5 daje zysk netto +12,
•	całkowity zwrot obejmuje również zwrot pierwotnej stawki.
Wewnątrz statystyk i rozliczeń zapisuj przede wszystkim wynik netto, żeby nie pomylić zwrotu z zyskiem.
8.2. Dealer S17 i H17
Obsługuj:
•	S17: dealer stoi na każdym 17, również soft 17,
•	H17: dealer dobiera na soft 17.
Dealer:
•	dobiera przy wartości poniżej 17,
•	stoi przy wartości powyżej 17,
•	przy dokładnie 17 zachowanie zależy od tego, czy ręka jest soft i od konfiguracji H17/S17.
8.3. Hole card i peek
Obsługuj dwa główne modele.
Model amerykański
Dealer otrzymuje:
•	kartę odkrytą,
•	kartę zakrytą.
Jeśli odkrytą kartą jest:
•	as,
•	karta dziesięciopunktowa,
dealer może wykonać peek, zależnie od konfiguracji.
Przy peeku:
•	jeśli dealer ma blackjacka, runda jest kończona przed wykonaniem ruchów gracza,
•	insurance należy rozliczyć,
•	ręce gracza nie wykonują splitów ani double.
European No Hole Card
Przy ENHC dealer początkowo otrzymuje tylko kartę odkrytą.
Drugą kartę otrzymuje dopiero po zakończeniu ruchów gracza.
Jeżeli dealer uzyska blackjacka po tym, gdy gracz wykonał split lub double, należy zastosować odpowiednią zasadę rozliczenia.
Przygotuj konfigurację sposobu utraty dodatkowych zakładów:
european_no_hole_card_loss_rule: all_bets
Obsługiwane warianty:
•	all_bets: gracz traci zakłady bazowe, splity i double,
•	original_bet_only: gracz traci tylko pierwotny zakład, a dodatkowe stawki są zwracane.
8.4. Double
Obsługuj:
•	brak double,
•	double tylko na dwóch pierwszych kartach,
•	double na dowolnych dwóch pierwszych kartach,
•	double tylko na określonych sumach, np. 9–11,
•	double after split,
•	osobne zasady double po splicie asów.
Po double:
1.	zakład ręki zwiększa się o wartość pierwotnego zakładu tej ręki,
2.	gracz otrzymuje dokładnie jedną kartę,
3.	ręka automatycznie kończy turę.
Basic strategy musi posiadać fallback, jeśli preferowana akcja double jest niedozwolona.
8.5. Surrender
Obsługuj:
•	none,
•	late,
•	early.
Late surrender
Gracz może poddać rękę dopiero po sprawdzeniu, że dealer nie ma blackjacka.
Gracz traci połowę zakładu.
Early surrender
Gracz może poddać rękę przed sprawdzeniem blackjacka dealera.
Gracz traci połowę zakładu.
Zaimplementuj surrender jako akcję zależną od:
•	zasad stołu,
•	liczby kart w ręce,
•	tego, czy ręka pochodzi ze splitu,
•	etapu rundy.
8.6. Split
Obsługuj:
•	włączenie lub wyłączenie splitu,
•	maksymalną liczbę rąk po splitach,
•	maksymalną głębokość splitu,
•	resplit,
•	resplit asów,
•	hit split aces,
•	double after split,
•	ograniczenia dla splitowanych asów,
•	blackjack po splicie jako zwykłe 21 lub naturalny blackjack.
Przykład:
split:
  max_hands: 4
Oznacza, że gracz może posiadać łącznie maksymalnie cztery aktywne ręce.
Przy splicie:
1.	pierwotna ręka jest dzielona na dwie,
2.	każda nowa ręka otrzymuje jedną z kart pierwotnej pary,
3.	do każdej ręki dodawana jest nowa karta z shoe,
4.	do drugiej ręki przypisywany jest nowy zakład o tej samej wysokości,
5.	bankroll musi zostać pomniejszony o dodatkowy zakład,
6.	obie ręce są rozgrywane osobno,
7.	statystyki muszą wiedzieć, że pochodzą z jednej rundy.
Nie wolno pomylić liczby rund z liczbą rozliczonych rąk.
8.7. Split asów
Obsługuj osobno:
•	możliwość resplitu asów,
•	możliwość dobierania więcej niż jednej karty po splicie asów,
•	możliwość double po splicie asów.
W typowej konfiguracji:
•	każdy splitowany as otrzymuje tylko jedną dodatkową kartę,
•	ręka automatycznie kończy turę,
•	A + 10 po splicie liczy się jako zwykłe 21.
Jeżeli po dołożeniu karty do splitowanego asa gracz otrzyma kolejnego asa, resplit może być dostępny, jeśli konfiguracja na to pozwala.
8.8. Insurance
Insurance jest osobnym zakładem.
Standardowo:
•	oferowany jest, gdy odkrytą kartą dealera jest as,
•	maksymalna stawka insurance wynosi połowę głównego zakładu,
•	wypłata wynosi 2:1.
Przykład:
•	główny zakład: 10,
•	insurance: 5,
•	dealer ma blackjacka,
•	zysk z insurance: +10 netto,
•	główna ręka jest rozliczana osobno.
Obsługuj konfigurowalne:
insurance:
  offered: true
  payout: 2.0
  max_bet_fraction: 0.5
8.9. Even money
Jeżeli gracz ma blackjacka, a dealer pokazuje asa, można potraktować even money jako szczególny przypadek insurance.
Obsługuj opcjonalnie:
even_money:
  offered: true
Strategia gracza może zdecydować:
•	przyjąć even money,
•	odrzucić even money.
Wynik even money powinien odpowiadać gwarantowanej wypłacie 1:1 dla blackjacka.
Należy jednak zaprojektować implementację tak, aby nie dublować logiki insurance.
________________________________________
9. Akcje gracza
Utwórz enum:
class Action(str, Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"
Dodatkowo strategia może posługiwać się akcjami warunkowymi:
class StrategyDecision(str, Enum):
    HIT = "hit"
    STAND = "stand"
    SPLIT = "split"
    DOUBLE_OR_HIT = "double_or_hit"
    DOUBLE_OR_STAND = "double_or_stand"
    SURRENDER_OR_HIT = "surrender_or_hit"
    SURRENDER_OR_STAND = "surrender_or_stand"
    SPLIT_OR_HIT = "split_or_hit"
Warstwa wykonująca strategię ma przekształcać decyzję warunkową na legalną akcję.
Przykłady:
•	DOUBLE_OR_HIT:
o	double, jeśli jest legalny,
o	w przeciwnym razie hit.
•	DOUBLE_OR_STAND:
o	double, jeśli jest legalny,
o	w przeciwnym razie stand.
•	SURRENDER_OR_HIT:
o	surrender, jeśli jest legalny,
o	w przeciwnym razie hit.
Strategia nie może wykonywać nielegalnej akcji.
________________________________________
10. Basic strategy
10.1. Ogólne założenia
Wszystkie ręce gracza mają być rozgrywane według basic strategy.
Basic strategy nie może być jedną uniwersalną tabelą dla wszystkich stołów.
Wybór decyzji zależy co najmniej od:
•	liczby talii,
•	S17 lub H17,
•	double after split,
•	surrender,
•	zasad splitu,
•	ograniczeń double,
•	hole card lub ENHC.
Zaimplementuj strategię w sposób tabelaryczny i rozszerzalny.
Nie buduj całej strategii jako ogromnego łańcucha przypadkowych instrukcji if/elif.
10.2. Kategorie rąk
Strategia musi rozróżniać:
1.	pary,
2.	soft totals,
3.	hard totals.
Kolejność oceny:
1.	jeżeli można rozważyć split, odczytaj tabelę par,
2.	w przeciwnym razie, jeśli ręka jest soft, odczytaj tabelę soft totals,
3.	w przeciwnym razie odczytaj tabelę hard totals.
10.3. Dealer upcard
Tabela powinna działać dla odkrytej karty dealera:
2, 3, 4, 5, 6, 7, 8, 9, 10, A
J, Q i K należy traktować jako 10 na potrzeby decyzji strategicznej.
10.4. Warianty strategii
W MVP zaimplementuj co najmniej:
•	4–8 decks, S17, DAS, late surrender,
•	4–8 decks, H17, DAS, late surrender,
•	4–8 decks, S17, bez surrender,
•	4–8 decks, H17, bez surrender.
Architektura musi pozwalać później dodać strategie dla:
•	single deck,
•	double deck,
•	ENHC,
•	innych ograniczeń double.
10.5. Dobór tabeli
Utwórz fabrykę:
strategy = BasicStrategyFactory.create(rules)
Fabryka ma:
1.	znaleźć najlepiej dopasowaną tabelę,
2.	zwrócić jasny błąd, jeśli konfiguracja nie jest wspierana,
3.	nie wybierać po cichu niewłaściwej tabeli.
Dopuszczalne jest wprowadzenie jawnego trybu przybliżonego:
playing_strategy:
  allow_nearest_supported_table: false
Domyślnie ma być false.
10.6. Walidacja tabel
Każda tabela basic strategy ma mieć testy pokrywające:
•	każdą kategorię hard total,
•	każdą kategorię soft total,
•	każdą parę,
•	wszystkie odkryte karty dealera,
•	fallback dla double,
•	fallback dla surrender,
•	fallback dla splitu.
Dodaj test sprawdzający kompletność tabeli.
________________________________________
11. Strategie insurance
Insurance nie może być zwykłym polem boolean.
Utwórz interfejs:
class InsuranceStrategy(Protocol):
    def decide(self, context: InsuranceContext) -> bool:
        ...
Kontekst powinien zawierać co najmniej:
@dataclass(frozen=True)
class InsuranceContext:
    player_hand: Hand
    dealer_upcard: Card
    main_bet: Decimal
    bankroll: Decimal
    running_count: int | None
    true_count: float | None
    rules: GameRules
Zaimplementuj strategie:
11.1. Never
insurance_strategy:
  type: never
Gracz nigdy nie kupuje insurance.
11.2. Always
insurance_strategy:
  type: always
Gracz zawsze kupuje maksymalne dostępne insurance, jeśli bankroll na to pozwala.
11.3. Only with blackjack
insurance_strategy:
  type: only_with_blackjack
Gracz kupuje insurance tylko wtedy, gdy posiada naturalnego blackjacka.
Strategię tę można traktować jako wariant decyzji even money.
11.4. Count based
insurance_strategy:
  type: count_based
  minimum_true_count: 3.0
Gracz kupuje insurance, jeśli true count jest większy lub równy określonej wartości.
Jeżeli system liczenia kart jest wyłączony, konfiguracja takiej strategii powinna powodować błąd walidacji.
11.5. Custom
Przygotuj interfejs umożliwiający późniejsze dodanie własnej strategii.
Nie musisz implementować dynamicznego wykonywania kodu użytkownika.
Nie używaj eval, exec ani ładowania niezaufanego kodu.
________________________________________
12. Systemy obstawiania
12.1. Interfejs
Utwórz wspólny interfejs:
class BettingStrategy(Protocol):
    def next_bet(self, context: BettingContext) -> Decimal:
        ...

    def update(self, result: RoundBettingResult) -> None:
        ...

    def reset(self) -> None:
        ...
Kontekst powinien zawierać co najmniej:
@dataclass(frozen=True)
class BettingContext:
    round_number: int
    bankroll: Decimal
    table_minimum: Decimal
    table_maximum: Decimal
    previous_bet: Decimal | None
    previous_round_net_result: Decimal | None
    consecutive_wins: int
    consecutive_losses: int
    running_count: int | None
    true_count: float | None
System obstawiania ustala zakład początkowy rundy.
Dodatkowe zakłady wynikające ze:
•	splitu,
•	double,
•	insurance,
muszą być rozliczane przez silnik rundy, a nie przez strategię początkowego zakładu.
12.2. Flat betting
betting_strategy:
  type: flat
  amount: 10
Każda runda rozpoczyna się od tej samej stawki.
Stawka ma być ograniczona przez:
•	minimum stołu,
•	maksimum stołu,
•	dostępny bankroll.
12.3. Martingale
betting_strategy:
  type: martingale
  base_bet: 10
  multiplier: 2
  max_bet: 640
  reset_after_win: true
  push_behavior: repeat
Zasady:
•	po przegranej kolejny zakład jest mnożony,
•	po wygranej system wraca do zakładu bazowego,
•	push domyślnie nie zmienia poziomu,
•	stawka nie może przekroczyć maksimum stołu ani limitu systemu,
•	system nie może obstawić więcej niż dostępny bankroll.
Należy jasno określić, czy wynik rundy obejmującej kilka rąk po splicie traktuje się jako:
•	wynik netto całej rundy,
•	osobne wyniki każdej ręki.
Domyślnie strategie progresywne powinny aktualizować się na podstawie wyniku netto całej rundy.
12.4. Paroli
betting_strategy:
  type: paroli
  base_bet: 10
  multiplier: 2
  max_steps: 3
  reset_after_loss: true
  push_behavior: repeat
Po wygranej:
•	zwiększ poziom progresji,
•	po osiągnięciu max_steps wróć do stawki bazowej.
Po przegranej wróć do stawki bazowej.
12.5. Fibonacci
betting_strategy:
  type: fibonacci
  base_unit: 10
  max_bet: 1000
  steps_back_after_win: 2
  push_behavior: repeat
Po przegranej przejdź o jeden element ciągu do przodu.
Po wygranej cofnij się o zadaną liczbę pozycji.
12.6. D’Alembert
betting_strategy:
  type: dalembert
  base_bet: 10
  step: 10
  max_bet: 1000
Po przegranej zwiększ stawkę o jeden krok.
Po wygranej zmniejsz stawkę o jeden krok, ale nie poniżej stawki bazowej.
12.7. Stawka zależna od true count
betting_strategy:
  type: true_count_spread
  base_bet: 10
  spread:
    "-2": 10
    "-1": 10
    "0": 10
    "1": 20
    "2": 40
    "3": 80
    "4": 120
Zdefiniuj sposób wyboru progu:
•	dla true count wybierz największy próg mniejszy lub równy bieżącemu true count.
Przykład:
•	TC = 2.7 wybiera próg 2,
•	TC = -1.2 wybiera próg -2, zależnie od sposobu zaokrąglania.
Sposób konwersji true count musi być jawnie skonfigurowany:
true_count_rounding: floor
Obsługuj:
•	floor,
•	truncate,
•	nearest.
12.8. Ograniczenia bankrolla
Każda strategia musi respektować:
•	minimum stołu,
•	maksimum stołu,
•	dostępny bankroll,
•	zakaz kredytu.
Jeśli bankroll jest niższy niż minimum stołu:
•	przy stop_on_ruin: true symulacja kończy się,
•	powód zakończenia ma zostać zapisany w raporcie.
Nie zaokrąglaj po cichu stawek w sposób zmieniający wynik.
Do wartości pieniężnych używaj Decimal, nie float.
________________________________________
13. Liczenie kart
Liczenie kart nie jest obowiązkowe dla pierwszego minimalnego etapu, ale architektura ma je obsługiwać.
Zaimplementuj system Hi-Lo.
13.1. Wartości Hi-Lo
•	2–6: +1,
•	7–9: 0,
•	10, J, Q, K, A: -1.
13.2. Running count
Running count należy aktualizować dla każdej odkrytej karty opuszczającej shoe.
Należy poprawnie określić moment ujawnienia hole card dealera.
Karta zakryta nie powinna wpływać na informacje gracza przed jej odkryciem.
13.3. True count
true_count = running_count / remaining_decks
Liczbę pozostałych talii oblicz jako:
remaining_cards / 52
Należy zabezpieczyć się przed dzieleniem przez bardzo małą wartość.
13.4. Reset
Po przetasowaniu shoe:
•	running count wraca do 0,
•	true count jest obliczany od nowa.
________________________________________
14. Przebieg rundy
Silnik pojedynczej rundy ma wykonać dokładnie określoną sekwencję.
14.1. Przygotowanie zakładu
1.	pobierz zakład ze strategii obstawiania,
2.	zwaliduj minimum i maksimum stołu,
3.	sprawdź bankroll,
4.	zarezerwuj lub pobierz zakład z bankrolla,
5.	zapisz pierwotny zakład rundy.
Przyjmij spójny model księgowania.
Preferowany model:
•	przy postawieniu zakładu bankroll jest pomniejszany,
•	podczas rozliczenia do bankrolla wraca zwrot zakładu oraz ewentualna wygrana.
Alternatywnie można księgować tylko wynik netto, ale należy wybrać jeden model i konsekwentnie stosować go w całym projekcie.
W statystykach zawsze przechowuj wynik netto.
14.2. Początkowe rozdanie
W modelu amerykańskim:
1.	karta gracza,
2.	karta odkryta dealera,
3.	druga karta gracza,
4.	karta zakryta dealera.
W ENHC:
1.	karta gracza,
2.	karta odkryta dealera,
3.	druga karta gracza.
Kolejność rozdawania ma być udokumentowana i przetestowana, ponieważ wpływa na deterministyczność symulacji.
14.3. Insurance
Jeśli dealer pokazuje asa i insurance jest oferowane:
1.	przekaż decyzję do strategii insurance,
2.	oblicz dozwoloną stawkę,
3.	sprawdź bankroll,
4.	pobierz stawkę insurance,
5.	zapisz osobny zakład.
14.4. Peek
Jeśli dealer wykonuje peek:
•	sprawdź blackjacka,
•	przy blackjacku dealera nie rozgrywaj dalej rąk gracza,
•	rozlicz insurance,
•	rozlicz blackjack gracza jako push, jeśli obie strony mają blackjacka,
•	w przeciwnym razie gracz przegrywa główny zakład.
14.5. Blackjack gracza
Jeżeli gracz ma blackjacka, a dealer nie ma blackjacka:
•	ręka nie wykonuje kolejnych akcji,
•	zostaje rozliczona zgodnie z blackjack_payout.
W ENHC należy poczekać na sprawdzenie ostatecznej ręki dealera.
14.6. Ruchy gracza
Dla każdej aktywnej ręki:
1.	sprawdź, czy ręka jest już zakończona,
2.	pobierz decyzję basic strategy,
3.	zamień decyzję warunkową na legalną akcję,
4.	wykonaj akcję,
5.	kontynuuj do zakończenia ręki.
Obsługa akcji:
Hit
•	dobierz jedną kartę,
•	jeśli bust, zakończ rękę,
•	w przeciwnym razie ponownie zapytaj strategię.
Stand
•	zakończ rękę.
Double
•	sprawdź legalność,
•	pobierz dodatkowy zakład,
•	dobierz jedną kartę,
•	zakończ rękę.
Split
•	sprawdź legalność,
•	utwórz dwie ręce,
•	pobierz dodatkowy zakład,
•	dodaj po jednej karcie do obu nowych rąk,
•	umieść ręce w odpowiedniej kolejności do dalszego rozegrania.
Surrender
•	oznacz rękę jako poddaną,
•	zakończ rękę,
•	podczas rozliczenia zwróć połowę zakładu albo zapisz stratę połowy zakładu zgodnie z wybranym modelem księgowania.
14.7. Ruch dealera
Dealer rozgrywa rękę tylko wtedy, gdy istnieje co najmniej jedna aktywna ręka gracza, która:
•	nie jest bust,
•	nie została poddana,
•	wymaga porównania z dealerem.
Dealer:
•	dobiera poniżej 17,
•	stosuje S17 lub H17,
•	kończy przy bust lub stand.
14.8. Rozliczenie
Każda ręka gracza ma być rozliczona osobno.
Kolejność priorytetów:
1.	surrender,
2.	bust gracza,
3.	naturalny blackjack gracza,
4.	blackjack dealera,
5.	bust dealera,
6.	porównanie wartości,
7.	push.
Insurance rozliczaj osobno od głównej ręki.
14.9. Aktualizacja statystyk
Po rundzie:
•	zapisz wynik każdej ręki,
•	zapisz wynik całej rundy,
•	zaktualizuj bankroll,
•	zaktualizuj system obstawiania,
•	zaktualizuj streaki,
•	zaktualizuj drawdown,
•	zapisz historię bankrolla zgodnie z częstotliwością próbkowania,
•	sprawdź warunek ruin,
•	sprawdź warunek tasowania.
________________________________________
15. Rozliczanie wyników
Utwórz typy wyników:
class HandOutcome(str, Enum):
    BLACKJACK = "blackjack"
    WIN = "win"
    PUSH = "push"
    LOSS = "loss"
    SURRENDER = "surrender"
Przykładowy wynik ręki:
@dataclass(frozen=True)
class HandResult:
    outcome: HandOutcome
    original_bet: Decimal
    additional_bet: Decimal
    total_wagered: Decimal
    net_profit: Decimal
    player_total: int | None
    dealer_total: int | None
    was_doubled: bool
    was_split_hand: bool
    was_blackjack: bool
Przykłady dla zakładu 10:
•	zwykła wygrana: +10,
•	przegrana: -10,
•	push: 0,
•	blackjack 3:2: +15,
•	blackjack 6:5: +12,
•	surrender: -5,
•	wygrany double: +20,
•	przegrany double: -20.
Przy ręce po splicie:
•	każda ręka ma własny zakład,
•	każda ręka ma własny wynik,
•	wynik rundy jest sumą wyników wszystkich rąk i insurance.
________________________________________
16. Statystyki
Raport ma rozróżniać:
•	rundy,
•	ręce,
•	zakłady,
•	wynik netto,
•	obrót,
•	bankroll.
16.1. Podstawowe liczniki
Zbieraj:
•	liczba żądanych rund,
•	liczba faktycznie rozegranych rund,
•	liczba rozliczonych rąk,
•	liczba wygranych,
•	liczba przegranych,
•	liczba push,
•	liczba blackjacków,
•	liczba surrender,
•	liczba splitów,
•	liczba utworzonych rąk po splitach,
•	liczba double,
•	liczba wygranych double,
•	liczba przegranych double,
•	liczba zakupionych insurance,
•	liczba wygranych insurance,
•	liczba przegranych insurance,
•	liczba blackjacków dealera,
•	liczba bustów gracza,
•	liczba bustów dealera,
•	liczba przetasowań.
16.2. Statystyki finansowe
Zbieraj:
•	początkowy bankroll,
•	końcowy bankroll,
•	wynik netto,
•	maksymalny bankroll,
•	minimalny bankroll,
•	maksymalny drawdown,
•	końcowy drawdown,
•	łączna suma zakładów początkowych,
•	łączna suma dodatkowych zakładów,
•	łączna kwota double,
•	łączna kwota splitów,
•	łączna kwota insurance,
•	całkowity obrót,
•	średni zakład początkowy,
•	średnia całkowita ekspozycja na rundę,
•	średni wynik na rundę,
•	średni wynik na rękę.
16.3. Procenty
Oblicz:
win rate wszystkich rąk
loss rate wszystkich rąk
push rate
blackjack rate
surrender rate
double rate
split rate
insurance take rate
insurance win rate
dealer bust rate
player bust rate
Dodatkowo:
win_rate_excluding_pushes = wins / (wins + losses)
Należy jasno opisywać mianownik każdego procentu.
Nie zapisuj enigmatycznego pola win_rate, jeśli nie wiadomo, czy push jest uwzględniony.
16.4. House edge
Oblicz co najmniej dwa wskaźniki.
House edge względem zakładów początkowych
house_edge_initial_bets = -net_profit / total_initial_bets
House edge względem całkowitego obrotu
house_edge_total_action = -net_profit / total_amount_wagered
Jeśli gracz osiągnie dodatni wynik w konkretnej symulacji, house edge estymowany z próbki może wyjść ujemny.
Nie wymuszaj dodatniej wartości.
To jest wynik empiryczny danej symulacji, nie teoretyczna przewaga kasyna.
16.5. RTP
Oblicz:
rtp_initial_bets = 1 - house_edge_initial_bets
Można również raportować RTP względem całkowitego obrotu.
Nazwy muszą jednoznacznie wskazywać podstawę obliczenia.
16.6. Wariancja
Dla każdej rundy zapisuj wynik netto wyrażony:
•	w walucie,
•	opcjonalnie w jednostkach zakładu bazowego.
Oblicz:
•	średnią,
•	wariancję,
•	odchylenie standardowe,
•	standard error,
•	95% przedział ufności średniego wyniku,
•	95% przedział ufności estymowanego house edge.
Dla dużych symulacji nie przechowuj wszystkich wyników rund w pamięci.
Użyj algorytmu strumieniowego, np. algorytmu Welforda.
16.7. Streaki
Zbieraj:
•	najdłuższą serię wygranych rund,
•	najdłuższą serię przegranych rund,
•	aktualną serię,
•	maksymalną serię push, opcjonalnie.
W przypadku rund z wieloma rękami wynik rundy określaj na podstawie zysku netto:
•	dodatni wynik: wygrana rundy,
•	ujemny wynik: przegrana rundy,
•	zero: push rundy.
16.8. Drawdown
Maksymalny drawdown:
1.	śledź historyczny najwyższy bankroll,
2.	oblicz bieżący spadek od szczytu,
3.	zapisz największy zaobserwowany spadek.
Raportuj:
•	kwotowy drawdown,
•	procentowy drawdown względem wcześniejszego szczytu.
16.9. Risk of ruin
Dla pojedynczego przebiegu raportuj:
ruin_observed: true/false
ruin_round: numer rundy lub null
Nie nazywaj tego prawdopodobieństwem bankructwa.
Prawdopodobieństwo bankructwa wymaga wielu niezależnych przebiegów.
Przygotuj późniejszy tryb batch:
batch:
  simulations: 1000
  rounds_per_simulation: 100000
Wtedy:
observed_risk_of_ruin = ruined_simulations / total_simulations
Tryb batch może zostać wykonany w późniejszym etapie.
________________________________________
17. Reprodukowalność
Dla tego samego:
•	seeda,
•	configu,
•	wersji programu,
•	liczby workerów,
•	sposobu podziału pracy,
wynik powinien być identyczny.
W raporcie zapisz:
•	seed,
•	wersję aplikacji,
•	hash konfiguracji,
•	datę uruchomienia,
•	liczbę workerów,
•	liczbę rund,
•	czas wykonania.
Przy wieloprocesowości każdy worker powinien otrzymać osobny deterministyczny seed pochodny.
Nie generuj seedów przez przypadkowe wywołania globalnego RNG.
________________________________________
18. Obsługa wielu workerów
W pierwszym działającym MVP można używać jednego workera.
W późniejszym etapie dodaj wieloprocesowość.
Nie używaj współdzielonego mutable state dla statystyk podczas symulacji.
Preferowane podejście:
1.	podziel liczbę rund na fragmenty,
2.	każdy worker tworzy własny silnik, shoe, RNG i kolektor,
3.	po zakończeniu scal wyniki kolektorów,
4.	zachowaj deterministyczny przydział seedów.
Należy przetestować poprawność scalania:
•	liczników,
•	sum,
•	średnich,
•	wariancji,
•	min/max,
•	streaków, jeśli są agregowane.
Jeżeli poprawne łączenie streaków między fragmentami jest zbyt złożone, przechowuj:
•	prefix streak,
•	suffix streak,
•	maximum streak,
•	typ pierwszego i ostatniego wyniku.
________________________________________
19. Konfiguracja i walidacja
Konfiguracja ma być odczytywana z YAML.
Utwórz również możliwość nadpisania najważniejszych wartości przez CLI.
Przykład:
blackjack-sim run \
  --config configs/standard_6_deck_s17.yaml \
  --rounds 1000000 \
  --seed 123456
Waliduj między innymi:
•	rounds > 0,
•	decks > 0,
•	0 < penetration <= 1,
•	blackjack_payout > 0,
•	bankroll nieujemny,
•	stawki dodatnie,
•	table minimum nie większe niż maksimum,
•	maksymalna liczba rąk po splicie co najmniej 1,
•	insurance fraction od 0 do 1,
•	count-based insurance wymaga systemu liczenia,
•	count spread wymaga systemu liczenia,
•	ENHC nie może jednocześnie używać amerykańskiego peeku,
•	strategia basic strategy musi obsługiwać zestaw zasad.
Błędy konfiguracji mają być czytelne.
Nie dopuszczaj do cichego ignorowania nieznanych pól YAML.
________________________________________
20. CLI
Zaimplementuj następujące komendy.
20.1. Uruchomienie symulacji
blackjack-sim run --config configs/standard_6_deck_s17.yaml
Opcje:
--rounds
--seed
--workers
--output-json
--output-csv
--quiet
--verbose
20.2. Walidacja konfiguracji
blackjack-sim validate --config configs/standard_6_deck_s17.yaml
Ma:
•	zweryfikować konfigurację,
•	sprawdzić dostępność tabeli basic strategy,
•	wyświetlić znormalizowane zasady,
•	nie uruchamiać symulacji.
20.3. Porównanie konfiguracji
Docelowo:
blackjack-sim compare \
  configs/standard_6_deck_s17.yaml \
  configs/blackjack_6_to_5.yaml
Komenda ma uruchomić konfiguracje na porównywalnej liczbie rund i przedstawić różnice.
Najważniejsze pola:
•	wynik netto,
•	house edge,
•	RTP,
•	odchylenie standardowe,
•	blackjack rate,
•	drawdown,
•	częstotliwość ruin.
Ta funkcja może zostać wykonana po podstawowym MVP.
20.4. Tryb debugowania pojedynczych rund
Dodaj możliwość:
blackjack-sim trace \
  --config configs/standard_6_deck_s17.yaml \
  --rounds 10 \
  --seed 123
Tryb ma wypisywać:
•	rozdane karty,
•	decyzje strategii,
•	legalność akcji,
•	wyniki splitów,
•	zachowanie dealera,
•	rozliczenie każdej ręki,
•	zmianę bankrolla.
Tryb trace jest wymagany, ponieważ bardzo ułatwia diagnozowanie błędów. Bez niego debugowanie miliona rozdań przypomina szukanie jednej złej śrubki w transatlantyku.
________________________________________
21. Format raportu konsolowego
Przykład:
BLACKJACK SIMULATION REPORT

Configuration
-------------
Rules profile:                 standard_6_deck_s17
Decks:                         6
Dealer rule:                   S17
Blackjack payout:              3:2
Double after split:            yes
Surrender:                     late
Insurance strategy:            never
Betting strategy:              flat 10.00
Seed:                          123456

Execution
---------
Requested rounds:              1,000,000
Played rounds:                 1,000,000
Resolved hands:                1,027,482
Shuffles:                      1,238
Duration:                      8.42 s
Rounds per second:             118,764

Results
-------
Wins:                          432,018
Losses:                        487,112
Pushes:                        108,352
Blackjacks:                    47,281
Surrenders:                    8,420

Win rate:                      42.05%
Loss rate:                     47.41%
Push rate:                     10.54%
Win rate excluding pushes:     47.01%
Blackjack rate:                4.60%

Bankroll
--------
Initial bankroll:              10,000.00
Final bankroll:                8,420.00
Net result:                    -1,580.00
Maximum bankroll:              12,780.00
Minimum bankroll:              5,770.00
Maximum drawdown:              4,230.00

Wagering
--------
Initial bets:                  10,000,000.00
Additional split bets:         214,230.00
Additional double bets:        387,810.00
Insurance bets:                0.00
Total action:                  10,602,040.00

Statistical estimates
---------------------
House edge, initial bets:      0.0158%
House edge, total action:      0.0149%
RTP, initial bets:             99.9842%
Average result per round:      -0.00158
Standard deviation per round:  1.141
95% confidence interval:       -0.00382 to 0.00066

Risk
----
Longest winning streak:        12
Longest losing streak:         18
Ruin observed:                 no
Liczby są przykładowe. Nie wpisuj ich na stałe.
________________________________________
22. JSON wynikowy
Raport JSON powinien mieć wersjonowany schemat.
Przykład:
{
  "schema_version": "1.0",
  "application_version": "0.1.0",
  "simulation": {
    "seed": 123456,
    "rounds_requested": 1000000,
    "rounds_played": 1000000,
    "hands_resolved": 1027482,
    "workers": 1,
    "duration_seconds": 8.42
  },
  "rules": {
    "decks": 6,
    "dealer_hits_soft_17": false,
    "blackjack_payout": 1.5,
    "double_after_split": true,
    "surrender": "late"
  },
  "results": {
    "wins": 432018,
    "losses": 487112,
    "pushes": 108352,
    "blackjacks": 47281,
    "surrenders": 8420
  },
  "bankroll": {
    "initial": "10000.00",
    "final": "8420.00",
    "net_profit": "-1580.00",
    "maximum": "12780.00",
    "minimum": "5770.00",
    "maximum_drawdown": "4230.00"
  },
  "wagering": {
    "initial_bets": "10000000.00",
    "split_bets": "214230.00",
    "double_bets": "387810.00",
    "insurance_bets": "0.00",
    "total_action": "10602040.00"
  },
  "metrics": {
    "win_rate": 0.4205,
    "loss_rate": 0.4741,
    "push_rate": 0.1054,
    "win_rate_excluding_pushes": 0.4701,
    "blackjack_rate": 0.046,
    "house_edge_initial_bets": 0.000158,
    "house_edge_total_action": 0.000149,
    "rtp_initial_bets": 0.999842
  }
}
Wartości Decimal zapisuj jako string lub według jasno ustalonej polityki, aby nie tracić precyzji.
________________________________________
23. CSV
CSV powinien być opcjonalny.
Możliwe raporty:
23.1. Podsumowanie
Jeden wiersz na symulację.
23.2. Historia bankrolla
Kolumny:
round_number
bankroll
running_peak
drawdown
current_bet
running_count
true_count
Nie zapisuj każdego rozdania przy milionach rund bez wyraźnego włączenia tej opcji.
Domyślnie próbkuj historię, np. co 100 lub 1000 rund.
________________________________________
24. Testy
Poprawność symulatora jest ważniejsza niż szybkość.
Każdy moduł domenowy musi mieć testy jednostkowe.
24.1. Testy wartości ręki
Przetestuj między innymi:
A + 6 = soft 17
A + 6 + 10 = hard 17
A + A = soft 12
A + A + 9 = 21
A + A + 9 + 9 = 20
10 + 7 = hard 17
10 + 6 + 6 = bust 22
A + K = blackjack
A + K po splicie = zwykłe 21
24.2. Testy dealera
Przetestuj:
•	S17 stoi na A+6,
•	H17 dobiera na A+6,
•	dealer dobiera na 16,
•	dealer stoi na hard 17,
•	dealer kończy po bust.
24.3. Testy blackjacka
Przetestuj:
•	blackjack gracza kontra zwykłe 21 dealera,
•	blackjack gracza kontra blackjack dealera,
•	blackjack 3:2,
•	blackjack 6:5,
•	21 z trzech kart nie jest blackjackiem,
•	21 po splicie nie jest blackjackiem domyślnie.
24.4. Testy double
Przetestuj:
•	zwiększenie zakładu,
•	dokładnie jedną dodatkową kartę,
•	automatyczne zakończenie ręki,
•	brak double bez wystarczającego bankrolla,
•	fallback basic strategy,
•	double after split włączone i wyłączone.
24.5. Testy splitów
Przetestuj:
•	zwykły split,
•	kolejność kart,
•	dodatkowy zakład,
•	limit liczby rąk,
•	resplit,
•	brak resplitu,
•	resplit asów,
•	brak resplitu asów,
•	splitowane asy z jedną kartą,
•	hit split aces,
•	blackjack po splicie jako 21,
•	wynik finansowy wielu rąk.
24.6. Testy surrender
Przetestuj:
•	late surrender,
•	early surrender,
•	brak surrender po dobraniu karty,
•	strata połowy zakładu,
•	brak surrender, gdy dealer ma blackjacka przy late surrender.
24.7. Testy insurance
Przetestuj:
•	insurance wygrane,
•	insurance przegrane,
•	prawidłową wypłatę 2:1,
•	limit połowy zakładu,
•	brak środków,
•	strategie never, always i only_with_blackjack,
•	count-based insurance.
24.8. Testy ENHC
Przetestuj:
•	dealer dobiera drugą kartę po graczu,
•	blackjack dealera po double,
•	blackjack dealera po splicie,
•	all_bets,
•	original_bet_only.
24.9. Testy basic strategy
Przetestuj wszystkie komórki tabel.
Dodaj testy przykładowych decyzji:
•	hard 16 kontra 10,
•	hard 12 kontra 4,
•	soft 18 kontra 9,
•	soft 18 kontra 6,
•	para 8 kontra 10,
•	para 10 kontra 6,
•	asy kontra dowolną kartę,
•	parę 5 traktowaną jako hard 10, jeśli strategia nie zaleca splitu.
Wartości zależą od wybranego wariantu zasad. Test musi jawnie wskazywać profil strategii.
24.10. Testy deterministyczności
Dwie symulacje z tym samym:
•	seedem,
•	configiem,
•	liczbą rund,
muszą zwrócić identyczny raport.
Dwie symulacje z różnymi seedami powinny zwykle zwracać inne wyniki.
24.11. Testy niezmienników
Po każdej rundzie:
bankroll końcowy = bankroll początkowy + suma wyników netto
Łączna liczba rozliczonych rąk:
wins + losses + pushes + surrenders = hands_resolved
O ile blackjack jest podkategorią wygranej, nie dodawaj go drugi raz do sumy outcome.
Należy jasno zdefiniować:
•	czy blackjack jest osobnym outcome,
•	czy podkategorią win.
Preferowane rozwiązanie:
•	outcome = BLACKJACK,
•	suma wszystkich głównych outcome obejmuje blackjack zamiast zwykłego win.
Wtedy:
wins + blackjacks + losses + pushes + surrenders = hands_resolved
24.12. Testy statystyczne
Nie buduj testów, które wymagają dokładnie określonego house edge po małej liczbie losowych rund.
Można dodać testy integracyjne o szerokich granicach dla dużej próbki, ale nie mogą być kruche.
Przykładowo:
•	blackjack rate powinien znajdować się w rozsądnym przedziale,
•	suma procentów outcome powinna wynosić około 100%,
•	flat betting z tym samym seedem musi być deterministyczny.
________________________________________
25. Wydajność
Najpierw zapewnij poprawność.
Następnie wykonaj profilowanie.
Cele orientacyjne dla jednego procesu:
•	co najmniej dziesiątki tysięcy rund na sekundę,
•	brak przechowywania wszystkich obiektów rąk po zakończeniu rundy,
•	brak przechowywania całej historii, jeśli nie jest potrzebna.
Nie optymalizuj przez:
•	usuwanie typów i walidacji bez pomiarów,
•	łączenie całego kodu w jedną funkcję,
•	używanie globalnego stanu,
•	zastępowanie poprawnego modelu trudnym do zweryfikowania kodem.
Możliwe optymalizacje:
•	slots=True,
•	lekkie enumy,
•	unikanie niepotrzebnego kopiowania kart,
•	strumieniowe statystyki,
•	ograniczone logowanie w trybie produkcyjnym,
•	wieloprocesowość.
________________________________________
26. Logowanie
Użyj standardowego modułu logging.
Poziomy:
•	DEBUG: szczegóły każdej karty i decyzji,
•	INFO: start, koniec, podsumowanie,
•	WARNING: nietypowa, ale obsłużona sytuacja,
•	ERROR: błąd konfiguracji lub działania.
Nie używaj print() wewnątrz silnika domenowego.
CLI może korzystać z warstwy prezentacji.
________________________________________
27. Obsługa błędów
Utwórz własne wyjątki, np.:
class BlackjackSimulatorError(Exception):
    pass


class ConfigurationError(BlackjackSimulatorError):
    pass


class IllegalActionError(BlackjackSimulatorError):
    pass


class InsufficientBankrollError(BlackjackSimulatorError):
    pass


class UnsupportedStrategyProfileError(BlackjackSimulatorError):
    pass
Nie przechwytuj wszędzie ogólnego Exception.
Nie ignoruj błędów.
Nie próbuj kontynuować symulacji po naruszeniu niezmiennika domenowego.
________________________________________
28. README
README ma zawierać:
1.	opis projektu,
2.	cele,
3.	ostrzeżenie, że systemy obstawiania nie eliminują przewagi kasyna,
4.	funkcje,
5.	wymagania,
6.	instalację,
7.	szybki start,
8.	przykład konfiguracji,
9.	użycie CLI,
10.	opis raportu,
11.	informacje o testach,
12.	informacje o licencji,
13.	roadmapę,
14.	informacje o wkładzie społeczności.
Dodaj wyraźną informację:
Projekt jest narzędziem symulacyjnym i edukacyjnym. Nie gwarantuje zysku i nie stanowi porady finansowej ani zachęty do hazardu.
Bez moralizatorskiego tonu. To ma być techniczna informacja o przeznaczeniu projektu.
________________________________________
29. AGENTS.md
Utwórz plik AGENTS.md zawierający instrukcje dla kolejnych agentów.
Ma zawierać co najmniej:
29.1. Zasady pracy
•	przed zmianą przeczytaj README, architekturę i aktywne zadanie,
•	nie implementuj funkcji spoza aktualnego taska bez uzasadnienia,
•	nie zmieniaj zachowania domenowego bez testu,
•	każda poprawka błędu musi mieć test regresyjny,
•	nie usuwaj istniejących testów tylko po to, żeby pipeline był zielony,
•	nie zmieniaj publicznych interfejsów bez aktualizacji dokumentacji,
•	zachowuj deterministyczność.
29.2. Kontrola jakości
Przed zakończeniem zadania uruchom:
pytest
ruff check .
ruff format --check .
mypy src
Jeśli użyte komendy różnią się zależnie od konfiguracji projektu, wpisz właściwe komendy.
29.3. Zakres commitów
Każdy commit powinien być:
•	mały,
•	spójny,
•	możliwy do opisania jednym zdaniem,
•	zawierać testy właściwe dla zmiany.
Nie łącz w jednym commicie:
•	refaktoryzacji,
•	nowej funkcji,
•	zmian dokumentacji niezwiązanych z funkcją,
•	masowego formatowania.
29.4. Zakaz zgadywania zasad
Jeżeli agent nie jest pewny reguły blackjacka:
1.	nie powinien zgadywać,
2.	powinien zapisać założenie w dokumentacji,
3.	powinien wprowadzić regułę jako konfigurowalną, jeśli istnieją różne warianty,
4.	powinien dodać test potwierdzający wybrane zachowanie.
________________________________________
30. Commity i wersjonowanie
Stosuj Conventional Commits.
Przykłady:
feat: add dealer soft 17 behavior
feat: implement late surrender settlement
fix: prevent blackjack payout after split
fix: preserve bankroll on insurance push scenario
test: add resplit aces regression coverage
refactor: extract hand value calculation
docs: document european no hole card rules
chore: configure ruff and mypy
perf: reduce card allocation during simulation
30.1. Typy commitów
•	feat: nowa funkcja,
•	fix: poprawka błędu,
•	test: testy bez zmiany logiki,
•	refactor: zmiana struktury bez zmiany zachowania,
•	docs: dokumentacja,
•	chore: konfiguracja i narzędzia,
•	perf: poprawa wydajności,
•	ci: pipeline CI,
•	build: system budowania lub zależności.
30.2. Wersjonowanie
Stosuj Semantic Versioning.
Przykłady:
•	0.1.0: podstawowe hit/stand i flat betting,
•	0.2.0: basic strategy,
•	0.3.0: split, double i surrender,
•	0.4.0: insurance i ENHC,
•	0.5.0: dodatkowe systemy obstawiania,
•	0.6.0: statystyki rozszerzone i batch simulations,
•	1.0.0: stabilny publiczny interfejs i kompletne MVP.
Przed wersją 1.0.0 można zmieniać publiczne API, ale każda zmiana musi być opisana w changelogu.
________________________________________
31. CHANGELOG
Prowadź CHANGELOG.md zgodnie z formatem Keep a Changelog.
Sekcje:
Added
Changed
Deprecated
Removed
Fixed
Security
Każde zadanie kończące widoczną funkcję użytkownika powinno aktualizować changelog.
Nie wpisuj do changelogu każdego wewnętrznego przesunięcia funkcji między plikami, jeśli nie ma wpływu na użytkownika.
________________________________________
32. Licencja i credits
Projekt ma być open source.
Domyślnie użyj licencji MIT, chyba że istnieje powód wyboru innej licencji.
Utwórz:
•	LICENSE,
•	sekcję credits w README,
•	opcjonalnie THIRD_PARTY_NOTICES.md.
Dla każdej zależności zewnętrznej:
1.	sprawdź jej licencję,
2.	upewnij się, że jest zgodna z licencją projektu,
3.	umieść wymagane informacje w credits lub notices,
4.	nie kopiuj kodu z projektu o niezgodnej licencji.
Nie deklaruj licencji zależności bez sprawdzenia jej metadanych.
________________________________________
33. CI
Utwórz GitHub Actions uruchamiane dla:
•	push,
•	pull request.
Pipeline powinien wykonywać:
instalację zależności
ruff check
ruff format --check
mypy
pytest
Opcjonalnie:
•	coverage,
•	test na kilku wersjach Pythona.
Minimalny próg pokrycia można początkowo ustawić na 80%, ale moduły domenowe powinny mieć znacznie wyższe pokrycie.
Nie optymalizuj projektu pod sam procent coverage. Testy mają wykrywać błędy, a nie ceremonialnie wykonywać linie kodu.
________________________________________
34. Dokumentacja architektury
Utwórz docs/architecture.md.
Dokument ma zawierać:
•	diagram modułów,
•	przepływ pojedynczej rundy,
•	model zależności,
•	sposób wyboru basic strategy,
•	sposób rozliczania bankrolla,
•	sposób liczenia statystyk,
•	sposób dodawania nowej strategii obstawiania,
•	sposób dodawania nowej strategii insurance,
•	sposób dodawania nowej reguły stołu.
Można użyć diagramów Mermaid.
Przykład:
flowchart TD
    Config --> Engine
    Engine --> Shoe
    Engine --> Round
    Round --> PlayingStrategy
    Round --> InsuranceStrategy
    Engine --> BettingStrategy
    Round --> Settlement
    Settlement --> StatisticsCollector
    StatisticsCollector --> Report
________________________________________
35. Dokumentacja zasad
Utwórz docs/rules.md.
Dla każdej reguły opisz:
•	nazwę,
•	pole konfiguracji,
•	dozwolone wartości,
•	wartość domyślną,
•	wpływ na przebieg rundy,
•	wpływ na basic strategy,
•	przykład.
W szczególności opisz:
•	S17/H17,
•	payout blackjacka,
•	DAS,
•	split aces,
•	resplit aces,
•	surrender,
•	peek,
•	ENHC,
•	OBO,
•	insurance,
•	even money,
•	penetrację.
________________________________________
36. Pliki z zadaniami
Utwórz osobne pliki Markdown w katalogu tasks.
Każdy task powinien zawierać:
Cel
Zakres
Poza zakresem
Wymagania funkcjonalne
Wymagania techniczne
Testy
Kryteria akceptacji
Pliki prawdopodobnie objęte zmianą
Ryzyka
Nie realizuj automatycznie wszystkich tasków naraz.
Agent powinien wykonywać jedno zadanie, uruchamiać testy i dopiero potem przechodzić do następnego.
________________________________________
37. Kolejność implementacji
Task 001: Fundament projektu
Zakres:
•	struktura katalogów,
•	pyproject.toml,
•	konfiguracja pytest, ruff i mypy,
•	bazowe wyjątki,
•	README,
•	AGENTS,
•	LICENSE,
•	CHANGELOG,
•	CI.
Kryteria:
•	projekt instaluje się,
•	test przykładowy działa,
•	pipeline jest zielony.
Task 002: Karty i ręka
Zakres:
•	Rank,
•	Card,
•	Hand,
•	wartość ręki,
•	soft/hard,
•	blackjack,
•	bust,
•	para.
Kryteria:
•	wszystkie przypadki z asami są przetestowane,
•	blackjack po splicie jest poprawnie rozpoznawany.
Task 003: Shoe i dealer
Zakres:
•	generowanie shoe,
•	liczba talii,
•	tasowanie,
•	seed,
•	penetracja,
•	S17/H17.
Kryteria:
•	shoe ma prawidłową liczbę kart,
•	wyniki są deterministyczne,
•	dealer poprawnie rozgrywa soft 17.
Task 004: Podstawowa runda i rozliczenie
Zakres:
•	początkowe rozdanie,
•	hit,
•	stand,
•	blackjack,
•	bust,
•	push,
•	flat betting,
•	bankroll.
Kryteria:
•	można uruchomić wielorundową symulację bez splitów, double, surrender i insurance,
•	wynik bankrolla zgadza się z sumą wyników netto.
Task 005: Basic strategy
Zakres:
•	interfejs strategii,
•	tabele hard/soft/pairs,
•	profile S17 i H17,
•	factory,
•	fallback actions.
Kryteria:
•	strategia nie wykonuje nielegalnych akcji,
•	tabela jest kompletna,
•	wszystkie komórki mają testy.
Task 006: Double i surrender
Zakres:
•	double,
•	ograniczenia double,
•	DAS,
•	early surrender,
•	late surrender,
•	fallback basic strategy.
Kryteria:
•	prawidłowe zakłady i rozliczenie,
•	testy przypadków z blackjackiem dealera.
Task 007: Splity
Zakres:
•	split,
•	resplit,
•	limit rąk,
•	split aces,
•	resplit aces,
•	hit split aces,
•	double after split.
Kryteria:
•	poprawny bankroll,
•	poprawna kolejność rozgrywania,
•	21 po splicie nie jest blackjackiem domyślnie.
Task 008: Insurance, even money i peek
Zakres:
•	zakład insurance,
•	strategie insurance,
•	even money,
•	amerykański peek.
Kryteria:
•	osobne rozliczenie insurance,
•	poprawne zachowanie przy blackjacku gracza i dealera.
Task 009: ENHC
Zakres:
•	europejski brak hole card,
•	dobieranie drugiej karty po graczu,
•	all bets lost,
•	original bets only.
Kryteria:
•	prawidłowe rozliczenie splitów i double przy blackjacku dealera.
Task 010: Systemy obstawiania
Zakres:
•	Martingale,
•	Paroli,
•	Fibonacci,
•	D’Alembert,
•	limity stołu,
•	brak środków.
Kryteria:
•	każdy system ma testy stanu,
•	push ma jawnie określone zachowanie,
•	split nie aktualizuje systemu jak osobna runda.
Task 011: Liczenie kart
Zakres:
•	Hi-Lo,
•	running count,
•	true count,
•	insurance count-based,
•	true count spread.
Kryteria:
•	count resetuje się po shuffle,
•	hole card aktualizuje count dopiero po ujawnieniu.
Task 012: Statystyki i raporty
Zakres:
•	kolektor,
•	Welford,
•	house edge,
•	RTP,
•	drawdown,
•	streaki,
•	JSON,
•	CSV,
•	raport konsolowy.
Kryteria:
•	statystyki nie wymagają trzymania wszystkich rund,
•	wartości są spójne z licznikami.
Task 013: CLI i konfiguracja
Zakres:
•	YAML,
•	walidacja,
•	run,
•	validate,
•	trace,
•	override parametrów.
Kryteria:
•	użytkownik może uruchomić pełną symulację z pliku YAML,
•	błędny config daje czytelny komunikat.
Task 014: Wydajność i wielu workerów
Zakres:
•	profilowanie,
•	multiprocessing,
•	scalanie statystyk,
•	deterministyczne seedy workerów.
Kryteria:
•	wyniki agregacji są poprawne,
•	nie ma współdzielonego mutable state.
Task 015: Walidacja końcowa
Zakres:
•	pełny test suite,
•	analiza konfiguracji przykładowych,
•	test milionowej symulacji,
•	dokumentacja,
•	changelog,
•	przygotowanie wersji MVP.
Kryteria:
•	wszystkie testy przechodzą,
•	przykładowe konfiguracje działają,
•	raporty są czytelne,
•	nie ma znanych błędów krytycznych.
________________________________________
38. Zasady wykonywania pracy przez agenta
Agent ma postępować według poniższej procedury.
38.1. Przed rozpoczęciem zadania
1.	przeczytaj AGENTS.md,
2.	przeczytaj aktywny plik taska,
3.	sprawdź istniejące moduły i testy,
4.	wypisz krótki plan zmian,
5.	zidentyfikuj ryzyka i przypadki brzegowe.
38.2. Podczas implementacji
1.	najpierw dodaj lub zaktualizuj testy,
2.	zaimplementuj najmniejszą zmianę spełniającą wymagania,
3.	unikaj zmian niezwiązanych z taskiem,
4.	nie duplikuj logiki,
5.	zachowuj deterministyczność,
6.	aktualizuj typy i dokumentację.
38.3. Przed zakończeniem zadania
Uruchom:
pytest
ruff check .
ruff format --check .
mypy src
Następnie:
1.	sprawdź diff,
2.	usuń debug printy,
3.	sprawdź, czy testy rzeczywiście pokrywają zmianę,
4.	zaktualizuj changelog,
5.	zaktualizuj dokumentację, jeśli zachowanie użytkowe się zmieniło,
6.	przygotuj mały, spójny commit.
38.4. Raport po zadaniu
Po każdym zadaniu agent ma przedstawić:
Co zostało wykonane
Jakie pliki zmieniono
Jakie decyzje architektoniczne podjęto
Jakie testy dodano
Wyniki testów
Znane ograniczenia
Proponowany następny task
Nie rozpoczynaj kolejnego dużego etapu w tym samym kroku, jeśli aktualny task nie został zakończony i przetestowany.
________________________________________
39. Kryteria ukończenia MVP
MVP uznaje się za ukończone, jeśli:
•	można skonfigurować od 1 do 8 talii,
•	działa S17 i H17,
•	działa payout 3:2 i 6:5,
•	działa blackjack, hit, stand, double, split i surrender,
•	działa DAS,
•	działają zasady splitowanych asów,
•	działa insurance z opcją always i never,
•	działa amerykański peek,
•	działa ENHC,
•	gracz stosuje basic strategy dopasowaną do zasad,
•	działa flat betting,
•	działa co najmniej Martingale, Paroli, Fibonacci i D’Alembert,
•	można ustawić bankroll, minimum i maksimum stołu,
•	można ustawić liczbę rund i seed,
•	można wykonać co najmniej milion rund,
•	raport zawiera pełne statystyki,
•	wynik jest deterministyczny dla tego samego seeda,
•	istnieją testy jednostkowe i integracyjne,
•	konfiguracja jest walidowana,
•	działa CLI,
•	wyniki można zapisać do JSON,
•	dokumentacja wyjaśnia zasady i metryki,
•	CI przechodzi.
________________________________________
40. Elementy poza zakresem pierwszego MVP
Nie implementuj w pierwszym MVP, chyba że wszystkie wymagane funkcje są już ukończone i przetestowane:
•	panelu webowego,
•	symulacji gry wieloosobowej przy jednym stole,
•	wizualnego stołu blackjacka,
•	side betów typu Perfect Pairs lub 21+3,
•	dynamicznego wykonywania strategii użytkownika,
•	uczenia maszynowego,
•	automatycznego pobierania zasad z internetu.
Architektura może pozostawić miejsce na późniejsze dodanie panelu webowego i side betów.
________________________________________
41. Przyszły panel webowy
Po ukończeniu silnika można dodać:
•	backend FastAPI,
•	frontend React, Vue lub Svelte,
•	formularz konfiguracji,
•	wykres bankrolla,
•	porównywanie wielu konfiguracji,
•	kolejkę zadań dla długich symulacji,
•	zapis historii uruchomień.
Silnik domenowy nie może wymagać modyfikacji tylko dlatego, że dodano API.
API powinno wywoływać istniejący serwis symulacji.
Przykładowe endpointy przyszłego API:
POST /api/v1/simulations
GET /api/v1/simulations/{id}
GET /api/v1/simulations/{id}/results
POST /api/v1/configurations/validate
Nie implementuj tego w pierwszym zadaniu.
________________________________________
42. Najważniejsze pułapki
Podczas implementacji zwróć szczególną uwagę na:
1.	odróżnienie naturalnego blackjacka od zwykłego 21,
2.	blackjack po splicie,
3.	S17 kontra H17,
4.	splitowane asy,
5.	bankroll po splitach i double,
6.	insurance jako osobny zakład,
7.	late surrender a blackjack dealera,
8.	ENHC i utratę dodatkowych zakładów,
9.	odróżnienie rund od rąk,
10.	house edge względem zakładów początkowych i całkowitego obrotu,
11.	aktualizowanie systemu obstawiania raz na rundę,
12.	deterministyczny RNG,
13.	ujawnianie hole card przy liczeniu kart,
14.	brak środków na double lub split,
15.	legalne fallbacki basic strategy,
16.	błędy zaokrągleń pieniędzy,
17.	prawidłową kolejność kart w shoe,
18.	nieprzechowywanie całej historii przy milionach rund.
________________________________________
43. Pierwsze polecenie wykonawcze
Rozpocznij od przygotowania fundamentu projektu.
W pierwszym kroku wykonaj wyłącznie:
1.	utworzenie struktury katalogów,
2.	skonfigurowanie pyproject.toml,
3.	skonfigurowanie pytest, ruff i mypy,
4.	utworzenie README,
5.	utworzenie AGENTS.md,
6.	utworzenie CHANGELOG.md,
7.	dodanie licencji MIT,
8.	utworzenie dokumentów architektury,
9.	utworzenie plików z taskami,
10.	dodanie podstawowego pipeline CI,
11.	dodanie minimalnego testu sprawdzającego instalację pakietu.
Nie implementuj jeszcze pełnego silnika blackjacka.
Po wykonaniu pierwszego kroku przedstaw:
•	utworzoną strukturę,
•	najważniejsze decyzje,
•	listę plików,
•	wynik uruchomionych narzędzi,
•	propozycję commita,
•	wskazanie następnego taska.
Nie przechodź automatycznie do kolejnego taska.

