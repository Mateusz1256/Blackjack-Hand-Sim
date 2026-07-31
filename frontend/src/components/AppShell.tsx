import { Activity, BarChart3, History, Layers3, Moon, Settings, SlidersHorizontal, Star, Sun } from "lucide-react";
import { PropsWithChildren, useEffect, useState } from "react";
import { NavLink } from "react-router-dom";

type ThemeMode = "light" | "dark";

export function AppShell({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<ThemeMode>("light");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Activity size={22} aria-hidden="true" />
          <span>Blackjack Simulator</span>
        </div>
        <nav className="nav-list" aria-label="Primary navigation">
          <NavLink to="/" end>
            <Activity size={18} aria-hidden="true" />
            <span>Overview</span>
          </NavLink>
          <NavLink to="/configuration">
            <SlidersHorizontal size={18} aria-hidden="true" />
            <span>Configuration</span>
          </NavLink>
          <NavLink to="/comparisons">
            <BarChart3 size={18} aria-hidden="true" />
            <span>Comparisons</span>
          </NavLink>
          <NavLink to="/batches">
            <Layers3 size={18} aria-hidden="true" />
            <span>Batches</span>
          </NavLink>
          <NavLink to="/presets">
            <Star size={18} aria-hidden="true" />
            <span>Presets</span>
          </NavLink>
          <NavLink to="/history">
            <History size={18} aria-hidden="true" />
            <span>History</span>
          </NavLink>
          <NavLink to="/settings">
            <Settings size={18} aria-hidden="true" />
            <span>Settings</span>
          </NavLink>
        </nav>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow">Analytical workspace</p>
            <h1>Simulation Console</h1>
          </div>
          <button
            className="icon-button"
            type="button"
            aria-label="Toggle color theme"
            title="Toggle color theme"
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          >
            {theme === "light" ? (
              <Moon size={18} aria-hidden="true" />
            ) : (
              <Sun size={18} aria-hidden="true" />
            )}
          </button>
        </header>
        <section className="content-region">{children}</section>
      </main>
    </div>
  );
}
