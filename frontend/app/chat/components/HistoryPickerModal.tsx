/* eslint-disable @next/next/no-img-element */

import type { AttachmentRole, RunRecord } from "../types";

type HistoryPickerModalProps = {
  backendUrl: string;
  historyOpen: boolean;
  historyRuns: RunRecord[];
  historyTargetSlot: AttachmentRole;
  onAddHistoryAttachment: (imageId: string) => void;
  onClose: () => void;
};

export function HistoryPickerModal({
  backendUrl,
  historyOpen,
  historyRuns,
  historyTargetSlot,
  onAddHistoryAttachment,
  onClose
}: HistoryPickerModalProps) {
  if (!historyOpen) {
    return null;
  }

  const outputRuns = historyRuns.filter((run) => run.output_image_id);
  const pendingReviewCount = historyRuns.filter(
    (run) => !run.output_image_id && run.pending_output_image_id
  ).length;
  const title =
    historyTargetSlot === "base" ? "Pick a base image to edit" : "Pick a reference image";
  const actionLabel =
    historyTargetSlot === "base" ? "Use as base image" : "Use as reference image";

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40 px-4 py-10"
      data-testid="history-picker-modal"
    >
      <div className="max-h-[85vh] w-full max-w-4xl overflow-hidden rounded-3xl border border-slate-200/70 bg-white/95 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)] backdrop-blur">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Output library</p>
            <h2 className="font-display text-2xl text-slate-900">{title}</h2>
          </div>
          <button
            type="button"
            className="rounded-full border border-slate-900 px-4 py-2 text-xs font-semibold text-slate-700"
            onClick={onClose}
          >
            Close
          </button>
        </div>
        <div className="max-h-[65vh] overflow-y-auto px-6 py-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {outputRuns.map((run) => (
              <div
                key={run.id}
                className="rounded-2xl border border-slate-200 bg-white p-3"
                data-testid={`history-output-${run.id}`}
              >
                <img
                  src={`${backendUrl}/api/images/${run.output_image_id}`}
                  alt="history output"
                  className="h-36 w-full rounded-xl object-cover"
                  data-testid={`history-output-image-${run.id}`}
                />
                <div className="mt-3 space-y-1">
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    {run.type ?? "run"}
                  </p>
                  <p className="text-sm text-slate-700">{run.prompt}</p>
                  <button
                    type="button"
                    className="mt-2 w-full rounded-full border border-slate-900 px-3 py-1 text-xs font-semibold text-slate-800"
                    onClick={() => {
                      if (run.output_image_id) {
                        onAddHistoryAttachment(run.output_image_id);
                      }
                    }}
                    data-testid={`history-output-use-${run.id}`}
                  >
                    {actionLabel}
                  </button>
                </div>
              </div>
            ))}
          </div>
          {!outputRuns.length ? (
            <p className="text-sm text-slate-500">No outputs available yet.</p>
          ) : null}
          {pendingReviewCount ? (
            <p className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
              {pendingReviewCount} pending review output
              {pendingReviewCount === 1 ? "" : "s"} must be revealed from Recent runs before
              reuse.
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
