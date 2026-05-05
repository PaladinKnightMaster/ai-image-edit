type WorkflowLandingStateProps = {
  attachmentsCount: number;
  isEditMode: boolean;
  onModeChange: (mode: "edit" | "create") => void;
  onOpenHistory: () => void;
};

const editSteps = [
  {
    id: "base",
    label: "1. Bring in a base image",
    body: "Upload a portrait or pull a previous result from the output library without leaving the main flow."
  },
  {
    id: "guide",
    label: "2. Describe the change",
    body: "Use plain editing language first. Presets lead, and advanced controls stay secondary."
  },
  {
    id: "review",
    label: "3. Review and iterate",
    body: "Keep the output local, compare before and after, then save or run another round."
  }
];

const createSteps = [
  {
    id: "prompt",
    label: "1. Create a draft",
    body: "Use Create from Scratch when you need a starting image, not as the product's main destination."
  },
  {
    id: "select",
    label: "2. Pick a keeper",
    body: "Choose the generated result that is closest to your direction and hit Edit this."
  },
  {
    id: "bridge",
    label: "3. Finish in editing",
    body: "The strongest loop is still create, bridge to edit, compare, and save."
  }
];

export function WorkflowLandingState({
  attachmentsCount,
  isEditMode,
  onModeChange,
  onOpenHistory
}: WorkflowLandingStateProps) {
  const eyebrow = isEditMode ? "Primary workflow" : "Secondary workflow";
  const title = isEditMode ? "Start with a portrait." : "Create a draft, then finish in editing.";
  const body = isEditMode
    ? "Editing is the main product path now. Start with a base image, steer the change clearly, and keep the result local."
    : "Create from Scratch stays available, but it now supports the editing workflow instead of replacing it.";
  const steps = isEditMode ? editSteps : createSteps;

  return (
    <div className="rounded-3xl border border-slate-200/70 bg-gradient-to-br from-white via-slate-50 to-stone-100 p-6 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)]">
      <div className="max-w-2xl">
        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">{eyebrow}</p>
        <h2 className="mt-3 font-display text-3xl text-slate-900">{title}</h2>
        <p className="mt-3 text-sm text-slate-600">{body}</p>
      </div>
      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        {steps.map((step) => (
          <div
            key={step.id}
            className="rounded-3xl border border-slate-200/70 bg-white/90 p-5 shadow-[0_18px_45px_-35px_rgba(15,23,42,0.35)]"
          >
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{step.label}</p>
            <p className="mt-3 text-sm leading-relaxed text-slate-700">{step.body}</p>
          </div>
        ))}
      </div>
      <div className="mt-6 flex flex-wrap items-center gap-3 text-sm">
        {isEditMode ? (
          <>
            <button
              type="button"
              onClick={onOpenHistory}
              className="rounded-full border border-slate-900 px-4 py-2 font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
            >
              Open output library
            </button>
            <button
              type="button"
              onClick={() => onModeChange("create")}
              className="rounded-full border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition hover:border-slate-500 hover:text-slate-900"
            >
              Need a fresh draft first?
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={() => onModeChange("edit")}
              className="rounded-full border border-slate-900 px-4 py-2 font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white"
            >
              Back to Edit Photo
            </button>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              {attachmentsCount
                ? `${attachmentsCount} edit input${attachmentsCount > 1 ? "s" : ""} ready in edit mode`
                : "Create remains the supporting lane"}
            </p>
          </>
        )}
      </div>
    </div>
  );
}
