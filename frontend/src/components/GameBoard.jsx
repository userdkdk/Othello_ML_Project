export function GameBoard({ state, onMove }) {
  const validMoves = new Set((state?.valid_moves ?? []).map((move) => `${move.row},${move.col}`));

  return (
    <div className="board-shell">
      <div className="board-labels">
        <div />
        {Array.from({ length: 8 }, (_, value) => (
          <div className="board-label" key={`column-${value}`}>
            {value}
          </div>
        ))}
      </div>
      <div className="board-grid">
        {Array.from({ length: 8 }, (_, row) => (
          <div className="board-row" key={`row-${row}`}>
            <div className="board-label">{row}</div>
            {Array.from({ length: 8 }, (_, col) => {
              const value = state?.board?.[row]?.[col] ?? "EMPTY";
              const key = `${row},${col}`;
              const isValid = validMoves.has(key);
              return (
                <button
                  key={key}
                  className={isValid ? "board-cell board-cell--valid" : "board-cell"}
                  disabled={!isValid}
                  onClick={() => onMove(row, col)}
                >
                  {value === "BLACK" ? <span className="disc disc--black" /> : null}
                  {value === "WHITE" ? <span className="disc disc--white" /> : null}
                </button>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
