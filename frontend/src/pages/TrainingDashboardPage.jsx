import { useEffect, useState } from "react";

import { Panel } from "../components/Panel.jsx";
import { StatusPill } from "../components/StatusPill.jsx";
import { fetchJson } from "../lib/api.js";

export function TrainingDashboardPage() {
  const [snapshot, setSnapshot] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    try {
      const [statePayload, comparisonPayload] = await Promise.all([
        fetchJson("/api/training/state"),
        fetchJson("/api/training/comparisons/latest"),
      ]);
      setSnapshot(statePayload);
      setComparison(comparisonPayload.comparison);
      setError("");
    } catch (requestError) {
      setError(requestError.payload?.message ?? requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  const inventory = snapshot?.checkpoint_inventory?.items ?? [];
  const epochTracking = snapshot?.epoch_tracking;
  const latestIteration = snapshot?.latest_iteration;

  return (
    <div className="page-grid page-grid--training">
      <Panel
        title="Training Dashboard"
        eyebrow="Runtime Ops"
        actions={<StatusPill tone={snapshot?.session?.status === "idle" ? "muted" : "accent"}>{loading ? "Syncing" : snapshot?.session?.status ?? "idle"}</StatusPill>}
      >
        <p className="lede">
          This frontend is separated from the game client so training controls, checkpoint inventory, and evaluation metadata can grow without bloating the game runtime page.
        </p>
        <div className="button-row">
          <button className="button button--primary" onClick={refresh}>Refresh State</button>
          <button className="button" disabled>Start Training</button>
          <button className="button" disabled>Compare Checkpoints</button>
        </div>
        <div className="metric-grid">
          <div className="metric-card">
            <span>Session status</span>
            <strong>{snapshot?.session?.status ?? "idle"}</strong>
          </div>
          <div className="metric-card">
            <span>Epoch progress</span>
            <strong>{epochTracking ? `${epochTracking.current_epoch}/${epochTracking.target_epochs}` : "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Epoch percent</span>
            <strong>{epochTracking ? `${epochTracking.current_epoch_progress_percent}%` : "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Total epochs</span>
            <strong>{epochTracking?.completed_epochs_after_run ?? "-"}</strong>
          </div>
        </div>
        <div className="metric-grid">
          <div className="metric-card">
            <span>Latest iteration</span>
            <strong>{latestIteration?.iteration ?? "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Policy loss</span>
            <strong>{latestIteration?.policy_loss ?? "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Value loss</span>
            <strong>{latestIteration?.value_loss ?? "-"}</strong>
          </div>
          <div className="metric-card">
            <span>Last comparison</span>
            <strong>{comparison ? "available" : "none"}</strong>
          </div>
        </div>
        {error ? <div className="callout callout--error">{error}</div> : null}
      </Panel>

      <Panel title="Checkpoint Inventory" eyebrow="Metrics">
        {inventory.length ? (
          <div className="inventory-list">
            {inventory.map((item) => (
              <article className="inventory-card" key={`${item.slot}-${item.path}`}>
                <div className="inventory-card__head">
                  <strong>{item.slot}</strong>
                  <StatusPill tone={item.exists ? "muted" : "accent"}>{item.kind}</StatusPill>
                </div>
                <div className="inventory-card__path">{item.path}</div>
                <div className="inventory-card__meta">
                  <span>Load status</span>
                  <strong>{item.load_status}</strong>
                </div>
                <div className="inventory-card__meta">
                  <span>Track</span>
                  <strong>{item.metadata?.track ?? "-"}</strong>
                </div>
                <div className="inventory-card__meta">
                  <span>Model version</span>
                  <strong>{item.metadata?.model_version ?? "-"}</strong>
                </div>
                <div className="inventory-card__meta">
                  <span>Balanced score</span>
                  <strong>{item.metadata?.balanced_eval_score ?? "-"}</strong>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-note">No checkpoint inventory found.</p>
        )}
      </Panel>

      <Panel title="Latest Comparison" eyebrow="Evaluation">
        <pre className="mono-box">{comparison ? JSON.stringify(comparison, null, 2) : "No comparison recorded yet."}</pre>
      </Panel>
    </div>
  );
}
