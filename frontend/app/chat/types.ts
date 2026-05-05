export type ModelInfo = {
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

export type RunRecord = {
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

export type AttachmentRole = "base" | "reference";

export type AttachmentDraft = {
  id: string;
  kind: "upload";
  file: File;
  previewUrl: string;
  slot?: AttachmentRole;
};

export type AttachmentHistory = {
  id: string;
  kind: "history";
  imageId: string;
  previewUrl: string;
  origin?: "history" | "generated";
  slot?: AttachmentRole;
};

export type AttachmentItem = AttachmentDraft | AttachmentHistory;

export type AttachmentSnapshot = {
  id: string;
  previewUrl: string;
  source?: "upload" | "history" | "generated";
  imageId?: string;
  slot?: AttachmentRole;
};

export type ProductMode = "edit" | "create";

export type JobRequest = {
  mode: "t2i" | "edit";
  modelId: string;
  params: Record<string, unknown>;
  inputPreviews?: AttachmentSnapshot[];
};

export type ChatMessage = {
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

export type PromptTemplate = {
  id: string;
  label: string;
  text: string;
};

export type ActiveDefaults = {
  steps: number;
  width: number;
  height: number;
  guidance_scale?: number;
  true_cfg_scale?: number;
  strength?: number;
};

export type BenchmarkDimension =
  | "identity_preservation"
  | "skin_realism"
  | "eye_detail"
  | "hair_detail"
  | "lighting_coherence"
  | "background_cleanliness"
  | "prompt_or_instruction_adherence"
  | "artifact_absence";

export type EditPresetBenchmarkReview = {
  primaryCases: string[];
  secondaryCases?: string[];
  reviewFocus: BenchmarkDimension[];
  watchouts: string[];
};

export type EditPreset = {
  id: string;
  name: string;
  description: string;
  promptTemplate: string;
  compatibleModes: ProductMode[];
  draftDefaults: {
    steps?: number;
    guidanceScale?: number;
    trueCfgScale?: number;
    strength?: number;
  };
  benchmarkReview: EditPresetBenchmarkReview;
  note?: string;
};
