import { describe, expect, it } from "vitest";

import {
  changedConfigurationObject,
  configurationToJson,
  configurationToYaml,
  defaultConfigurationState,
  importConfigurationText
} from "./configurationModel";

describe("configuration import and export model", () => {
  it("roundtrips YAML export into form state", () => {
    const state = structuredClone(defaultConfigurationState);
    state.simulation.rounds = 2500;
    state.betting.type = "paroli";
    state.betting.maxWins = 4;

    const preview = importConfigurationText(configurationToYaml(state));

    expect(preview.errors).toEqual([]);
    expect(preview.state?.simulation.rounds).toBe(2500);
    expect(preview.state?.betting.type).toBe("paroli");
    expect(preview.state?.betting.maxWins).toBe(4);
  });

  it("roundtrips JSON export into form state", () => {
    const state = structuredClone(defaultConfigurationState);
    state.rules.holeCardMode = "european_no_hole_card";
    state.rules.enhcLossRule = "original_bets_only";

    const preview = importConfigurationText(configurationToJson(state));

    expect(preview.errors).toEqual([]);
    expect(preview.state?.rules.holeCardMode).toBe("european_no_hole_card");
    expect(preview.state?.rules.enhcLossRule).toBe("original_bets_only");
  });

  it("reports unknown fields before mapping", () => {
    const preview = importConfigurationText(`
schema_version: 1
simulation:
  rounds: 10
  surprise: true
`);

    expect(preview.errors).toContain("Imported configuration contains unknown fields.");
    expect(preview.unknownFields).toContain("simulation.surprise");
    expect(preview.state).toBeNull();
  });

  it("runs migration hooks for legacy schema names", () => {
    const preview = importConfigurationText(
      JSON.stringify({
        schemaVersion: 1,
        simulation: { rounds: 50 }
      })
    );

    expect(preview.errors).toEqual([]);
    expect(preview.migrationMessages).toContain("Migrated schemaVersion to schema_version.");
    expect(preview.state?.simulation.rounds).toBe(50);
  });

  it("exports changed-only configuration", () => {
    const state = structuredClone(defaultConfigurationState);
    state.simulation.seed = 777;

    expect(changedConfigurationObject(state)).toEqual({
      schema_version: 1,
      simulation: {
        seed: 777
      }
    });
  });
});
