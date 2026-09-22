type ModeSwitchHeroProps = {
  attachmentsCount: number;
  isEditMode: boolean;
  onModeChange: (mode: "edit" | "create") => void;
};

export function ModeSwitchHero({
  attachmentsCount,
  isEditMode,
  onModeChange
}: ModeSwitchHeroProps) {
  const modeHeading = isEditMode ? "Edit Photo" : "Create from Scratch";
  const modeDescription = isEditMode
    ? "Start from a base image, use references only as visual guidance, compare the result, and keep refining locally."
    : "Draft something new here, then move the strongest result into Edit Photo with one click.";

  return (
    <header className="rounded-3xl border border-slate-200/70 bg-white/80 p-6 shadow-[0_25px_70px_-50px_rgba(15,23,42,0.6)] backdrop-blur motion-safe:animate-fade-up">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Studio session</p>
          <h1 className="mt-2 font-display text-3xl text-slate-900">{modeHeading}</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-600">{modeDescription}</p>
        </div>
      </div>
      <div className="mt-6 grid gap-3 md:grid-cols-2">
        <button
          type="button"
          onClick={() => onModeChange("edit")}
          className={`rounded-3xl border px-5 py-4 text-left transition ${
            isEditMode
              ? "border-slate-900 bg-slate-900 text-white shadow-[0_20px_50px_-35px_rgba(15,23,42,0.5)]"
              : "border-slate-200 bg-white text-slate-700 hover:border-slate-400"
          }`}
        >
          <p
            className={`text-xs uppercase tracking-[0.3em] ${
              isEditMode ? "text-slate-300" : "text-slate-500"
            }`}
          >
            Primary mode
          </p>
          <h2 className="mt-2 font-display text-2xl">Edit Photo</h2>
          <p className={`mt-2 text-sm ${isEditMode ? "text-slate-100" : "text-slate-600"}`}>
            Build around one base portrait. Add a reference only to guide lighting, style, framing, or angle.
          </p>
        </button>
        <button
          type="button"
          onClick={() => onModeChange("create")}
          className={`rounded-3xl border px-5 py-4 text-left transition ${
            !isEditMode
              ? "border-slate-900 bg-slate-900 text-white shadow-[0_20px_50px_-35px_rgba(15,23,42,0.5)]"
              : "border-slate-200 bg-white text-slate-700 hover:border-slate-400"
          }`}
        >
          <p
            className={`text-xs uppercase tracking-[0.3em] ${
              !isEditMode ? "text-slate-300" : "text-slate-500"
            }`}
          >
            Secondary mode
          </p>
          <h2 className="mt-2 font-display text-2xl">Create from Scratch</h2>
          <p className={`mt-2 text-sm ${!isEditMode ? "text-slate-100" : "text-slate-600"}`}>
            Create an initial draft here, then send a keeper into Edit Photo when you are ready.
          </p>
        </button>
      </div>
      {!isEditMode && attachmentsCount ? (
        <p className="mt-4 text-xs text-slate-500">
          {attachmentsCount} edit input{attachmentsCount > 1 ? "s stay" : " stays"} ready when you
          switch back to Edit Photo.
        </p>
      ) : null}
    </header>
  );
}
