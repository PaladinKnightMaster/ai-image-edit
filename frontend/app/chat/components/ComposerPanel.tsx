/* eslint-disable @next/next/no-img-element */

import type { ChangeEvent } from "react";

import type {
  ActiveDefaults,
  AttachmentItem,
  AttachmentRole,
  EditPreset,
  ModelInfo,
  PromptTemplate
} from "../types";

type ComposerPanelProps = {
  activeDefaults: ActiveDefaults;
  activeModel?: ModelInfo;
  activeReviewMode: string;
  attachments: AttachmentItem[];
  activeEditPresetId: string | null;
  backendUrl: string;
  editPresets: EditPreset[];
  editInputNotice: string | null;
  editModelConstraintNote: string | null;
  error: string | null;
  guidanceScale: string;
  height: string;
  isEditMode: boolean;
  isSubmitting: boolean;
  maxAttachments: number;
  modelOptions: ModelInfo[];
  negativePrompt: string;
  onApplyAcceptancePreset: () => void;
  onApplyDraftPreset: () => void;
  onApplyEditPreset: (preset: EditPreset) => void;
  onApplyPromptTemplate: (template: string) => void;
  onApplySmokePreset: () => void;
  onAttachImages: (event: ChangeEvent<HTMLInputElement>, slot: AttachmentRole) => void;
  onGuidanceScaleChange: (value: string) => void;
  onHeightChange: (value: string) => void;
  onHistoryPicker: (slot: AttachmentRole) => void;
  onNegativePromptChange: (value: string) => void;
  onPromptChange: (value: string) => void;
  onRemoveAttachment: (id: string) => void;
  onSeedChange: (value: string) => void;
  onSelectModel: (id: string) => void;
  onSettingsToggle: () => void;
  onStepsChange: (value: string) => void;
  onStrengthChange: (value: string) => void;
  onSubmit: () => void;
  onTrueCfgScaleChange: (value: string) => void;
  onWidthChange: (value: string) => void;
  prompt: string;
  promptPlaceholder: string;
  promptTemplates: PromptTemplate[];
  seed: string;
  selectedModelValue: string;
  settingsOpen: boolean;
  steps: string;
  strength: string;
  submitLabel: string;
  presetThumbnails?: Record<string, string>;
  trueCfgScale: string;
  width: string;
};

type SettingLabelProps = {
  label: string;
  tooltip: string;
};

const SettingLabel = ({ label, tooltip }: SettingLabelProps) => (
  <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-500">
    <span>{label}</span>
    <span
      className="inline-flex h-4 w-4 items-center justify-center rounded-full border border-slate-300 text-[10px] text-slate-500"
      title={tooltip}
      aria-label={tooltip}
    >
      i
    </span>
  </span>
);

const getAttachmentLabel = (item: AttachmentItem) => {
  if (item.kind === "upload") {
    return "Upload";
  }
  return item.origin === "generated" ? "Generated result" : "Library";
};

const getAttachmentSlot = (item: AttachmentItem, fallbackIndex = 0): AttachmentRole =>
  item.slot ?? (fallbackIndex === 0 ? "base" : "reference");

const getAttachmentBySlot = (attachments: AttachmentItem[], slot: AttachmentRole) =>
  attachments.find((item, index) => getAttachmentSlot(item, index) === slot);

const presetSwatch = (id: string) => {
  const swatches = [
    "bg-rose-200",
    "bg-amber-200",
    "bg-sky-200",
    "bg-emerald-200",
    "bg-violet-200",
    "bg-slate-300"
  ];
  const index = Math.abs(id.split("").reduce((sum, char) => sum + char.charCodeAt(0), 0)) % swatches.length;
  return swatches[index];
};

export function ComposerPanel({
  activeDefaults,
  activeModel,
  activeReviewMode,
  attachments,
  activeEditPresetId,
  backendUrl,
  editPresets,
  editInputNotice,
  editModelConstraintNote,
  error,
  guidanceScale,
  height,
  isEditMode,
  isSubmitting,
  maxAttachments,
  modelOptions,
  negativePrompt,
  onApplyAcceptancePreset,
  onApplyDraftPreset,
  onApplyEditPreset,
  onApplyPromptTemplate,
  onApplySmokePreset,
  onAttachImages,
  onGuidanceScaleChange,
  onHeightChange,
  onHistoryPicker,
  onNegativePromptChange,
  onPromptChange,
  onRemoveAttachment,
  onSeedChange,
  onSelectModel,
  onSettingsToggle,
  onStepsChange,
  onStrengthChange,
  onSubmit,
  onTrueCfgScaleChange,
  onWidthChange,
  prompt,
  promptPlaceholder,
  promptTemplates,
  seed,
  selectedModelValue,
  settingsOpen,
  steps,
  strength,
  submitLabel,
  presetThumbnails = {},
  trueCfgScale,
  width
}: ComposerPanelProps) {
  const baseAttachment = getAttachmentBySlot(attachments, "base");
  const referenceAttachment = getAttachmentBySlot(attachments, "reference");
  const referenceEnabled = maxAttachments > 1;
  const activeModelLabel = activeModel?.label ?? activeModel?.id ?? "No model selected";

  return (
    <div className="rounded-3xl border border-slate-200/70 bg-white/90 p-6 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)] backdrop-blur">
      {isEditMode ? (
        <div className="mb-5">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                Portrait presets
              </p>
              <p className="mt-1 text-xs text-slate-500">
                Pick a starting look in photography language, then fine-tune the prompt if needed.
              </p>
            </div>
            {activeEditPresetId ? (
              <span className="rounded-full bg-slate-900 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-white">
                Preset selected
              </span>
            ) : null}
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2" id="studio-presets">
            {editPresets.map((preset) => {
              const isActive = preset.id === activeEditPresetId;
              return (
                <button
                  key={preset.id}
                  type="button"
                  aria-label={`Edit preset ${preset.name}`}
                  onClick={() => onApplyEditPreset(preset)}
                  className={`w-40 shrink-0 rounded-2xl border p-3 text-left transition ${
                    isActive
                      ? "border-slate-900 bg-slate-900 text-white"
                      : "border-slate-200 bg-white text-slate-700 hover:border-slate-400"
                  }`}
                >
                  <span className="block h-16 overflow-hidden rounded-xl">
                    {presetThumbnails[preset.id] ? (
                      <img
                        src={`${backendUrl}/api/images/${presetThumbnails[preset.id]}`}
                        alt=""
                        className="h-full w-full object-cover"
                        data-testid={`preset-thumb-${preset.id}`}
                      />
                    ) : (
                      <span className={`block h-full ${presetSwatch(preset.id)}`} aria-hidden="true" />
                    )}
                  </span>
                  <span className="mt-2 block text-sm font-semibold">{preset.name}</span>
                  <span className={`mt-1 block text-[10px] uppercase tracking-[0.16em] ${isActive ? "text-slate-300" : "text-slate-500"}`}>
                    Use
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ) : null}
      {!isEditMode ? (
        <div className="mb-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <span className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
            Starter prompts
          </span>
          {promptTemplates.map((template) => (
            <button
              key={template.id}
              type="button"
              className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
              onClick={() => onApplyPromptTemplate(template.text)}
            >
              {template.label}
            </button>
          ))}
        </div>
      ) : null}
      <div
        id="studio-prompt"
        className="sticky top-0 z-20 -mx-2 mb-4 flex items-start gap-4 rounded-3xl bg-white/95 px-2 py-3 backdrop-blur"
      >
        <textarea
          value={prompt}
          onChange={(event) => onPromptChange(event.target.value)}
          placeholder={promptPlaceholder}
          className="min-h-[120px] w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20"
        />
        <div className="flex flex-col gap-3">
          {isEditMode ? (
            <span className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600">
              {referenceEnabled ? "Base identity + optional guide" : "Base image only"}
            </span>
          ) : null}
          <button
            type="button"
            disabled={isSubmitting}
            className="rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-[0_18px_40px_-28px_rgba(15,23,42,0.6)] transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={onSubmit}
          >
            {submitLabel}
          </button>
        </div>
      </div>

      {isEditMode && editInputNotice ? (
        <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          <p className="text-[10px] uppercase tracking-[0.2em] text-emerald-700">
            Edit bridge ready
          </p>
          <p className="mt-2 leading-relaxed">{editInputNotice}</p>
        </div>
      ) : null}

      {isEditMode && editModelConstraintNote ? (
        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
          <p className="text-[10px] uppercase tracking-[0.2em] text-amber-700">
            Model lane note
          </p>
          <p className="mt-2 leading-relaxed">{editModelConstraintNote}</p>
        </div>
      ) : null}

      {isEditMode ? (
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          {([
            {
              slot: "base" as const,
              eyebrow: "Primary input",
              title: "Base image",
              description: "Required. This portrait is the identity and source image for the edit.",
              attachment: baseAttachment
            },
            {
              slot: "reference" as const,
              eyebrow: "Optional guide",
              title: "Reference image",
              description: referenceEnabled
                ? "Optional. Guides lighting, style, framing, or angle without replacing the base identity."
                : "This model currently supports only one input image.",
              attachment: referenceAttachment
            }
          ]).map((slotCard) => (
            (() => {
              const slotAttachment = slotCard.attachment;

              return (
                <div
                  key={slotCard.slot}
                  data-testid={`input-slot-${slotCard.slot}`}
                  className={`rounded-2xl border p-4 ${
                    slotCard.slot === "reference" && !referenceEnabled
                      ? "border-slate-200/70 bg-slate-50/70"
                      : "border-slate-200 bg-white"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                        {slotCard.eyebrow}
                      </p>
                      <h3 className="mt-2 text-sm font-semibold text-slate-900">{slotCard.title}</h3>
                      <p className="mt-2 text-xs leading-relaxed text-slate-600">
                        {slotCard.description}
                      </p>
                    </div>
                    {slotAttachment ? (
                      <button
                        type="button"
                        onClick={() => onRemoveAttachment(slotAttachment.id)}
                        className="rounded-full border border-slate-300 px-3 py-1 text-[11px] font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
                      >
                        Remove
                      </button>
                    ) : null}
                  </div>

                  {slotAttachment ? (
                    <div className="relative mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
                      <img
                        src={
                          slotAttachment.previewUrl ||
                          (slotAttachment.kind === "history"
                            ? `${backendUrl}/api/images/${slotAttachment.imageId}`
                            : "")
                        }
                        alt={slotCard.title}
                        className="h-40 w-full object-cover"
                      />
                      <span className="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-600">
                        {getAttachmentLabel(slotAttachment)}
                      </span>
                    </div>
                  ) : (
                    <div className="mt-4 flex h-40 items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white/70 px-4 text-center text-xs leading-relaxed text-slate-500">
                      {slotCard.slot === "base"
                        ? "Choose the portrait whose identity and details should stay central."
                        : referenceEnabled
                          ? "Add a second image only when you need visual direction, not a new subject."
                          : "Reference input is unavailable for the selected model."}
                    </div>
                  )}

                  <div className="mt-4 flex flex-wrap gap-2">
                    <label
                      className={`cursor-pointer rounded-full border px-3 py-2 text-xs font-semibold transition ${
                        slotCard.slot === "base" || referenceEnabled
                          ? "border-slate-900 text-slate-900 hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
                          : "cursor-not-allowed border-slate-200 text-slate-400"
                      }`}
                    >
                      {slotAttachment ? "Replace upload" : "Upload image"}
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        disabled={slotCard.slot === "reference" && !referenceEnabled}
                        onChange={(event) => onAttachImages(event, slotCard.slot)}
                      />
                    </label>
                    <button
                      type="button"
                      disabled={slotCard.slot === "reference" && !referenceEnabled}
                      onClick={() => onHistoryPicker(slotCard.slot)}
                      className={`rounded-full border px-3 py-2 text-xs font-semibold transition ${
                        slotCard.slot === "base" || referenceEnabled
                          ? "border-slate-900/60 text-slate-700 hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                          : "cursor-not-allowed border-slate-200 text-slate-400"
                      }`}
                >
                      {slotAttachment ? "Replace from library" : "Pick from library"}
                    </button>
                  </div>
                </div>
              );
            })()
          ))}
        </div>
      ) : null}

      <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
        {isEditMode ? (
          <span>
            {baseAttachment
              ? referenceEnabled && referenceAttachment
                ? "Base identity and reference guidance are ready for the edit run."
                : "Base image is ready. Add a reference only if it improves visual direction."
              : "Add a base image to start the edit flow."}
          </span>
        ) : (
          <span>Create from Scratch stays text-led. Move a keeper into Edit Photo when you are ready.</span>
        )}
        {error ? (
          <span className="text-rose-600" data-testid="composer-error" role="alert">
            {error}
          </span>
        ) : null}
      </div>

      <div className="mt-4 rounded-2xl border border-slate-200/70 bg-slate-50/90 p-4">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
              Advanced controls
            </p>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">
              Model choice and raw tuning stay here so presets, prompt, and image inputs remain the
              main workflow.
            </p>
            <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
              <span className="rounded-full border border-slate-200 bg-white px-3 py-1 font-semibold text-slate-700">
                Model: {activeModelLabel}
              </span>
              {activeReviewMode === "manual" ? (
                <span className="rounded-full bg-amber-200 px-3 py-1 font-semibold text-amber-900">
                  Manual review
                </span>
              ) : null}
              {activeModel && !activeModel.present ? (
                <span className="rounded-full bg-rose-200 px-3 py-1 font-semibold text-rose-900">
                  Missing files
                </span>
              ) : null}
            </div>
          </div>
          <button
            type="button"
            className="rounded-full border border-slate-900 px-4 py-2 text-xs font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
            onClick={onSettingsToggle}
          >
            {settingsOpen ? "Hide advanced controls" : "Open advanced controls"}
          </button>
        </div>

        {settingsOpen ? (
          <div className="mt-4 grid gap-4 rounded-2xl border border-slate-100 bg-white/80 p-4 text-sm text-slate-700">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  Model and run profile
                </div>
                <p className="mt-2 text-xs text-slate-500">
                  Adjust these only when presets or prompt guidance are not enough.
                </p>
              </div>
              <select
                value={selectedModelValue}
                onChange={(event) => onSelectModel(event.target.value)}
                disabled={!modelOptions.length}
                className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm"
              >
                {modelOptions.map((model) => (
                  <option key={model.id} value={model.id} disabled={!model.present}>
                    {model.label ?? model.id}
                    {model.present ? "" : " (missing)"}
                  </option>
                ))}
              </select>
            </div>
            {activeModel && !activeModel.present && activeModel.detail ? (
              <p className="text-xs text-rose-700">{activeModel.detail}</p>
            ) : null}

            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Run profile</div>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                  onClick={onApplySmokePreset}
                >
                  Smoke
                </button>
                <button
                  type="button"
                  className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                  onClick={onApplyDraftPreset}
                >
                  Draft
                </button>
                <button
                  type="button"
                  className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                  onClick={onApplyAcceptancePreset}
                >
                  Acceptance
                </button>
              </div>
            </div>
            <p className="text-xs text-slate-500">
              Smoke = correctness, Draft = daily iteration, Acceptance = checkpoint quality review.
            </p>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <SettingLabel
                  label="Negative prompt"
                  tooltip="Optional terms to steer away from."
                />
                <input
                  value={negativePrompt}
                  onChange={(event) => onNegativePromptChange(event.target.value)}
                  disabled={isEditMode}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder="Optional"
                />
              </label>
              <label className="space-y-2">
                <SettingLabel label="Seed" tooltip="Same seed + params gives similar results." />
                <input
                  value={seed}
                  onChange={(event) => onSeedChange(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder="Leave blank for random"
                />
              </label>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <SettingLabel label="Steps" tooltip="More steps = slower, often sharper." />
                <input
                  value={steps}
                  onChange={(event) => onStepsChange(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder={String(activeDefaults.steps)}
                />
              </label>
              <label className="space-y-2">
                <SettingLabel
                  label="Guidance scale"
                  tooltip="How strongly the prompt is followed."
                />
                <input
                  value={guidanceScale}
                  onChange={(event) => onGuidanceScaleChange(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder={
                    activeDefaults.guidance_scale !== undefined
                      ? String(activeDefaults.guidance_scale)
                      : "Optional"
                  }
                />
              </label>
            </div>

            {isEditMode && activeDefaults.strength !== undefined ? (
              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-2">
                  <SettingLabel
                    label="Strength"
                    tooltip="How much to change the input image (0-1)."
                  />
                  <input
                    value={strength}
                    onChange={(event) => onStrengthChange(event.target.value)}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder={
                      activeDefaults.strength !== undefined
                        ? String(activeDefaults.strength)
                        : "0.65"
                    }
                  />
                </label>
              </div>
            ) : null}

            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <SettingLabel
                  label="True CFG scale"
                  tooltip="Qwen-specific guidance. 1.0 disables."
                />
                <input
                  value={trueCfgScale}
                  onChange={(event) => onTrueCfgScaleChange(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder={
                    activeDefaults.true_cfg_scale !== undefined
                      ? String(activeDefaults.true_cfg_scale)
                      : "Optional"
                  }
                />
              </label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="space-y-2">
                  <SettingLabel
                    label="Width"
                    tooltip="Output size in pixels (divisible by 8)."
                  />
                  <input
                    value={width}
                    onChange={(event) => onWidthChange(event.target.value)}
                    disabled={isEditMode}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder={String(activeDefaults.width)}
                  />
                </label>
                <label className="space-y-2">
                  <SettingLabel
                    label="Height"
                    tooltip="Output size in pixels (divisible by 8)."
                  />
                  <input
                    value={height}
                    onChange={(event) => onHeightChange(event.target.value)}
                    disabled={isEditMode}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder={String(activeDefaults.height)}
                  />
                </label>
              </div>
            </div>
          </div>
        ) : (
          <p className="mt-4 text-xs text-slate-500">
            Presets, prompt, and the base/guide image slots stay in the main workflow. Open this
            drawer only when you need manual tuning or a different model lane.
          </p>
        )}
      </div>
    </div>
  );
}
