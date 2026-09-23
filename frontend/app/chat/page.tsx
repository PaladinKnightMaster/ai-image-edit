
"use client";

/* eslint-disable @next/next/no-img-element */

import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

import { EDIT_PRESETS } from "./edit-presets";
import { rememberPresetThumbnail, thumbnailsFromRuns, loadPresetThumbnails, savePresetThumbnails } from "./preset-thumbnails";
import { ComposerPanel } from "./components/ComposerPanel";
import { HardwareAdvisorPanel } from "./components/HardwareAdvisorPanel";
import { HistoryPickerModal } from "./components/HistoryPickerModal";
import { MessageTimeline } from "./components/MessageTimeline";
import { ModeSwitchHero } from "./components/ModeSwitchHero";
import { StudioGallery } from "./components/StudioGallery";
import { StudioRail } from "./components/StudioRail";
import { UtilitiesPanel } from "./components/UtilitiesPanel";
import type { HardwareAdvice } from "./types";

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
  edit_input_limit?: number | null;
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
  pending_output_image_id?: string | null;
  latency_ms?: number | null;
  type?: string | null;
  status?: string | null;
  error?: string | null;
  created_at?: number | null;
  finished_at?: number | null;
};

type AttachmentRole = "base" | "reference";

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
  slot?: AttachmentRole;
};

type AttachmentHistory = {
  id: string;
  kind: "history";
  imageId: string;
  previewUrl: string;
  origin?: "history" | "generated";
  slot?: AttachmentRole;
};

type AttachmentItem = AttachmentDraft | AttachmentHistory;

type AttachmentSnapshot = {
  id: string;
  previewUrl: string;
  source?: "upload" | "history" | "generated";
  imageId?: string;
  slot?: AttachmentRole;
};

type ProductMode = "edit" | "create";

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
  progressStep?: number;
  progressTotal?: number;
  stageElapsedMs?: number;
  etaMs?: number;
  lastActivityAt?: number;
  outputImageId?: string;
  requiresReview?: boolean;
  reviewNote?: string;
  error?: string;
  run?: RunRecord;
  request?: JobRequest;
};

const STORAGE_KEY = "ai-image-chat-thread-v1";
const MODEL_PREF_KEY = "ai-image-chat-model-v1";
const MODEL_T2I = "sdxl-openvino";
const MODEL_EDIT_LOCAL_DRAFT = "sdxl-openvino";
const TERMINAL_JOB_STATUSES = new Set([
  "succeeded",
  "failed",
  "pending_review",
  "cancelled"
]);
const STREAM_RECONNECT_BASE_MS = 1000;
const STREAM_RECONNECT_MAX_MS = 15000;
const STREAM_RECONNECT_MAX_ATTEMPTS = 8;
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

const getRequestMode = (mode: ProductMode): "t2i" | "edit" =>
  mode === "edit" ? "edit" : "t2i";

const getDefaultModelIdForMode = (mode: ProductMode) =>
  mode === "edit" ? MODEL_EDIT_LOCAL_DRAFT : MODEL_T2I;

const getSupportedModel = (
  availableModels: ModelInfo[],
  mode: ProductMode,
  preferredId?: string
) => {
  const requestMode = getRequestMode(mode);
  const compatibleModels = availableModels.filter((model) =>
    model.capabilities.includes(requestMode)
  );
  if (!compatibleModels.length) {
    return availableModels.find((model) => model.id === preferredId) ?? availableModels[0];
  }
  return (
    compatibleModels.find((model) => model.id === preferredId) ??
    compatibleModels.find((model) => model.id === getDefaultModelIdForMode(mode)) ??
    compatibleModels[0]
  );
};

const getEditInputLimitForModel = (model?: ModelInfo) =>
  model?.capabilities.includes("edit") ? model.edit_input_limit ?? 2 : 0;

const modelSupportsReferenceImage = (model?: ModelInfo) =>
  getEditInputLimitForModel(model) > 1;

const modelSupportsStrengthControl = (model?: ModelInfo) =>
  model?.defaults?.strength !== undefined;

const attachmentSlotRank: Record<AttachmentRole, number> = {
  base: 0,
  reference: 1
};

const getAttachmentSlot = (
  item: { slot?: AttachmentRole },
  fallbackIndex = 0
): AttachmentRole => item.slot ?? (fallbackIndex === 0 ? "base" : "reference");

const sortAttachmentsForEdit = <T extends { slot?: AttachmentRole }>(items: T[]) =>
  [...items].sort(
    (left, right) =>
      attachmentSlotRank[getAttachmentSlot(left)] - attachmentSlotRank[getAttachmentSlot(right)]
  );

const ensureAttachmentSlot = (item: AttachmentItem, slot: AttachmentRole): AttachmentItem =>
  item.slot === slot ? item : { ...item, slot };

const normalizeAttachmentsForEditLimit = (
  current: AttachmentItem[],
  maxAttachments: number
) => {
  if (!current.length || maxAttachments < 1) {
    return [];
  }
  const sorted = sortAttachmentsForEdit(current);
  const baseAttachment =
    sorted.find((item, index) => getAttachmentSlot(item, index) === "base") ?? sorted[0];
  const normalized = [ensureAttachmentSlot(baseAttachment, "base")];
  if (maxAttachments < 2) {
    return normalized;
  }
  const referenceAttachment =
    sorted.find(
      (item, index) =>
        item.id !== baseAttachment.id && getAttachmentSlot(item, index) === "reference"
    ) ?? sorted.find((item) => item.id !== baseAttachment.id);
  if (referenceAttachment) {
    normalized.push(ensureAttachmentSlot(referenceAttachment, "reference"));
  }
  return normalized;
};

const attachmentsMatch = (left: AttachmentItem[], right: AttachmentItem[]) =>
  left.length === right.length &&
  left.every(
    (item, index) =>
      item.id === right[index]?.id &&
      getAttachmentSlot(item, index) === getAttachmentSlot(right[index], index)
  );

const buildHistoryAttachment = (
  imageId: string,
  backendUrl: string,
  slot: AttachmentRole,
  origin: "history" | "generated" = "history"
): AttachmentHistory => ({
  id: makeId(),
  kind: "history",
  imageId,
  previewUrl: `${backendUrl}/api/images/${imageId}`,
  origin,
  slot
});

const upsertAttachmentForSlot = (
  current: AttachmentItem[],
  nextItem: AttachmentItem,
  maxAttachments: number
) => {
  const slot = getAttachmentSlot(nextItem);
  const withoutSlot = current.filter((item, index) => getAttachmentSlot(item, index) !== slot);
  return sortAttachmentsForEdit([...withoutSlot, nextItem]).slice(0, maxAttachments);
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

export default function ChatPage() {
  const backendUrl = useMemo(
    () => process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000",
    []
  );
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [hardwareAdvice, setHardwareAdvice] = useState<HardwareAdvice | null>(null);
  const [readyState, setReadyState] = useState<ReadyState | null>(null);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [recentRuns, setRecentRuns] = useState<RunRecord[]>([]);
  const [presetThumbnails, setPresetThumbnails] = useState<Record<string, string>>({});
  const [failedRuns, setFailedRuns] = useState<RunRecord[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [workflowMode, setWorkflowMode] = useState<ProductMode>("edit");
  const [selectedEditPresetId, setSelectedEditPresetId] = useState<string | null>(null);
  const [selectedModelId, setSelectedModelId] = useState(MODEL_EDIT_LOCAL_DRAFT);
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
  const [historyTargetSlot, setHistoryTargetSlot] = useState<AttachmentRole>("base");
  const [historyRuns, setHistoryRuns] = useState<RunRecord[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [maintenanceOpen, setMaintenanceOpen] = useState(true);
  const [importWarnings, setImportWarnings] = useState<string[]>([]);
  const [editInputNotice, setEditInputNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [deleteImagesOnCleanup, setDeleteImagesOnCleanup] = useState(false);
  const [revealingJobIds, setRevealingJobIds] = useState<Set<string>>(() => new Set());
  const eventSources = useRef<Map<string, EventSource>>(new Map());
  const streamReconnectAttempts = useRef<Map<string, number>>(new Map());
  const streamReconnectTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());
  const attachEventSourceRef = useRef<(jobId: string) => void>(() => undefined);
  const timelineRef = useRef<HTMLDivElement | null>(null);
  const importInputRef = useRef<HTMLInputElement | null>(null);
  const lastDefaultsRef = useRef({ steps: "", width: "", height: "" });
  const historyLoadingRef = useRef(false);
  const isEditMode = workflowMode === "edit";

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
    const activeTimers = streamReconnectTimers.current;
    return () => {
      activeEventSources.forEach((source) => source.close());
      activeEventSources.clear();
      activeTimers.forEach((timer) => clearTimeout(timer));
      activeTimers.clear();
    };
  }, []);

  useEffect(() => {
    if (!hydrated) {
      return;
    }
    const handle = window.setTimeout(() => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    }, 400);
    return () => window.clearTimeout(handle);
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
  }, [messages.length]);

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

  const loadHardware = useCallback(async () => {
    try {
      const response = await fetch(`${backendUrl}/api/hardware`, { cache: "no-store" });
      if (!response.ok) {
        return;
      }
      const data = (await response.json()) as HardwareAdvice;
      setHardwareAdvice(data);
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
      const merged = { ...loadPresetThumbnails(), ...thumbnailsFromRuns(data) };
      savePresetThumbnails(merged);
      setPresetThumbnails(merged);
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

  const markRunRevealed = (jobId: string, imageId: string) => {
    const updateRuns = (runs: RunRecord[]) =>
      runs.map((run) =>
        run.job_id === jobId
          ? {
              ...run,
              status: "succeeded",
              output_image_id: imageId,
              pending_output_image_id: null
            }
          : run
      );
    setRecentRuns(updateRuns);
    setHistoryRuns(updateRuns);
    setFailedRuns(updateRuns);
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
    void loadHardware();
    void loadRuns();
    void loadReady();
    void loadFailedRuns();
  }, [loadSystem, loadModels, loadHardware, loadRuns, loadReady, loadFailedRuns]);

  useEffect(() => {
    setPresetThumbnails(loadPresetThumbnails());
  }, []);

  useEffect(() => {
    if (!models.length) {
      return;
    }
    const fallback = getSupportedModel(models, workflowMode, selectedModelId);
    if (fallback && fallback.id !== selectedModelId) {
      setSelectedModelId(fallback.id);
    }
  }, [models, selectedModelId, workflowMode]);

  const activeMode = getRequestMode(workflowMode);
  const activeModel =
    getSupportedModel(models, workflowMode, selectedModelId) ??
    models.find((model) => model.id === selectedModelId);
  const activeDefaults = {
    steps: activeModel?.defaults?.steps ?? systemInfo?.defaults.steps ?? 24,
    width: activeModel?.defaults?.width ?? systemInfo?.defaults.width ?? 1024,
    height: activeModel?.defaults?.height ?? systemInfo?.defaults.height ?? 1024,
    guidance_scale: activeModel?.defaults?.guidance_scale,
    true_cfg_scale: activeModel?.defaults?.true_cfg_scale,
    strength: activeModel?.defaults?.strength
  };
  const activeReviewMode = activeModel?.review_mode ?? "off";
  const selectableModels = models.filter((model) => model.capabilities.includes(activeMode));
  const modelOptions = selectableModels.length ? selectableModels : models;
  const selectedModelValue = modelOptions.some((model) => model.id === selectedModelId)
    ? selectedModelId
    : activeModel?.id ?? selectedModelId;
  const editModeModel = getSupportedModel(models, "edit", selectedModelId);
  const maxAttachments = getEditInputLimitForModel(editModeModel);
  const editModelConstraintNote =
    isEditMode && !modelSupportsReferenceImage(editModeModel)
      ? "This model edits one base image. A reference image is not used on this lane."
      : null;
  const promptPlaceholder = isEditMode
    ? "Describe the portrait edit you want..."
    : "Describe the image you want to create...";
  const submitLabel = isEditMode ? "Run edit" : "Create draft";

  useEffect(() => {
    if (!isEditMode) {
      return;
    }
    const normalizedAttachments = normalizeAttachmentsForEditLimit(attachments, maxAttachments);
    if (attachmentsMatch(attachments, normalizedAttachments)) {
      return;
    }
    const hadReference = attachments.some(
      (item, index) => getAttachmentSlot(item, index) === "reference"
    );
    const hadBase = attachments.some((item, index) => getAttachmentSlot(item, index) === "base");
    setAttachments(normalizedAttachments);
    if (hadReference && !modelSupportsReferenceImage(editModeModel)) {
      setEditInputNotice(
        "Visual guide removed. The selected local draft model runs with one base image only."
      );
    } else if (!hadBase && normalizedAttachments.length) {
      setEditInputNotice("Selected image moved into the base slot for the edit run.");
    }
  }, [attachments, editModeModel, isEditMode, maxAttachments]);

  const handleModeChange = (nextMode: ProductMode) => {
    setWorkflowMode(nextMode);
    setError(null);
    const fallback = getSupportedModel(models, nextMode, selectedModelId);
    if (fallback && fallback.id !== selectedModelId) {
      setSelectedModelId(fallback.id);
    }
  };

  const applyDraftPreset = () => {
    if (activeModel?.id === "flux2-klein-9b-gguf") {
      setSteps("8");
      setGuidanceScale("4.0");
      if (!isEditMode) {
        setWidth("512");
        setHeight("512");
      }
      if (isEditMode) {
        setStrength("0.6");
      }
      return;
    }

    if (activeModel?.id?.startsWith("qwen-image")) {
      setSteps("12");
      setGuidanceScale("4.0");
      setTrueCfgScale("1.2");
      if (!isEditMode) {
        setWidth("512");
        setHeight("512");
      }
      if (isEditMode) {
        setStrength("0.6");
      }
    }
  };

  const applySmokePreset = () => {
    if (activeModel?.id === "flux2-klein-9b-gguf") {
      setSteps("4");
      setGuidanceScale("3.5");
      if (!isEditMode) {
        setWidth("512");
        setHeight("512");
      }
      if (isEditMode) {
        setStrength("0.55");
      }
      return;
    }

    if (activeModel?.id?.startsWith("qwen-image")) {
      setSteps("8");
      setGuidanceScale("3.5");
      setTrueCfgScale("1.1");
      if (!isEditMode) {
        setWidth("512");
        setHeight("512");
      }
      if (isEditMode) {
        setStrength("0.55");
      }
    }
  };

  const applyAcceptancePreset = () => {
    if (activeModel?.id === "flux2-klein-9b-gguf") {
      setSteps("12");
      setGuidanceScale("4.5");
      if (!isEditMode) {
        setWidth("768");
        setHeight("768");
      }
      if (isEditMode) {
        setStrength("0.65");
      }
      return;
    }

    if (activeModel?.id?.startsWith("qwen-image")) {
      setSteps("20");
      setGuidanceScale("5.0");
      setTrueCfgScale("1.4");
      if (!isEditMode) {
        setWidth("768");
        setHeight("768");
      }
      if (isEditMode) {
        setStrength("0.65");
      }
    }
  };

  const applyPromptTemplate = (template: string) => {
    setPrompt((current) => (current ? `${current}\n\n${template}` : template));
  };

  const applyEditPreset = (preset: (typeof EDIT_PRESETS)[number]) => {
    if (!isEditMode) {
      handleModeChange("edit");
    }
    setSelectedEditPresetId(preset.id);
    setPrompt(preset.promptTemplate);
    applyDraftPreset();
    if (preset.draftDefaults.steps !== undefined) {
      setSteps(String(preset.draftDefaults.steps));
    }
    if (preset.draftDefaults.guidanceScale !== undefined) {
      setGuidanceScale(String(preset.draftDefaults.guidanceScale));
    }
    if (preset.draftDefaults.trueCfgScale !== undefined) {
      setTrueCfgScale(String(preset.draftDefaults.trueCfgScale));
    }
    if (preset.draftDefaults.strength !== undefined) {
      setStrength(String(preset.draftDefaults.strength));
    }
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
    if (modelSupportsStrengthControl(activeModel) && activeDefaults.strength !== undefined) {
      setStrength((current) =>
        current === "" ? String(activeDefaults.strength) : current
      );
    }
    lastDefaultsRef.current = nextDefaults;
  }, [
    activeDefaults.steps,
    activeDefaults.width,
    activeDefaults.height,
    activeDefaults.strength,
    activeModel
  ]);

  const updateMessageByJob = useCallback((jobId: string, patch: Partial<ChatMessage>) => {
    setMessages((current) =>
      current.map((message) => {
        if (message.jobId !== jobId) {
          return message;
        }
        const next = { ...message, ...patch };
        const promptText =
          next.prompt ||
          (typeof next.request?.params?.prompt === "string"
            ? next.request.params.prompt
            : undefined) ||
          next.run?.prompt;
        if (next.outputImageId && promptText) {
          setPresetThumbnails(rememberPresetThumbnail(promptText, next.outputImageId));
        }
        return next;
      })
    );
  }, []);

  const progressPending = useRef<Map<string, Partial<ChatMessage>>>(new Map());
  const progressTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());
  const PROGRESS_FLUSH_MS = 250;

  const dropPendingProgress = useCallback((jobId: string) => {
    const timer = progressTimers.current.get(jobId);
    if (timer) {
      clearTimeout(timer);
    }
    progressTimers.current.delete(jobId);
    progressPending.current.delete(jobId);
  }, []);

  const queueProgress = useCallback(
    (jobId: string, patch: Partial<ChatMessage>) => {
      progressPending.current.set(jobId, {
        ...progressPending.current.get(jobId),
        ...patch
      });
      if (progressTimers.current.has(jobId)) {
        return;
      }
      const timer = setTimeout(() => {
        progressTimers.current.delete(jobId);
        const pending = progressPending.current.get(jobId);
        progressPending.current.delete(jobId);
        if (pending) {
          updateMessageByJob(jobId, pending);
        }
      }, PROGRESS_FLUSH_MS);
      progressTimers.current.set(jobId, timer);
    },
    [updateMessageByJob]
  );

  const updateMessageById = useCallback((id: string, patch: Partial<ChatMessage>) => {
    setMessages((current) =>
      current.map((message) => (message.id === id ? { ...message, ...patch } : message))
    );
  }, []);

  const fetchJob = useCallback(async (jobId: string) => {
    try {
      const response = await fetch(`${backendUrl}/api/jobs/${jobId}`, { cache: "no-store" });
      if (!response.ok) {
        return null;
      }
      const data = await response.json();
      const terminal = TERMINAL_JOB_STATUSES.has(data.status);
      if (terminal) {
        dropPendingProgress(jobId);
      }
      updateMessageByJob(jobId, {
        status: data.status,
        run: data.run,
        stage: data.status === "pending_review" ? "review" : data.stage,
        progress:
          typeof data.progress_percent === "number" ? data.progress_percent : undefined,
        progressStep:
          typeof data.progress_step === "number" ? data.progress_step : undefined,
        progressTotal:
          typeof data.progress_total === "number" ? data.progress_total : undefined,
        lastActivityAt:
          typeof data.last_activity_at === "number" ? data.last_activity_at : undefined,
        outputImageId: data.run?.output_image_id ?? undefined,
        requiresReview: data.status === "pending_review",
        reviewNote: data.status === "pending_review" ? "Manual review required." : undefined,
        ...(data.status === "succeeded" || data.status === "pending_review"
          ? { error: undefined }
          : {})
      });
      if (terminal) {
        eventSources.current.get(jobId)?.close();
        eventSources.current.delete(jobId);
        streamReconnectAttempts.current.delete(jobId);
        const timer = streamReconnectTimers.current.get(jobId);
        if (timer) {
          clearTimeout(timer);
          streamReconnectTimers.current.delete(jobId);
        }
        loadRuns();
      }
      return data as { status?: string };
    } catch {
      return null;
    }
  }, [backendUrl, dropPendingProgress, loadRuns, updateMessageByJob]);

  const clearStreamReconnect = useCallback((jobId: string) => {
    streamReconnectAttempts.current.delete(jobId);
    const timer = streamReconnectTimers.current.get(jobId);
    if (timer) {
      clearTimeout(timer);
      streamReconnectTimers.current.delete(jobId);
    }
  }, []);

  const scheduleStreamReconnect = useCallback((jobId: string) => {
    if (streamReconnectTimers.current.has(jobId)) {
      return;
    }
    const attempt = streamReconnectAttempts.current.get(jobId) ?? 0;
    if (attempt >= STREAM_RECONNECT_MAX_ATTEMPTS) {
      updateMessageByJob(jobId, {
        error:
          "Live progress disconnected. The job may still be running — check Recent runs or refresh."
      });
      return;
    }
    const delay = Math.min(
      STREAM_RECONNECT_MAX_MS,
      STREAM_RECONNECT_BASE_MS * 2 ** attempt
    );
    streamReconnectAttempts.current.set(jobId, attempt + 1);
    const timer = setTimeout(() => {
      streamReconnectTimers.current.delete(jobId);
      attachEventSourceRef.current(jobId);
    }, delay);
    streamReconnectTimers.current.set(jobId, timer);
  }, [updateMessageByJob]);

  const handleTransportDisconnect = useCallback(
    async (jobId: string) => {
      // Claim reconnect ownership before any setState so the messages effect cannot
      // immediately re-attach and bypass bounded backoff.
      if (!streamReconnectAttempts.current.has(jobId)) {
        streamReconnectAttempts.current.set(jobId, 0);
      }
      const data = await fetchJob(jobId);
      if (data?.status && TERMINAL_JOB_STATUSES.has(data.status)) {
        clearStreamReconnect(jobId);
        return;
      }
      updateMessageByJob(jobId, {
        error: data?.status
          ? "Live progress reconnecting…"
          : "Stream interrupted — reconciling job status…"
      });
      scheduleStreamReconnect(jobId);
    },
    [clearStreamReconnect, fetchJob, scheduleStreamReconnect, updateMessageByJob]
  );

  const attachEventSource = useCallback(
    (jobId: string) => {
      if (eventSources.current.has(jobId)) {
        return;
      }
      const source = new EventSource(`${backendUrl}/api/jobs/${jobId}/events`);
      source.addEventListener("status", (event) => {
        const payload = JSON.parse((event as MessageEvent).data);
        const patch: Partial<ChatMessage> = {
          status: payload.status,
          stage: payload.stage,
          error: undefined,
          lastActivityAt:
            typeof payload.last_activity_at === "number" ? payload.last_activity_at : undefined
        };
        if (payload.status === "running") {
          patch.startedAt = Date.now();
        }
        clearStreamReconnect(jobId);
        streamReconnectAttempts.current.delete(jobId);
        if (TERMINAL_JOB_STATUSES.has(payload.status)) {
          dropPendingProgress(jobId);
        }
        updateMessageByJob(jobId, patch);
      });
      source.addEventListener("stage", (event) => {
        const payload = JSON.parse((event as MessageEvent).data);
        updateMessageByJob(jobId, {
          stage: payload.stage,
          stageElapsedMs:
            typeof payload.elapsed_ms === "number" ? payload.elapsed_ms : undefined,
          lastActivityAt:
            typeof payload.last_activity_at === "number" ? payload.last_activity_at : undefined
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
        queueProgress(jobId, {
          progress: payload.percent,
          progressStep: typeof payload.step === "number" ? payload.step : undefined,
          progressTotal:
            typeof payload.total_steps === "number" ? payload.total_steps : undefined,
          etaMs,
          stageElapsedMs: elapsedMs,
          error: undefined,
          lastActivityAt:
            typeof payload.last_activity_at === "number" ? payload.last_activity_at : undefined
        });
      });
      source.addEventListener("result", (event) => {
        const payload = JSON.parse((event as MessageEvent).data);
        clearStreamReconnect(jobId);
        dropPendingProgress(jobId);
        updateMessageByJob(jobId, {
          status: "succeeded",
          outputImageId: payload.output_image_id,
          stage: "complete",
          progress: 100,
          error: undefined,
          lastActivityAt:
            typeof payload.last_activity_at === "number" ? payload.last_activity_at : undefined
        });
        void fetchJob(jobId);
      });
      source.addEventListener("review_required", (event) => {
        const payload = JSON.parse((event as MessageEvent).data);
        clearStreamReconnect(jobId);
        dropPendingProgress(jobId);
        updateMessageByJob(jobId, {
          status: "pending_review",
          requiresReview: true,
          reviewNote: payload.message,
          stage: "review",
          error: undefined,
          lastActivityAt:
            typeof payload.last_activity_at === "number" ? payload.last_activity_at : undefined
        });
        source.close();
        eventSources.current.delete(jobId);
        loadRuns();
      });
      // Named SSE "error" events carry a JSON body from the backend.
      // Native EventSource transport failures also surface as "error" without data —
      // those must reconcile via GET /api/jobs, not mark the job failed.
      source.addEventListener("error", (event) => {
        const messageEvent = event as MessageEvent;
        if (typeof messageEvent.data === "string" && messageEvent.data.length > 0) {
          try {
            const payload = JSON.parse(messageEvent.data);
            clearStreamReconnect(jobId);
            dropPendingProgress(jobId);
            updateMessageByJob(jobId, {
              status: "failed",
              error: payload.message,
              lastActivityAt:
                typeof payload.last_activity_at === "number"
                  ? payload.last_activity_at
                  : undefined
            });
            source.close();
            eventSources.current.delete(jobId);
            loadRuns();
            return;
          } catch {
            // Fall through to transport handling.
          }
        }
        source.close();
        eventSources.current.delete(jobId);
        void handleTransportDisconnect(jobId);
      });
      source.onerror = () => {
        if (!eventSources.current.has(jobId)) {
          return;
        }
        source.close();
        eventSources.current.delete(jobId);
        void handleTransportDisconnect(jobId);
      };
      eventSources.current.set(jobId, source);
    },
    [
      backendUrl,
      clearStreamReconnect,
      dropPendingProgress,
      fetchJob,
      handleTransportDisconnect,
      loadRuns,
      queueProgress,
      updateMessageByJob
    ]
  );

  attachEventSourceRef.current = attachEventSource;

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
        if (TERMINAL_JOB_STATUSES.has(message.status ?? "")) {
          return;
        }
        if (eventSources.current.has(message.jobId)) {
          return;
        }
        // Reconnect path owns attach while a backoff timer is pending or after a
        // transport disconnect claimed the job (including max-attempt exhaustion).
        if (
          streamReconnectTimers.current.has(message.jobId) ||
          streamReconnectAttempts.current.has(message.jobId)
        ) {
          return;
        }
        void fetchJob(message.jobId);
        attachEventSource(message.jobId);
      });
  }, [attachEventSource, fetchJob, hydrated, messages]);

  const handleAttachImages = async (
    event: ChangeEvent<HTMLInputElement>,
    slot: AttachmentRole
  ) => {
    const files = Array.from(event.target.files ?? []);
    if (!files.length) {
      return;
    }
    handleModeChange("edit");
    setError(null);
    setEditInputNotice(null);
    if (slot === "reference" && maxAttachments < 2) {
      setError("This model only supports a single base image.");
      event.target.value = "";
      return;
    }
    const file = files[0];
    const preview = {
      id: makeId(),
      kind: "upload" as const,
      file,
      previewUrl: await readFileAsDataUrl(file),
      slot
    };
    setAttachments((current) => upsertAttachmentForSlot(current, preview, maxAttachments));
    setEditInputNotice(
      slot === "base"
        ? "Base image ready for editing."
        : "Visual guide added for lighting, style, framing, or angle."
    );
    event.target.value = "";
  };

  const removeAttachment = (id: string) => {
    setEditInputNotice(null);
    setAttachments((current) => current.filter((item) => item.id !== id));
  };

  const addHistoryAttachment = (imageId: string) => {
    handleModeChange("edit");
    setError(null);
    if (historyTargetSlot === "reference" && maxAttachments < 2) {
      setError("This model only supports a single base image.");
      setHistoryOpen(false);
      return;
    }
    let added = false;
    setAttachments((current) => {
      const duplicateSlotItem = current.find(
        (item, index) => getAttachmentSlot(item, index) === historyTargetSlot
      );
      if (
        duplicateSlotItem?.kind === "history" &&
        duplicateSlotItem.imageId === imageId &&
        duplicateSlotItem.origin === "history"
      ) {
        return sortAttachmentsForEdit(current);
      }
      added = true;
      return upsertAttachmentForSlot(
        current,
        buildHistoryAttachment(imageId, backendUrl, historyTargetSlot),
        maxAttachments
      );
    });
    if (added) {
      setEditInputNotice(
        historyTargetSlot === "base"
          ? "Library output staged as the base image."
          : "Library output staged as the visual guide."
      );
    }
    setHistoryOpen(false);
  };

  const startEditFromOutput = (imageId: string) => {
    const switchingFromCreate = !isEditMode;
    handleModeChange("edit");
    setError(null);
    setAttachments([buildHistoryAttachment(imageId, backendUrl, "base", "generated")]);
    setEditInputNotice("Generated result staged as the new base image for Edit Photo.");
    setHistoryOpen(false);
    if (switchingFromCreate) {
      setPrompt("");
      setSelectedEditPresetId(null);
    }
  };

  const openHistoryPicker = async (slot: AttachmentRole) => {
    if (historyLoadingRef.current) {
      return;
    }
    historyLoadingRef.current = true;
    setHistoryLoading(true);
    setError(null);
    try {
      handleModeChange("edit");
      setHistoryTargetSlot(slot);
      await loadHistoryRuns();
      setHistoryOpen(true);
    } finally {
      historyLoadingRef.current = false;
      setHistoryLoading(false);
    }
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
      setError(isEditMode ? "Add an edit instruction before running." : "Add a prompt before generating.");
      return;
    }
    const isEdit = isEditMode;
    const hasBaseAttachment = attachments.some(
      (item, index) => getAttachmentSlot(item, index) === "base"
    );
    if (isEdit && !hasBaseAttachment) {
      setError("Add a base image before running the edit.");
      return;
    }
    if (isEdit && attachments.length > maxAttachments) {
      setError(
        maxAttachments > 1
          ? `This model supports up to ${maxAttachments} input images.`
          : "This model supports only a base image. Remove the visual guide or switch models."
      );
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      const modelForMode = getSupportedModel(
        models,
        isEdit ? "edit" : "create",
        selectedModelId
      );
      if (!modelForMode) {
        throw new Error(`No model available for ${isEdit ? "edit" : "t2i"}.`);
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
        const orderedAttachments = sortAttachmentsForEdit(attachments);
        const hasOrderedBaseAttachment = orderedAttachments.some(
          (item, index) => getAttachmentSlot(item, index) === "base"
        );
        if (!hasOrderedBaseAttachment) {
          throw new Error("Add a base image before running the edit.");
        }
        imageIds = await Promise.all(
          orderedAttachments.map(async (item) =>
            item.kind === "history" ? item.imageId : uploadImage(item)
          )
        );
        attachmentSnapshots = orderedAttachments.map((item, index) => ({
          id: item.id,
          previewUrl: item.previewUrl,
          source: item.kind === "history" ? item.origin ?? "history" : item.kind,
          imageId: imageIds[index],
          slot: getAttachmentSlot(item, index)
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
        if (modelSupportsStrengthControl(modelForMode)) {
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
      if (isEdit) {
        setAttachments([]);
      }
      setEditInputNotice(null);
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
      run.input_image_ids?.map((imageId, index) => ({
        id: makeId(),
        previewUrl: `${backendUrl}/api/images/${imageId}`,
        source: "history",
        imageId,
        slot: index === 0 ? "base" : "reference"
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
    if (message.jobId) {
      setError(null);
      try {
        const response = await fetch(`${backendUrl}/api/jobs/${message.jobId}/retry`, {
          method: "POST"
        });
        if (!response.ok) {
          throw new Error(await parseErrorMessage(response));
        }
        updateMessageByJob(message.jobId, { status: "queued", stage: "queued", error: undefined });
        attachEventSource(message.jobId);
        void fetchJob(message.jobId);
      } catch (retryError) {
        setError(retryError instanceof Error ? retryError.message : "Retry failed.");
      }
      return;
    }
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

  const handleCancel = async (message: ChatMessage) => {
    if (!message.jobId) {
      return;
    }
    setError(null);
    try {
      const response = await fetch(`${backendUrl}/api/jobs/${message.jobId}/cancel`, {
        method: "POST"
      });
      if (!response.ok) {
        throw new Error(await parseErrorMessage(response));
      }
      void fetchJob(message.jobId);
    } catch (cancelError) {
      setError(cancelError instanceof Error ? cancelError.message : "Cancel failed.");
    }
  };

  const revealJobOutput = async (jobId: string) => {
    const response = await fetch(`${backendUrl}/api/jobs/${jobId}/reveal`, {
      method: "POST"
    });
    if (!response.ok) {
      const detail = await parseErrorMessage(response);
      throw new Error(detail || "Reveal failed.");
    }
    const data = (await response.json()) as { image_id: string };
    markRunRevealed(jobId, data.image_id);
    return data.image_id;
  };

  const handleReveal = async (message: ChatMessage) => {
    if (!message.jobId) {
      return;
    }
    if (revealingJobIds.has(message.jobId)) {
      return;
    }
    setError(null);
    setRevealingJobIds((current) => new Set(current).add(message.jobId!));
    try {
      const imageId = await revealJobOutput(message.jobId);
      updateMessageByJob(message.jobId, {
        status: "succeeded",
        outputImageId: imageId,
        requiresReview: false,
        reviewNote: undefined,
        stage: "complete",
        progress: 100
      });
      fetchJob(message.jobId);
      void Promise.all([loadRuns(), loadHistoryRuns()]);
    } catch (revealError) {
      const messageText =
        revealError instanceof Error ? revealError.message : "Reveal failed.";
      setError(messageText);
    } finally {
      setRevealingJobIds((current) => {
        const next = new Set(current);
        next.delete(message.jobId!);
        return next;
      });
    }
  };

  const handleRevealRun = async (run: RunRecord) => {
    if (!run.job_id) {
      return;
    }
    if (revealingJobIds.has(run.job_id)) {
      return;
    }
    setError(null);
    setRevealingJobIds((current) => new Set(current).add(run.job_id));
    try {
      const imageId = await revealJobOutput(run.job_id);
      updateMessageByJob(run.job_id, {
        status: "succeeded",
        outputImageId: imageId,
        requiresReview: false,
        reviewNote: undefined,
        stage: "complete",
        progress: 100
      });
      void Promise.all([loadRuns(), loadHistoryRuns()]);
    } catch (revealError) {
      const messageText =
        revealError instanceof Error ? revealError.message : "Reveal failed.";
      setError(messageText);
    } finally {
      setRevealingJobIds((current) => {
        const next = new Set(current);
        next.delete(run.job_id);
        return next;
      });
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
    link.download = `studio-session-${Date.now()}.json`;
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
      missing.length ? [`Missing studio image IDs: ${missing.slice(0, 4).join(", ")}`] : []
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
        throw new Error("Invalid studio session file.");
      }
      setMessages(payload.messages);
      await checkMissingImages(payload.messages);
    } catch (importError) {
      const message =
        importError instanceof Error ? importError.message : "Failed to import studio session.";
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
    streamReconnectTimers.current.forEach((timer) => clearTimeout(timer));
    streamReconnectTimers.current.clear();
    streamReconnectAttempts.current.clear();
    setMessages([]);
    setImportWarnings([]);
  };

  return (
    <main className="min-h-screen">
      <div className="flex min-h-screen">
        <StudioRail
          setup={
          <HardwareAdvisorPanel
            advice={hardwareAdvice}
            selectedModelId={selectedModelId}
            backendUrl={backendUrl}
            onSelectModel={setSelectedModelId}
            onRefresh={() => {
              void loadHardware();
              void loadModels();
            }}
          />
          }
          utilities={
          <UtilitiesPanel
            deleteImagesOnCleanup={deleteImagesOnCleanup}
            failedRuns={failedRuns}
            importInputRef={importInputRef}
            importWarnings={importWarnings}
            maintenanceOpen={maintenanceOpen}
            onClearFailedRuns={clearFailedRuns}
            onClearHistory={clearHistory}
            onClearRecentRuns={clearRecentRuns}
            onDeleteImagesOnCleanupChange={setDeleteImagesOnCleanup}
            onDeleteRun={deleteRun}
            onExportThread={exportThread}
            onHandleImportThread={handleImportThread}
            onLoadFailedRuns={loadFailedRuns}
            onSubmitReplay={submitReplay}
            onToggleMaintenance={() => setMaintenanceOpen((current) => !current)}
            onTriggerImport={triggerImport}
            runtimeDetails={
              <div className="space-y-4 text-sm text-slate-700" data-testid="studio-runtime-details">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Runtime</p>
                  <p className="mt-2 text-sm text-slate-700">
                    {systemInfo
                      ? `${systemInfo.profile} (${systemInfo.profile_reason})`
                      : "Loading device profile..."}
                  </p>
                  <p className="mt-1 font-mono text-xs text-slate-500">{backendUrl}</p>
                  {readyState ? (
                    <p className="mt-2 text-xs uppercase tracking-[0.16em] text-slate-500">
                      {readyState.ready ? "Backend ready" : readyState.status}
                      {readyState.details?.error
                        ? ` · ${String(readyState.details.error)}`
                        : readyState.details?.message
                          ? ` · ${String(readyState.details.message)}`
                          : ""}
                    </p>
                  ) : null}
                  {systemInfo ? (
                    <p className="mt-2 text-xs text-slate-500">
                      RAM {systemInfo.hardware.ram_gb ?? "n/a"} GB · CUDA{" "}
                      {systemInfo.hardware.has_cuda ? "yes" : "no"} · VRAM{" "}
                      {systemInfo.hardware.vram_gb ?? "n/a"} GB
                    </p>
                  ) : null}
                  {systemInfo?.storage ? (
                    <p className="mt-1 text-xs text-slate-500">
                      Images {formatBytes(systemInfo.storage.images_bytes)} · Disk free{" "}
                      {formatBytes(systemInfo.storage.disk_free_bytes)}
                    </p>
                  ) : null}
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Installed models</p>
                  <div className="mt-2 space-y-2">
                    {models.length ? (
                      models.map((model) => (
                        <div key={model.id} className="flex items-start justify-between gap-2">
                          <div>
                            <p className="font-semibold text-slate-800">{model.label ?? model.id}</p>
                            <p className="text-xs text-slate-500">
                              {model.capabilities.join(", ")}
                              {model.review_mode === "manual" ? " · manual review" : ""}
                            </p>
                          </div>
                          <span className="text-[10px] uppercase tracking-[0.16em] text-slate-500">
                            {model.present ? "ready" : "missing"}
                          </span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500">Loading models...</p>
                    )}
                  </div>
                </div>
              </div>
            }
          />
          }
        />

        <section className="min-w-0 flex-1 px-4 pb-24 pt-6 lg:px-8">
          <div className="mx-auto flex max-w-5xl flex-col gap-6">
          <div className="order-1">
          <ModeSwitchHero
            attachmentsCount={attachments.length}
            isEditMode={isEditMode}
            onModeChange={handleModeChange}
          />
          </div>

          <div className="order-3">
          <StudioGallery
            backendUrl={backendUrl}
            formatLatency={formatLatency}
            formatTime={formatTime}
            recentRuns={recentRuns}
            revealingJobIds={revealingJobIds}
            onDeleteRun={deleteRun}
            onRefresh={loadRuns}
            onRevealRun={handleRevealRun}
            onStartEditFromOutput={startEditFromOutput}
          />
          </div>

          <div className="order-4">
          <MessageTimeline
            attachmentsCount={attachments.length}
            backendUrl={backendUrl}
            formatDuration={formatDuration}
            formatLatency={formatLatency}
            formatTime={formatTime}
            historyLoading={historyLoading}
            isEditMode={isEditMode}
            messages={messages}
            revealingJobIds={revealingJobIds}
            onStartEditFromOutput={startEditFromOutput}
            onCopyDebugInfo={copyDebugInfo}
            onCopyRunParams={copyRunParams}
            onModeChange={handleModeChange}
            onOpenHistory={() => {
              void openHistoryPicker("base");
            }}
            onReveal={handleReveal}
            onRetry={handleRetry}
            onCancel={handleCancel}
            timelineRef={timelineRef}
          />
          </div>

          <div className="order-2">
          <ComposerPanel
            activeDefaults={activeDefaults}
            activeModel={activeModel}
            activeReviewMode={activeReviewMode}
            attachments={attachments}
            activeEditPresetId={selectedEditPresetId}
            backendUrl={backendUrl}
            editPresets={EDIT_PRESETS}
            editInputNotice={editInputNotice}
            editModelConstraintNote={editModelConstraintNote}
            error={error}
            guidanceScale={guidanceScale}
            height={height}
            isEditMode={isEditMode}
            isSubmitting={isSubmitting}
            maxAttachments={maxAttachments}
            modelOptions={modelOptions}
            negativePrompt={negativePrompt}
            onApplyAcceptancePreset={applyAcceptancePreset}
            onApplyDraftPreset={applyDraftPreset}
            onApplyEditPreset={applyEditPreset}
            onApplyPromptTemplate={applyPromptTemplate}
            onApplySmokePreset={applySmokePreset}
            onAttachImages={handleAttachImages}
            onGuidanceScaleChange={setGuidanceScale}
            onHeightChange={setHeight}
            onHistoryPicker={(slot) => {
              void openHistoryPicker(slot);
            }}
            onNegativePromptChange={setNegativePrompt}
            onPromptChange={setPrompt}
            onRemoveAttachment={removeAttachment}
            onSeedChange={setSeed}
            onSelectModel={setSelectedModelId}
            onSettingsToggle={() => setSettingsOpen((open) => !open)}
            onStepsChange={setSteps}
            onStrengthChange={setStrength}
            onSubmit={handleSubmit}
            onTrueCfgScaleChange={setTrueCfgScale}
            onWidthChange={setWidth}
            prompt={prompt}
            promptPlaceholder={promptPlaceholder}
            promptTemplates={PROMPT_TEMPLATES}
            seed={seed}
            selectedModelValue={selectedModelValue}
            settingsOpen={settingsOpen}
            steps={steps}
            strength={strength}
            submitLabel={submitLabel}
            presetThumbnails={presetThumbnails}
            trueCfgScale={trueCfgScale}
            width={width}
          />
          </div>
          </div>
        </section>
      </div>
      <HistoryPickerModal
        backendUrl={backendUrl}
        historyOpen={historyOpen}
        historyRuns={historyRuns}
        historyTargetSlot={historyTargetSlot}
        onAddHistoryAttachment={addHistoryAttachment}
        onClose={() => setHistoryOpen(false)}
      />
    </main>
  );
}
