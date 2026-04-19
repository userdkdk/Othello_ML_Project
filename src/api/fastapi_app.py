from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from engine.game_engine import (
    apply_move,
    create_new_game,
    get_valid_moves_for_current_player,
    pass_turn,
)
from engine.types import CellState, GameState


app = FastAPI(title="Othello Engine Demo", version="0.1.0")

CURRENT_STATE: GameState = create_new_game()


class MoveRequest(BaseModel):
    row: int
    col: int


def _serialize_state(state: GameState) -> Dict[str, Any]:
    counts = state.board.count_cells()
    return {
        "board": state.board.to_strings(),
        "current_player": state.current_player.value,
        "counts": {
            "BLACK": counts[CellState.BLACK],
            "WHITE": counts[CellState.WHITE],
            "EMPTY": counts[CellState.EMPTY],
        },
        "status": {
            "is_finished": state.status.is_finished,
            "winner": state.status.winner.value if state.status.winner else None,
        },
        "valid_moves": [
            {"row": row, "col": col}
            for row, col in get_valid_moves_for_current_player(state)
        ],
        "move_history": [
            {"row": move[0], "col": move[1]} if isinstance(move, tuple) else move
            for move in state.move_history
        ],
        "last_move": (
            {"row": state.last_move[0], "col": state.last_move[1]}
            if isinstance(state.last_move, tuple)
            else state.last_move
        ),
    }


def _serialize_result(result: Any) -> Dict[str, Any]:
    return {
        "success": result.success,
        "applied_move": (
            {"row": result.applied_move[0], "col": result.applied_move[1]}
            if result.applied_move is not None
            else None
        ),
        "applied_player": result.applied_player.value if result.applied_player else None,
        "flipped_positions": [
            {"row": row, "col": col} for row, col in result.flipped_positions
        ],
        "next_player": result.next_player.value if result.next_player else None,
        "status": {
            "is_finished": result.status.is_finished,
            "winner": result.status.winner.value if result.status.winner else None,
        },
        "error_code": result.error_code.value if result.error_code else None,
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Othello Engine Demo</title>
  <style>
    :root {
      --paper: #f6f1e8;
      --panel: rgba(255, 250, 242, 0.88);
      --line: #1d3a2d;
      --board: #1c6e50;
      --board-dark: #144f3a;
      --valid: #f4c542;
      --text: #16231d;
      --muted: #62756a;
      --white: #f7f5ee;
      --black: #101714;
      --accent: #b55d35;
      --shadow: rgba(24, 38, 31, 0.14);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(255, 241, 201, 0.9) 0, transparent 30%),
        radial-gradient(circle at bottom right, rgba(186, 212, 197, 0.85) 0, transparent 28%),
        linear-gradient(145deg, #eee4d5, #d7e0d7 72%, #c5d0c6);
      color: var(--text);
    }
    .page {
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 18px 40px;
      display: grid;
      grid-template-columns: minmax(320px, 560px) minmax(280px, 1fr);
      gap: 24px;
    }
    .panel {
      background: var(--panel);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(31, 58, 46, 0.12);
      border-radius: 24px;
      padding: 20px;
      box-shadow: 0 18px 44px var(--shadow);
    }
    .hero {
      margin-bottom: 18px;
    }
    .eyebrow {
      display: inline-block;
      margin-bottom: 10px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(181, 93, 53, 0.1);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-family: "Segoe UI", sans-serif;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 40px;
      line-height: 0.95;
      letter-spacing: -0.03em;
    }
    .sub {
      color: var(--muted);
      margin-bottom: 0;
      font-size: 15px;
      line-height: 1.5;
    }
    .board-wrap {
      display: grid;
      gap: 10px;
      justify-content: start;
      padding: 14px;
      border-radius: 22px;
      background: linear-gradient(180deg, rgba(23,35,29,0.06), rgba(23,35,29,0.02));
    }
    .coords {
      display: grid;
      grid-template-columns: 28px repeat(8, 1fr);
      gap: 6px;
      align-items: center;
    }
    .coord {
      text-align: center;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }
    .board {
      display: grid;
      grid-template-columns: 28px repeat(8, 1fr);
      gap: 6px;
      width: min(100%, 520px);
    }
    .row-label {
      display: grid;
      place-items: center;
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }
    .cell {
      aspect-ratio: 1 / 1;
      border: 0;
      border-radius: 16px;
      background: linear-gradient(145deg, var(--board), var(--board-dark));
      display: grid;
      place-items: center;
      cursor: pointer;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08);
      transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease;
      position: relative;
    }
    .cell:hover { transform: translateY(-1px); filter: saturate(1.05); }
    .cell[disabled] {
      cursor: default;
      opacity: 1;
    }
    .cell.valid::after {
      content: "";
      width: 18%;
      height: 18%;
      border-radius: 999px;
      background: var(--valid);
      box-shadow: 0 0 0 4px rgba(255, 214, 10, 0.18);
      position: absolute;
    }
    .disc {
      width: 72%;
      height: 72%;
      border-radius: 999px;
      box-shadow: inset 0 2px 6px rgba(255,255,255,0.2), 0 6px 14px rgba(0,0,0,0.18);
    }
    .disc.black {
      background: radial-gradient(circle at 30% 30%, #2f4039, var(--black));
    }
    .disc.white {
      background: radial-gradient(circle at 30% 30%, #ffffff, #dfddd5);
    }
    .stats {
      display: grid;
      gap: 16px;
    }
    .status-banner {
      border-radius: 18px;
      padding: 14px 16px;
      background: linear-gradient(135deg, rgba(181,93,53,0.1), rgba(23,35,29,0.03));
      border: 1px solid rgba(181,93,53,0.12);
      font-family: "Segoe UI", sans-serif;
    }
    .status-title {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 4px;
    }
    .status-copy {
      font-size: 17px;
      font-weight: 700;
    }
    .score-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }
    .score-card {
      border-radius: 18px;
      padding: 14px;
      background: rgba(23, 35, 29, 0.05);
      min-height: 88px;
      display: grid;
      align-content: space-between;
      gap: 8px;
      font-family: "Segoe UI", sans-serif;
    }
    .score-card.dark {
      background: linear-gradient(180deg, #17231d, #223229);
      color: white;
    }
    .score-card.light {
      background: linear-gradient(180deg, #f7f4ec, #ece7dc);
    }
    .score-label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: inherit;
      opacity: 0.72;
      font-weight: 700;
    }
    .score-value {
      font-size: 28px;
      font-weight: 600;
    }
    .turn-chip {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border-radius: 999px;
      padding: 9px 12px;
      background: rgba(23, 35, 29, 0.08);
      font-family: "Segoe UI", sans-serif;
      font-weight: 700;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: var(--black);
    }
    .dot.white {
      background: white;
      border: 1px solid rgba(0,0,0,0.15);
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 8px;
    }
    button.action {
      border: 0;
      border-radius: 16px;
      padding: 12px 16px;
      background: #17231d;
      color: white;
      font-weight: 700;
      cursor: pointer;
      font-family: "Segoe UI", sans-serif;
    }
    button.action.secondary {
      background: #dde7df;
      color: #17231d;
    }
    .section-title {
      margin: 0 0 8px;
      font-size: 15px;
      font-weight: 700;
      font-family: "Segoe UI", sans-serif;
    }
    .hint {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
      font-family: "Segoe UI", sans-serif;
    }
    .history {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .history-item {
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(23, 35, 29, 0.06);
      font-size: 13px;
      font-family: "Segoe UI", sans-serif;
      font-weight: 700;
    }
    .result-box {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      color: #304238;
      background: rgba(23, 35, 29, 0.04);
      border-radius: 14px;
      padding: 14px;
      font-family: "Segoe UI", sans-serif;
    }
    @media (max-width: 900px) {
      .page {
        grid-template-columns: 1fr;
      }
      .score-grid {
        grid-template-columns: 1fr 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="panel">
      <div class="hero">
        <div class="eyebrow">Engine Playground</div>
        <h1>Othello Demo</h1>
        <div class="sub">Click a highlighted cell to apply a move. The board updates live, and the side panel tracks score, last result, and move history.</div>
      </div>
      <div class="board-wrap">
        <div class="coords">
          <div></div>
          <div class="coord">0</div><div class="coord">1</div><div class="coord">2</div><div class="coord">3</div>
          <div class="coord">4</div><div class="coord">5</div><div class="coord">6</div><div class="coord">7</div>
        </div>
        <div class="board" id="board"></div>
      </div>
    </section>
    <section class="panel stats">
      <div class="status-banner">
        <div class="status-title">Game State</div>
        <div class="status-copy" id="statusCopy">Loading...</div>
      </div>
      <div class="score-grid">
        <div class="score-card dark">
          <div class="score-label">Black</div>
          <div class="score-value" id="blackScore">0</div>
        </div>
        <div class="score-card light">
          <div class="score-label">White</div>
          <div class="score-value" id="whiteScore">0</div>
        </div>
        <div class="score-card">
          <div class="score-label">Empty</div>
          <div class="score-value" id="emptyScore">0</div>
        </div>
      </div>
      <div class="turn-chip" id="turnChip"><span class="dot"></span><span>Current: -</span></div>
      <div class="actions">
        <button class="action" id="newGameBtn">New Game</button>
        <button class="action secondary" id="passBtn">Pass</button>
      </div>
      <div>
        <div class="section-title">Last Result</div>
        <div class="result-box" id="info">Loading...</div>
      </div>
      <div>
        <div class="section-title">Move History</div>
        <div class="history hint" id="history">No moves yet.</div>
      </div>
    </section>
  </div>

  <script>
    const boardEl = document.getElementById("board");
    const infoEl = document.getElementById("info");
    const historyEl = document.getElementById("history");
    const statusCopy = document.getElementById("statusCopy");
    const turnChip = document.getElementById("turnChip");
    const blackScore = document.getElementById("blackScore");
    const whiteScore = document.getElementById("whiteScore");
    const emptyScore = document.getElementById("emptyScore");

    let currentState = null;

    function validMoveSet(validMoves) {
      const s = new Set();
      for (const move of validMoves) s.add(`${move.row},${move.col}`);
      return s;
    }

    function renderBoard(state) {
      boardEl.innerHTML = "";
      const validMoves = validMoveSet(state.valid_moves);
      for (let row = 0; row < 8; row++) {
        const rowLabel = document.createElement("div");
        rowLabel.className = "row-label";
        rowLabel.textContent = row;
        boardEl.appendChild(rowLabel);

        for (let col = 0; col < 8; col++) {
          const cell = document.createElement("button");
          const key = `${row},${col}`;
          cell.className = "cell";
          if (validMoves.has(key)) cell.classList.add("valid");
          cell.onclick = () => playMove(row, col);
          if (!validMoves.has(key)) cell.disabled = true;

          const value = state.board[row][col];
          if (value === "BLACK" || value === "WHITE") {
            const disc = document.createElement("div");
            disc.className = `disc ${value.toLowerCase()}`;
            cell.appendChild(disc);
          }
          boardEl.appendChild(cell);
        }
      }
    }

    function renderState(state, result = null) {
      currentState = state;
      renderBoard(state);
      blackScore.textContent = state.counts.BLACK;
      whiteScore.textContent = state.counts.WHITE;
      emptyScore.textContent = state.counts.EMPTY;

      const dotClass = state.current_player === "WHITE" ? "dot white" : "dot";
      turnChip.innerHTML = `<span class="${dotClass}"></span><span>Current: ${state.current_player}</span>`;

      if (state.status.is_finished) {
        statusCopy.textContent = `Game finished. Winner: ${state.status.winner ?? "DRAW"}`;
      } else {
        statusCopy.textContent = `Waiting for ${state.current_player} to play`;
      }

      if (state.move_history.length === 0) {
        historyEl.className = "history hint";
        historyEl.textContent = "No moves yet.";
      } else {
        historyEl.className = "history";
        historyEl.innerHTML = "";
        state.move_history.forEach((move, index) => {
          const item = document.createElement("div");
          item.className = "history-item";
          item.textContent = typeof move === "string"
            ? `${index + 1}. ${move}`
            : `${index + 1}. (${move.row},${move.col})`;
          historyEl.appendChild(item);
        });
      }

      if (!result) {
        infoEl.textContent = "Ready. Pick one of the highlighted moves.";
        return;
      }

      const actionText = result.applied_move
        ? `move=(${result.applied_move.row},${result.applied_move.col})`
        : "move=PASS";
      const flips = result.flipped_positions.length
        ? result.flipped_positions.map(pos => `(${pos.row},${pos.col})`).join(", ")
        : "-";
      infoEl.textContent = [
        `success=${result.success}`,
        `action=${actionText}`,
        `player=${result.applied_player ?? "-"}`,
        `error=${result.error_code ?? "-"}`,
        `flipped=${flips}`,
        `next=${result.next_player ?? "-"}`,
      ].join("\\n");
    }

    async function fetchState() {
      const response = await fetch("/api/state");
      const data = await response.json();
      renderState(data);
    }

    async function playMove(row, col) {
      const response = await fetch("/api/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ row, col }),
      });
      const data = await response.json();
      renderState(data.state, data.result);
    }

    async function newGame() {
      const response = await fetch("/api/new", { method: "POST" });
      const data = await response.json();
      renderState(data.state);
    }

    async function passTurn() {
      const response = await fetch("/api/pass", { method: "POST" });
      const data = await response.json();
      renderState(data.state, data.result);
    }

    document.getElementById("newGameBtn").onclick = newGame;
    document.getElementById("passBtn").onclick = passTurn;

    fetchState();
  </script>
</body>
</html>
"""


@app.get("/api/state")
def get_state() -> Dict[str, Any]:
    return _serialize_state(CURRENT_STATE)


@app.post("/api/new")
def new_game() -> Dict[str, Any]:
    global CURRENT_STATE
    CURRENT_STATE = create_new_game()
    return {"state": _serialize_state(CURRENT_STATE)}


@app.post("/api/move")
def move(payload: MoveRequest) -> Dict[str, Any]:
    result = apply_move(CURRENT_STATE, (payload.row, payload.col))
    return {
        "state": _serialize_state(CURRENT_STATE),
        "result": _serialize_result(result),
    }


@app.post("/api/pass")
def do_pass() -> Dict[str, Any]:
    result = pass_turn(CURRENT_STATE)
    return {
        "state": _serialize_state(CURRENT_STATE),
        "result": _serialize_result(result),
    }
