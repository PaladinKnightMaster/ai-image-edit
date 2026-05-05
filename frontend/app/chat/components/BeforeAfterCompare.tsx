/* eslint-disable @next/next/no-img-element */

import { useState } from "react";

type CompareMode = "before" | "split" | "after";

type BeforeAfterCompareProps = {
  afterImageUrl: string;
  beforeImageUrl: string;
  extraInputsCount?: number;
};

const compareModes: Array<{ id: CompareMode; label: string }> = [
  { id: "before", label: "Before" },
  { id: "split", label: "Split" },
  { id: "after", label: "After" }
];

export function BeforeAfterCompare({
  afterImageUrl,
  beforeImageUrl,
  extraInputsCount = 0
}: BeforeAfterCompareProps) {
  const [mode, setMode] = useState<CompareMode>("split");
  const [splitPosition, setSplitPosition] = useState(50);

  return (
    <div className="rounded-2xl border border-slate-200/70 bg-slate-50/80 p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">Compare</p>
          <p className="mt-1 text-xs text-slate-600">
            Check the base image against the latest edit without rerunning the job.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {compareModes.map((compareMode) => (
            <button
              key={compareMode.id}
              type="button"
              className={`rounded-full border px-3 py-1 text-[11px] font-semibold transition ${
                mode === compareMode.id
                  ? "border-slate-900 bg-slate-900 text-white"
                  : "border-slate-300 bg-white text-slate-600 hover:border-slate-500 hover:text-slate-900"
              }`}
              onClick={() => setMode(compareMode.id)}
            >
              {compareMode.label}
            </button>
          ))}
        </div>
      </div>

      <div className="relative mt-3 overflow-hidden rounded-2xl bg-slate-100 aspect-[4/3]">
        {mode === "before" ? (
          <img
            src={beforeImageUrl}
            alt="before edit"
            className="h-full w-full object-cover"
            loading="lazy"
          />
        ) : null}
        {mode === "after" ? (
          <img
            src={afterImageUrl}
            alt="after edit"
            className="h-full w-full object-cover"
            loading="lazy"
          />
        ) : null}
        {mode === "split" ? (
          <>
            <img
              src={afterImageUrl}
              alt="after edit"
              className="absolute inset-0 h-full w-full object-cover"
              loading="lazy"
            />
            <div
              className="absolute inset-0 overflow-hidden"
              style={{ clipPath: `inset(0 ${100 - splitPosition}% 0 0)` }}
            >
              <img
                src={beforeImageUrl}
                alt="before edit"
                className="h-full w-full object-cover"
                loading="lazy"
              />
            </div>
            <div
              className="absolute inset-y-0 z-10 w-0.5 bg-white/95 shadow-[0_0_0_1px_rgba(15,23,42,0.15)]"
              style={{ left: `calc(${splitPosition}% - 1px)` }}
            />
          </>
        ) : null}

        <span className="absolute left-3 top-3 rounded-full bg-white/90 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-700">
          Before
        </span>
        <span className="absolute right-3 top-3 rounded-full bg-slate-900/90 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-white">
          After
        </span>
      </div>

      {mode === "split" ? (
        <label className="mt-3 block space-y-2">
          <div className="flex items-center justify-between text-[11px] uppercase tracking-[0.2em] text-slate-500">
            <span>Split position</span>
            <span>{splitPosition}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={splitPosition}
            onChange={(event) => setSplitPosition(Number(event.target.value))}
            className="w-full accent-slate-900"
          />
        </label>
      ) : null}

      {extraInputsCount > 0 ? (
        <p className="mt-3 text-xs text-slate-500">
          Comparing against the base image. {extraInputsCount} additional reference
          image{extraInputsCount > 1 ? "s stay" : " stays"} outside the compare view.
        </p>
      ) : null}
    </div>
  );
}
