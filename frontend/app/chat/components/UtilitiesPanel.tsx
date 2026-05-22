import type { ChangeEvent, RefObject } from "react";

import type { RunRecord } from "../types";
import { getFailureDetail, getJobStatusLabel } from "../status-copy";

type UtilitiesPanelProps = {
  deleteImagesOnCleanup: boolean;
  failedRuns: RunRecord[];
  importInputRef: RefObject<HTMLInputElement | null>;
  importWarnings: string[];
  maintenanceOpen: boolean;
  onClearFailedRuns: () => void;
  onClearHistory: () => void;
  onClearRecentRuns: () => void;
  onDeleteRun: (runId: string) => void;
  onDeleteImagesOnCleanupChange: (checked: boolean) => void;
  onExportThread: () => void;
  onHandleImportThread: (event: ChangeEvent<HTMLInputElement>) => void;
  onLoadFailedRuns: () => void;
  onSubmitReplay: (run: RunRecord) => void;
  onToggleMaintenance: () => void;
  onTriggerImport: () => void;
};

export function UtilitiesPanel({
  deleteImagesOnCleanup,
  failedRuns,
  importInputRef,
  importWarnings,
  maintenanceOpen,
  onClearFailedRuns,
  onClearHistory,
  onClearRecentRuns,
  onDeleteRun,
  onDeleteImagesOnCleanupChange,
  onExportThread,
  onHandleImportThread,
  onLoadFailedRuns,
  onSubmitReplay,
  onToggleMaintenance,
  onTriggerImport
}: UtilitiesPanelProps) {
  return (
    <div className="rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.45)] backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
            Utilities
          </h3>
          <p className="mt-2 text-xs text-slate-500">
            Recovery, cleanup, and session transfer stay available here without crowding the main flow.
          </p>
        </div>
        <button
          type="button"
          className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
          onClick={onToggleMaintenance}
        >
          {maintenanceOpen ? "Hide" : "Open"}
        </button>
      </div>

      {maintenanceOpen ? (
        <div className="mt-5 space-y-5">
          <div className="flex flex-col gap-3">
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                className="rounded-full border border-slate-900 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
                onClick={onExportThread}
              >
                Export session
              </button>
              <button
                type="button"
                className="rounded-full border border-slate-900/60 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                onClick={onTriggerImport}
              >
                Import session
              </button>
              <button
                type="button"
                className="rounded-full border border-slate-900/60 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                onClick={onClearHistory}
              >
                Clear local session
              </button>
            </div>
            <input
              ref={importInputRef}
              type="file"
              accept="application/json"
              className="hidden"
              onChange={onHandleImportThread}
            />
            {importWarnings.length ? (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
                {importWarnings.join(" ")}
              </div>
            ) : null}
          </div>

          <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Cleanup</p>
                <p className="mt-2 text-xs text-slate-500">
                  Destructive run cleanup stays outside the main editing workflow.
                </p>
              </div>
              <button
                type="button"
                className="rounded-full border border-rose-300 px-3 py-1 text-xs font-semibold text-rose-600 transition hover:border-rose-500 hover:text-rose-700"
                onClick={onClearRecentRuns}
              >
                Clear recent runs
              </button>
            </div>
            <label className="mt-4 flex items-center gap-3 text-xs text-slate-600">
              <input
                type="checkbox"
                checked={deleteImagesOnCleanup}
                onChange={(event) => onDeleteImagesOnCleanupChange(event.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-slate-900"
              />
              Also delete output images
            </label>
            <p className="mt-2 text-xs text-slate-500">
              Removes PNGs from <code className="font-mono">data/images</code> when you clear runs.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Failed runs</p>
                <p className="mt-2 text-xs text-slate-500">
                  Replay or remove failed jobs only when you need recovery work.
                </p>
              </div>
              <div className="flex items-center gap-3 text-xs">
                <button
                  type="button"
                  className="text-slate-500 underline underline-offset-4"
                  onClick={onLoadFailedRuns}
                >
                  Refresh
                </button>
                <button
                  type="button"
                  className="text-rose-500 underline underline-offset-4"
                  onClick={onClearFailedRuns}
                >
                  Clear
                </button>
              </div>
            </div>
            <div className="mt-4 space-y-4">
              {failedRuns.length ? (
                failedRuns.map((run) => (
                  <div key={run.id} className="rounded-2xl border border-rose-200 bg-rose-50 p-3">
                    <p className="text-xs uppercase tracking-[0.2em] text-rose-500">
                      {run.type ?? "run"} / {getJobStatusLabel(run.status)}
                    </p>
                    <p className="mt-1 text-sm text-slate-700">{run.prompt}</p>
                    <p className="mt-2 text-xs text-rose-600">{getFailureDetail(run.error)}</p>
                    <div className="mt-2 flex items-center gap-2">
                      <button
                        type="button"
                        className="flex-1 rounded-full border border-rose-500 px-3 py-1 text-xs font-semibold text-rose-600"
                        onClick={() => onSubmitReplay(run)}
                      >
                        Replay
                      </button>
                      <button
                        type="button"
                        className="flex-1 rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600"
                        onClick={() => onDeleteRun(run.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No failed runs.</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
