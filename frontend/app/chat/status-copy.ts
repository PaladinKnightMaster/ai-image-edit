export const getJobStatusLabel = (status?: string | null) => {
  switch (status) {
    case "queued":
      return "Queued";
    case "running":
      return "Running locally";
    case "pending_review":
      return "Ready for review";
    case "succeeded":
      return "Complete";
    case "failed":
      return "Failed";
    default:
      return "Waiting";
  }
};

export const getStageLabel = (stage?: string | null) => {
  switch (stage) {
    case "queued":
      return "Queued";
    case "running":
      return "Running";
    case "review":
      return "Review";
    case "complete":
      return "Complete";
    default:
      return stage ? stage.replace(/_/g, " ") : null;
  }
};

export const getJobStatusTone = (status?: string | null) => {
  switch (status) {
    case "pending_review":
      return "bg-amber-100 text-amber-800";
    case "succeeded":
      return "bg-emerald-100 text-emerald-800";
    case "failed":
      return "bg-rose-100 text-rose-700";
    case "running":
      return "bg-sky-100 text-sky-800";
    case "queued":
      return "bg-slate-100 text-slate-600";
    default:
      return "bg-slate-100 text-slate-500";
  }
};

export const getJobStatusHelp = (status?: string | null) => {
  switch (status) {
    case "queued":
      return "Waiting for the local backend to start the job.";
    case "running":
      return "Local inference is active. CPU runs can take a long time; progress updates when the backend reports activity.";
    case "pending_review":
      return "The output is ready but hidden until you reveal it. Reveal before download or reuse.";
    case "succeeded":
      return "The output is available for compare, download, or reuse.";
    case "failed":
      return "The job stopped before producing a usable output. Retry if the setup issue is resolved, or copy debug info for investigation.";
    default:
      return "Waiting for a backend status update.";
  }
};

export const getFailureDetail = (error?: string | null) => {
  if (!error) {
    return "No backend error detail was recorded.";
  }
  if (error.toLowerCase().includes("server restarted")) {
    return "This job was marked failed during backend restart recovery. The run metadata is safe, but the job is not resumable.";
  }
  if (error.toLowerCase().includes("observer_timeout")) {
    return "The observer stopped waiting while the job may still have been active. Treat this as monitoring evidence, not model-quality failure.";
  }
  return error;
};
