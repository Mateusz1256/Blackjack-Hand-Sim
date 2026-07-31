import { Copy, Download, FileInput, RefreshCw, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  deletePreset,
  duplicatePreset,
  importPreset,
  listPresets,
  presetExportUrl,
  PresetResponse
} from "../../services/apiClient";

export function PresetsPage() {
  const [presets, setPresets] = useState<PresetResponse[]>([]);
  const [selected, setSelected] = useState<PresetResponse | null>(null);
  const [category, setCategory] = useState("");
  const [duplicateName, setDuplicateName] = useState("");
  const [importText, setImportText] = useState("");
  const [deleteTarget, setDeleteTarget] = useState<PresetResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const categories = useMemo(
    () => [...new Set(presets.map((preset) => String(preset.metadata.category ?? "uncategorized")))],
    [presets]
  );

  const loadPresets = async (nextCategory = category) => {
    setError(null);
    try {
      const payload = await listPresets(nextCategory || undefined);
      setPresets(payload.presets);
      setSelected((current) => {
        if (!current) {
          return payload.presets[0] ?? null;
        }
        return payload.presets.find((preset) => preset.id === current.id) ?? payload.presets[0] ?? null;
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Preset list failed");
    }
  };

  useEffect(() => {
    void loadPresets("");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const duplicateSelected = async () => {
    if (!selected || duplicateName.trim() === "") {
      return;
    }
    const id = duplicateName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    try {
      const duplicated = await duplicatePreset(selected.id, id || `${selected.id}-copy`, duplicateName.trim());
      setMessage(`Duplicated ${duplicated.name}.`);
      setDuplicateName("");
      await loadPresets();
      setSelected(duplicated);
    } catch (duplicateError) {
      setError(duplicateError instanceof Error ? duplicateError.message : "Preset duplicate failed");
    }
  };

  const importCustomPreset = async () => {
    if (importText.trim() === "") {
      return;
    }
    try {
      const imported = await importPreset(importText);
      setMessage(`Imported ${imported.name}.`);
      setImportText("");
      await loadPresets();
      setSelected(imported);
    } catch (importError) {
      setError(importError instanceof Error ? importError.message : "Preset import failed");
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) {
      return;
    }
    try {
      await deletePreset(deleteTarget.id);
      setMessage(`Deleted ${deleteTarget.name}.`);
      setDeleteTarget(null);
      await loadPresets();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Preset delete failed");
    }
  };

  return (
    <div className="management-layout">
      <section className="panel management-list">
        <div className="panel-heading">
          <h2>Presets</h2>
          <button className="icon-button" type="button" aria-label="Refresh presets" title="Refresh presets" onClick={() => void loadPresets()}>
            <RefreshCw size={16} aria-hidden="true" />
          </button>
        </div>
        <label className="field">
          Category
          <select
            value={category}
            onChange={(event) => {
              setCategory(event.target.value);
              void loadPresets(event.target.value);
            }}
          >
            <option value="">All</option>
            {categories.map((entry) => (
              <option key={entry} value={entry}>
                {entry}
              </option>
            ))}
          </select>
        </label>
        <div className="record-list" aria-label="Preset list">
          {presets.map((preset) => (
            <button
              className={selected?.id === preset.id ? "active" : undefined}
              key={preset.id}
              type="button"
              onClick={() => setSelected(preset)}
            >
              <strong>{preset.name}</strong>
              <span>{preset.read_only ? "built-in" : "custom"}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="panel management-detail">
        <div className="panel-heading">
          <h2>{selected?.name ?? "Preset Detail"}</h2>
          {selected && <span className="status-pill">{selected.read_only ? "read-only" : "editable"}</span>}
        </div>
        {selected ? (
          <>
            <dl className="metric-list compact">
              <div>
                <dt>ID</dt>
                <dd>{selected.id}</dd>
              </div>
              <div>
                <dt>Category</dt>
                <dd>{String(selected.metadata.category ?? "n/a")}</dd>
              </div>
              <div>
                <dt>Source</dt>
                <dd>{String(selected.metadata.source ?? "n/a")}</dd>
              </div>
            </dl>
            <div className="button-row">
              <a className="result-link" href={presetExportUrl(selected.id)}>
                <Download size={16} aria-hidden="true" />
                Export
              </a>
              <button className="secondary-button full-width-button" type="button" onClick={() => setDeleteTarget(selected)} disabled={selected.read_only}>
                <Trash2 size={16} aria-hidden="true" />
                Delete
              </button>
            </div>
            <pre className="result-json">{selected.config_text}</pre>
          </>
        ) : (
          <p className="muted">No presets are available.</p>
        )}
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Duplicate</h2>
          <Copy size={18} aria-hidden="true" />
        </div>
        <label className="field">
          New preset name
          <input value={duplicateName} onChange={(event) => setDuplicateName(event.target.value)} />
        </label>
        <button className="primary-button" type="button" onClick={duplicateSelected} disabled={!selected || duplicateName.trim() === ""}>
          Duplicate preset
        </button>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Import</h2>
          <FileInput size={18} aria-hidden="true" />
        </div>
        <label className="field">
          Preset YAML
          <textarea rows={12} value={importText} onChange={(event) => setImportText(event.target.value)} />
        </label>
        <button className="primary-button" type="button" onClick={importCustomPreset} disabled={importText.trim() === ""}>
          Import preset
        </button>
      </section>

      {deleteTarget && (
        <section className="confirm-panel" role="dialog" aria-label="Delete preset confirmation">
          <div className="panel">
            <h2>Delete {deleteTarget.name}?</h2>
            <p className="muted">This removes the custom preset from local storage.</p>
            <div className="button-row">
              <button className="secondary-button" type="button" onClick={() => setDeleteTarget(null)}>
                Cancel
              </button>
              <button className="primary-button" type="button" onClick={confirmDelete}>
                Confirm delete
              </button>
            </div>
          </div>
        </section>
      )}

      {message && <p className="status-success">{message}</p>}
      {error && <p className="status-error">{error}</p>}
    </div>
  );
}
