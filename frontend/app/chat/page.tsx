
"use client";

/* eslint-disable @next/next/no-img-element */

import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

type SystemInfo = {
  profile: string;
  profile_reason: string;
  hardware: {
    has_cuda?: boolean;
    vram_gb?: number;
    device_name?: string;
    ram_gb?: number;
  };
  defaults: {
    width: number;
    height: number;
    steps: number;
  };
  limits: {
    max_width: number;
    max_height: number;
    max_steps: number;
  };
  memory: {
    attention_slicing: boolean;
    vae_slicing: boolean;
    vae_tiling: boolean;
  };
  storage?: {
    data_root?: string;
    images_bytes?: number;
    flux_outputs_bytes?: number;
    db_bytes?: number;
    db_wal_bytes?: number;
    db_shm_bytes?: number;
    total_bytes?: number;
    disk_free_bytes?: number;
    disk_total_bytes?: number;
  };
};

type ModelInfo = {
  id: string;
  label?: string;
  capabilities: string[];
  present: boolean;
  local_path?: string | null;
  revision?: string | null;
  detail?: string | null;
  defaults?: {
    steps?: number;
    width?: number;
    height?: number;
    guidance_scale?: number;
    true_cfg_scale?: number;
    strength?: number;
  };
  review_mode?: string | null;
};

type RunRecord = {
  id: string;
  job_id: string;
  model_id: string;
  prompt: string;
  negative_prompt?: string | null;
  seed: number;
  steps: number;
  width?: number | null;
  height?: number | null;
  guidance_scale?: number | null;
  true_cfg_scale?: number | null;
  strength?: number | null;
  input_image_ids?: string[] | null;
  output_image_id?: string | null;
  latency_ms?: number | null;
  type?: string | null;
  status?: string | null;
  error?: string | null;
  created_at?: number | null;
  finished_at?: number | null;
};

type ReadyState = {
  ready: boolean;
  status: string;
  details: Record<string, unknown>;
};

type AttachmentDraft = {
  id: string;
  kind: "upload";
  file: File;
  previewUrl: string;
};

type AttachmentHistory = {
  id: string;
  kind: "history";
  imageId: string;
  previewUrl: string;
};

type AttachmentItem = AttachmentDraft | AttachmentHistory;

type AttachmentSnapshot = {
  id: string;
  previewUrl: string;
  source?: "upload" | "history";
  imageId?: string;
};

type JobRequest = {
  mode: "t2i" | "edit";
  modelId: string;
  params: Record<string, unknown>;
  inputPreviews?: AttachmentSnapshot[];
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  createdAt: number;
  startedAt?: number;
  mode?: "generate" | "edit";
  prompt?: string;
  attachments?: AttachmentSnapshot[];
  jobId?: string;
  status?: string;
  stage?: string;
  progress?: number;
  stageElapsedMs?: number;
  etaMs?: number;
  outputImageId?: string;
  requiresReview?: boolean;
  reviewNote?: string;
  error?: string;
  run?: RunRecord;
  request?: JobRequest;
};

const STORAGE_KEY = "ai-image-chat-thread-v1";
const MODEL_PREF_KEY = "ai-image-chat-model-v1";
const MODEL_T2I = "qwen-image-2512";
const PROMPT_TEMPLATES = [
  {
    id: "portrait",
    label: "Portrait (natural)",
    text: "A realistic portrait photo with natural skin texture, subtle imperfections, soft diffused light, 50mm lens, balanced contrast, documentary style."
  },
  {
    id: "product",
    label: "Product (studio)",
    text: "A clean studio product photo on a seamless backdrop, soft box lighting, crisp edges, realistic materials, minimal shadows."
  },
  {
    id: "cinematic",
    label: "Cinematic scene",
    text: "A cinematic wide shot, atmospheric lighting, depth, subtle grain, realistic color grading, dramatic but natural shadows."
  }
];

const makeId = () => `${Date.now().toString(36)}${Math.random().toString(16).slice(2)}`;

const formatTime = (timestamp?: number) => {
  if (!timestamp) {
    return "";
  }
  return new Date(timestamp).toLocaleTimeString();
};

const formatLatency = (latency?: number | null) => {
  if (!latency) {
    return "n/a";
  }
  if (latency < 1000) {
    return `${latency} ms`;
  }
  return `${(latency / 1000).toFixed(2)} s`;
};

const formatBytes = (bytes?: number | null) => {
  if (!bytes && bytes !== 0) {
    return "n/a";
  }
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let idx = 0;
  while (value >= 1024 && idx < units.length - 1) {
    value /= 1024;
    idx += 1;
  }
  return `${value.toFixed(value >= 10 ? 1 : 2)} ${units[idx]}`;
};

const formatDuration = (ms?: number | null) => {
  if (!ms && ms !== 0) {
    return "n/a";
  }
  const totalSeconds = Math.max(0, Math.round(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  }
  return `${seconds}s`;
};

const readFileAsDataUrl = (file: File) =>
  new Promise<string>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });

const parseIntOr = (value: string, fallback: number) => {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const parseFloatOr = (value: string) => {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : undefined;
};

const parseErrorMessage = async (response: Response) => {
  const text = await response.text();
  if (!text) {
    return "Request failed.";
  }
  try {
    const payload = JSON.parse(text) as { error?: { message?: string } };
    return payload?.error?.message ?? text;
  } catch {
    return text;
  }
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

export default function ChatPage() {
  const backendUrl = useMemo(
    () => process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000",
    []
  );
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [readyState, setReadyState] = useState<ReadyState | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [recentRuns, setRecentRuns] = useState<RunRecord[]>([]);
  const [failedRuns, setFailedRuns] = useState<RunRecord[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [selectedModelId, setSelectedModelId] = useState(MODEL_T2I);
  const [prompt, setPrompt] = useState("");
  const [negativePrompt, setNegativePrompt] = useState("");
  const [seed, setSeed] = useState("");
  const [steps, setSteps] = useState("");
  const [width, setWidth] = useState("");
  const [height, setHeight] = useState("");
  const [guidanceScale, setGuidanceScale] = useState("");
  const [trueCfgScale, setTrueCfgScale] = useState("");
  const [strength, setStrength] = useState("");
  const [attachments, setAttachments] = useState<AttachmentItem[]>([]);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyRuns, setHistoryRuns] = useState<RunRecord[]>([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [maintenanceOpen, setMaintenanceOpen] = useState(false);
  const [importWarnings, setImportWarnings] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteImagesOnCleanup, setDeleteImagesOnCleanup] = useState(false);
  const eventSources = useRef<Map<string, EventSource>>(new Map());
  const timelineRef = useRef<HTMLDivElement | null>(null);
  const importInputRef = useRef<HTMLInputElement | null>(null);
  const lastDefaultsRef = useRef({ steps: "", width: "", height: "" });

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ChatMessage[];
        setMessages(parsed);
      } catch {
        setMessages([]);
      }
    }
    const storedModel = localStorage.getItem(MODEL_PREF_KEY);
    if (storedModel) {
      setSelectedModelId(storedModel);
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    const activeEventSources = eventSources.current;
    return () => {
      activeEventSources.forEach((source) => source.close());
      activeEventSources.clear();
    };
  }, []);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages, hydrated]);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    localStorage.setItem(MODEL_PREF_KEY, selectedModelId);
  }, [selectedModelId, hydrated]);

  useEffect(() => {
    const container = timelineRef.current;
    if (!container) {
      return;
    }
    container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const loadSystem = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl}/api/system`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as SystemInfo;
      setSystemInfo(data);
      setSteps((current) => current || String(data.defaults.steps));
      setWidth((current) => current || String(data.defaults.width));
      setHeight((current) => current || String(data.defaults.height));
    } catch {
      // ignore
    }
  }, [backendUrl]);

  const loadReady = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl}/ready`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as ReadyState;
      setReadyState(data);
    } catch {
      // ignore
    }
  }, [backendUrl]);

  const loadModels = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl}/api/models`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as ModelInfo[];
      setModels(data);
      setSelectedModelId((current) => {
        if (data.some((model) => model.id === current)) {
          return current;
        }
        const fallback = data.find((model) => model.capabilities.includes("t2i"));
        return fallback?.id ?? data[0]?.id ?? current;
      });
    } catch {
      // ignore
    }
  }, [backendUrl]);

  const loadRuns = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl}/api/runs?limit=6`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as RunRecord[];
      setRecentRuns(data);
    } catch {
      // ignore
    }
  }, [backendUrl]);

  const loadHistoryRuns = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl}/api/runs?limit=50`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as RunRecord[];
      setHistoryRuns(data);
    } catch {
      // ignore
    }
  }, [backendUrl]);

  const loadFailedRuns = useCallback(async () => {
    try {
      const response = await fetch(
        `${backendUrl}/api/runs?status=failed&limit=6`,
        { cache: "no-store" }
      );
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as RunRecord[];
      setFailedRuns(data);
    } catch {
      // ignore
    }
  }, [backendUrl]);

  const removeRunFromState = (runId: string) => {
    setRecentRuns((runs) => runs.filter((run) => run.id !== runId));
    setFailedRuns((runs) => runs.filter((run) => run.id !== runId));
    setHistoryRuns((runs) => runs.filter((run) => run.id !== runId));
  };

  const deleteRun = async (runId: string) => {
    try {
      const response = await fetch(
        `${backendUrl}/api/runs/${runId}${deleteImagesOnCleanup ? "?delete_images=1" : ""}`,
        {
          method: "DELETE"
        }
      );
      if (!response.ok) {
        setError(await parseErrorMessage(response));
        return;
      }
      removeRunFromState(runId);
      setError(null);
    } catch {
      setError("Failed to delete run.");
    }
  };

  const clearRecentRuns = async () => {
    try {
      const response = await fetch(
        `${backendUrl}/api/runs?limit=6${deleteImagesOnCleanup ? "&delete_images=1" : ""}`,
        {
          method: "DELETE"
        }
      );
      if (!response.ok) {
        setError(await parseErrorMessage(response));
        return;
      }
      await Promise.all([loadRuns(), loadFailedRuns(), loadHistoryRuns()]);
      setError(null);
    } catch {
      setError("Failed to clear recent runs.");
    }
  };

  const clearFailedRuns = async () => {
    try {
      const response = await fetch(
        `${backendUrl}/api/runs?status=failed${deleteImagesOnCleanup ? "&delete_images=1" : ""}`,
        {
          method: "DELETE"
        }
      );
      if (!response.ok) {
        setError(await parseErrorMessage(response));
        return;
      }
      await Promise.all([loadFailedRuns(), loadRuns(), loadHistoryRuns()]);
      setError(null);
    } catch {
      setError("Failed to clear failed runs.");
    }
  };

  useEffect(() => {
    void loadSystem();
    void loadModels();
    void loadRuns();
    void loadReady();
    void loadFailedRuns();
  }, [loadSystem, loadModels, loadRuns, loadReady, loadFailedRuns]);

  useEffect(() => {
    if (!models.length) {
      return;
    }
    const mode = attachments.length ? "edit" : "t2i";
    const selected = models.find((model) => model.id === selectedModelId);
    const supportsMode = selected?.capabilities.includes(mode);
    if (supportsMode) {
      return;
    }
    const fallback = models.find((model) => model.capabilities.includes(mode));
    if (fallback) {
      setSelectedModelId(fallback.id);
    }
  }, [attachments.length, models, selectedModelId]);

  const activeModel = models.find((model) => model.id === selectedModelId);
  const activeDefaults = {
    steps: activeModel?.defaults?.steps ?? systemInfo?.defaults.steps ?? 24,
    width: activeModel?.defaults?.width ?? systemInfo?.defaults.width ?? 1024,
    height: activeModel?.defaults?.height ?? systemInfo?.defaults.height ?? 1024,
    guidance_scale: activeModel?.defaults?.guidance_scale,
    true_cfg_scale: activeModel?.defaults?.true_cfg_scale,
    strength: activeModel?.defaults?.strength
  };
  const activeReviewMode = activeModel?.review_mode ?? "off";
  const activeMode = attachments.length ? "edit" : "t2i";
  const selectableModels = models.filter((model) => model.capabilities.includes(activeMode));
  const maxAttachments = activeModel?.id === "flux2-klein-9b-gguf" ? 1 : 2;

  const applyDraftPreset = () => {
    if (activeModel?.id === "flux2-klein-9b-gguf") {
      setSteps("8");
      setGuidanceScale("4.0");
      if (!attachments.length) {
        setWidth("512");
        setHeight("512");
      }
      if (attachments.length) {
        setStrength("0.6");
      }
      return;
    }

    if (activeModel?.id?.startsWith("qwen-image")) {
      setSteps("12");
      setGuidanceScale("4.0");
      setTrueCfgScale("1.2");
      if (!attachments.length) {
        setWidth("512");
        setHeight("512");
      }
      if (attachments.length) {
        setStrength("0.6");
      }
    }
  };

  const applySmokePreset = () => {
    if (activeModel?.id === "flux2-klein-9b-gguf") {
      setSteps("4");
      setGuidanceScale("3.5");
      if (!attachments.length) {
        setWidth("512");
        setHeight("512");
      }
      if (attachments.length) {
        setStrength("0.55");
      }
      return;
    }

    if (activeModel?.id?.startsWith("qwen-image")) {
      setSteps("8");
      setGuidanceScale("3.5");
      setTrueCfgScale("1.1");
      if (!attachments.length) {
        setWidth("512");
        setHeight("512");
      }
      if (attachments.length) {
        setStrength("0.55");
      }
    }
  };

  const applyAcceptancePreset = () => {
    if (activeModel?.id === "flux2-klein-9b-gguf") {
      setSteps("12");
      setGuidanceScale("4.5");
      if (!attachments.length) {
        setWidth("768");
        setHeight("768");
      }
      if (attachments.length) {
        setStrength("0.65");
      }
      return;
    }

    if (activeModel?.id?.startsWith("qwen-image")) {
      setSteps("20");
      setGuidanceScale("5.0");
      setTrueCfgScale("1.4");
      if (!attachments.length) {
        setWidth("768");
        setHeight("768");
      }
      if (attachments.length) {
        setStrength("0.65");
      }
    }
  };

  const applyPromptTemplate = (template: string) => {
    setPrompt((current) => (current ? `${current}\n\n${template}` : template));
  };

  useEffect(() => {
    const nextDefaults = {
      steps: String(activeDefaults.steps),
      width: String(activeDefaults.width),
      height: String(activeDefaults.height)
    };
    setSteps((current) =>
      current === "" || current === lastDefaultsRef.current.steps
        ? nextDefaults.steps
        : current
    );
    setWidth((current) =>
      current === "" || current === lastDefaultsRef.current.width
        ? nextDefaults.width
        : current
    );
    setHeight((current) =>
      current === "" || current === lastDefaultsRef.current.height
        ? nextDefaults.height
        : current
    );
    if (activeModel?.id === "flux2-klein-9b-gguf" && activeDefaults.strength !== undefined) {
      setStrength((current) =>
        current === "" ? String(activeDefaults.strength) : current
      );
    }
    lastDefaultsRef.current = nextDefaults;
  }, [activeDefaults.steps, activeDefaults.width, activeDefaults.height, activeDefaults.strength, activeModel?.id]);

  const updateMessageByJob = useCallback((jobId: string, patch: Partial<ChatMessage>) => {
    setMessages((current) =>
      current.map((message) => (message.jobId === jobId ? { ...message, ...patch } : message))
    );
  }, []);

  const updateMessageById = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages((current) =>
      current.map((message) => (message.id === id ? { ...message, ...patch } : message))
    );
  }, []);

  const fetchJob = useCallback(async (jobId: string) => {
    try {
      const response = await fetch(`${backendUrl}/api/jobs/${jobId}`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      updateMessageByJob(jobId, {
        status: data.status,
        run: data.run,
        outputImageId: data.run?.output_image_id ?? undefined,
        requiresReview: data.status === "pending_review",
        reviewNote: data.status === "pending_review" ? "Manual review required." : undefined,
        ...(data.status === "pending_review" ? { stage: "review" } : {})
      });
      if (data.status === "succeeded" || data.status === "failed" || data.status === "pending_review") {
        eventSources.current.get(jobId)?.close();
        eventSources.current.delete(jobId);
        loadRuns();
      }
    } catch {
      // ignore
    }
  }, [backendUrl, loadRuns, updateMessageByJob]);

  const attachEventSource = useCallback((jobId: string) => {
    if (eventSources.current.has(jobId)) {
      return;
    }
    const source = new EventSource(`${backendUrl}/api/jobs/${jobId}/events`);
    source.addEventListener("status", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      const patch: Partial<ChatMessage> = { status: payload.status };
      if (payload.status === "running") {
        patch.startedAt = Date.now();
      }
      updateMessageByJob(jobId, patch);
    });
    source.addEventListener("stage", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      updateMessageByJob(jobId, {
        stage: payload.stage,
        stageElapsedMs:
          typeof payload.elapsed_ms === "number" ? payload.elapsed_ms : undefined
      });
    });
    source.addEventListener("progress", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      const elapsedMs =
        typeof payload.elapsed_ms === "number" ? payload.elapsed_ms : undefined;
      const etaMs =
        elapsedMs && payload.percent > 0
          ? Math.max(0, (elapsedMs / payload.percent) * (100 - payload.percent))
          : undefined;
      updateMessageByJob(jobId, {
        progress: payload.percent,
        etaMs,
        stageElapsedMs: elapsedMs
      });
    });
    source.addEventListener("result", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      updateMessageByJob(jobId, {
        status: "succeeded",
        outputImageId: payload.output_image_id,
        stage: "complete",
        progress: 100
      });
      fetchJob(jobId);
    });
    source.addEventListener("review_required", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      updateMessageByJob(jobId, {
        status: "pending_review",
        requiresReview: true,
        reviewNote: payload.message,
        stage: "review"
      });
      source.close();
      eventSources.current.delete(jobId);
      loadRuns();
    });
    source.addEventListener("error", (event) => {
      try {
        const payload = JSON.parse((event as MessageEvent).data);
        updateMessageByJob(jobId, { status: "failed", error: payload.message });
      } catch {
        updateMessageByJob(jobId, { status: "failed", error: "Stream disconnected." });
      }
      source.close();
      eventSources.current.delete(jobId);
    });
    source.onerror = () => {
      updateMessageByJob(jobId, { error: "Stream disconnected." });
    };
    eventSources.current.set(jobId, source);
  }, [backendUrl, fetchJob, loadRuns, updateMessageByJob]);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    messages
      .filter((message) => message.role === "assistant" && message.jobId)
      .forEach((message) => {
        if (!message.jobId) {
          return;
        }
        if (message.status === "succeeded" || message.status === "failed") {
          return;
        }
        fetchJob(message.jobId);
        attachEventSource(message.jobId);
      });
  }, [attachEventSource, fetchJob, hydrated, messages]);

  const handleAttachImages = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files ?? []);
    if (!files.length) {
      return;
    }
    setError(null);
    if (attachments.length + files.length > maxAttachments) {
      setError(`Attach up to ${maxAttachments} image${maxAttachments > 1 ? "s" : ""}.`);
      event.target.value = "";
      return;
    }
    const previews = await Promise.all(
      files.map(async (file) => ({
        id: makeId(),
        kind: "upload" as const,
        file,
        previewUrl: await readFileAsDataUrl(file)
      }))
    );
    setAttachments((current) => [...current, ...previews]);
    event.target.value = "";
  };

  const removeAttachment = (id: string) => {
    setAttachments((current) => current.filter((item) => item.id !== id));
  };

  const addHistoryAttachment = (imageId: string) => {
    setError(null);
    setAttachments((current) => {
      if (current.length >= maxAttachments) {
        setError(`Attach up to ${maxAttachments} image${maxAttachments > 1 ? "s" : ""}.`);
        return current;
      }
      if (current.some((item) => item.kind === "history" && item.imageId === imageId)) {
        return current;
      }
      return [
        ...current,
        {
          id: makeId(),
          kind: "history",
          imageId,
          previewUrl: `${backendUrl}/api/images/${imageId}`
        }
      ];
    });
  };

  const openHistoryPicker = async () => {
    await loadHistoryRuns();
    setHistoryOpen(true);
  };

  const uploadImage = async (item: AttachmentDraft) => {
    const payload = new FormData();
    payload.append("file", item.file, item.file.name);
    const response = await fetch(`${backendUrl}/api/images/upload`, {
      method: "POST",
      body: payload
    });
    if (!response.ok) {
      const detail = await parseErrorMessage(response);
      throw new Error(detail || "Image upload failed.");
    }
    const data = (await response.json()) as { image_id: string };
    return data.image_id;
  };

  const submitJob = async (request: JobRequest, userMessage?: ChatMessage) => {
    const assistantId = makeId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      createdAt: Date.now(),
      status: "queued",
      stage: "queued",
      request
    };
    setMessages((current) => [
      ...current,
      ...(userMessage ? [userMessage] : []),
      assistantMessage
    ]);

    const endpoint = request.mode === "t2i" ? "/api/jobs/t2i" : "/api/jobs/edit";
    try {
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_id: request.modelId, ...request.params })
      });
      if (!response.ok) {
        const detail = await parseErrorMessage(response);
        throw new Error(detail || "Job submission failed.");
      }
      const data = (await response.json()) as { job_id: string };
      updateMessageById(assistantId, { jobId: data.job_id });
      attachEventSource(data.job_id);
      fetchJob(data.job_id);
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Job submission failed.";
      updateMessageById(assistantId, { status: "failed", error: message });
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError("Add a prompt before generating.");
      return;
    }
    const isEdit = attachments.length > 0;
    if (isEdit && attachments.length === 0) {
      setError("Attach at least one image to edit.");
      return;
    }
    if (attachments.length > maxAttachments) {
      setError(`This model supports up to ${maxAttachments} input image${maxAttachments > 1 ? "s" : ""}.`);
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      const mode = isEdit ? "edit" : "t2i";
      const modelForMode =
        models.find(
          (model) => model.id === selectedModelId && model.capabilities.includes(mode)
        ) ?? models.find((model) => model.capabilities.includes(mode));
      if (!modelForMode) {
        throw new Error(`No model available for ${mode}.`);
      }
      if (!modelForMode.present) {
        const detail = modelForMode.detail ? ` ${modelForMode.detail}` : "";
        throw new Error(
          `Model files missing for ${modelForMode.label ?? modelForMode.id}.${detail}`
        );
      }
      if (modelForMode.id !== selectedModelId) {
        setSelectedModelId(modelForMode.id);
      }

      const defaults = {
        width: modelForMode.defaults?.width ?? systemInfo?.defaults.width ?? 1024,
        height: modelForMode.defaults?.height ?? systemInfo?.defaults.height ?? 1024,
        steps: modelForMode.defaults?.steps ?? systemInfo?.defaults.steps ?? 24,
        guidance_scale: modelForMode.defaults?.guidance_scale,
        true_cfg_scale: modelForMode.defaults?.true_cfg_scale,
        strength: modelForMode.defaults?.strength
      };
      const limits = systemInfo?.limits ?? {
        max_width: 2048,
        max_height: 2048,
        max_steps: 60
      };
      const stepsValue = parseIntOr(steps, defaults.steps);
      if (stepsValue > limits.max_steps) {
        throw new Error(`Steps exceed max ${limits.max_steps}.`);
      }

      const widthValue = parseIntOr(width, defaults.width);
      const heightValue = parseIntOr(height, defaults.height);
      if (!isEdit) {
        if (widthValue > limits.max_width || heightValue > limits.max_height) {
          throw new Error(`Resolution exceeds ${limits.max_width}x${limits.max_height}.`);
        }
        if (widthValue % 8 !== 0 || heightValue % 8 !== 0) {
          throw new Error("Width and height must be divisible by 8.");
        }
      }

      let imageIds: string[] = [];
      let attachmentSnapshots: AttachmentSnapshot[] = [];
      if (isEdit) {
        imageIds = await Promise.all(
          attachments.map(async (item) =>
            item.kind === "history" ? item.imageId : uploadImage(item)
          )
        );
        attachmentSnapshots = attachments.map((item, index) => ({
          id: item.id,
          previewUrl: item.previewUrl,
          source: item.kind,
          imageId: imageIds[index]
        }));
      }

      const params: Record<string, unknown> = {
        prompt: prompt.trim(),
        steps: stepsValue
      };
      const parsedGuidance = guidanceScale.trim()
        ? parseFloatOr(guidanceScale)
        : defaults.guidance_scale;
      if (parsedGuidance !== undefined) {
        params.guidance_scale = parsedGuidance;
      }
      const parsedTrueCfg = trueCfgScale.trim()
        ? parseFloatOr(trueCfgScale)
        : defaults.true_cfg_scale;
      if (parsedTrueCfg !== undefined) {
        params.true_cfg_scale = parsedTrueCfg;
      }
      if (seed.trim()) {
        const parsedSeed = Number.parseInt(seed, 10);
        if (!Number.isFinite(parsedSeed) || parsedSeed < 0) {
          throw new Error("Seed must be a non-negative integer.");
        }
        params.seed = parsedSeed;
      }

      if (isEdit) {
        if (modelForMode.id === "flux2-klein-9b-gguf") {
          const parsedStrength = strength.trim()
            ? parseFloatOr(strength)
            : defaults.strength;
          if (parsedStrength !== undefined) {
            params.strength = parsedStrength;
          }
        }
        params.image_ids = imageIds;
      } else {
        params.width = widthValue;
        params.height = heightValue;
        if (negativePrompt.trim()) {
          params.negative_prompt = negativePrompt.trim();
        }
      }

      const userMessage: ChatMessage = {
        id: makeId(),
        role: "user",
        createdAt: Date.now(),
        mode: isEdit ? "edit" : "generate",
        prompt: prompt.trim(),
        attachments: attachmentSnapshots.length ? attachmentSnapshots : undefined
      };

      const request: JobRequest = {
        mode: isEdit ? "edit" : "t2i",
        modelId: modelForMode.id,
        params,
        inputPreviews: attachmentSnapshots.length ? attachmentSnapshots : undefined
      };

      await submitJob(request, userMessage);
      setPrompt("");
      setAttachments([]);
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Unable to submit job.";
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const buildRequestFromRun = (run: RunRecord): JobRequest | null => {
    if (!run.type) {
      return null;
    }
    if (run.type === "t2i") {
      return {
        mode: "t2i",
        modelId: run.model_id,
        params: {
          prompt: run.prompt,
          negative_prompt: run.negative_prompt ?? undefined,
          seed: run.seed,
          steps: run.steps,
          width: run.width ?? undefined,
          height: run.height ?? undefined,
          guidance_scale: run.guidance_scale ?? undefined,
          true_cfg_scale: run.true_cfg_scale ?? undefined
        }
      };
    }
    if (run.type === "edit") {
      return {
        mode: "edit",
        modelId: run.model_id,
        params: {
          prompt: run.prompt,
          image_ids: run.input_image_ids ?? [],
          seed: run.seed,
          steps: run.steps,
          guidance_scale: run.guidance_scale ?? undefined,
          true_cfg_scale: run.true_cfg_scale ?? undefined,
          strength: run.strength ?? undefined
        }
      };
    }
    return null;
  };

  const submitReplay = async (run: RunRecord) => {
    const request = buildRequestFromRun(run);
    if (!request) {
      setError("Replay data missing run type.");
      return;
    }

    const attachmentSnapshots: AttachmentSnapshot[] | undefined =
      run.input_image_ids?.map((imageId) => ({
        id: makeId(),
        previewUrl: `${backendUrl}/api/images/${imageId}`,
        source: "history",
        imageId
      })) ?? undefined;

    const userMessage: ChatMessage = {
      id: makeId(),
      role: "user",
      createdAt: Date.now(),
      mode: run.type === "edit" ? "edit" : "generate",
      prompt: run.prompt,
      attachments: attachmentSnapshots
    };

    const assistantId = makeId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      createdAt: Date.now(),
      status: "queued",
      stage: "queued",
      request
    };

    setMessages((current) => [...current, userMessage, assistantMessage]);

    try {
      const response = await fetch(`${backendUrl}/api/jobs/replay`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: run.id })
      });
      if (!response.ok) {
        const detail = await parseErrorMessage(response);
        throw new Error(detail || "Replay failed.");
      }
      const data = (await response.json()) as { job_id: string };
      updateMessageById(assistantId, { jobId: data.job_id });
      attachEventSource(data.job_id);
      fetchJob(data.job_id);
    } catch (submitError) {
      const message =
        submitError instanceof Error ? submitError.message : "Replay failed.";
      updateMessageById(assistantId, { status: "failed", error: message });
    }
  };

  const handleRetry = async (message: ChatMessage) => {
    if (!message.request) {
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await submitJob(message.request);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReveal = async (message: ChatMessage) => {
    if (!message.jobId) {
      return;
    }
    setError(null);
    try {
      const response = await fetch(`${backendUrl}/api/jobs/${message.jobId}/reveal`, {
        method: "POST"
      });
      if (!response.ok) {
        const detail = await parseErrorMessage(response);
        throw new Error(detail || "Reveal failed.");
      }
      const data = (await response.json()) as { image_id: string };
      updateMessageByJob(message.jobId, {
        status: "succeeded",
        outputImageId: data.image_id,
        requiresReview: false,
        reviewNote: undefined,
        stage: "complete",
        progress: 100
      });
      fetchJob(message.jobId);
    } catch (revealError) {
      const messageText =
        revealError instanceof Error ? revealError.message : "Reveal failed.";
      setError(messageText);
    }
  };

  const copyDebugInfo = async (message: ChatMessage) => {
    const payload = {
      job_id: message.jobId,
      error: message.error,
      request: message.request,
      run: message.run,
      backend_url: backendUrl
    };
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    } catch {
      setError("Unable to copy debug info.");
    }
  };

  const exportThread = () => {
    const payload = {
      exported_at: new Date().toISOString(),
      backend_url: backendUrl,
      messages
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json"
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `chat-thread-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const checkMissingImages = async (messagesToCheck: ChatMessage[]) => {
    const imageIds = new Set<string>();
    messagesToCheck.forEach((message) => {
      message.attachments?.forEach((item) => {
        if (item.imageId) {
          imageIds.add(item.imageId);
        }
      });
      if (message.outputImageId) {
        imageIds.add(message.outputImageId);
      }
    });

    if (imageIds.size === 0) {
      setImportWarnings([]);
      return;
    }

    const missing: string[] = [];
    for (const imageId of imageIds) {
      try {
        const response = await fetch(`${backendUrl}/api/images/${imageId}/meta`, {
          cache: "no-store"
        });
        if (!response.ok) {
          missing.push(imageId);
        }
      } catch {
        missing.push(imageId);
      }
    }
    setImportWarnings(
      missing.length ? [`Missing image IDs: ${missing.slice(0, 4).join(", ")}`] : []
    );
  };

  const handleImportThread = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    try {
      const text = await file.text();
      const payload = JSON.parse(text) as { messages?: ChatMessage[] };
      if (!payload.messages || !Array.isArray(payload.messages)) {
        throw new Error("Invalid thread payload.");
      }
      setMessages(payload.messages);
      await checkMissingImages(payload.messages);
    } catch (importError) {
      const message =
        importError instanceof Error ? importError.message : "Failed to import thread.";
      setError(message);
    } finally {
      event.target.value = "";
    }
  };

  const triggerImport = () => {
    importInputRef.current?.click();
  };

  const copyRunParams = async (run?: RunRecord) => {
    if (!run) {
      return;
    }
    const payload: Record<string, unknown> = {
      model_id: run.model_id,
      prompt: run.prompt,
      negative_prompt: run.negative_prompt,
      seed: run.seed,
      steps: run.steps,
      width: run.width,
      height: run.height,
      guidance_scale: run.guidance_scale,
      true_cfg_scale: run.true_cfg_scale,
      strength: run.strength,
      input_image_ids: run.input_image_ids
    };
    Object.keys(payload).forEach((key) => {
      if (payload[key] === undefined || payload[key] === null) {
        delete payload[key];
      }
    });
    try {
      await navigator.clipboard.writeText(JSON.stringify(payload, null, 2));
    } catch {
      setError("Unable to copy params to clipboard.");
    }
  };

  const clearHistory = () => {
    localStorage.removeItem(STORAGE_KEY);
    eventSources.current.forEach((source) => source.close());
    eventSources.current.clear();
    setMessages([]);
    setImportWarnings([]);
  };

  return (
    <main className="mx-auto min-h-screen max-w-7xl px-6 pb-24 pt-10 lg:px-10">
      <div className="grid gap-10 lg:grid-cols-[320px_minmax(0,1fr)] xl:grid-cols-[340px_minmax(0,1fr)]">
        <aside className="flex flex-col gap-7 lg:sticky lg:top-8 lg:max-h-[calc(100vh-4rem)] lg:overflow-y-auto">
          <div className="rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.5)] backdrop-blur">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">System profile</p>
            <h2 className="mt-3 font-display text-xl text-slate-900">Local studio runtime</h2>
            <p className="mt-2 text-sm text-slate-600">
              {systemInfo
                ? `${systemInfo.profile} (${systemInfo.profile_reason})`
                : "Loading device profile..."}
            </p>
            {readyState ? (
              <div className="mt-3 flex items-center gap-2 text-xs uppercase tracking-[0.2em]">
                <span
                  className={`rounded-full px-2 py-1 ${
                    readyState.ready ? "bg-emerald-500 text-white" : "bg-amber-400 text-slate-900"
                  }`}
                >
                  {readyState.ready ? "Ready" : readyState.status}
                </span>
                <span className="text-slate-500">
                  {(readyState.details?.message as string) ??
                    (readyState.details?.error as string) ??
                    ""}
                </span>
              </div>
            ) : null}
            {systemInfo ? (
              <div className="mt-4 space-y-2 text-xs text-slate-500">
                <div>RAM: {systemInfo.hardware.ram_gb ?? "n/a"} GB</div>
                <div>CUDA: {systemInfo.hardware.has_cuda ? "yes" : "no"}</div>
                <div>VRAM: {systemInfo.hardware.vram_gb ?? "n/a"} GB</div>
              </div>
            ) : null}
            {systemInfo?.storage ? (
              <div className="mt-4 rounded-2xl border border-slate-200/70 bg-white/90 px-3 py-2 text-xs text-slate-600">
                <div className="flex items-center justify-between">
                  <span>Data total</span>
                  <span className="font-semibold text-slate-800">
                    {formatBytes(systemInfo.storage.total_bytes)}
                  </span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <span>Images</span>
                  <span>{formatBytes(systemInfo.storage.images_bytes)}</span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <span>Flux outputs</span>
                  <span>{formatBytes(systemInfo.storage.flux_outputs_bytes)}</span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <span>DB</span>
                  <span>{formatBytes(systemInfo.storage.db_bytes)}</span>
                </div>
                <div className="mt-2 flex items-center justify-between text-slate-500">
                  <span>Disk free</span>
                  <span>{formatBytes(systemInfo.storage.disk_free_bytes)}</span>
                </div>
              </div>
            ) : null}
          </div>

          <div className="rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.45)] backdrop-blur">
            <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
              Models
            </h3>
            <div className="mt-4 space-y-3 text-sm text-slate-700">
              {models.length ? (
                models.map((model) => (
                  <div key={model.id} className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-semibold text-slate-800">
                        {model.label ?? model.id}
                      </p>
                      <p className="text-xs text-slate-500">
                        {model.capabilities.join(", ")}
                        {model.review_mode === "manual" ? " · manual review" : ""}
                      </p>
                      {!model.present && model.detail ? (
                        <p className="mt-1 text-xs text-rose-600">{model.detail}</p>
                      ) : null}
                    </div>
                    <span
                      className={`rounded-full px-3 py-1 text-[10px] uppercase tracking-[0.2em] ${
                        model.present ? "bg-emerald-500 text-white" : "bg-rose-500 text-white"
                      }`}
                    >
                      {model.present ? "ready" : "missing"}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">Loading models...</p>
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200/70 bg-white/80 p-6 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.6)] backdrop-blur">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
                Recent runs
              </h3>
              <div className="flex items-center gap-3 text-xs">
                <button
                  type="button"
                  className="text-slate-500 underline underline-offset-4"
                  onClick={loadRuns}
                >
                  Refresh
                </button>
              </div>
            </div>
            <div className="mt-4 space-y-4">
              {recentRuns.length ? (
                recentRuns.map((run) => (
                  <div
                    key={run.id}
                    className="group flex gap-3 rounded-2xl border border-slate-200/70 bg-white/95 p-3 shadow-[0_18px_40px_-30px_rgba(15,23,42,0.35)]"
                  >
                    <div className="h-16 w-16 overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
                      {run.output_image_id ? (
                        <img
                          src={`${backendUrl}/api/images/${run.output_image_id}`}
                          alt="recent output"
                          className="h-full w-full object-cover"
                          loading="lazy"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center text-[10px] uppercase tracking-[0.2em] text-slate-400">
                          n/a
                        </div>
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-[10px] uppercase tracking-[0.2em] text-slate-500">
                          {run.model_id}
                        </p>
                        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-500">
                          {run.status ?? "done"}
                        </span>
                      </div>
                      <p className="mt-1 max-h-10 overflow-hidden text-sm text-slate-700">
                        {run.prompt}
                      </p>
                      <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500">
                        <span>{run.created_at ? formatTime(run.created_at) : ""}</span>
                        <span>{formatLatency(run.latency_ms)}</span>
                      </div>
                      <div className="mt-2 flex items-center gap-2 text-[11px]">
                        {run.output_image_id ? (
                          <button
                            type="button"
                            className="rounded-full border border-slate-300 px-2 py-0.5 font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                            onClick={() => addHistoryAttachment(run.output_image_id!)}
                          >
                            Use
                          </button>
                        ) : null}
                        <button
                          type="button"
                          className="rounded-full border border-slate-300 px-2 py-0.5 font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                          onClick={() => deleteRun(run.id)}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">No runs yet.</p>
              )}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-[0_20px_60px_-40px_rgba(15,23,42,0.45)] backdrop-blur">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
                  Utilities
                </h3>
                <p className="mt-2 text-xs text-slate-500">
                  Recovery, cleanup, and import/export stay available here without crowding the main flow.
                </p>
              </div>
              <button
                type="button"
                className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                onClick={() => setMaintenanceOpen((current) => !current)}
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
                      onClick={exportThread}
                    >
                      Export thread
                    </button>
                    <button
                      type="button"
                      className="rounded-full border border-slate-900/60 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                      onClick={triggerImport}
                    >
                      Import thread
                    </button>
                    <button
                      type="button"
                      className="rounded-full border border-slate-900/60 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                      onClick={clearHistory}
                    >
                      Clear local history
                    </button>
                  </div>
                  <input
                    ref={importInputRef}
                    type="file"
                    accept="application/json"
                    className="hidden"
                    onChange={handleImportThread}
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
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        Cleanup
                      </p>
                      <p className="mt-2 text-xs text-slate-500">
                        Destructive run cleanup stays out of the main workflow.
                      </p>
                    </div>
                    <button
                      type="button"
                      className="rounded-full border border-rose-300 px-3 py-1 text-xs font-semibold text-rose-600 transition hover:border-rose-500 hover:text-rose-700"
                      onClick={clearRecentRuns}
                    >
                      Clear recent runs
                    </button>
                  </div>
                  <label className="mt-4 flex items-center gap-3 text-xs text-slate-600">
                    <input
                      type="checkbox"
                      checked={deleteImagesOnCleanup}
                      onChange={(event) => setDeleteImagesOnCleanup(event.target.checked)}
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
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                        Failed runs
                      </p>
                      <p className="mt-2 text-xs text-slate-500">
                        Replay or remove failed jobs only when you need recovery work.
                      </p>
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <button
                        type="button"
                        className="text-slate-500 underline underline-offset-4"
                        onClick={loadFailedRuns}
                      >
                        Refresh
                      </button>
                      <button
                        type="button"
                        className="text-rose-500 underline underline-offset-4"
                        onClick={clearFailedRuns}
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
                            {run.type ?? "run"}
                          </p>
                          <p className="mt-1 text-sm text-slate-700">{run.prompt}</p>
                          {run.error ? (
                            <p className="mt-2 text-xs text-rose-600">{run.error}</p>
                          ) : null}
                          <div className="mt-2 flex items-center gap-2">
                            <button
                              type="button"
                              className="flex-1 rounded-full border border-rose-500 px-3 py-1 text-xs font-semibold text-rose-600"
                              onClick={() => submitReplay(run)}
                            >
                              Replay
                            </button>
                            <button
                              type="button"
                              className="flex-1 rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600"
                              onClick={() => deleteRun(run.id)}
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
        </aside>

        <section className="flex min-h-[80vh] flex-col gap-6">
          <header className="rounded-3xl border border-slate-200/70 bg-white/80 p-6 shadow-[0_25px_70px_-50px_rgba(15,23,42,0.6)] backdrop-blur motion-safe:animate-fade-up">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Studio session</p>
                <h1 className="mt-2 font-display text-3xl text-slate-900">
                  Generate or edit in a single local session.
                </h1>
              </div>
              <div className="rounded-2xl border border-slate-200/70 bg-white/90 px-4 py-3 text-xs text-slate-600">
                Backend: <span className="font-mono text-slate-800">{backendUrl}</span>
              </div>
            </div>
          </header>

          <div
            ref={timelineRef}
            className="flex-1 space-y-6 overflow-y-auto rounded-3xl border border-slate-200/70 bg-white/70 p-6 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)] backdrop-blur"
          >
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center text-slate-500">
                <p className="font-display text-2xl text-slate-700">Start with a prompt.</p>
                <p className="mt-2 text-sm">
                  Generate a new scene or attach an image to edit.
                </p>
              </div>
            ) : (
              messages.map((message) => {
                const isUser = message.role === "user";
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
                          <span>{message.mode === "edit" ? "Edit" : "Generate"}</span>
                          <span>{formatTime(message.createdAt)}</span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between gap-3 text-xs uppercase tracking-[0.2em] text-slate-500">
                          <span>Assistant</span>
                          <span>{formatTime(message.createdAt)}</span>
                        </div>
                      )}

                      {message.prompt ? (
                        <p className="mt-3 text-sm leading-relaxed">{message.prompt}</p>
                      ) : null}

                      {message.attachments?.length ? (
                        <div className="mt-4 grid grid-cols-2 gap-3">
                          {message.attachments.map((item) => (
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
                                {item.source === "history" ? "History" : "Upload"}
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
                          </div>
                          {typeof message.progress === "number" ? (
                            <div className="h-2 w-full rounded-full bg-slate-200">
                              <div
                                className="h-2 rounded-full bg-slate-900 transition-all"
                                style={{ width: `${message.progress}%` }}
                              />
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
                              onClick={() => handleReveal(message)}
                            >
                              Reveal result
                            </button>
                          ) : null}
                          {message.outputImageId ? (
                            <img
                              src={`${backendUrl}/api/images/${message.outputImageId}`}
                              alt="generated output"
                              className="w-full rounded-2xl object-cover"
                              loading="lazy"
                            />
                          ) : null}
                          {message.outputImageId ? (
                            <div className="flex flex-wrap gap-2 text-xs">
                              <button
                                type="button"
                                className="rounded-full border border-slate-900 px-3 py-1 font-semibold text-slate-800"
                                onClick={() => addHistoryAttachment(message.outputImageId!)}
                              >
                                Use as input
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
                                  onClick={() => copyRunParams(message.run)}
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
                              onClick={() => handleRetry(message)}
                            >
                              Retry
                            </button>
                          ) : null}
                          {message.status === "failed" ? (
                            <button
                              type="button"
                              className="rounded-full border border-slate-900/60 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                              onClick={() => copyDebugInfo(message)}
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
                                <div>
                                  Guidance: {message.run.guidance_scale ?? "n/a"}
                                </div>
                                <div>
                                  True CFG: {message.run.true_cfg_scale ?? "n/a"}
                                </div>
                                <div>
                                  Strength: {message.run.strength ?? "n/a"}
                                </div>
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

          <div className="rounded-3xl border border-slate-200/70 bg-white/90 p-6 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)] backdrop-blur lg:sticky lg:bottom-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3 text-xs uppercase tracking-[0.2em] text-slate-500">
              <div className="flex items-center gap-3">
                <span>Model</span>
                <select
                  value={selectedModelId}
                  onChange={(event) => setSelectedModelId(event.target.value)}
                  disabled={!models.length}
                  className="rounded-full border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 shadow-sm"
                >
                  {(selectableModels.length ? selectableModels : models).map((model) => (
                    <option key={model.id} value={model.id} disabled={!model.present}>
                      {model.label ?? model.id}
                      {model.present ? "" : " (missing)"}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-center gap-2">
                {activeReviewMode === "manual" ? (
                  <span className="rounded-full bg-amber-200 px-3 py-1 text-[10px] font-semibold text-amber-900">
                    Manual review
                  </span>
                ) : null}
                {activeModel && !activeModel.present ? (
                  <span className="rounded-full bg-rose-200 px-3 py-1 text-[10px] font-semibold text-rose-900">
                    Missing files
                  </span>
                ) : null}
              </div>
            </div>
            {activeModel && !activeModel.present && activeModel.detail ? (
              <p className="mb-4 text-xs text-rose-700">{activeModel.detail}</p>
            ) : null}
            <div className="mb-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
              <span className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                Templates
              </span>
              {PROMPT_TEMPLATES.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
                  onClick={() => applyPromptTemplate(template.text)}
                >
                  {template.label}
                </button>
              ))}
            </div>
            <div className="flex items-start justify-between gap-4">
              <textarea
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Describe the scene or edit you want..."
                className="min-h-[120px] w-full resize-none rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20"
              />
              <div className="flex flex-col gap-3">
                <label className="cursor-pointer rounded-full border border-slate-900 px-4 py-2 text-xs font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:bg-slate-900 hover:text-white">
                  Attach images
                  <input
                    type="file"
                    accept="image/*"
                    multiple={maxAttachments > 1}
                    className="hidden"
                    onChange={handleAttachImages}
                  />
                </label>
                <button
                  type="button"
                  onClick={openHistoryPicker}
                  className="rounded-full border border-slate-900/60 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-slate-900 hover:text-slate-900"
                >
                  Pick from history
                </button>
                <button
                  type="button"
                  disabled={isSubmitting}
                  className="rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-[0_18px_40px_-28px_rgba(15,23,42,0.6)] transition hover:-translate-y-0.5 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                  onClick={handleSubmit}
                >
                  {attachments.length ? "Edit" : "Generate"}
                </button>
              </div>
            </div>

            {attachments.length ? (
              <div className="mt-4 grid grid-cols-2 gap-3">
                {attachments.map((item) => (
                  <div key={item.id} className="relative">
                    <img
                      src={
                        item.previewUrl ||
                        (item.kind === "history" ? `${backendUrl}/api/images/${item.imageId}` : "")
                      }
                      alt="attachment"
                      className="h-32 w-full rounded-2xl object-cover"
                    />
                    <span className="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[10px] uppercase tracking-[0.2em] text-slate-600">
                      {item.kind === "history" ? "History" : "Upload"}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeAttachment(item.id)}
                      className="absolute right-2 top-2 rounded-full bg-white/90 px-2 py-1 text-xs text-slate-700 shadow"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            ) : null}

            <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
              <span>
                {attachments.length}/{maxAttachments} image
                {maxAttachments > 1 ? "s" : ""} attached
              </span>
              <button
                type="button"
                className="text-xs uppercase tracking-[0.2em] text-slate-500 underline underline-offset-4"
                onClick={() => setSettingsOpen((open) => !open)}
              >
                {settingsOpen ? "Hide settings" : "Show settings"}
              </button>
              {error ? <span className="text-rose-600">{error}</span> : null}
            </div>

            {settingsOpen ? (
              <div className="mt-4 grid gap-4 rounded-2xl border border-slate-100 bg-white/70 p-4 text-sm text-slate-700">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="text-xs uppercase tracking-[0.2em] text-slate-500">
                    Presets
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                      onClick={applySmokePreset}
                    >
                      Smoke
                    </button>
                    <button
                      type="button"
                      className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                      onClick={applyDraftPreset}
                    >
                      Draft
                    </button>
                    <button
                      type="button"
                      className="rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-500 hover:text-slate-900"
                      onClick={applyAcceptancePreset}
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
                      onChange={(event) => setNegativePrompt(event.target.value)}
                      disabled={attachments.length > 0}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                      placeholder="Optional"
                    />
                  </label>
                  <label className="space-y-2">
                    <SettingLabel
                      label="Seed"
                      tooltip="Same seed + params gives similar results."
                    />
                    <input
                      value={seed}
                      onChange={(event) => setSeed(event.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                      placeholder="Leave blank for random"
                    />
                  </label>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <label className="space-y-2">
                    <SettingLabel
                      label="Steps"
                      tooltip="More steps = slower, often sharper."
                    />
                    <input
                      value={steps}
                      onChange={(event) => setSteps(event.target.value)}
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
                      onChange={(event) => setGuidanceScale(event.target.value)}
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                      placeholder={
                        activeDefaults.guidance_scale !== undefined
                          ? String(activeDefaults.guidance_scale)
                          : "Optional"
                      }
                    />
                  </label>
                </div>

                {attachments.length && activeModel?.id === "flux2-klein-9b-gguf" ? (
                  <div className="grid gap-4 md:grid-cols-2">
                    <label className="space-y-2">
                      <SettingLabel
                        label="Strength"
                        tooltip="How much to change the input image (0-1)."
                      />
                      <input
                        value={strength}
                        onChange={(event) => setStrength(event.target.value)}
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
                      onChange={(event) => setTrueCfgScale(event.target.value)}
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
                        onChange={(event) => setWidth(event.target.value)}
                        disabled={attachments.length > 0}
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
                        onChange={(event) => setHeight(event.target.value)}
                        disabled={attachments.length > 0}
                        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                        placeholder={String(activeDefaults.height)}
                      />
                    </label>
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </section>
      </div>
      {historyOpen ? (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40 px-4 py-10">
          <div className="max-h-[85vh] w-full max-w-4xl overflow-hidden rounded-3xl border border-slate-200/70 bg-white/95 shadow-[0_30px_80px_-60px_rgba(15,23,42,0.5)] backdrop-blur">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
                  History picker
                </p>
                <h2 className="font-display text-2xl text-slate-900">
                  Pick an output to edit
                </h2>
              </div>
              <button
                type="button"
                className="rounded-full border border-slate-900 px-4 py-2 text-xs font-semibold text-slate-700"
                onClick={() => setHistoryOpen(false)}
              >
                Close
              </button>
            </div>
            <div className="max-h-[65vh] overflow-y-auto px-6 py-6">
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {historyRuns
                  .filter((run) => run.output_image_id)
                  .map((run) => (
                    <div
                      key={run.id}
                      className="rounded-2xl border border-slate-200 bg-white p-3"
                    >
                      <img
                        src={`${backendUrl}/api/images/${run.output_image_id}`}
                        alt="history output"
                        className="h-36 w-full rounded-xl object-cover"
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
                              addHistoryAttachment(run.output_image_id);
                            }
                          }}
                        >
                          Use as input
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
              {!historyRuns.some((run) => run.output_image_id) ? (
                <p className="text-sm text-slate-500">No outputs available yet.</p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}
