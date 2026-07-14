Instrukcja dla agenta AI: rozwój symulatora blackjacka po ukończeniu MVP
1. Kontekst projektu
Istnieje już działające MVP konfigurowalnego symulatora blackjacka.
Aktualny projekt powinien posiadać przynajmniej:
•	model kart i shoe,
•	obsługę jednej lub wielu talii,
•	konfigurację zasad stołu,
•	S17 i H17,
•	blackjack payout 3:2 i 6:5,
•	hit,
•	stand,
•	double,
•	split,
•	surrender,
•	insurance,
•	podstawowe systemy obstawiania,
•	basic strategy,
•	bankroll,
•	statystyki,
•	konfigurację przez pliki,
•	CLI,
•	testy jednostkowe i integracyjne.
Twoim zadaniem jest rozwinięcie projektu do postaci pełnego narzędzia analitycznego z rozbudowanym panelem webowym.
Nie przepisuj istniejącego silnika bez potrzeby.
Najpierw przeanalizuj aktualną strukturę repozytorium, istniejące interfejsy, testy i dokumentację. Rozbudowę prowadź etapami, zachowując kompatybilność z istniejącym silnikiem tam, gdzie jest to rozsądne.
Najważniejsze cele:
1.	umożliwić dokładne śledzenie przebiegu rund,
2.	walidować poprawność matematyczną silnika,
3.	porównywać różne konfiguracje,
4.	uruchamiać wiele niezależnych symulacji,
5.	dodawać gotowe profile stołów,
6.	rozbudować liczenie kart,
7.	dodać deviations od basic strategy,
8.	rozbudować systemy obstawiania,
9.	stworzyć pełny backend API,
10.	stworzyć bardzo rozbudowany i estetyczny panel webowy,
11.	umożliwić import i eksport konfiguracji,
12.	umożliwić eksport wyników i raportów.
Nie implementuj modułu automatycznych eksperymentów polegającego na generowaniu wszystkich kombinacji zmiennych konfiguracyjnych. Funkcja ta jest poza zakresem tego etapu.
________________________________________
2. Zasady pracy
Nie implementuj wszystkiego naraz.
Podziel rozwój na osobne taski opisane w katalogu tasks.
Każdy task powinien zawierać:
•	cel,
•	zakres,
•	elementy poza zakresem,
•	wymagania funkcjonalne,
•	wymagania techniczne,
•	wymagane testy,
•	kryteria akceptacji,
•	ryzyka,
•	przewidywane pliki do zmiany.
Po zakończeniu każdego taska:
1.	uruchom testy,
2.	uruchom linting,
3.	uruchom type checking,
4.	sprawdź diff,
5.	zaktualizuj dokumentację,
6.	zaktualizuj changelog,
7.	przygotuj mały commit zgodny z Conventional Commits.
Nie rozpoczynaj kolejnego dużego etapu przed zakończeniem i przetestowaniem obecnego.
________________________________________
3. Wymagany kierunek architektury
Rozbuduj projekt w układzie podobnym do:
blackjack-simulator/
├── backend/
│   ├── src/
│   │   └── blackjack_api/
│   │       ├── main.py
│   │       ├── config.py
│   │       ├── dependencies.py
│   │       ├── exceptions.py
│   │       │
│   │       ├── api/
│   │       │   ├── router.py
│   │       │   └── routes/
│   │       │       ├── simulations.py
│   │       │       ├── comparisons.py
│   │       │       ├── batches.py
│   │       │       ├── configurations.py
│   │       │       ├── presets.py
│   │       │       ├── reports.py
│   │       │       └── health.py
│   │       │
│   │       ├── schemas/
│   │       │   ├── simulation.py
│   │       │   ├── configuration.py
│   │       │   ├── comparison.py
│   │       │   ├── batch.py
│   │       │   ├── trace.py
│   │       │   └── report.py
│   │       │
│   │       ├── services/
│   │       │   ├── simulation_service.py
│   │       │   ├── comparison_service.py
│   │       │   ├── batch_service.py
│   │       │   ├── configuration_service.py
│   │       │   ├── export_service.py
│   │       │   └── preset_service.py
│   │       │
│   │       ├── repositories/
│   │       │   ├── simulation_repository.py
│   │       │   ├── configuration_repository.py
│   │       │   └── preset_repository.py
│   │       │
│   │       └── workers/
│   │           ├── task_queue.py
│   │           └── simulation_worker.py
│   │
│   └── tests/
│
├── engine/
│   ├── src/
│   │   └── blackjack_simulator/
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   ├── public/
│   └── tests/
│
├── configs/
├── presets/
├── reports/
├── tasks/
├── docs/
├── docker-compose.yml
├── README.md
├── AGENTS.md
└── CHANGELOG.md
Jeśli obecna struktura projektu jest inna, dostosuj rozwiązanie do istniejącego repozytorium. Nie przenoś bezmyślnie całego projektu tylko po to, żeby zgadzał się katalog po katalogu z powyższym przykładem.
Silnik domenowy ma pozostać niezależny od FastAPI i frontendu.
Backend ma korzystać z silnika przez publiczny interfejs aplikacyjny.
Frontend nie może zawierać logiki rozliczania blackjacka.
________________________________________
4. Etap 1: rozbudowany tryb trace
4.1. Cel
Dodaj możliwość dokładnego śledzenia pojedynczych rund.
Tryb trace musi pozwalać odtworzyć każdą decyzję i każde rozliczenie.
4.2. Zakres danych
Dla każdej rundy zapisuj:
•	numer rundy,
•	seed,
•	numer shoe,
•	liczbę kart pozostałych przed rundą,
•	running count,
•	true count,
•	wysokość zakładu początkowego,
•	bankroll przed rundą,
•	kolejność rozdanych kart,
•	rękę początkową gracza,
•	kartę odkrytą dealera,
•	kartę zakrytą dealera, gdy zostanie ujawniona,
•	decyzję insurance,
•	kwotę insurance,
•	rezultat peeku,
•	wszystkie ręce utworzone po splitach,
•	kolejność rozgrywania rąk,
•	każdą decyzję basic strategy,
•	decyzję przed zastosowaniem fallbacku,
•	legalność każdej możliwej akcji,
•	ostatecznie wykonaną akcję,
•	wszystkie dobrane karty,
•	moment double,
•	moment surrender,
•	moment splitu,
•	wynik każdej ręki,
•	wynik insurance,
•	łączny wynik rundy,
•	bankroll po rundzie.
4.3. Model zdarzeń
Zaprojektuj trace jako listę typowanych zdarzeń, nie jako jeden długi string.
Przykładowe zdarzenia:
RoundStarted
InitialBetPlaced
CardDealt
InsuranceOffered
InsuranceDecisionMade
DealerPeeked
StrategyDecisionRequested
StrategyDecisionResolved
PlayerHit
PlayerStood
PlayerDoubled
PlayerSplit
PlayerSurrendered
DealerTurnStarted
DealerHit
DealerStood
HandSettled
InsuranceSettled
RoundSettled
ShoeShuffled
Każde zdarzenie powinno mieć:
•	typ,
•	timestamp lub kolejność sekwencyjną,
•	numer rundy,
•	identyfikator ręki,
•	dane szczegółowe.
4.4. Wyjście
Obsługuj:
•	raport czytelny w terminalu,
•	JSON,
•	prezentację w panelu webowym.
Przykład CLI:
blackjack-sim trace \
  --config configs/standard.yaml \
  --rounds 10 \
  --seed 123
4.5. Panel trace
Frontend powinien prezentować trace jako wizualną oś czasu.
Dla każdej rundy pokaż:
•	karty gracza,
•	karty dealera,
•	wszystkie splity jako osobne gałęzie,
•	decyzje strategii,
•	uzasadnienie decyzji,
•	zmiany zakładu,
•	wynik ręki,
•	zmianę bankrolla.
Dodaj możliwość:
•	rozwijania i zwijania szczegółów,
•	filtrowania po rodzaju zdarzenia,
•	przechodzenia między rundami,
•	wyszukiwania rundy po numerze,
•	pokazywania wyłącznie rund zawierających split, double, surrender, blackjack lub insurance.
________________________________________
5. Etap 2: audit i walidacja silnika
5.1. Cel
Dodaj moduł audytu poprawności silnika.
Komenda:
blackjack-sim audit \
  --config configs/standard.yaml \
  --rounds 1000000
5.2. Kontrole
Audit powinien sprawdzać co najmniej:
Spójność kart
•	shoe zawiera poprawną liczbę kart,
•	żadna karta nie znika,
•	żadna karta nie jest rozdawana dwa razy,
•	liczba kart rozdanych i pozostałych jest spójna,
•	shuffle resetuje shoe poprawnie.
Spójność bankrolla
•	bankroll końcowy odpowiada bankrollowi początkowemu i sumie wyników,
•	dodatkowe zakłady są poprawnie pobierane,
•	zwroty po push są poprawne,
•	surrender zwraca właściwą część zakładu,
•	insurance jest księgowane osobno.
Legalność akcji
•	strategia nigdy nie wykonuje nielegalnej akcji,
•	double nie występuje bez odpowiednich środków,
•	split nie występuje po osiągnięciu limitu,
•	surrender nie występuje po hit,
•	split asów respektuje ustawienia.
Spójność statystyk
•	suma outcome odpowiada liczbie rąk,
•	suma rund odpowiada żądanej liczbie lub wcześniejszemu zakończeniu,
•	procenty mają poprawne mianowniki,
•	house edge i RTP są obliczane spójnie.
Deterministyczność
•	ten sam seed i config dają identyczny wynik,
•	trace dla tego samego seeda jest identyczny,
•	wynik po serializacji i ponownym odczycie configu jest identyczny.
Basic strategy
•	wybrany profil strategii pasuje do zasad,
•	wszystkie komórki tabel są zdefiniowane,
•	fallbacki są poprawnie stosowane,
•	każda decyzja kończy się legalną akcją.
5.3. Raport
Raport audytu powinien mieć statusy:
PASS
WARNING
FAIL
SKIPPED
Dla każdego testu pokaż:
•	nazwę,
•	status,
•	opis,
•	szczegóły,
•	liczbę wykrytych naruszeń,
•	numery przykładowych rund,
•	możliwość przejścia do trace problematycznej rundy.
5.4. Tryb strict
Dodaj:
--strict
W trybie strict każde ostrzeżenie ma powodować niezerowy kod wyjścia.
________________________________________
6. Etap 3: porównywanie konfiguracji
6.1. Cel
Dodaj funkcję porównującą wiele konfiguracji.
Przykład:
blackjack-sim compare \
  configs/standard_3_2_s17.yaml \
  configs/standard_6_5_h17.yaml \
  --rounds 5000000
6.2. Porównywane metryki
Dla każdej konfiguracji pokaż:
•	liczbę rund,
•	liczbę rąk,
•	wynik netto,
•	końcowy bankroll,
•	house edge względem zakładów początkowych,
•	house edge względem całkowitego obrotu,
•	RTP,
•	standard deviation,
•	confidence interval,
•	win rate,
•	loss rate,
•	push rate,
•	blackjack rate,
•	surrender rate,
•	split rate,
•	double rate,
•	dealer bust rate,
•	maksymalny drawdown,
•	najdłuższy losing streak,
•	observed ruin,
•	średnią ekspozycję na rundę.
6.3. Porównanie względne
Dla każdej konfiguracji oblicz różnicę względem konfiguracji bazowej.
Przykład:
Blackjack payout 6:5:
house edge: +1.36 p.p.
RTP: -1.36 p.p.
average result per round: -0.136 units
6.4. Fair comparison
Dodaj dwa tryby:
Independent seeds
Każda konfiguracja korzysta z osobnego seeda.
Common random numbers
Konfiguracje korzystają z porównywalnych strumieni losowych, jeśli architektura silnika na to pozwala.
Jeśli różne reguły zmieniają liczbę dobieranych kart, nie udawaj pełnej identyczności przebiegów. Udokumentuj ograniczenia.
6.5. Panel porównania
Panel ma pozwalać:
•	wybrać zapisane konfiguracje,
•	dodać bieżący config z formularza,
•	wskazać konfigurację bazową,
•	ustawić liczbę rund,
•	uruchomić porównanie,
•	sortować wyniki,
•	ukrywać i pokazywać kolumny,
•	prezentować różnice procentowe i bezwzględne,
•	eksportować porównanie do JSON, CSV i PDF.
Dodaj wykresy:
•	house edge,
•	RTP,
•	wynik netto,
•	drawdown,
•	standard deviation,
•	końcowy bankroll,
•	win/loss/push,
•	skumulowany bankroll.
________________________________________
7. Etap 4: batch simulations
7.1. Cel
Dodaj możliwość uruchamiania wielu niezależnych sesji.
Przykład:
batch:
  simulations: 1000
  rounds_per_simulation: 100000
  base_seed: 123456
7.2. Metryki batch
Raportuj:
•	liczbę sesji,
•	liczbę sesji ukończonych,
•	liczbę sesji zakończonych bankructwem,
•	observed risk of ruin,
•	średni końcowy bankroll,
•	medianę końcowego bankrolla,
•	minimum,
•	maksimum,
•	odchylenie standardowe,
•	percentyle 1, 5, 10, 25, 50, 75, 90, 95 i 99,
•	odsetek sesji z zyskiem,
•	odsetek sesji ze stratą,
•	odsetek sesji z wynikiem zero,
•	średni maksymalny drawdown,
•	medianę maksymalnego drawdownu,
•	percentyle drawdownu,
•	średnią rundę bankructwa,
•	medianę rundy bankructwa,
•	najlepszą i najgorszą sesję,
•	średni house edge z sesji,
•	przedział ufności średniego wyniku.
7.3. Rozkłady
Przechowuj dane pozwalające tworzyć:
•	histogram końcowego bankrolla,
•	histogram wyniku netto,
•	histogram maksymalnego drawdownu,
•	histogram rundy bankructwa,
•	wykres percentyli bankrolla w czasie.
Nie przechowuj pełnej historii każdej rundy każdej sesji, jeśli nie jest to potrzebne.
Dodaj konfigurowalne próbkowanie historii.
7.4. Panel batch
Panel ma zawierać:
•	liczbę sesji,
•	liczbę rund na sesję,
•	bazowy seed,
•	liczbę workerów,
•	bankroll,
•	warunki stop-loss i stop-win,
•	informację o przewidywanej wielkości danych,
•	postęp wykonania,
•	liczbę ukończonych sesji,
•	możliwość anulowania zadania.
Wyniki przedstaw jako:
•	karty metryk,
•	histogramy,
•	percentyle,
•	tabelę najlepszych i najgorszych sesji,
•	wykres ryzyka bankructwa,
•	wykres rozkładu końcowego bankrolla.
________________________________________
8. Etap 5: gotowe profile stołów
8.1. Cel
Dodaj system presetów zasad.
Preset powinien być zwykłą, walidowaną konfiguracją z dodatkowymi metadanymi.
8.2. Metadane presetu
Każdy preset powinien mieć:
id: standard-6d-s17
name: Standard 6 Deck S17
description: Standardowy stół sześciotaliowy
category: standard
tags:
  - 6-deck
  - s17
  - das
source: built-in
version: 1
8.3. Presety wbudowane
Dodaj co najmniej:
•	6 Deck S17, 3:2, DAS, late surrender,
•	6 Deck H17, 3:2, DAS,
•	8 Deck H17,
•	6 Deck 6:5,
•	Single Deck 3:2,
•	Single Deck 6:5,
•	European No Hole Card,
•	Atlantic City style,
•	player-friendly table,
•	casino-friendly table.
Nie używaj nazw sugerujących autentyczne zasady konkretnego kasyna, jeśli nie masz zweryfikowanego źródła.
8.4. Własne presety
Użytkownik ma móc:
•	utworzyć preset z bieżącej konfiguracji,
•	nadać nazwę,
•	dodać opis,
•	dodać tagi,
•	zduplikować preset,
•	edytować preset,
•	usunąć własny preset,
•	przywrócić preset wbudowany,
•	importować preset,
•	eksportować preset.
Presety wbudowane powinny być tylko do odczytu.
________________________________________
9. Etap 6: rozbudowane liczenie kart
9.1. Systemy liczenia
Obsługuj co najmniej:
•	Hi-Lo,
•	KO,
•	Hi-Opt I,
•	Hi-Opt II,
•	Omega II.
Każdy system powinien definiować:
•	wartości rang,
•	czy jest balanced,
•	sposób obliczania true count,
•	domyślny initial running count,
•	obsługiwane indeksy.
9.2. True count
Obsługuj sposoby zaokrąglania:
•	floor,
•	truncate,
•	nearest,
•	none.
Dodaj konfigurację minimalnej liczby pozostałych talii używanej w mianowniku.
9.3. Wonging
Obsługuj:
•	wejście do gry od określonego true count,
•	opuszczenie gry poniżej określonego true count,
•	obserwowanie stołu bez stawiania,
•	ponowne wejście po wzroście count,
•	pozostawanie przy stole do końca shoe,
•	reset zachowania po shuffle.
Przykład:
counting:
  enabled: true
  system: hi_lo
  true_count_rounding: floor

table_entry:
  mode: wonging
  enter_at_true_count: 1
  leave_below_true_count: 0
  reentry_allowed: true
9.4. Bet spread
Panel i config mają umożliwiać tworzenie dowolnego spreadu.
Przykład:
betting_strategy:
  type: true_count_spread
  spread:
    - min_true_count: null
      max_true_count: 0
      bet: 10
    - min_true_count: 1
      max_true_count: 1
      bet: 20
    - min_true_count: 2
      max_true_count: 2
      bet: 40
    - min_true_count: 3
      max_true_count: 3
      bet: 80
    - min_true_count: 4
      max_true_count: null
      bet: 120
Waliduj:
•	brak luk,
•	brak nakładających się zakresów,
•	dodatnie stawki,
•	zgodność z limitami stołu.
9.5. Statystyki count
Raportuj:
•	średni running count,
•	średni true count,
•	rozkład true count,
•	liczbę rund dla każdego przedziału count,
•	wynik netto w każdym przedziale,
•	house edge w każdym przedziale,
•	średnią stawkę w każdym przedziale,
•	liczbę wejść i wyjść ze stołu,
•	odsetek rund przesiedzianych bez zakładu.
________________________________________
10. Etap 7: deviations od basic strategy
10.1. Cel
Dodaj strategię basic strategy rozszerzoną o indeksy zależne od count.
10.2. Model deviation
Przykład:
playing_strategy:
  type: basic_strategy_with_deviations
  deviations:
    - id: hard-16-vs-10-stand
      hand_type: hard
      player_total: 16
      dealer_upcard: 10
      condition:
        operator: greater_or_equal
        true_count: 0
      action: stand
      priority: 100
Deviation powinien móc uwzględniać:
•	typ ręki,
•	sumę gracza,
•	konkretną parę,
•	soft total,
•	kartę dealera,
•	minimalny true count,
•	maksymalny true count,
•	możliwość surrender,
•	możliwość double,
•	możliwość splitu,
•	to, czy ręka pochodzi ze splitu.
10.3. Priorytety
Jeśli pasuje kilka deviations:
1.	wybierz deviation o najwyższym priorytecie,
2.	przy tym samym priorytecie zgłoś błąd konfiguracji,
3.	nie wybieraj przypadkowo.
10.4. Wbudowane zestawy
Dodaj:
•	Illustrious 18,
•	Fab 4 surrender.
Zestawy powinny być jawnie opisane i wersjonowane.
10.5. Panel deviations
Panel ma umożliwiać:
•	wybór gotowego zestawu,
•	włączenie i wyłączenie konkretnych deviations,
•	dodanie własnego deviation,
•	edycję warunku,
•	ustawienie akcji,
•	ustawienie priorytetu,
•	walidację konfliktów,
•	import i eksport zestawu,
•	podgląd tabeli deviations.
Dodaj licznik pokazujący:
•	ile razy każde deviation zostało użyte,
•	jaki wynik finansowy przyniosły ręce, w których go użyto,
•	różnicę względem zwykłej basic strategy, jeśli dostępna.
________________________________________
11. Etap 8: dodatkowe systemy obstawiania
11.1. Bankroll percentage
betting_strategy:
  type: bankroll_percentage
  percentage: 0.01
  minimum_bet: 10
  maximum_bet: 500
  rounding:
    mode: floor
    unit: 5
11.2. Kelly criterion
Obsługuj:
•	full Kelly,
•	half Kelly,
•	quarter Kelly,
•	dowolny fractional Kelly.
betting_strategy:
  type: fractional_kelly
  fraction: 0.5
  edge_source: true_count_estimate
  minimum_bet: 0
  maximum_bet: 1000
Nie pozwalaj Kelly obstawiać dodatniej kwoty przy zerowej lub ujemnej przewadze, chyba że użytkownik jawnie ustawi minimalny zakład stołu i strategia ma grać mimo braku przewagi.
11.3. Stop-loss i stop-win
Dodaj opcjonalne warunki sesji:
session_limits:
  stop_loss: 1000
  stop_win: 1000
  max_rounds: 100000
  max_drawdown: 1500
Raportuj powód zakończenia.
11.4. Reset systemu
Systemy progresywne powinny obsługiwać reset:
•	po shuffle,
•	po określonej liczbie rund,
•	po osiągnięciu stop-win,
•	po osiągnięciu określonego poziomu,
•	po ręcznym resecie.
11.5. Builder systemów
Panel ma umożliwiać konfigurowanie systemów bez edycji YAML.
Dla każdej strategii wyświetlaj tylko właściwe pola.
Przykład:
•	flat: kwota,
•	Martingale: baza, mnożnik, limit, zachowanie po push,
•	Fibonacci: jednostka, cofnięcie po wygranej,
•	count spread: edytowalna tabela progów,
•	bankroll percentage: procent i sposób zaokrąglania,
•	Kelly: ułamek Kelly i źródło przewagi.
________________________________________
12. Backend API
12.1. Technologia
Użyj FastAPI.
Wymagania:
•	Pydantic,
•	OpenAPI,
•	wersjonowanie /api/v1,
•	czytelne błędy walidacji,
•	health check,
•	generowanie dokumentacji Swagger,
•	osobna warstwa usług,
•	brak logiki domenowej w kontrolerach.
12.2. Główne endpointy
Konfiguracje
POST   /api/v1/configurations/validate
POST   /api/v1/configurations/import
POST   /api/v1/configurations/export
GET    /api/v1/configurations
POST   /api/v1/configurations
GET    /api/v1/configurations/{id}
PUT    /api/v1/configurations/{id}
DELETE /api/v1/configurations/{id}
POST   /api/v1/configurations/{id}/duplicate
Presety
GET    /api/v1/presets
GET    /api/v1/presets/{id}
POST   /api/v1/presets
PUT    /api/v1/presets/{id}
DELETE /api/v1/presets/{id}
POST   /api/v1/presets/import
GET    /api/v1/presets/{id}/export
Symulacje
POST   /api/v1/simulations
GET    /api/v1/simulations
GET    /api/v1/simulations/{id}
GET    /api/v1/simulations/{id}/status
GET    /api/v1/simulations/{id}/results
GET    /api/v1/simulations/{id}/trace
POST   /api/v1/simulations/{id}/cancel
DELETE /api/v1/simulations/{id}
Batch
POST   /api/v1/batches
GET    /api/v1/batches
GET    /api/v1/batches/{id}
GET    /api/v1/batches/{id}/results
POST   /api/v1/batches/{id}/cancel
Porównania
POST   /api/v1/comparisons
GET    /api/v1/comparisons
GET    /api/v1/comparisons/{id}
GET    /api/v1/comparisons/{id}/results
POST   /api/v1/comparisons/{id}/cancel
Eksport
GET /api/v1/reports/{id}/json
GET /api/v1/reports/{id}/csv
GET /api/v1/reports/{id}/pdf
12.3. Zadania długotrwałe
Symulacji wielomilionowych nie wykonuj bezpośrednio w request handlerze.
Zastosuj kolejkę zadań.
Dopuszczalne rozwiązania:
•	Celery i Redis,
•	RQ i Redis,
•	arq,
•	własny prosty worker dla pierwszej wersji.
Preferuj rozwiązanie dobrze pasujące do skali projektu.
Zadanie powinno mieć status:
queued
running
completed
failed
cancelled
Dodatkowo:
•	postęp procentowy,
•	liczba wykonanych rund,
•	aktualna prędkość,
•	czas rozpoczęcia,
•	czas zakończenia,
•	komunikat błędu.
12.4. Aktualizacje postępu
Frontend powinien pobierać postęp przez:
•	WebSocket,
•	Server-Sent Events,
•	ewentualnie polling jako fallback.
Preferuj SSE, jeśli komunikacja jest głównie jednokierunkowa.
________________________________________
13. Przechowywanie danych
13.1. Wymagania
Przechowuj:
•	zapisane konfiguracje,
•	własne presety,
•	historię uruchomień,
•	metadane zadań,
•	podsumowania wyników,
•	ścieżki do plików eksportu.
Nie przechowuj pełnego trace każdej rundy wielomilionowej symulacji.
Trace powinien być zapisywany tylko:
•	w trybie trace,
•	dla wybranych rund,
•	dla rund zawierających określone zdarzenia,
•	przy wykrytym błędzie audytu.
13.2. Baza danych
Dla wersji lokalnej można użyć SQLite.
Architektura repository ma umożliwiać późniejszą zmianę na PostgreSQL.
Nie wiąż całej aplikacji bezpośrednio z SQLite.
________________________________________
14. Panel webowy
14.1. Główny cel
Panel ma umożliwiać pełną konfigurację symulatora bez ręcznego edytowania YAML.
Użytkownik powinien móc wyklikać praktycznie każdą opcję dostępną w configu.
Nie twórz uproszczonego formularza obejmującego tylko najpopularniejsze pola.
Każde wspierane pole konfiguracji powinno być dostępne w panelu albo jawnie oznaczone jako zaawansowane.
14.2. Technologia frontendu
Użyj:
•	React z TypeScript lub Vue 3 z TypeScript,
•	nowoczesnego routera,
•	biblioteki do zapytań i cache,
•	biblioteki formularzy,
•	walidacji schematów,
•	biblioteki wykresów,
•	komponentów dostępnych klawiaturą.
Preferowany zestaw dla React:
•	React,
•	TypeScript,
•	Vite,
•	React Router,
•	TanStack Query,
•	React Hook Form,
•	Zod,
•	Zustand lub Context dla lekkiego stanu,
•	Recharts, ECharts lub Apache ECharts,
•	Tailwind CSS lub dobrze dobrany system komponentów.
Nie używaj jednocześnie kilku konkurencyjnych bibliotek UI bez powodu.
14.3. Styl wizualny
Panel ma wyglądać jak profesjonalne narzędzie analityczne, a nie formularz urzędu skarbowego z gradientem.
Założenia:
•	ciemny i jasny motyw,
•	czytelna typografia,
•	spójny system odstępów,
•	profesjonalne tabele,
•	dobre wykresy,
•	responsywność,
•	przejrzyste stany loading, empty i error,
•	subtelne animacje,
•	brak zbędnych efektów,
•	dostępność,
•	czytelność na monitorach desktopowych.
Główny nacisk połóż na desktop, ale panel powinien być używalny również na tablecie.
14.4. Nawigacja
Główne sekcje:
Dashboard
New Simulation
Configurations
Presets
Comparisons
Batch Simulations
History
Audit
Trace Viewer
Documentation
Settings
14.5. Dashboard
Dashboard powinien pokazywać:
•	ostatnie symulacje,
•	ostatnie porównania,
•	ostatnie batch simulations,
•	liczbę zapisanych konfiguracji,
•	skróty do popularnych presetów,
•	ostatnie wyniki,
•	średni czas wykonania,
•	aktualnie działające zadania,
•	status workerów.
Dodaj szybkie akcje:
•	nowa symulacja,
•	import configu,
•	porównaj konfiguracje,
•	uruchom batch,
•	otwórz ostatni raport.
________________________________________
15. Kreator konfiguracji symulacji
15.1. Układ
Podziel konfigurację na logiczne kroki lub sekcje:
1.	General,
2.	Table Rules,
3.	Dealer Rules,
4.	Player Actions,
5.	Splits,
6.	Insurance and Even Money,
7.	Shoe and Shuffle,
8.	Counting,
9.	Basic Strategy,
10.	Deviations,
11.	Betting,
12.	Bankroll and Session Limits,
13.	Simulation Execution,
14.	Output and Trace,
15.	Review.
Panel może używać:
•	bocznej nawigacji,
•	zakładek,
•	kroków kreatora,
•	połączenia sekcji i wyszukiwarki ustawień.
15.2. Ogólne ustawienia
Pola:
•	nazwa konfiguracji,
•	opis,
•	tagi,
•	liczba rund,
•	seed,
•	liczba workerów,
•	tryb zwykły lub batch,
•	profil bazowy.
15.3. Table Rules
Pola:
•	liczba talii,
•	blackjack payout,
•	własny payout,
•	minimum stołu,
•	maksimum stołu,
•	waluta lub jednostki,
•	europejski lub amerykański model rozdania,
•	sposób utraty zakładów w ENHC.
15.4. Dealer Rules
Pola:
•	S17/H17,
•	peek,
•	karty wywołujące peek,
•	kolejność hole card,
•	zasady blackjacka dealera.
15.5. Double
Pola:
•	double włączony,
•	tylko na dwóch kartach,
•	dowolne dwie karty,
•	tylko wybrane sumy,
•	lista dozwolonych sum,
•	double after split,
•	double po splicie asów,
•	double przy ograniczonym bankrollu.
15.6. Surrender
Pola:
•	none,
•	early,
•	late,
•	surrender po splicie,
•	wyjątki zależne od hole card.
15.7. Splits
Pola:
•	split włączony,
•	identyczna ranga lub ta sama wartość,
•	maksymalna liczba rąk,
•	maksymalna głębokość,
•	resplit,
•	resplit asów,
•	hit split aces,
•	liczba kart po splicie asów,
•	double after split,
•	double split aces,
•	blackjack po splicie,
•	zasady insufficient bankroll.
15.8. Insurance
Pola:
•	insurance oferowane,
•	payout,
•	maksymalna część zakładu,
•	strategia never,
•	strategia always,
•	only with blackjack,
•	count-based,
•	własny próg true count,
•	even money.
15.9. Shoe
Pola:
•	liczba talii,
•	penetracja,
•	cut card,
•	shuffle po każdej rundzie,
•	shuffle przy określonej liczbie kart,
•	seed,
•	sposób generowania seedów workerów.
15.10. Basic Strategy
Pola:
•	automatyczny dobór profilu,
•	ręczny profil,
•	nearest supported table,
•	zachowanie przy braku tabeli,
•	podgląd wybranej tabeli,
•	podgląd różnic między tabelami.
15.11. Counting
Pola:
•	counting enabled,
•	system,
•	initial running count,
•	true count rounding,
•	wonging,
•	enter threshold,
•	leave threshold,
•	reentry,
•	bet spread.
15.12. Deviations
Pola:
•	zestaw wbudowany,
•	lista aktywnych deviations,
•	własne deviations,
•	priorytety,
•	warunki,
•	akcje,
•	walidacja konfliktów.
15.13. Betting
Dynamiczny formularz zależny od wybranej strategii.
Obsługuj wszystkie strategie dostępne w silniku.
Dodatkowo pokaż wizualizację kolejnych stawek dla przykładowej serii:
L, L, L, W, P, L
Pozwoli to użytkownikowi zobaczyć, jak zachowuje się system, zanim puści milion rund ku chwale wariancji.
15.14. Bankroll
Pola:
•	bankroll początkowy,
•	stop on ruin,
•	allow credit,
•	stop-loss,
•	stop-win,
•	maksymalny drawdown,
•	maksymalna liczba rund,
•	sposób zaokrąglania stawek.
15.15. Output
Pola:
•	zapisz JSON,
•	zapisz CSV,
•	zapisz PDF,
•	historia bankrolla,
•	częstotliwość próbkowania,
•	pełny trace,
•	trace tylko dla splitów,
•	trace tylko dla double,
•	trace tylko dla błędów,
•	liczba przechowywanych rund trace.
________________________________________
16. Walidacja formularza
Walidacja powinna działać na dwóch poziomach:
1.	lokalnie w przeglądarce,
2.	po stronie backendu.
Przykłady zależności:
•	ENHC wyklucza amerykański peek,
•	count-based insurance wymaga counting,
•	count spread wymaga counting,
•	deviations count-based wymagają counting,
•	minimum stołu nie może być większe niż maksimum,
•	max hands musi być dodatnie,
•	resplit aces wymaga split aces,
•	double after split wymaga włączonego double,
•	stop-loss nie może przekraczać bankrolla bez ostrzeżenia,
•	batch wymaga liczby sesji większej od zera.
Błędy pokazuj bezpośrednio przy polach oraz w podsumowaniu.
Dodaj panel ostrzeżeń:
•	konfiguracja poprawna,
•	konfiguracja poprawna z ostrzeżeniami,
•	konfiguracja niepoprawna.
________________________________________
17. Import konfiguracji
17.1. Formaty
Obsługuj import:
•	YAML,
•	JSON.
17.2. Metody importu
Użytkownik powinien móc:
•	przeciągnąć plik,
•	wybrać plik,
•	wkleić tekst configu,
•	wkleić JSON,
•	otworzyć config z historii.
17.3. Podgląd przed importem
Przed zastosowaniem pokaż:
•	wersję schematu,
•	nazwę,
•	wykryte pola,
•	nieznane pola,
•	brakujące pola,
•	wartości domyślne,
•	błędy,
•	ostrzeżenia,
•	różnice względem bieżącej konfiguracji.
17.4. Migracje schematu
Każdy config powinien zawierać:
schema_version: "1.0"
Przy starszym schemacie:
•	wykonaj migrację,
•	pokaż zmiany,
•	pozwól pobrać zaktualizowany config.
Nie ignoruj nieznanych pól.
________________________________________
18. Eksport konfiguracji
Użytkownik powinien móc eksportować config jako:
•	YAML,
•	JSON.
Opcje:
•	pełny config,
•	config tylko ze zmienionymi wartościami,
•	config z komentarzami,
•	preset,
•	kopia do schowka,
•	pobranie pliku.
Dodaj czytelne nazwy plików:
standard-6d-s17-flat-10-2026-07-14.yaml
________________________________________
19. Wyniki symulacji
19.1. Widok podsumowania
Pokaż karty:
•	wynik netto,
•	końcowy bankroll,
•	house edge,
•	RTP,
•	win rate,
•	loss rate,
•	push rate,
•	blackjack rate,
•	maximum drawdown,
•	standard deviation,
•	confidence interval,
•	czas wykonania,
•	rounds per second.
19.2. Zakładki wyników
Overview
Bankroll
Outcomes
Betting
Rules
Counting
Risk
Hands
Trace
Raw Data
19.3. Wykres bankrolla
Dodaj:
•	zoom,
•	przesuwanie,
•	tooltip,
•	wybór zakresu,
•	logarytmiczną skalę opcjonalnie,
•	markery shuffle,
•	markery stop-loss,
•	markery stop-win,
•	markery ruin,
•	nakładkę moving average.
19.4. Outcomes
Wykresy:
•	win/loss/push,
•	blackjack,
•	surrender,
•	double,
•	split,
•	dealer bust,
•	player bust.
19.5. Betting
Pokaż:
•	rozkład stawek,
•	średnią stawkę,
•	maksymalną stawkę,
•	stawki w czasie,
•	ekspozycję po splitach i double,
•	wynik dla poszczególnych poziomów progresji,
•	wynik dla poszczególnych true count.
19.6. Risk
Pokaż:
•	drawdown,
•	longest losing streak,
•	rozkład losing streaków,
•	prawdopodobieństwo ruin z batch,
•	percentyle końcowego bankrolla,
•	Value at Risk, jeśli zostanie poprawnie zdefiniowane i udokumentowane.
19.7. Rules summary
Pokaż pełne zasady użyte w symulacji.
Nie pokazuj wyłącznie nazwy presetu.
Wynik musi być samowystarczalny i pozwalać odtworzyć symulację.
Dodaj przycisk:
Run again with this configuration
________________________________________
20. Eksport wyników
20.1. JSON
Pełny raport maszynowy.
Powinien zawierać:
•	wersję schematu,
•	wersję aplikacji,
•	konfigurację,
•	seed,
•	metadane wykonania,
•	podsumowanie,
•	statystyki,
•	dane wykresów,
•	ostrzeżenia audytu.
20.2. CSV
Obsługuj osobne pliki:
•	summary.csv,
•	bankroll_history.csv,
•	outcomes.csv,
•	betting_distribution.csv,
•	count_distribution.csv,
•	batch_sessions.csv,
•	comparison.csv.
Można także generować ZIP z kompletem plików.
20.3. PDF
PDF powinien wyglądać jak raport analityczny.
Powinien zawierać:
•	tytuł,
•	datę,
•	konfigurację,
•	główne metryki,
•	wykresy,
•	analizę ryzyka,
•	ostrzeżenia,
•	informacje o seedzie i wersji aplikacji.
Nie generuj PDF jako zrzutu całego ekranu.
20.4. Obraz wykresu
Dodaj eksport wykresów do:
•	PNG,
•	SVG, jeśli biblioteka pozwala.
________________________________________
21. Historia
Panel historii powinien przechowywać:
•	symulacje,
•	batch,
•	porównania,
•	audyty.
Filtry:
•	data,
•	typ,
•	status,
•	nazwa configu,
•	tag,
•	preset,
•	system obstawiania,
•	liczba rund,
•	wynik dodatni lub ujemny.
Akcje:
•	otwórz,
•	uruchom ponownie,
•	duplikuj config,
•	porównaj,
•	eksportuj,
•	usuń.
________________________________________
22. UX i dostępność
Wymagania:
•	pełna obsługa klawiaturą,
•	widoczne focus states,
•	prawidłowe etykiety formularzy,
•	odpowiedni kontrast,
•	tooltipy dla skomplikowanych terminów,
•	brak polegania tylko na kolorze,
•	komunikaty błędów czytelne dla użytkownika,
•	potwierdzenie przed usunięciem,
•	autosave wersji roboczej konfiguracji.
Dodaj wyszukiwarkę ustawień.
Przykład:
Użytkownik wpisuje:
split aces
Panel pokazuje wszystkie ustawienia związane ze splitowanymi asami.
________________________________________
23. Responsywność i wydajność frontendu
Nie renderuj tysięcy punktów wykresu bez agregacji.
Dla dużej historii bankrolla:
•	downsampling,
•	agregacja,
•	lazy loading,
•	wirtualizacja tabel.
Duże tabele powinny wspierać:
•	paginację,
•	sortowanie,
•	filtrowanie,
•	wybór kolumn,
•	wirtualizację.
________________________________________
24. Obsługa błędów w panelu
Każdy request powinien mieć:
•	loading state,
•	error state,
•	retry,
•	czytelny komunikat.
Dla błędów symulacji pokaż:
•	typ błędu,
•	komunikat,
•	etap,
•	numer rundy, jeśli dostępny,
•	link do trace,
•	możliwość pobrania diagnostyki.
Nie pokazuj użytkownikowi surowego tracebacka jako głównego komunikatu.
________________________________________
25. Testy backendu
Dodaj:
•	testy modeli Pydantic,
•	testy walidacji configów,
•	testy endpointów,
•	testy autoryzacji, jeśli zostanie później dodana,
•	testy statusów zadań,
•	testy anulowania,
•	testy importu i eksportu,
•	testy migracji schematu,
•	testy generowania raportów.
Użyj testowego silnika lub krótkich deterministycznych symulacji.
Nie uruchamiaj milionów rund w każdym teście endpointu.
________________________________________
26. Testy frontendu
Dodaj:
•	testy komponentów formularza,
•	testy zależności między polami,
•	testy importu configu,
•	testy eksportu,
•	testy kreatora,
•	testy tabel,
•	testy stanów loading/error/empty,
•	testy dostępności,
•	testy głównych przepływów użytkownika.
Dodaj E2E dla:
1.	utworzenia konfiguracji,
2.	uruchomienia symulacji,
3.	sprawdzenia postępu,
4.	otwarcia wyników,
5.	eksportu JSON,
6.	importu configu,
7.	porównania dwóch konfiguracji,
8.	uruchomienia batch.
Można użyć Playwright.
________________________________________
27. Dokumentacja użytkownika
Dodaj dokumentację:
Getting Started
Table Rules
Basic Strategy
Betting Systems
Card Counting
Deviations
Batch Simulations
Comparisons
Import and Export
Understanding Results
House Edge and RTP
Risk and Drawdown
FAQ
Każde skomplikowane pole w panelu powinno mieć link do odpowiedniej sekcji dokumentacji.
________________________________________
28. Bezpieczeństwo
Mimo że projekt może działać lokalnie:
•	waliduj importowane pliki,
•	ogranicz rozmiar uploadu,
•	nie wykonuj kodu z configów,
•	nie używaj eval,
•	nie pozwalaj na dowolne ścieżki eksportu,
•	zabezpiecz nazwy plików,
•	nie ufaj nazwom przesyłanych plików,
•	nie zwracaj wewnętrznych ścieżek systemowych,
•	ogranicz liczbę jednoczesnych ciężkich zadań,
•	dodaj limit maksymalnej liczby rund konfigurowalny przez administratora.
________________________________________
29. Docker
Przygotuj środowisko uruchomieniowe:
frontend
backend
worker
redis
database
Dla wersji lokalnej dopuszczalne jest SQLite bez osobnego kontenera bazy.
Dodaj:
docker compose up
Po uruchomieniu użytkownik powinien otrzymać działający panel.
________________________________________
30. Kolejność implementacji
Wykonuj etapy w tej kolejności:
Task 101: analiza istniejącego MVP
•	przeanalizuj kod,
•	zidentyfikuj brakujące interfejsy,
•	sprawdź testy,
•	przygotuj dokument różnic między stanem obecnym a wymaganym.
Nie zmieniaj jeszcze dużej części kodu.
Task 102: typed trace events
•	model zdarzeń,
•	kolektor,
•	JSON,
•	testy.
Task 103: trace CLI
•	czytelny raport,
•	filtrowanie,
•	testy.
Task 104: audit engine
•	kontrole,
•	raport,
•	strict mode,
•	testy.
Task 105: configuration comparison
•	usługa porównania,
•	raport CLI,
•	eksport.
Task 106: batch simulations
•	wiele sesji,
•	agregacja,
•	risk of ruin,
•	percentyle.
Task 107: presets
•	model,
•	presety wbudowane,
•	import i eksport.
Task 108: advanced counting
•	dodatkowe systemy,
•	true count,
•	wonging,
•	statystyki.
Task 109: strategy deviations
•	model,
•	priorytety,
•	Illustrious 18,
•	Fab 4,
•	testy.
Task 110: advanced betting
•	bankroll percentage,
•	Kelly,
•	session limits,
•	reset rules.
Task 111: backend foundation
•	FastAPI,
•	modele,
•	konfiguracja,
•	health,
•	OpenAPI.
Task 112: persistence
•	baza,
•	repositories,
•	konfiguracje,
•	historia.
Task 113: task queue
•	worker,
•	status,
•	postęp,
•	anulowanie.
Task 114: API simulations
•	uruchomienie,
•	status,
•	wyniki,
•	trace.
Task 115: API comparisons and batches
•	endpointy,
•	eksport,
•	status.
Task 116: frontend foundation
•	routing,
•	layout,
•	motyw,
•	system komponentów.
Task 117: configuration builder
•	wszystkie sekcje,
•	dynamiczne pola,
•	walidacja.
Task 118: config import and export
•	YAML,
•	JSON,
•	preview,
•	migracje.
Task 119: simulation execution UI
•	progress,
•	cancel,
•	status,
•	błędy.
Task 120: results dashboard
•	metryki,
•	wykresy,
•	tabele,
•	trace.
Task 121: comparison UI
•	wybór configów,
•	tabele,
•	wykresy,
•	eksport.
Task 122: batch UI
•	konfiguracja,
•	postęp,
•	histogramy,
•	percentyle.
Task 123: presets and history UI
•	zarządzanie,
•	filtry,
•	duplikowanie,
•	ponowne uruchamianie.
Task 124: PDF and export
•	JSON,
•	CSV,
•	ZIP,
•	PDF,
•	obrazy wykresów.
Task 125: E2E and accessibility
•	Playwright,
•	dostępność,
•	główne przepływy.
Task 126: Docker and deployment
•	compose,
•	dokumentacja,
•	konfiguracja środowiska.
Task 127: final validation
•	pełne testy,
•	audit,
•	wydajność,
•	dokumentacja,
•	release.
________________________________________
31. Kryteria ukończenia rozbudowanej wersji
Projekt można uznać za ukończony, gdy:
•	działa szczegółowy trace,
•	działa audit,
•	można porównywać konfiguracje,
•	działa batch simulations,
•	działa observed risk of ruin,
•	istnieją gotowe presety,
•	działa kilka systemów liczenia kart,
•	działa wonging,
•	działają deviations,
•	istnieją rozbudowane strategie obstawiania,
•	backend wykonuje zadania asynchronicznie,
•	panel pozwala skonfigurować wszystkie wspierane opcje,
•	można importować YAML i JSON,
•	można eksportować YAML i JSON,
•	można eksportować wyniki do JSON, CSV i PDF,
•	można zapisać i zarządzać presetami,
•	istnieje historia uruchomień,
•	panel pokazuje postęp,
•	zadania można anulować,
•	panel ma jasny i ciemny motyw,
•	panel jest dostępny i responsywny,
•	istnieją testy backendu, frontendu i E2E,
•	działa Docker Compose,
•	dokumentacja opisuje wszystkie funkcje,
•	istnieją przykładowe konfiguracje,
•	cały pipeline CI przechodzi.
________________________________________
32. Ważne ograniczenia
Nie wolno:
•	przenosić logiki blackjacka do frontendu,
•	tworzyć dwóch różnych implementacji zasad,
•	wykonywać wielomilionowej symulacji bezpośrednio w request handlerze,
•	przechowywać pełnego trace wszystkich rund bez limitu,
•	ignorować nieznanych pól configu,
•	automatycznie wybierać niewłaściwej basic strategy,
•	używać floatów do księgowania pieniędzy,
•	wykonywać kodu z importowanych configów,
•	ukrywać błędów walidacji,
•	tworzyć formularza obejmującego tylko część istniejących opcji.
________________________________________
33. Pierwsze polecenie wykonawcze
Rozpocznij od Task 101.
W pierwszym kroku:
1.	przeczytaj całe repozytorium,
2.	przeanalizuj strukturę silnika,
3.	sprawdź modele konfiguracji,
4.	sprawdź publiczne interfejsy,
5.	sprawdź testy,
6.	sprawdź aktualne raporty i CLI,
7.	określ, które wymagania są już spełnione,
8.	określ, które wymagania wymagają zmian,
9.	wykryj potencjalne problemy architektoniczne,
10.	utwórz dokument docs/post-mvp-gap-analysis.md,
11.	utwórz pliki tasków 102–127,
12.	nie implementuj jeszcze panelu ani nowych funkcji silnika.
Dokument analizy ma zawierać:
•	aktualną architekturę,
•	mapę modułów,
•	listę dostępnych funkcji,
•	listę brakujących funkcji,
•	problemy techniczne,
•	problemy testowe,
•	ryzyka migracji,
•	rekomendowaną kolejność zmian,
•	elementy, które można zachować bez zmian,
•	elementy wymagające refaktoryzacji.
Po zakończeniu pokaż:
•	podsumowanie analizy,
•	listę utworzonych plików,
•	najważniejsze ryzyka,
•	proponowany pierwszy commit,
•	wskazanie Task 102 jako następnego etapu.
Nie przechodź automatycznie do Task 102.

