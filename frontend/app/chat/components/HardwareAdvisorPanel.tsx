import type { HardwareAdvice, HardwareModelAdvice } from "../types";

type HardwareAdvisorPanelProps = {
  advice: HardwareAdvice | null;
  selectedModelId: string;
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

function ModelAdviceRow({
  model,
  isBest,
  isSelected,
  onSelect
}: {
  model: HardwareModelAdvice;
  isBest: boolean;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const canSelect = model.present && model.downloadable;
  return (
    <div
      className={`rounded-2xl border px-3 py-3 ${
        isBest
          ? "border-emerald-300/80 bg-emerald-50/70"
          : "border-slate-200/70 bg-white/90"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-semibold text-slate-800">
            {model.label}
            {isBest ? (
              <span className="ml-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-emerald-700">
                Best pick
              </span>
            ) : null}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {model.capabilities.join(" · ")} · {model.engine}
          </p>
          <p className="mt-2 text-xs leading-relaxed text-slate-600">{model.reason}</p>
        </div>
        <span
          className={`shrink-0 rounded-full px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] ${verdictTone(
            model.verdict
          )}`}
        >
          {model.verdict_label}
        </span>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span
          className={`rounded-full px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] ${
            model.present ? "bg-emerald-500 text-white" : "bg-rose-500 text-white"
          }`}
        >
          {model.present ? "on disk" : "not downloaded"}
        </span>
        {canSelect ? (
          <button
            type="button"
            className={`rounded-full border px-3 py-1 text-xs font-semibold transition ${
              isSelected
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-300 text-slate-700 hover:border-slate-900 hover:text-slate-900"
            }`}
            onClick={onSelect}
            disabled={isSelected}
          >
            {isSelected ? "Selected" : "Use this model"}
          </button>
        ) : null}
      </div>
    </div>
  );
}

export function HardwareAdvisorPanel({
  advice,
  selectedModelId,
  onSelectModel,
  onRefresh
}: HardwareAdvisorPanelProps) {
  const best = advice?.models.find((model) => model.id === advice.best_choice) ?? null;
  const canUseBest =
    Boolean(best?.present && best?.downloadable && best.id !== selectedModelId);

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
            Which local models fit this machine — same scan as{" "}
            <code className="text-[11px]">GET /api/hardware</code>.
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

          {advice.hardware.openvino_devices?.length ? (
            <p className="mt-2 text-xs text-slate-500">
              OpenVINO devices: {advice.hardware.openvino_devices.join(", ")}
            </p>
          ) : null}

          {canUseBest && best ? (
            <button
              type="button"
              className="mt-4 w-full rounded-full border border-slate-900 bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:-translate-y-0.5"
              onClick={() => onSelectModel(best.id)}
            >
              Use recommended: {best.label}
            </button>
          ) : null}

          <div className="mt-4 space-y-3">
            {advice.models.map((model) => (
              <ModelAdviceRow
                key={model.id}
                model={model}
                isBest={model.id === advice.best_choice}
                isSelected={model.id === selectedModelId}
                onSelect={() => onSelectModel(model.id)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
