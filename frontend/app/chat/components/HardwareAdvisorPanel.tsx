import { useEffect, useState } from "react";

import type { HardwareAdvice, HardwareModelAdvice } from "../types";

type ModelLocation = {
  path: string;
  default_path: string;
  confirmed: boolean;
  locked_by_env: boolean;
  source: string;
  exists: boolean;
};

type DownloadStatus = {
  model_id: string | null;
  status: string;
  bytes_downloaded: number;
  bytes_total: number | null;
  message: string;
  error: string | null;
};

type HardwareAdvisorPanelProps = {
  advice: HardwareAdvice | null;
  selectedModelId: string;
  backendUrl: string;
  onSelectModel: (modelId: string) => void;
  onRefresh: () => void;
};

function verdictTone(verdict: string): string {
  if (verdict === "recommended") {
    return "bg-emerald-500 text-white";
  }
  if (verdict === "usable" || verdict === "usable_slow") {
    return "bg-amber-400 text-slate-900";
  }
  return "bg-slate-200 text-slate-700";
}

function formatGb(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) {
    return "unknown";
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} GB`;
}

export function HardwareAdvisorPanel({
  advice,
  selectedModelId,
  backendUrl,
  onSelectModel,
  onRefresh
}: HardwareAdvisorPanelProps) {
  const [download, setDownload] = useState<DownloadStatus | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [showOthers, setShowOthers] = useState(false);
  const [folderOpen, setFolderOpen] = useState(false);
  const [location, setLocation] = useState<ModelLocation | null>(null);
  const [folderDraft, setFolderDraft] = useState("");
  const [folderError, setFolderError] = useState<string | null>(null);
  const [savingFolder, setSavingFolder] = useState(false);

  const best = advice?.models.find((model) => model.id === advice.best_choice) ?? null;
  const others = advice?.models.filter((model) => model.id !== advice.best_choice) ?? [];
  const canDownload =
    Boolean(best && !best.present && best.downloadable && best.in_app_download);
  const downloading = download?.status === "running";
  const folderConfirmed = Boolean(location?.confirmed || location?.locked_by_env);

  useEffect(() => {
    if (!best?.in_app_download) {
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        const response = await fetch(`${backendUrl}/api/settings/model-location`, {
          cache: "no-store"
        });
        if (!response.ok) {
          return;
        }
        const data = (await response.json()) as ModelLocation;
        if (cancelled) {
          return;
        }
        setLocation(data);
        setFolderDraft(data.path);
      } catch {
        // the setup card still shows once advice has loaded
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [backendUrl, best?.id, best?.in_app_download]);

  useEffect(() => {
    if (!downloading || !best) {
      return;
    }
    const timer = window.setInterval(async () => {
      try {
        const response = await fetch(`${backendUrl}/api/models/${best.id}/download`, {
          cache: "no-store"
        });
        if (!response.ok) {
          return;
        }
        const next = (await response.json()) as DownloadStatus;
        setDownload(next);
        if (next.status === "succeeded") {
          onSelectModel(best.id);
          onRefresh();
        }
      } catch {
        // keep the last status; the next poll retries
      }
    }, 1000);
    return () => window.clearInterval(timer);
  }, [backendUrl, best, downloading, onRefresh, onSelectModel]);

  async function confirmFolder() {
    setFolderError(null);
    setSavingFolder(true);
    try {
      const response = await fetch(`${backendUrl}/api/settings/model-location`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: folderDraft })
      });
      const payload = (await response.json()) as ModelLocation & {
        error?: { message?: string };
      };
      if (!response.ok) {
        setFolderError(payload.error?.message || "Could not save that folder.");
        return;
      }
      setLocation(payload);
      setFolderDraft(payload.path);
      onRefresh();
    } catch {
      setFolderError("Could not save that folder.");
    } finally {
      setSavingFolder(false);
    }
  }

  async function startDownload(modelId: string) {
    setDownloadError(null);
    try {
      const response = await fetch(`${backendUrl}/api/models/${modelId}/download`, {
        method: "POST"
      });
      const payload = (await response.json()) as {
        status?: string;
        bytes_downloaded?: number;
        bytes_total?: number | null;
        message?: string;
        error?: string | { message?: string } | null;
        model_id?: string | null;
      };
      if (!response.ok) {
        const apiError = payload.error;
        const message =
          apiError && typeof apiError === "object" && apiError.message
            ? apiError.message
            : "Download could not start.";
        setDownloadError(message);
        return;
      }
      const next: DownloadStatus = {
        model_id: payload.model_id ?? modelId,
        status: payload.status ?? "idle",
        bytes_downloaded: payload.bytes_downloaded ?? 0,
        bytes_total: payload.bytes_total ?? null,
        message: payload.message ?? "",
        error: typeof payload.error === "string" ? payload.error : null
      };
      setDownload(next);
      if (next.status === "succeeded") {
        onSelectModel(modelId);
        onRefresh();
      }
    } catch {
      setDownloadError("Download could not start.");
    }
  }

  const percent =
    download?.bytes_total && download.bytes_total > 0
      ? Math.min(100, Math.round((download.bytes_downloaded / download.bytes_total) * 100))
      : null;

  return (
    <div
      className="rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.45)] backdrop-blur"
      data-testid="hardware-advisor-panel"
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
            Hardware fit
          </h3>
          <p className="mt-2 text-xs text-slate-500">
            This PC, the model that fits it, and whether that model is ready to use.
          </p>
        </div>
        <button
          type="button"
          className="text-xs text-slate-500 underline underline-offset-4"
          onClick={onRefresh}
        >
          Rescan
        </button>
      </div>

      {!advice ? (
        <p className="mt-4 text-sm text-slate-500">Scanning this machine...</p>
      ) : (
        <>
          <p className="mt-4 text-sm leading-relaxed text-slate-700">{advice.summary}</p>
          <p className="mt-2 text-xs text-slate-500">
            Free disk {formatGb(advice.hardware.disk_free_gb)}
            {advice.hardware.openvino_devices?.length
              ? ` · OpenVINO ${advice.hardware.openvino_devices.join(", ")}`
              : ""}
          </p>

          {best?.present ? (
            <div
              className="mt-4 rounded-2xl border border-emerald-300/80 bg-emerald-50/80 px-4 py-3"
              data-testid="hardware-ready"
            >
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-700">
                Ready
              </p>
              <p className="mt-1 font-semibold text-slate-800">{best.label}</p>
              <p className="mt-1 text-xs leading-relaxed text-slate-600">
                {best.reason}
                {best.id === "sdxl-openvino"
                  ? " A draft portrait edit on this CPU has completed in about 40 seconds."
                  : ""}
              </p>
              {location && best.in_app_download ? (
                <div className="mt-3">
                  <button
                    type="button"
                    className="text-xs text-slate-500 underline underline-offset-4"
                    data-testid="toggle-model-folder"
                    onClick={() => setFolderOpen((open) => !open)}
                  >
                    {folderOpen ? "Hide folder" : "Change folder"}
                  </button>
                  {folderOpen ? (
                    <div className="mt-3" data-testid="model-folder-picker">
                  <label className="text-xs font-semibold text-slate-700" htmlFor="model-folder-ready">
                    Model folder
                  </label>
                  <input
                    id="model-folder-ready"
                    className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-800 disabled:bg-slate-100"
                    data-testid="model-folder-input"
                    value={folderDraft}
                    disabled={location.locked_by_env || savingFolder}
                    onChange={(event) => setFolderDraft(event.target.value)}
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    {location.locked_by_env
                      ? "This folder is set by SDXL_OV_BASE_DIR and cannot be changed here."
                      : "New downloads use this folder. Files already stored elsewhere stay where they are."}
                  </p>
                  {!location.locked_by_env ? (
                    <button
                      type="button"
                      className="mt-2 text-xs text-slate-500 underline underline-offset-4"
                      data-testid="save-model-folder"
                      disabled={savingFolder || !folderDraft.trim()}
                      onClick={() => void confirmFolder()}
                    >
                      {savingFolder ? "Saving…" : "Save folder"}
                    </button>
                  ) : null}
                  {folderError ? <p className="mt-2 text-xs text-rose-600">{folderError}</p> : null}
                    </div>
                  ) : null}
                </div>
              ) : null}
              {best.id !== selectedModelId ? (
                <button
                  type="button"
                  className="mt-3 rounded-full border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
                  onClick={() => onSelectModel(best.id)}
                >
                  Use {best.label}
                </button>
              ) : (
                <p className="mt-2 text-xs text-slate-500">Selected for the next run.</p>
              )}
            </div>
          ) : best ? (
            <div
              className="mt-4 rounded-2xl border border-slate-200 bg-white px-4 py-3"
              data-testid="hardware-setup"
            >
              <p className="font-semibold text-slate-800">{best.label}</p>
              <p className="mt-1 text-xs leading-relaxed text-slate-600">{best.reason}</p>
              <p className="mt-2 text-xs text-slate-500">
                About {formatGb(best.approx_disk_gb)} on disk.
              </p>
              {canDownload ? (
                <div className="mt-3" data-testid="model-folder-picker">
                  <label className="text-xs font-semibold text-slate-700" htmlFor="model-folder">
                    Model folder
                  </label>
                  <input
                    id="model-folder"
                    className="mt-1 w-full rounded-xl border border-slate-300 px-3 py-2 text-xs text-slate-800 disabled:bg-slate-100"
                    data-testid="model-folder-input"
                    value={folderDraft}
                    disabled={Boolean(location?.locked_by_env) || savingFolder}
                    onChange={(event) => setFolderDraft(event.target.value)}
                  />
                  <p className="mt-2 text-xs text-slate-500">
                    {location?.locked_by_env
                      ? "This folder is set by SDXL_OV_BASE_DIR and cannot be changed here."
                      : "Suggested default. Confirm it, or type another folder. Later downloads reuse this choice."}
                  </p>
                  {!location?.locked_by_env && !folderConfirmed ? (
                    <button
                      type="button"
                      className="mt-3 w-full rounded-full border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                      data-testid="confirm-model-folder"
                      disabled={savingFolder || !folderDraft.trim()}
                      onClick={() => void confirmFolder()}
                    >
                      {savingFolder ? "Saving…" : "Use this folder"}
                    </button>
                  ) : null}
                  {!location?.locked_by_env && folderConfirmed ? (
                    <button
                      type="button"
                      className="mt-2 text-xs text-slate-500 underline underline-offset-4"
                      data-testid="save-model-folder"
                      disabled={savingFolder}
                      onClick={() => void confirmFolder()}
                    >
                      Save folder
                    </button>
                  ) : null}
                  {folderError ? <p className="mt-2 text-xs text-rose-600">{folderError}</p> : null}
                </div>
              ) : null}
              {canDownload && folderConfirmed ? (
                <button
                  type="button"
                  className="mt-3 w-full rounded-full border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  data-testid="download-recommended-model"
                  disabled={downloading}
                  onClick={() => void startDownload(best.id)}
                >
                  {downloading ? "Downloading…" : `Download ${best.label}`}
                </button>
              ) : null}
              {!canDownload ? (
                <p className="mt-3 text-xs text-slate-500">
                  This machine cannot download that model yet. Rescan after freeing disk or RAM.
                </p>
              ) : null}
              {downloading ? (
                <div className="mt-3" data-testid="download-progress">
                  <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                    <div
                      className="h-full bg-slate-900 transition-all"
                      style={{ width: percent == null ? "40%" : `${percent}%` }}
                    />
                  </div>
                  <p className="mt-2 text-xs text-slate-500">
                    {download?.message || "Downloading"}
                    {percent != null ? ` · ${percent}%` : ""}
                  </p>
                </div>
              ) : null}
              {download?.status === "failed" ? (
                <p className="mt-2 text-xs text-rose-600">{download.error || "Download failed."}</p>
              ) : null}
              {downloadError ? <p className="mt-2 text-xs text-rose-600">{downloadError}</p> : null}
            </div>
          ) : null}

          {others.length ? (
            <div className="mt-4">
              <button
                type="button"
                className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500"
                data-testid="other-models-toggle"
                onClick={() => setShowOthers((open) => !open)}
              >
                {showOthers ? "Hide other models" : "Other models"}
              </button>
              {showOthers ? (
                <div className="mt-3 space-y-3" data-testid="other-models">
                  {others.map((model) => (
                    <OtherModelRow
                      key={model.id}
                      model={model}
                      isSelected={model.id === selectedModelId}
                      onSelect={() => onSelectModel(model.id)}
                    />
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}
        </>
      )}
    </div>
  );
}

function OtherModelRow({
  model,
  isSelected,
  onSelect
}: {
  model: HardwareModelAdvice;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const canSelect = model.present && model.downloadable;
  return (
    <div className="rounded-2xl border border-slate-200/70 bg-white/90 px-3 py-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-slate-800">{model.label}</p>
          <p className="mt-1 text-xs leading-relaxed text-slate-600">{model.reason}</p>
        </div>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] ${verdictTone(
            model.verdict
          )}`}
        >
          {model.verdict_label}
        </span>
      </div>
      <p className="mt-2 text-[10px] uppercase tracking-[0.16em] text-slate-500">
        {model.present ? "On disk" : "Not downloaded"}
      </p>
      {canSelect ? (
        <button
          type="button"
          className="mt-2 rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700"
          onClick={onSelect}
          disabled={isSelected}
        >
          {isSelected ? "Selected" : "Use this model"}
        </button>
      ) : null}
    </div>
  );
}
