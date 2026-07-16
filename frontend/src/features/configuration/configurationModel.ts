import { parse as parseYaml, stringify as stringifyYaml } from "yaml";

export const CONFIG_SCHEMA_VERSION = 1;

export const BETTING_STRATEGIES = [
  "flat",
  "martingale",
  "paroli",
  "fibonacci",
  "dalembert",
  "true_count_spread",
  "bankroll_percentage",
  "kelly"
] as const;

export type BettingStrategyType = (typeof BETTING_STRATEGIES)[number];

export interface ConfigurationFormState {
  simulation: {
    rounds: number;
    seed: number;
    workers: number;
  };
  bankroll: {
    initial: number;
    stopLoss: string;
    stopWin: string;
    tableMinimum: string;
    tableMaximum: string;
  };
  rules: {
    decks: number;
    penetration: number;
    blackjackPayout: number;
    shuffleAfterEachRound: boolean;
    dealerHitsSoft17: boolean;
    dealerPeeksForBlackjack: boolean;
    doubleAllowed: boolean;
    doubleAfterSplit: boolean;
    doubleAllowedTotals: string;
    surrenderType: "none" | "early" | "late";
    splitAllowed: boolean;
    splitMaxHands: number;
    splitRequireSameRank: boolean;
    resplitAces: boolean;
    hitSplitAces: boolean;
    doubleAfterSplitAces: boolean;
    splitBlackjackCounts: boolean;
    insuranceOffered: boolean;
    insurancePayout: number;
    insuranceMaxBetFraction: number;
    holeCardMode: "american" | "european_no_hole_card";
    enhcLossRule: "all_bets" | "original_bets_only";
  };
  strategy: {
    playingStrategy: "basic_strategy";
    insuranceStrategy: "never" | "always" | "even_money";
  };
  counting: {
    enabled: boolean;
    system: "hi_lo" | "hi_opt_i" | "hi_opt_ii" | "omega_ii";
    trueCountRounding: "none" | "floor" | "truncate" | "nearest";
    minRemainingDecks: number;
    initialRunningCount: string;
    wongingEnterAtTrueCount: string;
  };
  betting: {
    type: BettingStrategyType;
    amount: number;
    maxWins: number;
    spread: string;
    percentage: number;
    edge: number;
    variance: number;
    fraction: number;
    roundingMode: "none" | "floor" | "ceiling" | "nearest";
    roundingIncrement: number;
  };
  output: {
    console: boolean;
    jsonFile: string;
    csvFile: string;
  };
  deviations: {
    enabled: boolean;
    useIllustrious18: boolean;
    useFab4: boolean;
    customEnabled: boolean;
    customId: string;
    customHandType: "hard" | "soft" | "pair";
    customPlayerTotal: string;
    customDealerUpcard: string;
    customTrueCountMin: string;
    customTrueCountMax: string;
    customAction: "hit" | "stand" | "double" | "split" | "surrender";
    customPriority: number;
  };
  batch: {
    sessions: number;
    roundsPerSession: number;
    baseSeed: number;
  };
}

export interface ValidationIssue {
  field: string;
  message: string;
}

export interface ImportPreview {
  state: ConfigurationFormState | null;
  parsed: Record<string, unknown> | null;
  normalized: Record<string, unknown> | null;
  unknownFields: string[];
  migrationMessages: string[];
  errors: string[];
}

export interface ConfigDiffEntry {
  path: string;
  before: unknown;
  after: unknown;
}

export const defaultConfigurationState: ConfigurationFormState = {
  simulation: {
    rounds: 10000,
    seed: 123,
    workers: 1
  },
  bankroll: {
    initial: 1000,
    stopLoss: "",
    stopWin: "",
    tableMinimum: "",
    tableMaximum: ""
  },
  rules: {
    decks: 6,
    penetration: 0.75,
    blackjackPayout: 1.5,
    shuffleAfterEachRound: false,
    dealerHitsSoft17: false,
    dealerPeeksForBlackjack: true,
    doubleAllowed: true,
    doubleAfterSplit: true,
    doubleAllowedTotals: "9,10,11",
    surrenderType: "late",
    splitAllowed: true,
    splitMaxHands: 4,
    splitRequireSameRank: true,
    resplitAces: false,
    hitSplitAces: false,
    doubleAfterSplitAces: false,
    splitBlackjackCounts: false,
    insuranceOffered: true,
    insurancePayout: 2,
    insuranceMaxBetFraction: 0.5,
    holeCardMode: "american",
    enhcLossRule: "all_bets"
  },
  strategy: {
    playingStrategy: "basic_strategy",
    insuranceStrategy: "never"
  },
  counting: {
    enabled: false,
    system: "hi_lo",
    trueCountRounding: "none",
    minRemainingDecks: 0,
    initialRunningCount: "",
    wongingEnterAtTrueCount: ""
  },
  betting: {
    type: "flat",
    amount: 10,
    maxWins: 3,
    spread: "0: 1\n2: 4\n5: 8",
    percentage: 0.02,
    edge: 0.02,
    variance: 1,
    fraction: 0.5,
    roundingMode: "none",
    roundingIncrement: 1
  },
  output: {
    console: true,
    jsonFile: "",
    csvFile: ""
  },
  deviations: {
    enabled: false,
    useIllustrious18: false,
    useFab4: false,
    customEnabled: false,
    customId: "stand-12-vs-4",
    customHandType: "hard",
    customPlayerTotal: "12",
    customDealerUpcard: "4",
    customTrueCountMin: "1",
    customTrueCountMax: "",
    customAction: "stand",
    customPriority: 200
  },
  batch: {
    sessions: 20,
    roundsPerSession: 1000,
    baseSeed: 1000
  }
};

export function importConfigurationText(text: string): ImportPreview {
  const errors: string[] = [];
  let parsed: unknown;
  try {
    parsed = parseConfigText(text);
  } catch (error) {
    return {
      state: null,
      parsed: null,
      normalized: null,
      unknownFields: [],
      migrationMessages: [],
      errors: [error instanceof Error ? error.message : "Import failed."]
    };
  }

  if (!isRecord(parsed)) {
    return {
      state: null,
      parsed: null,
      normalized: null,
      unknownFields: [],
      migrationMessages: [],
      errors: ["Imported configuration must be an object."]
    };
  }

  let migration: { config: Record<string, unknown>; messages: string[] };
  try {
    migration = migrateConfigurationObject(parsed);
  } catch (error) {
    return {
      state: null,
      parsed,
      normalized: null,
      unknownFields: [],
      migrationMessages: [],
      errors: [error instanceof Error ? error.message : "Migration failed."]
    };
  }
  const unknownFields = collectUnknownFields(migration.config);
  if (unknownFields.length > 0) {
    errors.push("Imported configuration contains unknown fields.");
  }

  let state: ConfigurationFormState | null = null;
  if (errors.length === 0) {
    try {
      state = stateFromConfigurationObject(migration.config);
    } catch (error) {
      errors.push(error instanceof Error ? error.message : "Configuration mapping failed.");
    }
  }

  return {
    state,
    parsed,
    normalized: migration.config,
    unknownFields,
    migrationMessages: migration.messages,
    errors
  };
}

export function configurationToObject(
  state: ConfigurationFormState
): Record<string, unknown> {
  const config: Record<string, unknown> = {
    schema_version: CONFIG_SCHEMA_VERSION,
    simulation: {
      rounds: state.simulation.rounds,
      seed: state.simulation.seed,
      workers: state.simulation.workers
    },
    bankroll: compactObject({
      initial: state.bankroll.initial,
      stop_loss: optionalNumber(state.bankroll.stopLoss),
      stop_win: optionalNumber(state.bankroll.stopWin),
      table_minimum: optionalNumber(state.bankroll.tableMinimum),
      table_maximum: optionalNumber(state.bankroll.tableMaximum)
    }),
    player: {
      betting_strategy: bettingToObject(state),
      playing_strategy: {
        type: state.strategy.playingStrategy
      },
      insurance_strategy: {
        type: state.strategy.insuranceStrategy
      }
    },
    rules: {
      decks: state.rules.decks,
      penetration: state.rules.penetration,
      shuffle_after_each_round: state.rules.shuffleAfterEachRound,
      blackjack_payout: state.rules.blackjackPayout,
      dealer: {
        hits_soft_17: state.rules.dealerHitsSoft17,
        peeks_for_blackjack: state.rules.dealerPeeksForBlackjack
      },
      double: {
        allowed: state.rules.doubleAllowed,
        after_split: state.rules.doubleAfterSplit,
        allowed_totals: state.rules.doubleAllowedTotals
          .split(",")
          .map((value) => Number(value.trim()))
          .filter(Number.isFinite)
      },
      surrender: {
        type: state.rules.surrenderType
      },
      split: {
        allowed: state.rules.splitAllowed,
        max_hands: state.rules.splitMaxHands,
        require_same_rank: state.rules.splitRequireSameRank,
        resplit_aces: state.rules.resplitAces,
        hit_split_aces: state.rules.hitSplitAces,
        double_after_split_aces: state.rules.doubleAfterSplitAces,
        blackjack_after_split_counts_as_blackjack: state.rules.splitBlackjackCounts
      },
      insurance: {
        offered: state.rules.insuranceOffered,
        payout: state.rules.insurancePayout,
        max_bet_fraction: state.rules.insuranceMaxBetFraction
      },
      hole_card: {
        mode: state.rules.holeCardMode,
        enhc_loss_rule: state.rules.enhcLossRule
      }
    },
    counting: compactObject({
      enabled: state.counting.enabled,
      system: state.counting.system,
      true_count_rounding: state.counting.trueCountRounding,
      min_remaining_decks: state.counting.minRemainingDecks,
      initial_running_count: optionalNumber(state.counting.initialRunningCount),
      wonging: state.counting.wongingEnterAtTrueCount
        ? { enter_at_true_count: Number(state.counting.wongingEnterAtTrueCount) }
        : undefined
    }),
    deviations: {
      enabled: state.deviations.enabled,
      sets: [
        ...(state.deviations.useIllustrious18 ? ["illustrious_18"] : []),
        ...(state.deviations.useFab4 ? ["fab_4"] : [])
      ],
      custom:
        state.deviations.enabled && state.deviations.customEnabled
          ? [
              compactObject({
                id: state.deviations.customId,
                hand_type: state.deviations.customHandType,
                player_total: optionalNumber(state.deviations.customPlayerTotal),
                dealer_upcard: state.deviations.customDealerUpcard,
                true_count_min: optionalNumber(state.deviations.customTrueCountMin),
                true_count_max: optionalNumber(state.deviations.customTrueCountMax),
                action: state.deviations.customAction,
                priority: state.deviations.customPriority
              })
            ]
          : []
    },
    output: compactObject({
      console: state.output.console,
      json_file: optionalString(state.output.jsonFile),
      csv_file: optionalString(state.output.csvFile)
    }),
    batch: {
      sessions: state.batch.sessions,
      rounds_per_session: state.batch.roundsPerSession,
      base_seed: state.batch.baseSeed
    }
  };
  return config;
}

export function stateFromConfigurationObject(
  imported: Record<string, unknown>
): ConfigurationFormState {
  const base = structuredClone(defaultConfigurationState);
  const simulation = readRecord(imported.simulation);
  const bankroll = readRecord(imported.bankroll);
  const player = readRecord(imported.player);
  const betting = readRecord(player.betting_strategy);
  const playingStrategy = readRecord(player.playing_strategy);
  const insuranceStrategy = readRecord(player.insurance_strategy);
  const rules = readRecord(imported.rules);
  const dealer = readRecord(rules.dealer);
  const double = readRecord(rules.double);
  const surrender = readRecord(rules.surrender);
  const split = readRecord(rules.split);
  const insurance = readRecord(rules.insurance);
  const holeCard = readRecord(rules.hole_card);
  const counting = readRecord(imported.counting);
  const wonging = readRecord(counting.wonging);
  const deviations = readRecord(imported.deviations);
  const output = readRecord(imported.output);
  const batch = readRecord(imported.batch);

  base.simulation.rounds = numberValue(simulation.rounds, base.simulation.rounds);
  base.simulation.seed = numberValue(simulation.seed, base.simulation.seed);
  base.simulation.workers = numberValue(simulation.workers, base.simulation.workers);
  base.bankroll.initial = numberValue(bankroll.initial, base.bankroll.initial);
  base.bankroll.stopLoss = stringValue(bankroll.stop_loss, base.bankroll.stopLoss);
  base.bankroll.stopWin = stringValue(bankroll.stop_win, base.bankroll.stopWin);
  base.bankroll.tableMinimum = stringValue(bankroll.table_minimum, base.bankroll.tableMinimum);
  base.bankroll.tableMaximum = stringValue(bankroll.table_maximum, base.bankroll.tableMaximum);

  base.betting.type = enumValue(
    betting.type,
    BETTING_STRATEGIES,
    base.betting.type
  );
  base.betting.amount = numberValue(
    betting.amount ?? betting.base_amount,
    base.betting.amount
  );
  base.betting.maxWins = numberValue(betting.max_wins, base.betting.maxWins);
  base.betting.spread = spreadToText(readRecord(betting.spread), base.betting.spread);
  base.betting.percentage = numberValue(betting.percentage, base.betting.percentage);
  base.betting.edge = numberValue(betting.edge, base.betting.edge);
  base.betting.variance = numberValue(betting.variance, base.betting.variance);
  base.betting.fraction = numberValue(betting.fraction, base.betting.fraction);
  const rounding = readRecord(betting.rounding);
  base.betting.roundingMode = enumValue(
    rounding.mode,
    ["none", "floor", "ceiling", "nearest"] as const,
    base.betting.roundingMode
  );
  base.betting.roundingIncrement = numberValue(
    rounding.increment,
    base.betting.roundingIncrement
  );

  base.strategy.playingStrategy = enumValue(
    playingStrategy.type,
    ["basic_strategy"] as const,
    base.strategy.playingStrategy
  );
  base.strategy.insuranceStrategy = enumValue(
    insuranceStrategy.type,
    ["never", "always", "even_money"] as const,
    base.strategy.insuranceStrategy
  );

  base.rules.decks = numberValue(rules.decks, base.rules.decks);
  base.rules.penetration = numberValue(rules.penetration, base.rules.penetration);
  base.rules.shuffleAfterEachRound = booleanValue(
    rules.shuffle_after_each_round,
    base.rules.shuffleAfterEachRound
  );
  base.rules.blackjackPayout = numberValue(
    rules.blackjack_payout,
    base.rules.blackjackPayout
  );
  base.rules.dealerHitsSoft17 = booleanValue(
    dealer.hits_soft_17,
    base.rules.dealerHitsSoft17
  );
  base.rules.dealerPeeksForBlackjack = booleanValue(
    dealer.peeks_for_blackjack,
    base.rules.dealerPeeksForBlackjack
  );
  base.rules.doubleAllowed = booleanValue(double.allowed, base.rules.doubleAllowed);
  base.rules.doubleAfterSplit = booleanValue(
    double.after_split,
    base.rules.doubleAfterSplit
  );
  base.rules.doubleAllowedTotals = arrayValue(double.allowed_totals)
    .map(String)
    .join(",") || base.rules.doubleAllowedTotals;
  base.rules.surrenderType = enumValue(
    surrender.type,
    ["none", "early", "late"] as const,
    base.rules.surrenderType
  );
  base.rules.splitAllowed = booleanValue(split.allowed, base.rules.splitAllowed);
  base.rules.splitMaxHands = numberValue(split.max_hands, base.rules.splitMaxHands);
  base.rules.splitRequireSameRank = booleanValue(
    split.require_same_rank,
    base.rules.splitRequireSameRank
  );
  base.rules.resplitAces = booleanValue(split.resplit_aces, base.rules.resplitAces);
  base.rules.hitSplitAces = booleanValue(split.hit_split_aces, base.rules.hitSplitAces);
  base.rules.doubleAfterSplitAces = booleanValue(
    split.double_after_split_aces,
    base.rules.doubleAfterSplitAces
  );
  base.rules.splitBlackjackCounts = booleanValue(
    split.blackjack_after_split_counts_as_blackjack,
    base.rules.splitBlackjackCounts
  );
  base.rules.insuranceOffered = booleanValue(
    insurance.offered,
    base.rules.insuranceOffered
  );
  base.rules.insurancePayout = numberValue(insurance.payout, base.rules.insurancePayout);
  base.rules.insuranceMaxBetFraction = numberValue(
    insurance.max_bet_fraction,
    base.rules.insuranceMaxBetFraction
  );
  base.rules.holeCardMode = enumValue(
    holeCard.mode,
    ["american", "european_no_hole_card"] as const,
    base.rules.holeCardMode
  );
  base.rules.enhcLossRule = enumValue(
    holeCard.enhc_loss_rule,
    ["all_bets", "original_bets_only"] as const,
    base.rules.enhcLossRule
  );

  base.counting.enabled = booleanValue(counting.enabled, base.counting.enabled);
  base.counting.system = enumValue(
    counting.system,
    ["hi_lo", "hi_opt_i", "hi_opt_ii", "omega_ii"] as const,
    base.counting.system
  );
  base.counting.trueCountRounding = enumValue(
    counting.true_count_rounding,
    ["none", "floor", "truncate", "nearest"] as const,
    base.counting.trueCountRounding
  );
  base.counting.minRemainingDecks = numberValue(
    counting.min_remaining_decks,
    base.counting.minRemainingDecks
  );
  base.counting.initialRunningCount = stringValue(
    counting.initial_running_count,
    base.counting.initialRunningCount
  );
  base.counting.wongingEnterAtTrueCount = stringValue(
    wonging.enter_at_true_count,
    base.counting.wongingEnterAtTrueCount
  );

  base.deviations.enabled = booleanValue(deviations.enabled, base.deviations.enabled);
  const sets = arrayValue(deviations.sets).map(String);
  base.deviations.useIllustrious18 = sets.includes("illustrious_18");
  base.deviations.useFab4 = sets.includes("fab_4");
  const custom = arrayValue(deviations.custom);
  const firstCustom = readRecord(custom[0]);
  base.deviations.customEnabled = custom.length > 0;
  base.deviations.customId = stringValue(firstCustom.id, base.deviations.customId);
  base.deviations.customHandType = enumValue(
    firstCustom.hand_type ?? firstCustom.type,
    ["hard", "soft", "pair"] as const,
    base.deviations.customHandType
  );
  base.deviations.customPlayerTotal = stringValue(
    firstCustom.player_total,
    base.deviations.customPlayerTotal
  );
  base.deviations.customDealerUpcard = stringValue(
    firstCustom.dealer_upcard,
    base.deviations.customDealerUpcard
  );
  base.deviations.customTrueCountMin = stringValue(
    firstCustom.true_count_min,
    base.deviations.customTrueCountMin
  );
  base.deviations.customTrueCountMax = stringValue(
    firstCustom.true_count_max,
    base.deviations.customTrueCountMax
  );
  base.deviations.customAction = enumValue(
    firstCustom.action,
    ["hit", "stand", "double", "split", "surrender"] as const,
    base.deviations.customAction
  );
  base.deviations.customPriority = numberValue(
    firstCustom.priority,
    base.deviations.customPriority
  );

  base.output.console = booleanValue(output.console, base.output.console);
  base.output.jsonFile = stringValue(output.json_file, base.output.jsonFile);
  base.output.csvFile = stringValue(output.csv_file, base.output.csvFile);
  base.batch.sessions = numberValue(batch.sessions, base.batch.sessions);
  base.batch.roundsPerSession = numberValue(
    batch.rounds_per_session,
    base.batch.roundsPerSession
  );
  base.batch.baseSeed = numberValue(batch.base_seed, base.batch.baseSeed);
  return base;
}

export function configurationToYaml(state: ConfigurationFormState): string {
  return stringifyYaml(configurationToObject(state), { sortMapEntries: false });
}

export function configurationToJson(state: ConfigurationFormState): string {
  return `${JSON.stringify(configurationToObject(state), null, 2)}\n`;
}

export function changedConfigurationObject(
  state: ConfigurationFormState
): Record<string, unknown> {
  const diff = diffObjects(
    configurationToObject(defaultConfigurationState),
    configurationToObject(state)
  );
  return {
    schema_version: CONFIG_SCHEMA_VERSION,
    ...diff
  };
}

export function changedConfigurationToYaml(state: ConfigurationFormState): string {
  return stringifyYaml(changedConfigurationObject(state), { sortMapEntries: false });
}

export function changedConfigurationToJson(state: ConfigurationFormState): string {
  return `${JSON.stringify(changedConfigurationObject(state), null, 2)}\n`;
}

export function diffConfigurationStates(
  before: ConfigurationFormState,
  after: ConfigurationFormState
): ConfigDiffEntry[] {
  return diffEntries(configurationToObject(before), configurationToObject(after));
}

export function validateConfigurationForm(
  state: ConfigurationFormState
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const positive = (value: number, field: string, label: string) => {
    if (!Number.isFinite(value) || value <= 0) {
      issues.push({ field, message: `${label} must be positive.` });
    }
  };

  positive(state.simulation.rounds, "simulation.rounds", "Rounds");
  positive(state.simulation.workers, "simulation.workers", "Workers");
  positive(state.bankroll.initial, "bankroll.initial", "Initial bankroll");
  positive(state.betting.amount, "player.betting_strategy.amount", "Base bet");
  positive(state.rules.decks, "rules.decks", "Decks");
  positive(state.rules.splitMaxHands, "rules.split.max_hands", "Max split hands");
  positive(state.batch.sessions, "batch.sessions", "Batch sessions");
  positive(
    state.batch.roundsPerSession,
    "batch.rounds_per_session",
    "Batch rounds per session"
  );

  if (state.rules.penetration <= 0 || state.rules.penetration > 1) {
    issues.push({
      field: "rules.penetration",
      message: "Penetration must be greater than 0 and at most 1."
    });
  }

  if (
    (state.bankroll.tableMinimum && !state.bankroll.tableMaximum) ||
    (!state.bankroll.tableMinimum && state.bankroll.tableMaximum)
  ) {
    issues.push({
      field: "bankroll.table_limits",
      message: "Table minimum and maximum must be configured together."
    });
  }

  if (
    state.bankroll.tableMinimum &&
    state.bankroll.tableMaximum &&
    Number(state.bankroll.tableMinimum) > Number(state.bankroll.tableMaximum)
  ) {
    issues.push({
      field: "bankroll.table_limits",
      message: "Table minimum cannot exceed table maximum."
    });
  }

  if (state.betting.type === "true_count_spread" && !state.counting.enabled) {
    issues.push({
      field: "counting.enabled",
      message: "True-count spread betting requires counting to be enabled."
    });
  }

  if (
    (state.betting.type === "bankroll_percentage" ||
      state.betting.type === "kelly") &&
    state.betting.roundingIncrement <= 0
  ) {
    issues.push({
      field: "player.betting_strategy.rounding.increment",
      message: "Rounding increment must be positive."
    });
  }

  if (state.deviations.enabled && state.deviations.customEnabled) {
    if (!state.deviations.customPlayerTotal) {
      issues.push({
        field: "deviations.custom.player_total",
        message: "Custom deviation player total is required."
      });
    }
    if (!state.deviations.customDealerUpcard) {
      issues.push({
        field: "deviations.custom.dealer_upcard",
        message: "Custom deviation dealer upcard is required."
      });
    }
  }

  return issues;
}

export function buildWarnings(state: ConfigurationFormState): string[] {
  const warnings: string[] = [];
  if (state.simulation.workers > state.simulation.rounds) {
    warnings.push("Workers exceed rounds; some workers may receive no useful work.");
  }
  if (state.rules.shuffleAfterEachRound && state.counting.enabled) {
    warnings.push("Shuffle-after-each-round makes card counting ineffective.");
  }
  if (state.deviations.enabled && !state.counting.enabled) {
    warnings.push("Count-based deviations need counting data to trigger reliably.");
  }
  if (
    state.rules.holeCardMode === "european_no_hole_card" &&
    state.rules.dealerPeeksForBlackjack
  ) {
    warnings.push("Dealer peek is ignored by European no-hole-card rules.");
  }
  return warnings;
}

export function buildBettingPreview(state: ConfigurationFormState): string[] {
  const base = state.betting.amount;
  const maximum = state.bankroll.tableMaximum ? Number(state.bankroll.tableMaximum) : 0;
  const cap = (value: number) => (maximum > 0 ? Math.min(value, maximum) : value);

  if (state.betting.type === "flat") {
    return Array.from({ length: 5 }, () => money(base));
  }
  if (state.betting.type === "martingale") {
    return [0, 1, 2, 3, 4].map((step) => money(cap(base * 2 ** step)));
  }
  if (state.betting.type === "paroli") {
    return [0, 1, 2, 3, 4].map((step) =>
      money(cap(base * 2 ** Math.min(step, state.betting.maxWins)))
    );
  }
  if (state.betting.type === "fibonacci") {
    return [1, 1, 2, 3, 5].map((multiplier) => money(cap(base * multiplier)));
  }
  if (state.betting.type === "dalembert") {
    return [1, 2, 3, 4, 5].map((multiplier) => money(cap(base * multiplier)));
  }
  if (state.betting.type === "true_count_spread") {
    return parseSpreadRows(state.betting.spread).map(
      ([threshold, multiplier]) => `TC ${threshold}: ${money(cap(base * multiplier))}`
    );
  }
  if (state.betting.type === "bankroll_percentage") {
    return [500, 1000, 1500, 2000, 2500].map((bankroll) =>
      `${money(bankroll)} -> ${money(roundBet(bankroll * state.betting.percentage, state))}`
    );
  }
  return [500, 1000, 1500, 2000, 2500].map((bankroll) =>
    `${money(bankroll)} -> ${money(
      roundBet(
        bankroll *
          (state.betting.edge / Math.max(state.betting.variance, 0.0001)) *
          state.betting.fraction,
        state
      )
    )}`
  );
}

function parseSpreadRows(raw: string): [number, number][] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [threshold, multiplier] = line.split(":").map((part) => Number(part.trim()));
      return [threshold, multiplier] as [number, number];
    })
    .filter(([threshold, multiplier]) => Number.isFinite(threshold) && Number.isFinite(multiplier));
}

function parseConfigText(text: string): unknown {
  const trimmed = text.trim();
  if (!trimmed) {
    throw new Error("Import text is empty.");
  }
  if (trimmed.startsWith("{")) {
    return JSON.parse(trimmed) as unknown;
  }
  return parseYaml(trimmed) as unknown;
}

function migrateConfigurationObject(config: Record<string, unknown>): {
  config: Record<string, unknown>;
  messages: string[];
} {
  const migrated = structuredClone(config);
  const messages: string[] = [];
  const schemaVersion = migrated.schema_version ?? migrated.schemaVersion;
  if (migrated.schemaVersion !== undefined) {
    migrated.schema_version = migrated.schemaVersion;
    delete migrated.schemaVersion;
    messages.push("Migrated schemaVersion to schema_version.");
  }
  if (schemaVersion === undefined) {
    migrated.schema_version = CONFIG_SCHEMA_VERSION;
    messages.push("Assigned schema_version 1 to legacy configuration.");
  }
  if (Number(migrated.schema_version) > CONFIG_SCHEMA_VERSION) {
    throw new Error(`Unsupported schema_version: ${String(migrated.schema_version)}.`);
  }
  migrated.schema_version = CONFIG_SCHEMA_VERSION;
  return { config: migrated, messages };
}

function collectUnknownFields(config: Record<string, unknown>): string[] {
  return collectUnknown(config, schemaShape, "");
}

const schemaShape = {
  schema_version: true,
  simulation: { rounds: true, seed: true, workers: true },
  bankroll: {
    initial: true,
    stop_loss: true,
    stop_win: true,
    table_minimum: true,
    table_maximum: true
  },
  player: {
    betting_strategy: {
      type: true,
      amount: true,
      base_amount: true,
      max_wins: true,
      spread: "record",
      percentage: true,
      edge: true,
      variance: true,
      fraction: true,
      rounding: { mode: true, increment: true },
      table_limits: { minimum: true, maximum: true, min: true, max: true }
    },
    playing_strategy: { type: true },
    insurance_strategy: { type: true }
  },
  rules: {
    decks: true,
    penetration: true,
    shuffle_after_each_round: true,
    blackjack_payout: true,
    dealer: { hits_soft_17: true, peeks_for_blackjack: true },
    double: { allowed: true, after_split: true, allowed_totals: true },
    surrender: { type: true },
    split: {
      allowed: true,
      max_hands: true,
      require_same_rank: true,
      resplit_aces: true,
      hit_split_aces: true,
      double_after_split_aces: true,
      blackjack_after_split_counts_as_blackjack: true
    },
    insurance: { offered: true, payout: true, max_bet_fraction: true },
    hole_card: { mode: true, enhc_loss_rule: true }
  },
  counting: {
    enabled: true,
    system: true,
    true_count_rounding: true,
    min_remaining_decks: true,
    initial_running_count: true,
    wonging: { enter_at_true_count: true }
  },
  deviations: {
    enabled: true,
    sets: true,
    custom: [
      {
        id: true,
        hand_type: true,
        type: true,
        player_total: true,
        dealer_upcard: true,
        true_count_min: true,
        true_count_max: true,
        action: true,
        priority: true
      }
    ]
  },
  output: { console: true, json_file: true, csv_file: true },
  batch: { sessions: true, rounds_per_session: true, base_seed: true }
} as const;

type SchemaNode = true | "record" | readonly [SchemaMap] | SchemaMap;
type SchemaMap = { readonly [key: string]: SchemaNode };

function collectUnknown(value: unknown, schema: SchemaNode, path: string): string[] {
  if (schema === true || schema === "record") {
    return [];
  }
  if (isSchemaArray(schema)) {
    return arrayValue(value).flatMap((item, index) =>
      collectUnknown(item, schema[0], `${path}[${index}]`)
    );
  }
  if (!isRecord(value)) {
    return [];
  }
  const unknown: string[] = [];
  for (const [key, child] of Object.entries(value)) {
    const childSchema = schema[key];
    const childPath = path ? `${path}.${key}` : key;
    if (!childSchema) {
      unknown.push(childPath);
    } else {
      unknown.push(...collectUnknown(child, childSchema, childPath));
    }
  }
  return unknown;
}

function isSchemaArray(schema: SchemaNode): schema is readonly [SchemaMap] {
  return Array.isArray(schema);
}

function bettingToObject(state: ConfigurationFormState): Record<string, unknown> {
  const betting: Record<string, unknown> = {
    type: state.betting.type,
    amount: state.betting.amount
  };
  if (state.betting.type === "paroli") {
    betting.max_wins = state.betting.maxWins;
  }
  if (state.betting.type === "true_count_spread") {
    betting.spread = Object.fromEntries(parseSpreadRows(state.betting.spread));
  }
  if (state.betting.type === "bankroll_percentage") {
    betting.percentage = state.betting.percentage;
    betting.rounding = {
      mode: state.betting.roundingMode,
      increment: state.betting.roundingIncrement
    };
  }
  if (state.betting.type === "kelly") {
    betting.edge = state.betting.edge;
    betting.variance = state.betting.variance;
    betting.fraction = state.betting.fraction;
    betting.rounding = {
      mode: state.betting.roundingMode,
      increment: state.betting.roundingIncrement
    };
  }
  return betting;
}

function compactObject<T extends Record<string, unknown>>(value: T): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(value).filter(([, entry]) => entry !== undefined && entry !== "")
  );
}

function optionalNumber(value: string): number | undefined {
  return value.trim() ? Number(value) : undefined;
}

function optionalString(value: string): string | undefined {
  return value.trim() ? value.trim() : undefined;
}

function readRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function arrayValue(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function numberValue(value: unknown, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function stringValue(value: unknown, fallback: string): string {
  return value === undefined || value === null ? fallback : String(value);
}

function booleanValue(value: unknown, fallback: boolean): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function enumValue<const Value extends readonly string[]>(
  value: unknown,
  allowed: Value,
  fallback: Value[number]
): Value[number] {
  return allowed.includes(String(value)) ? (String(value) as Value[number]) : fallback;
}

function spreadToText(spread: Record<string, unknown>, fallback: string): string {
  const rows = Object.entries(spread).map(([threshold, multiplier]) => {
    const numericMultiplier = Number(multiplier);
    return Number.isFinite(numericMultiplier) ? `${threshold}: ${numericMultiplier}` : "";
  });
  return rows.filter(Boolean).join("\n") || fallback;
}

function diffObjects(before: unknown, after: unknown): Record<string, unknown> {
  if (!isRecord(before) || !isRecord(after)) {
    return {};
  }
  const result: Record<string, unknown> = {};
  for (const [key, afterValue] of Object.entries(after)) {
    if (key === "schema_version") {
      continue;
    }
    const beforeValue = before[key];
    if (isRecord(beforeValue) && isRecord(afterValue)) {
      const child = diffObjects(beforeValue, afterValue);
      if (Object.keys(child).length > 0) {
        result[key] = child;
      }
    } else if (JSON.stringify(beforeValue) !== JSON.stringify(afterValue)) {
      result[key] = afterValue;
    }
  }
  return result;
}

function diffEntries(before: unknown, after: unknown, path = ""): ConfigDiffEntry[] {
  if (JSON.stringify(before) === JSON.stringify(after)) {
    return [];
  }
  if (!isRecord(before) || !isRecord(after)) {
    return [{ path, before, after }];
  }
  const keys = new Set([...Object.keys(before), ...Object.keys(after)]);
  return [...keys].flatMap((key) =>
    diffEntries(before[key], after[key], path ? `${path}.${key}` : key)
  );
}

function roundBet(value: number, state: ConfigurationFormState): number {
  const increment = Math.max(state.betting.roundingIncrement, 0.0001);
  if (state.betting.roundingMode === "floor") {
    return Math.floor(value / increment) * increment;
  }
  if (state.betting.roundingMode === "ceiling") {
    return Math.ceil(value / increment) * increment;
  }
  if (state.betting.roundingMode === "nearest") {
    return Math.round(value / increment) * increment;
  }
  return value;
}

function money(value: number): string {
  return value.toLocaleString("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(value) ? 0 : 2
  });
}
