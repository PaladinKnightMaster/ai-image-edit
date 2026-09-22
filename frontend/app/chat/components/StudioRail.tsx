"use client";

import { useEffect, useState, type ReactNode } from "react";

const STORAGE_KEY = "studio-rail-panel";

type Drawer = "setup" | "utilities";

type StudioRailProps = {
  setup: ReactNode;
  utilities: ReactNode;
};

const items = [
  { id: "edit", label: "Edit" },
  { id: "library", label: "Library" },
  { id: "setup", label: "Setup" },
  { id: "utilities", label: "Utilities" }
] as const;

export function StudioRail({ setup, utilities }: StudioRailProps) {
  const [drawer, setDrawer] = useState<Drawer | null>(null);

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (saved === "setup" || saved === "utilities") {
      setDrawer(saved);
    }
  }, []);

  function remember(next: Drawer | null) {
    setDrawer(next);
    window.localStorage.setItem(STORAGE_KEY, next ?? "");
  }

  function select(id: (typeof items)[number]["id"]) {
    if (id === "edit") {
      document.getElementById("studio-prompt")?.scrollIntoView({ behavior: "smooth", block: "start" });
      remember(null);
      return;
    }
    if (id === "library") {
      document.getElementById("studio-library")?.scrollIntoView({ behavior: "smooth", block: "start" });
      remember(null);
      return;
    }
    remember(drawer === id ? null : id);
  }

  return (
    <>
      <aside className="fixed bottom-0 z-40 flex w-full border-t border-slate-200 bg-white/95 backdrop-blur lg:sticky lg:top-0 lg:h-screen lg:w-14 lg:shrink-0 lg:flex-col lg:border-r lg:border-t-0">
        <nav className="flex w-full justify-around px-2 py-2 lg:flex-col lg:justify-start lg:gap-2 lg:px-2 lg:py-4">
          {items.map((item) => {
            const active = drawer === item.id;
            return (
              <button
                key={item.id}
                type="button"
                aria-pressed={active}
                className={`rounded-2xl px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.14em] ${
                  active ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
                }`}
                onClick={() => select(item.id)}
              >
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>
      {drawer ? (
        <div
          className="fixed inset-x-0 bottom-14 top-0 z-30 overflow-y-auto border-slate-200 bg-slate-50 p-4 lg:static lg:bottom-auto lg:top-auto lg:z-auto lg:h-screen lg:w-80 lg:shrink-0 lg:border-r"
          data-testid={`studio-drawer-${drawer}`}
        >
          {drawer === "setup" ? setup : utilities}
        </div>
      ) : null}
    </>
  );
}
