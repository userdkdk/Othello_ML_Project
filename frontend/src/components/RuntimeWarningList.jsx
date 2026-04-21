export function RuntimeWarningList({ warnings }) {
  if (!warnings?.length) {
    return null;
  }
  return (
    <div className="callout callout--warning">
      <div className="callout__title">Runtime warnings</div>
      <ul className="inline-list">
        {warnings.map((warning) => (
          <li key={warning}>{warning}</li>
        ))}
      </ul>
    </div>
  );
}
