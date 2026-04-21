import { useEffect, useState } from "react";

import { GameBoard } from "../components/GameBoard.jsx";
import { Panel } from "../components/Panel.jsx";
import { RuntimeWarningList } from "../components/RuntimeWarningList.jsx";
import { StatusPill } from "../components/StatusPill.jsx";
import { fetchJson } from "../lib/api.js";

export function GamePage() {
  const [state, setState] = useState(null);
  const [mode, setMode] = useState("human_vs_human");
  const [humanSide, setHumanSide] = useState("BLACK");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function refreshState() {
    setLoading(true);
    try {
      const payload = await fetchJson("/api/state");
      setState(payload);
      setMode(payload.mode);
      setHumanSide(payload.human_side ?? "BLACK");
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshState();
  }, []);

  async function createGame() {
    setLoading(true);
    try {
      const payload = await fetchJson("/api/new", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mode,
          human_side: humanSide,
        }),
      });
      setState(payload.state);
      setResult(null);
      setError("");
    } catch (requestError) {
      setError(requestError.payload?.message ?? requestError.message);
    } finally {
      setLoading(false);
    }
  }

  async function submit(path, body) {
    setLoading(true);
    try {
      const payload = await fetchJson(path, body);
      setState(payload.state);
      setResult(payload.result ?? null);
      setError("");
    } catch (requestError) {
      setError(requestError.payload?.message ?? requestError.message);
    } finally {
      setLoading(false);
    }
  }

  const moveHistory = state?.move_history ?? [];
  const currentTurnTone = state?.current_player === "WHITE" ? "light" : "dark";

  return (
    <div className="page-grid">
      <Panel
        title="Separated Game Client"
        eyebrow="Runtime"
        actions={<StatusPill tone={state?.status?.is_finished ? "accent" : "muted"}>{loading ? "Loading" : "Ready"}</StatusPill>}
      >
        <p className="lede">
          The board UI now lives in a dedicated frontend app. FastAPI remains the API layer and can optionally serve the built SPA for production.
        </p>
        {state ? (
          <GameBoard
            state={state}
            onMove={(row, col) =>
              submit("/api/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ row, col }),
              })
            }
          />
        ) : null}
      </Panel>

      <div className="stack">
        <Panel title="Session Controls" eyebrow="Modes">
          <div className="field-grid">
            <label className="field">
              <span>Mode</span>
              <select value={mode} onChange={(event) => setMode(event.target.value)}>
                <option value="human_vs_human">Human vs Human</option>
                <option value="human_vs_model">Human vs Model</option>
                <option value="model_vs_model">Model vs Model</option>
              </select>
            </label>
            <label className="field">
              <span>Human side</span>
              <select
                value={humanSide}
                disabled={mode !== "human_vs_model"}
                onChange={(event) => setHumanSide(event.target.value)}
              >
                <option value="BLACK">Human Black</option>
                <option value="WHITE">Human White</option>
              </select>
            </label>
          </div>
          <div className="button-row">
            <button className="button button--primary" onClick={createGame}>New Game</button>
            <button className="button" onClick={() => submit("/api/pass", { method: "POST" })}>Pass</button>
            <button className="button" onClick={() => submit("/api/step", { method: "POST" })}>Step Model</button>
          </div>
          {state ? (
            <>
              <div className="metric-grid">
                <div className={`metric-card metric-card--${currentTurnTone}`}>
                  <span>Current turn</span>
                  <strong>{state.current_player} · {state.current_turn_actor}</strong>
                </div>
                <div className="metric-card">
                  <span>Black</span>
                  <strong>{state.counts.BLACK}</strong>
                </div>
                <div className="metric-card">
                  <span>White</span>
                  <strong>{state.counts.WHITE}</strong>
                </div>
                <div className="metric-card">
                  <span>Empty</span>
                  <strong>{state.counts.EMPTY}</strong>
                </div>
              </div>
              <RuntimeWarningList warnings={state.runtime_warnings} />
            </>
          ) : null}
          {error ? <div className="callout callout--error">{error}</div> : null}
        </Panel>

        <Panel title="Runtime Signals" eyebrow="Model Loading">
          <div className="kv-list">
            <div><span>Model runtime</span><strong>{state?.model_runtime_available ? "torch available" : "torch missing"}</strong></div>
            <div><span>Black agent</span><strong>{state?.agents?.BLACK?.label ?? "-"}</strong></div>
            <div><span>White agent</span><strong>{state?.agents?.WHITE?.label ?? "-"}</strong></div>
            <div><span>Finished</span><strong>{String(state?.status?.is_finished ?? false)}</strong></div>
          </div>
          <pre className="mono-box">{result ? JSON.stringify(result, null, 2) : "No action executed yet."}</pre>
        </Panel>

        <Panel title="Move History" eyebrow="Trace">
          {moveHistory.length ? (
            <div className="chip-list">
              {moveHistory.map((move, index) => (
                <span className="chip" key={`${index}-${typeof move === "string" ? move : `${move.row}-${move.col}`}`}>
                  {typeof move === "string" ? `${index + 1}. ${move}` : `${index + 1}. (${move.row},${move.col})`}
                </span>
              ))}
            </div>
          ) : (
            <p className="empty-note">No moves yet.</p>
          )}
        </Panel>
      </div>
    </div>
  );
}
