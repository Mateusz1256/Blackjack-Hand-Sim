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

export function configurationToYaml(state: ConfigurationFormState): string {
  const lines: string[] = [
    "simulation:",
    `  rounds: ${state.simulation.rounds}`,
    `  seed: ${state.simulation.seed}`,
    `  workers: ${state.simulation.workers}`,
    "bankroll:",
    `  initial: ${state.bankroll.initial}`
  ];

  addOptional(lines, "  stop_loss", state.bankroll.stopLoss);
  addOptional(lines, "  stop_win", state.bankroll.stopWin);
  addOptional(lines, "  table_minimum", state.bankroll.tableMinimum);
  addOptional(lines, "  table_maximum", state.bankroll.tableMaximum);

  lines.push(
    "player:",
    "  betting_strategy:",
    `    type: ${state.betting.type}`,
    `    amount: ${state.betting.amount}`
  );

  if (state.betting.type === "paroli") {
    lines.push(`    max_wins: ${state.betting.maxWins}`);
  }
  if (state.betting.type === "true_count_spread") {
    lines.push("    spread:");
    for (const [threshold, multiplier] of parseSpreadRows(state.betting.spread)) {
      lines.push(`      ${threshold}: ${multiplier}`);
    }
  }
  if (state.betting.type === "bankroll_percentage") {
    lines.push(`    percentage: ${state.betting.percentage}`);
    addRounding(lines, state);
  }
  if (state.betting.type === "kelly") {
    lines.push(
      `    edge: ${state.betting.edge}`,
      `    variance: ${state.betting.variance}`,
      `    fraction: ${state.betting.fraction}`
    );
    addRounding(lines, state);
  }

  lines.push(
    "  playing_strategy:",
    `    type: ${state.strategy.playingStrategy}`,
    "  insurance_strategy:",
    `    type: ${state.strategy.insuranceStrategy}`,
    "rules:",
    `  decks: ${state.rules.decks}`,
    `  penetration: ${state.rules.penetration}`,
    `  shuffle_after_each_round: ${state.rules.shuffleAfterEachRound}`,
    `  blackjack_payout: ${state.rules.blackjackPayout}`,
    "  dealer:",
    `    hits_soft_17: ${state.rules.dealerHitsSoft17}`,
    `    peeks_for_blackjack: ${state.rules.dealerPeeksForBlackjack}`,
    "  double:",
    `    allowed: ${state.rules.doubleAllowed}`,
    `    after_split: ${state.rules.doubleAfterSplit}`,
    `    allowed_totals: [${state.rules.doubleAllowedTotals}]`,
    "  surrender:",
    `    type: ${state.rules.surrenderType}`,
    "  split:",
    `    allowed: ${state.rules.splitAllowed}`,
    `    max_hands: ${state.rules.splitMaxHands}`,
    `    require_same_rank: ${state.rules.splitRequireSameRank}`,
    `    resplit_aces: ${state.rules.resplitAces}`,
    `    hit_split_aces: ${state.rules.hitSplitAces}`,
    `    double_after_split_aces: ${state.rules.doubleAfterSplitAces}`,
    `    blackjack_after_split_counts_as_blackjack: ${state.rules.splitBlackjackCounts}`,
    "  insurance:",
    `    offered: ${state.rules.insuranceOffered}`,
    `    payout: ${state.rules.insurancePayout}`,
    `    max_bet_fraction: ${state.rules.insuranceMaxBetFraction}`,
    "  hole_card:",
    `    mode: ${state.rules.holeCardMode}`,
    `    enhc_loss_rule: ${state.rules.enhcLossRule}`,
    "counting:",
    `  enabled: ${state.counting.enabled}`,
    `  system: ${state.counting.system}`,
    `  true_count_rounding: ${state.counting.trueCountRounding}`,
    `  min_remaining_decks: ${state.counting.minRemainingDecks}`
  );

  addOptional(lines, "  initial_running_count", state.counting.initialRunningCount);
  if (state.counting.wongingEnterAtTrueCount) {
    lines.push(
      "  wonging:",
      `    enter_at_true_count: ${state.counting.wongingEnterAtTrueCount}`
    );
  }

  lines.push("deviations:", `  enabled: ${state.deviations.enabled}`);
  if (!state.deviations.useIllustrious18 && !state.deviations.useFab4) {
    lines.push("  sets: []");
  } else {
    lines.push("  sets:");
    if (state.deviations.useIllustrious18) {
      lines.push("    - illustrious_18");
    }
    if (state.deviations.useFab4) {
      lines.push("    - fab_4");
    }
  }

  if (state.deviations.enabled && state.deviations.customEnabled) {
    lines.push(
      "  custom:",
      `    - id: ${state.deviations.customId}`,
      `      hand_type: ${state.deviations.customHandType}`,
      `      player_total: ${state.deviations.customPlayerTotal}`,
      `      dealer_upcard: ${state.deviations.customDealerUpcard}`,
      `      action: ${state.deviations.customAction}`,
      `      priority: ${state.deviations.customPriority}`
    );
    addOptional(lines, "      true_count_min", state.deviations.customTrueCountMin);
    addOptional(lines, "      true_count_max", state.deviations.customTrueCountMax);
  } else {
    lines.push("  custom: []");
  }

  lines.push(
    "output:",
    `  console: ${state.output.console}`
  );
  addOptionalString(lines, "  json_file", state.output.jsonFile);
  addOptionalString(lines, "  csv_file", state.output.csvFile);

  return `${lines.join("\n")}\n`;
}

function addRounding(lines: string[], state: ConfigurationFormState) {
  lines.push(
    "    rounding:",
    `      mode: ${state.betting.roundingMode}`,
    `      increment: ${state.betting.roundingIncrement}`
  );
}

function addOptional(lines: string[], key: string, value: string) {
  if (value.trim()) {
    lines.push(`${key}: ${value.trim()}`);
  }
}

function addOptionalString(lines: string[], key: string, value: string) {
  if (value.trim()) {
    lines.push(`${key}: ${JSON.stringify(value.trim())}`);
  }
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
