/* eslint-disable @next/next/no-img-element */

import type { RunRecord } from "../types";
import { getJobStatusHelp, getJobStatusLabel, getJobStatusTone } from "../status-copy";

type StudioGalleryProps = {
  backendUrl: string;
  formatLatency: (value?: number | null) => string;
  formatTime: (value?: number) => string;
  recentRuns: RunRecord[];
  revealingJobIds: Set<string>;
  onDeleteRun: (runId: string) => void;
  onRefresh: () => void;
  onRevealRun: (run: RunRecord) => void;
  onStartEditFromOutput: (imageId: string) => void;
};

export function StudioGallery({
  backendUrl,
  formatLatency,
  formatTime,
  recentRuns,
  revealingJobIds,
  onDeleteRun,
  onRefresh,
  onRevealRun,
  onStartEditFromOutput
}: StudioGalleryProps) {
  return (
    <section id="studio-library" data-testid="recent-runs-panel">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Library</h2>
        <button
          type="button"
          className="text-xs text-slate-500 underline underline-offset-4"
          onClick={onRefresh}
        >
          Refresh
        </button>
      </div>
      {recentRuns.length ? (
        <div className="grid grid-cols-2 gap-3 xl:grid-cols-3">
          {recentRuns.map((run) => {
            const isPendingReview =
              run.status === "pending_review" && Boolean(run.pending_output_image_id);
            const isRevealing = revealingJobIds.has(run.job_id);
            return (
              <article
                key={run.id}
                className="overflow-hidden rounded-2xl border border-slate-200 bg-white"
                data-testid={`recent-run-${run.id}`}
              >
                <div className="aspect-square bg-slate-100">
                  {run.output_image_id ? (
                    <img
                      src={`${backendUrl}/api/images/${run.output_image_id}`}
                      alt={run.prompt}
                      className="h-full w-full object-cover"
                      data-testid={`recent-run-image-${run.id}`}
                    />
                  ) : (
                    <div
                      className="flex h-full items-center justify-center text-[10px] uppercase tracking-[0.16em] text-slate-400"
                      data-testid={`recent-run-placeholder-${run.id}`}
                    >
                      {isPendingReview ? "Review" : "n/a"}
                    </div>
                  )}
                </div>
                <div className="space-y-2 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate text-sm text-slate-700">{run.prompt}</p>
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] uppercase tracking-[0.16em] ${getJobStatusTone(run.status)}`}
                      data-testid={`recent-run-status-${run.id}`}
                      title={getJobStatusHelp(run.status)}
                    >
                      {getJobStatusLabel(run.status)}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    {run.created_at ? formatTime(run.created_at) : ""} · {formatLatency(run.latency_ms)}
                  </p>
                  <div className="flex flex-wrap gap-2 text-[11px]">
                    {run.output_image_id ? (
                      <button
                        type="button"
                        className="rounded-full border border-slate-300 px-2 py-0.5 font-semibold text-slate-600"
                        onClick={() => onStartEditFromOutput(run.output_image_id!)}
                        data-testid={`recent-run-edit-${run.id}`}
                      >
                        Edit this
                      </button>
                    ) : null}
                    {run.output_image_id ? (
                      <a
                        className="rounded-full border border-slate-300 px-2 py-0.5 font-semibold text-slate-600"
                        href={`${backendUrl}/api/images/${run.output_image_id}`}
                        download
                        data-testid={`recent-run-download-${run.id}`}
                      >
                        Download
                      </a>
                    ) : null}
                    {isPendingReview ? (
                      <button
                        type="button"
                        className="rounded-full border border-amber-400 px-2 py-0.5 font-semibold text-amber-700"
                        onClick={() => onRevealRun(run)}
                        disabled={isRevealing}
                        data-testid={`recent-run-reveal-${run.id}`}
                      >
                        {isRevealing ? "Revealing..." : "Reveal"}
                      </button>
                    ) : null}
                    <button
                      type="button"
                      className="rounded-full border border-slate-300 px-2 py-0.5 font-semibold text-slate-600"
                      onClick={() => onDeleteRun(run.id)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <p className="text-sm text-slate-500">No runs yet.</p>
      )}
    </section>
  );
}
