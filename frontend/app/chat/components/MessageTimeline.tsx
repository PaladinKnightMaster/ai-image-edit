/* eslint-disable @next/next/no-img-element */

import type { RefObject } from "react";

import type { ChatMessage, ProductMode, RunRecord } from "../types";
import { BeforeAfterCompare } from "./BeforeAfterCompare";
import { WorkflowLandingState } from "./WorkflowLandingState";

type MessageTimelineProps = {
  attachmentsCount: number;
  backendUrl: string;
  formatDuration: (ms?: number | null) => string;
  formatLatency: (latency?: number | null) => string;
  formatTime: (timestamp?: number) => string;
  isEditMode: boolean;
  messages: ChatMessage[];
  onStartEditFromOutput: (imageId: string) => void;
  onCopyDebugInfo: (message: ChatMessage) => void;
  onCopyRunParams: (run?: RunRecord) => void;
  onModeChange: (mode: ProductMode) => void;
  onOpenHistory: () => void;
  onReveal: (message: ChatMessage) => void;
  onRetry: (message: ChatMessage) => void;
  timelineRef: RefObject<HTMLDivElement | null>;
};

export function MessageTimeline({
  attachmentsCount,
  backendUrl,
  formatDuration,
  formatLatency,
  formatTime,
  isEditMode,
  messages,
  onStartEditFromOutput,
  onCopyDebugInfo,
  onCopyRunParams,
  onModeChange,
  onOpenHistory,
  onReveal,
  onRetry,
  timelineRef
}: MessageTimelineProps) {
  const getAttachmentBadge = (message: ChatMessage, index: number) => {
    const item = message.attachments?.[index];
    if (!item) {
      return "";
    }
    const slotLabel =
      item.slot === "reference"
        ? "Reference"
        : item.slot === "base"
          ? "Base"
          : index === 0
            ? "Base"
            : "Reference";
    const sourceLabel =
      item.source === "generated"
        ? "Generated result"
        : item.source === "history"
          ? "Library"
          : "Upload";
    return `${slotLabel} / ${sourceLabel}`;
  };

  return (
    <div
      ref={timelineRef}
      className="flex-1 space-y-6 overflow-y-auto rounded-3xl border border-slate-200/70 bg-white/70 p-6 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)] backdrop-blur"
    >
      {messages.length === 0 ? (
        <WorkflowLandingState
          attachmentsCount={attachmentsCount}
          isEditMode={isEditMode}
          onModeChange={onModeChange}
          onOpenHistory={onOpenHistory}
        />
      ) : (
        messages.map((message) => {
          const isUser = message.role === "user";
          const outputImageUrl = message.outputImageId
            ? `${backendUrl}/api/images/${message.outputImageId}`
            : null;
          const compareInputPreview =
            message.request?.inputPreviews?.find((item) => item.slot === "base") ??
            message.request?.inputPreviews?.[0];
          const compareInputImageId =
            compareInputPreview?.imageId ?? message.run?.input_image_ids?.[0];
          const compareInputUrl =
            compareInputPreview?.previewUrl ||
            (compareInputImageId ? `${backendUrl}/api/images/${compareInputImageId}` : null);
          const compareInputCount =
            message.request?.inputPreviews?.length ?? message.run?.input_image_ids?.length ?? 0;
          const extraCompareInputs =
            message.request?.inputPreviews?.filter((item) => item.slot === "reference").length ??
            (compareInputCount > 1 ? compareInputCount - 1 : 0);
          const showCompare = Boolean(outputImageUrl && compareInputUrl && compareInputCount);
          const isActiveJob =
            !isUser && !message.outputImageId && ["queued", "running"].includes(message.status ?? "");

          return (
            <div
              key={message.id}
              className={`flex ${isUser ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-[28px] border px-5 py-4 shadow-[0_20px_50px_-35px_rgba(15,23,42,0.4)] ${
                  isUser
                    ? "border-slate-900 bg-slate-900 text-white"
                    : "border-slate-200/70 bg-white text-slate-800"
                }`}
              >
                {isUser ? (
                  <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.2em] text-slate-300">
                    <span>{message.mode === "edit" ? "Edit" : "Create"}</span>
                    <span>{formatTime(message.createdAt)}</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.2em] text-slate-500">
                    <span>Studio engine</span>
                    <span>{formatTime(message.createdAt)}</span>
                  </div>
                )}

                {message.prompt ? (
                  <p className="mt-3 text-sm leading-relaxed">{message.prompt}</p>
                ) : null}

                {message.attachments?.length ? (
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {message.attachments.map((item, index) => (
                      <div key={item.id} className="relative">
                        <img
                          src={
                            item.previewUrl ||
                            (item.imageId ? `${backendUrl}/api/images/${item.imageId}` : "")
                          }
                          alt="attachment preview"
                          className="h-28 w-full rounded-2xl object-cover"
                        />
                        <span className="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-600">
                          {getAttachmentBadge(message, index)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : null}

                {!isUser ? (
                  <div className="mt-4 space-y-3">
                    <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-500">
                      <span>Status: {message.status ?? "queued"}</span>
                      {message.stage ? <span>Stage: {message.stage}</span> : null}
                      {typeof message.stageElapsedMs === "number" ? (
                        <span>Elapsed: {formatDuration(message.stageElapsedMs)}</span>
                      ) : null}
                      {typeof message.etaMs === "number" ? (
                        <span>ETA: {formatDuration(message.etaMs)}</span>
                      ) : null}
                      {typeof message.progressStep === "number" &&
                      typeof message.progressTotal === "number" ? (
                        <span>
                          Step: {message.progressStep}/{message.progressTotal}
                        </span>
                      ) : null}
                      {message.lastActivityAt ? (
                        <span>Last activity: {formatTime(message.lastActivityAt)}</span>
                      ) : null}
                    </div>
                    {typeof message.progress === "number" ? (
                      <div className="h-2 w-full rounded-full bg-slate-200">
                        <div
                          className="h-2 rounded-full bg-slate-900 transition-all"
                          style={{ width: `${message.progress}%` }}
                        />
                      </div>
                    ) : null}
                    {isActiveJob ? (
                      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-xs leading-relaxed text-slate-600">
                        Local inference is still running. Larger models can stay active for a long
                        time on CPU; this panel will update when the backend reports progress or a
                        terminal result.
                      </div>
                    ) : null}
                    {message.requiresReview ? (
                      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                        {message.reviewNote ?? "Manual review required."}
                      </div>
                    ) : null}
                    {message.requiresReview ? (
                      <button
                        type="button"
                        className="rounded-full border border-amber-300 bg-amber-100 px-4 py-2 text-xs font-semibold text-amber-900 transition hover:-translate-y-0.5"
                        onClick={() => onReveal(message)}
                      >
                        Reveal result
                      </button>
                    ) : null}
                    {message.outputImageId ? (
                      showCompare ? (
                        <BeforeAfterCompare
                          afterImageUrl={outputImageUrl!}
                          beforeImageUrl={compareInputUrl!}
                          extraInputsCount={extraCompareInputs}
                        />
                      ) : (
                        <img
                          src={outputImageUrl!}
                          alt="generated output"
                          className="w-full rounded-2xl object-cover"
                          loading="lazy"
                        />
                      )
                    ) : null}
                    {message.outputImageId ? (
                      <div className="flex flex-wrap gap-2 text-xs">
                        <button
                          type="button"
                          className="rounded-full border border-slate-900 px-3 py-1 font-semibold text-slate-800"
                          onClick={() => onStartEditFromOutput(message.outputImageId!)}
                        >
                          Edit this
                        </button>
                        <a
                          className="rounded-full border border-slate-900/60 px-3 py-1 font-semibold text-slate-700"
                          href={`${backendUrl}/api/images/${message.outputImageId}`}
                          download
                        >
                          Download
                        </a>
                        {message.run ? (
                          <button
                            type="button"
                            className="rounded-full border border-slate-900/60 px-3 py-1 font-semibold text-slate-700"
                            onClick={() => onCopyRunParams(message.run)}
                          >
                            Copy run params
                          </button>
                        ) : null}
                      </div>
                    ) : null}
                    {message.error ? (
                      <p className="text-sm text-rose-600">{message.error}</p>
                    ) : null}
                    {message.status === "failed" && message.request ? (
                      <button
                        type="button"
                        className="rounded-full border border-slate-900 px-4 py-2 text-xs font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
                        onClick={() => onRetry(message)}
                      >
                        Retry
                      </button>
                    ) : null}
                    {message.status === "failed" ? (
                      <button
                        type="button"
                        className="rounded-full border border-slate-900/60 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                        onClick={() => onCopyDebugInfo(message)}
                      >
                        Copy debug info
                      </button>
                    ) : null}
                    {message.run ? (
                      <details className="rounded-2xl border border-slate-200/70 bg-white/90 p-3 text-xs text-slate-600">
                        <summary className="cursor-pointer text-xs uppercase tracking-[0.2em] text-slate-500">
                          Metadata
                        </summary>
                        <div className="mt-3 grid gap-2">
                          <div>Model: {message.run.model_id}</div>
                          <div>Seed: {message.run.seed}</div>
                          <div>Steps: {message.run.steps}</div>
                          <div>
                            Size:{" "}
                            {message.run.width && message.run.height
                              ? `${message.run.width}x${message.run.height}`
                              : "n/a"}
                          </div>
                          <div>Guidance: {message.run.guidance_scale ?? "n/a"}</div>
                          <div>True CFG: {message.run.true_cfg_scale ?? "n/a"}</div>
                          <div>Strength: {message.run.strength ?? "n/a"}</div>
                          <div>Latency: {formatLatency(message.run.latency_ms)}</div>
                        </div>
                      </details>
                    ) : null}
                  </div>
                ) : null}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
