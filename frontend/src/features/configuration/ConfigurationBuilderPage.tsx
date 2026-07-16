import { CheckCircle2, CircleAlert, Wand2 } from "lucide-react";
import { ChangeEvent, FormEvent, ReactNode, useMemo, useState } from "react";

import {
  BETTING_STRATEGIES,
  BettingStrategyType,
  changedConfigurationToJson,
  changedConfigurationToYaml,
  buildBettingPreview,
  buildWarnings,
  configurationToJson,
  configurationToYaml,
  defaultConfigurationState,
  diffConfigurationStates,
  importConfigurationText,
  ImportPreview,
  validateConfigurationForm
} from "./configurationModel";
import { validateSimulationConfig, ValidationResponse } from "../../services/apiClient";

type SectionProps = {
  title: string;
  children: ReactNode;
};

export function ConfigurationBuilderPage() {
  const [form, setForm] = useState(defaultConfigurationState);
  const [backendResult, setBackendResult] = useState<ValidationResponse | null>(null);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [importText, setImportText] = useState("");
  const [importPreview, setImportPreview] = useState<ImportPreview | null>(null);
  const [exportFormat, setExportFormat] = useState<"yaml" | "json">("yaml");
  const [exportMode, setExportMode] = useState<"full" | "changed">("full");

  const yaml = useMemo(() => configurationToYaml(form), [form]);
  const json = useMemo(() => configurationToJson(form), [form]);
  const changedYaml = useMemo(() => changedConfigurationToYaml(form), [form]);
  const changedJson = useMemo(() => changedConfigurationToJson(form), [form]);
  const localIssues = useMemo(() => validateConfigurationForm(form), [form]);
  const warnings = useMemo(() => buildWarnings(form), [form]);
  const bettingPreview = useMemo(() => buildBettingPreview(form), [form]);
  const importIssues = useMemo(
    () => (importPreview?.state ? validateConfigurationForm(importPreview.state) : []),
    [importPreview]
  );
  const importDiff = useMemo(
    () => (importPreview?.state ? diffConfigurationStates(form, importPreview.state) : []),
    [form, importPreview]
  );
  const exportText =
    exportMode === "full"
      ? exportFormat === "yaml"
        ? yaml
        : json
      : exportFormat === "yaml"
        ? changedYaml
        : changedJson;

  const update = <Section extends keyof typeof form, Field extends keyof (typeof form)[Section]>(
    section: Section,
    field: Field,
    value: (typeof form)[Section][Field]
  ) => {
    setForm((current) => ({
      ...current,
      [section]: {
        ...current[section],
        [field]: value
      }
    }));
    setBackendResult(null);
    setBackendError(null);
  };

  const onNumber =
    <Section extends keyof typeof form, Field extends keyof (typeof form)[Section]>(
      section: Section,
      field: Field
    ) =>
    (event: ChangeEvent<HTMLInputElement>) => {
      update(section, field, Number(event.target.value) as (typeof form)[Section][Field]);
    };

  const onText =
    <Section extends keyof typeof form, Field extends keyof (typeof form)[Section]>(
      section: Section,
      field: Field
    ) =>
    (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      update(section, field, event.target.value as (typeof form)[Section][Field]);
    };

  const onBoolean =
    <Section extends keyof typeof form, Field extends keyof (typeof form)[Section]>(
      section: Section,
      field: Field
    ) =>
    (event: ChangeEvent<HTMLInputElement>) => {
      update(section, field, event.target.checked as (typeof form)[Section][Field]);
    };

  const validateWithBackend = async (event: FormEvent) => {
    event.preventDefault();
    setBackendResult(null);
    setBackendError(null);
    if (localIssues.length > 0) {
      return;
    }
    setIsValidating(true);
    try {
      const result = await validateSimulationConfig(yaml);
      setBackendResult(result);
    } catch (error) {
      setBackendError(error instanceof Error ? error.message : "Backend validation failed");
    } finally {
      setIsValidating(false);
    }
  };

  const previewImport = () => {
    setImportPreview(importConfigurationText(importText));
  };

  const applyImport = () => {
    if (!importPreview?.state || importPreview.errors.length > 0 || importIssues.length > 0) {
      return;
    }
    setForm(importPreview.state);
    setBackendResult(null);
    setBackendError(null);
  };

  const importFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    const text = await file.text();
    setImportText(text);
    setImportPreview(importConfigurationText(text));
  };

  return (
    <form className="builder-layout" onSubmit={validateWithBackend}>
      <div className="builder-main">
        <Section title="Simulation">
          <NumberField
            label="Rounds"
            value={form.simulation.rounds}
            onChange={onNumber("simulation", "rounds")}
          />
          <NumberField
            label="Seed"
            value={form.simulation.seed}
            onChange={onNumber("simulation", "seed")}
          />
          <NumberField
            label="Workers"
            value={form.simulation.workers}
            onChange={onNumber("simulation", "workers")}
          />
        </Section>

        <Section title="Bankroll">
          <NumberField
            label="Initial"
            value={form.bankroll.initial}
            onChange={onNumber("bankroll", "initial")}
          />
          <TextField
            label="Stop loss"
            value={form.bankroll.stopLoss}
            onChange={onText("bankroll", "stopLoss")}
          />
          <TextField
            label="Stop win"
            value={form.bankroll.stopWin}
            onChange={onText("bankroll", "stopWin")}
          />
          <TextField
            label="Table minimum"
            value={form.bankroll.tableMinimum}
            onChange={onText("bankroll", "tableMinimum")}
          />
          <TextField
            label="Table maximum"
            value={form.bankroll.tableMaximum}
            onChange={onText("bankroll", "tableMaximum")}
          />
        </Section>

        <Section title="Rules">
          <NumberField label="Decks" value={form.rules.decks} onChange={onNumber("rules", "decks")} />
          <NumberField
            label="Penetration"
            step="0.01"
            value={form.rules.penetration}
            onChange={onNumber("rules", "penetration")}
          />
          <NumberField
            label="Blackjack payout"
            step="0.1"
            value={form.rules.blackjackPayout}
            onChange={onNumber("rules", "blackjackPayout")}
          />
          <SelectField
            label="Surrender"
            value={form.rules.surrenderType}
            onChange={(value) => update("rules", "surrenderType", value as typeof form.rules.surrenderType)}
            options={["none", "early", "late"]}
          />
          <SelectField
            label="Hole card"
            value={form.rules.holeCardMode}
            onChange={(value) => update("rules", "holeCardMode", value as typeof form.rules.holeCardMode)}
            options={["american", "european_no_hole_card"]}
          />
          <SelectField
            label="ENHC loss"
            value={form.rules.enhcLossRule}
            onChange={(value) => update("rules", "enhcLossRule", value as typeof form.rules.enhcLossRule)}
            options={["all_bets", "original_bets_only"]}
          />
          <ToggleField
            label="Shuffle each round"
            checked={form.rules.shuffleAfterEachRound}
            onChange={onBoolean("rules", "shuffleAfterEachRound")}
          />
          <ToggleField
            label="Dealer hits soft 17"
            checked={form.rules.dealerHitsSoft17}
            onChange={onBoolean("rules", "dealerHitsSoft17")}
          />
          <ToggleField
            label="Dealer peeks"
            checked={form.rules.dealerPeeksForBlackjack}
            onChange={onBoolean("rules", "dealerPeeksForBlackjack")}
          />
        </Section>

        <Section title="Double and Split">
          <ToggleField
            label="Double allowed"
            checked={form.rules.doubleAllowed}
            onChange={onBoolean("rules", "doubleAllowed")}
          />
          <ToggleField
            label="Double after split"
            checked={form.rules.doubleAfterSplit}
            onChange={onBoolean("rules", "doubleAfterSplit")}
          />
          <TextField
            label="Double totals"
            value={form.rules.doubleAllowedTotals}
            onChange={onText("rules", "doubleAllowedTotals")}
          />
          <ToggleField
            label="Split allowed"
            checked={form.rules.splitAllowed}
            onChange={onBoolean("rules", "splitAllowed")}
          />
          <NumberField
            label="Max split hands"
            value={form.rules.splitMaxHands}
            onChange={onNumber("rules", "splitMaxHands")}
          />
          <ToggleField
            label="Same rank required"
            checked={form.rules.splitRequireSameRank}
            onChange={onBoolean("rules", "splitRequireSameRank")}
          />
          <ToggleField
            label="Resplit aces"
            checked={form.rules.resplitAces}
            onChange={onBoolean("rules", "resplitAces")}
          />
          <ToggleField
            label="Hit split aces"
            checked={form.rules.hitSplitAces}
            onChange={onBoolean("rules", "hitSplitAces")}
          />
          <ToggleField
            label="DAS aces"
            checked={form.rules.doubleAfterSplitAces}
            onChange={onBoolean("rules", "doubleAfterSplitAces")}
          />
          <ToggleField
            label="Split blackjack counts"
            checked={form.rules.splitBlackjackCounts}
            onChange={onBoolean("rules", "splitBlackjackCounts")}
          />
        </Section>

        <Section title="Insurance">
          <ToggleField
            label="Offered"
            checked={form.rules.insuranceOffered}
            onChange={onBoolean("rules", "insuranceOffered")}
          />
          <NumberField
            label="Payout"
            step="0.1"
            value={form.rules.insurancePayout}
            onChange={onNumber("rules", "insurancePayout")}
          />
          <NumberField
            label="Max bet fraction"
            step="0.05"
            value={form.rules.insuranceMaxBetFraction}
            onChange={onNumber("rules", "insuranceMaxBetFraction")}
          />
          <SelectField
            label="Insurance strategy"
            value={form.strategy.insuranceStrategy}
            onChange={(value) =>
              update("strategy", "insuranceStrategy", value as typeof form.strategy.insuranceStrategy)
            }
            options={["never", "always", "even_money"]}
          />
        </Section>

        <Section title="Counting">
          <ToggleField
            label="Enabled"
            checked={form.counting.enabled}
            onChange={onBoolean("counting", "enabled")}
          />
          <SelectField
            label="System"
            value={form.counting.system}
            onChange={(value) => update("counting", "system", value as typeof form.counting.system)}
            options={["hi_lo", "hi_opt_i", "hi_opt_ii", "omega_ii"]}
          />
          <SelectField
            label="TC rounding"
            value={form.counting.trueCountRounding}
            onChange={(value) =>
              update("counting", "trueCountRounding", value as typeof form.counting.trueCountRounding)
            }
            options={["none", "floor", "truncate", "nearest"]}
          />
          <NumberField
            label="Min decks"
            step="0.25"
            value={form.counting.minRemainingDecks}
            onChange={onNumber("counting", "minRemainingDecks")}
          />
          <TextField
            label="Initial RC"
            value={form.counting.initialRunningCount}
            onChange={onText("counting", "initialRunningCount")}
          />
          <TextField
            label="Wong in TC"
            value={form.counting.wongingEnterAtTrueCount}
            onChange={onText("counting", "wongingEnterAtTrueCount")}
          />
        </Section>

        <Section title="Betting">
          <SelectField
            label="Betting strategy"
            value={form.betting.type}
            onChange={(value) => update("betting", "type", value as BettingStrategyType)}
            options={[...BETTING_STRATEGIES]}
          />
          <NumberField
            label="Base bet"
            value={form.betting.amount}
            onChange={onNumber("betting", "amount")}
          />
          {form.betting.type === "paroli" && (
            <NumberField
              label="Max wins"
              value={form.betting.maxWins}
              onChange={onNumber("betting", "maxWins")}
            />
          )}
          {form.betting.type === "true_count_spread" && (
            <label className="field field-wide">
              <span>Spread</span>
              <textarea
                value={form.betting.spread}
                onChange={onText("betting", "spread")}
                rows={4}
              />
            </label>
          )}
          {form.betting.type === "bankroll_percentage" && (
            <NumberField
              label="Percentage"
              step="0.005"
              value={form.betting.percentage}
              onChange={onNumber("betting", "percentage")}
            />
          )}
          {form.betting.type === "kelly" && (
            <>
              <NumberField label="Edge" step="0.005" value={form.betting.edge} onChange={onNumber("betting", "edge")} />
              <NumberField
                label="Variance"
                step="0.1"
                value={form.betting.variance}
                onChange={onNumber("betting", "variance")}
              />
              <NumberField
                label="Fraction"
                step="0.05"
                value={form.betting.fraction}
                onChange={onNumber("betting", "fraction")}
              />
            </>
          )}
          {(form.betting.type === "bankroll_percentage" || form.betting.type === "kelly") && (
            <>
              <SelectField
                label="Rounding"
                value={form.betting.roundingMode}
                onChange={(value) =>
                  update("betting", "roundingMode", value as typeof form.betting.roundingMode)
                }
                options={["none", "floor", "ceiling", "nearest"]}
              />
              <NumberField
                label="Increment"
                value={form.betting.roundingIncrement}
                onChange={onNumber("betting", "roundingIncrement")}
              />
            </>
          )}
        </Section>

        <Section title="Deviations">
          <ToggleField
            label="Enabled"
            checked={form.deviations.enabled}
            onChange={onBoolean("deviations", "enabled")}
          />
          <ToggleField
            label="Illustrious 18"
            checked={form.deviations.useIllustrious18}
            onChange={onBoolean("deviations", "useIllustrious18")}
          />
          <ToggleField
            label="Fab 4"
            checked={form.deviations.useFab4}
            onChange={onBoolean("deviations", "useFab4")}
          />
          <ToggleField
            label="Custom row"
            checked={form.deviations.customEnabled}
            onChange={onBoolean("deviations", "customEnabled")}
          />
          {form.deviations.customEnabled && (
            <>
              <TextField label="ID" value={form.deviations.customId} onChange={onText("deviations", "customId")} />
              <SelectField
                label="Hand"
                value={form.deviations.customHandType}
                onChange={(value) =>
                  update("deviations", "customHandType", value as typeof form.deviations.customHandType)
                }
                options={["hard", "soft", "pair"]}
              />
              <TextField
                label="Player total"
                value={form.deviations.customPlayerTotal}
                onChange={onText("deviations", "customPlayerTotal")}
              />
              <TextField
                label="Dealer upcard"
                value={form.deviations.customDealerUpcard}
                onChange={onText("deviations", "customDealerUpcard")}
              />
              <TextField
                label="TC min"
                value={form.deviations.customTrueCountMin}
                onChange={onText("deviations", "customTrueCountMin")}
              />
              <TextField
                label="TC max"
                value={form.deviations.customTrueCountMax}
                onChange={onText("deviations", "customTrueCountMax")}
              />
              <SelectField
                label="Action"
                value={form.deviations.customAction}
                onChange={(value) =>
                  update("deviations", "customAction", value as typeof form.deviations.customAction)
                }
                options={["hit", "stand", "double", "split", "surrender"]}
              />
              <NumberField
                label="Priority"
                value={form.deviations.customPriority}
                onChange={onNumber("deviations", "customPriority")}
              />
            </>
          )}
        </Section>

        <Section title="Output and Batch">
          <ToggleField
            label="Console output"
            checked={form.output.console}
            onChange={onBoolean("output", "console")}
          />
          <TextField label="JSON file" value={form.output.jsonFile} onChange={onText("output", "jsonFile")} />
          <TextField label="CSV file" value={form.output.csvFile} onChange={onText("output", "csvFile")} />
          <NumberField
            label="Batch sessions"
            value={form.batch.sessions}
            onChange={onNumber("batch", "sessions")}
          />
          <NumberField
            label="Rounds/session"
            value={form.batch.roundsPerSession}
            onChange={onNumber("batch", "roundsPerSession")}
          />
          <NumberField
            label="Batch base seed"
            value={form.batch.baseSeed}
            onChange={onNumber("batch", "baseSeed")}
          />
        </Section>
      </div>

      <aside className="builder-sidebar">
        <section className="panel import-panel">
          <h2>Import</h2>
          <label className="field field-wide">
            <span>Pasted config</span>
            <textarea
              value={importText}
              onChange={(event) => setImportText(event.target.value)}
              rows={8}
            />
          </label>
          <label className="file-field">
            <input
              type="file"
              accept=".yaml,.yml,.json,application/json,text/yaml,text/plain"
              onChange={importFile}
            />
            <span>Import file</span>
          </label>
          <div className="button-row">
            <button className="secondary-button" type="button" onClick={previewImport}>
              Preview
            </button>
            <button
              className="primary-button"
              type="button"
              disabled={!importPreview?.state || importPreview.errors.length > 0 || importIssues.length > 0}
              onClick={applyImport}
            >
              Apply import
            </button>
          </div>
          {importPreview && (
            <ImportSummary
              preview={importPreview}
              issues={importIssues}
              diffCount={importDiff.length}
            />
          )}
          {importDiff.length > 0 && (
            <ol className="diff-list" aria-label="Import diff">
              {importDiff.slice(0, 8).map((entry) => (
                <li key={entry.path}>
                  <strong>{entry.path}</strong>
                  <span>
                    {formatValue(entry.before)} {"->"} {formatValue(entry.after)}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Validation</h2>
            {backendResult ? <CheckCircle2 size={18} aria-hidden="true" /> : <CircleAlert size={18} aria-hidden="true" />}
          </div>
          <button className="primary-button" type="submit" disabled={isValidating || localIssues.length > 0}>
            <Wand2 size={16} aria-hidden="true" />
            {isValidating ? "Validating" : "Validate config"}
          </button>
          {localIssues.length > 0 && (
            <ul className="issue-list" aria-label="Local validation issues">
              {localIssues.map((issue) => (
                <li key={`${issue.field}-${issue.message}`}>{issue.message}</li>
              ))}
            </ul>
          )}
          {backendError && <p className="status-error">{backendError}</p>}
          {backendResult && (
            <dl className="metric-list compact">
              <div>
                <dt>Status</dt>
                <dd>valid</dd>
              </div>
              <div>
                <dt>Rounds</dt>
                <dd>{backendResult.rounds}</dd>
              </div>
              <div>
                <dt>Seed</dt>
                <dd>{backendResult.seed}</dd>
              </div>
            </dl>
          )}
        </section>

        <section className="panel">
          <h2>Warnings</h2>
          {warnings.length === 0 ? (
            <p className="muted">No warnings.</p>
          ) : (
            <ul className="issue-list">
              {warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel">
          <h2>Betting Preview</h2>
          <ol className="preview-list" aria-label="Betting preview sequence">
            {bettingPreview.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ol>
        </section>

        <section className="panel yaml-panel">
          <h2>Export</h2>
          <div className="segmented-row">
            <label>
              <span>Format</span>
              <select
                value={exportFormat}
                onChange={(event) => setExportFormat(event.target.value as "yaml" | "json")}
              >
                <option value="yaml">YAML</option>
                <option value="json">JSON</option>
              </select>
            </label>
            <label>
              <span>Scope</span>
              <select
                value={exportMode}
                onChange={(event) => setExportMode(event.target.value as "full" | "changed")}
              >
                <option value="full">Full</option>
                <option value="changed">Changed only</option>
              </select>
            </label>
          </div>
          <pre>{exportText}</pre>
        </section>
      </aside>
    </form>
  );
}

function ImportSummary({
  preview,
  issues,
  diffCount
}: {
  preview: ImportPreview;
  issues: { message: string }[];
  diffCount: number;
}) {
  return (
    <div className="import-summary">
      {preview.migrationMessages.length > 0 && (
        <ul className="issue-list">
          {preview.migrationMessages.map((message) => (
            <li key={message}>{message}</li>
          ))}
        </ul>
      )}
      {preview.errors.length > 0 && (
        <ul className="issue-list" aria-label="Import errors">
          {preview.errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}
      {preview.unknownFields.length > 0 && (
        <ul className="issue-list" aria-label="Unknown import fields">
          {preview.unknownFields.map((field) => (
            <li key={field}>Unknown field: {field}</li>
          ))}
        </ul>
      )}
      {issues.length > 0 && (
        <ul className="issue-list" aria-label="Imported validation issues">
          {issues.map((issue) => (
            <li key={issue.message}>{issue.message}</li>
          ))}
        </ul>
      )}
      {preview.state && preview.errors.length === 0 && issues.length === 0 && (
        <p className="muted">Import preview is valid. {diffCount} changes detected.</p>
      )}
    </div>
  );
}

function formatValue(value: unknown): string {
  if (value === undefined) {
    return "unset";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function Section({ title, children }: SectionProps) {
  return (
    <section className="panel form-section">
      <h2>{title}</h2>
      <div className="field-grid">{children}</div>
    </section>
  );
}

function NumberField({
  label,
  value,
  onChange,
  step = "1"
}: {
  label: string;
  value: number;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  step?: string;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input type="number" step={step} value={value} onChange={onChange} />
    </label>
  );
}

function TextField({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input type="text" value={value} onChange={onChange} />
    </label>
  );
}

function SelectField({
  label,
  value,
  onChange,
  options
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function ToggleField({
  label,
  checked,
  onChange
}: {
  label: string;
  checked: boolean;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <label className="toggle-field">
      <input type="checkbox" checked={checked} onChange={onChange} />
      <span>{label}</span>
    </label>
  );
}
