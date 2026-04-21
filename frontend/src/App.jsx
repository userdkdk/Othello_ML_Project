import { Nav } from "./components/Nav.jsx";
import { GamePage } from "./pages/GamePage.jsx";
import { TrainingDashboardPage } from "./pages/TrainingDashboardPage.jsx";
import { useRoute } from "./lib/useRoute.js";


export function App() {
  const { route, navigate } = useRoute();

  return (
    <div className="shell">
      <header className="shell__header">
        <div>
          <div className="shell__eyebrow">Othello Runtime</div>
          <h1 className="shell__title">Frontend / Backend Split</h1>
          <p className="shell__copy">
            Vite + React handles interactive runtime views. FastAPI stays focused on engine, inference, and training APIs.
          </p>
        </div>
        <Nav route={route} navigate={navigate} />
      </header>
      {route === "/training" ? <TrainingDashboardPage /> : <GamePage />}
    </div>
  );
}
