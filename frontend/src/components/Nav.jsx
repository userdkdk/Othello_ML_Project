export function Nav({ route, navigate }) {
  return (
    <nav className="shell__nav">
      <button
        className={route === "/" ? "nav-link nav-link--active" : "nav-link"}
        onClick={() => navigate("/")}
      >
        Game Runtime
      </button>
      <button
        className={route === "/training" ? "nav-link nav-link--active" : "nav-link"}
        onClick={() => navigate("/training")}
      >
        Training Dashboard
      </button>
    </nav>
  );
}
