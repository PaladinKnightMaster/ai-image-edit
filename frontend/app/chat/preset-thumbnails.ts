import { EDIT_PRESETS } from "./edit-presets";
import type { RunRecord } from "./types";

const STORAGE_KEY = "studio-preset-thumbnails";

export function loadPresetThumbnails(): Record<string, string> {
  if (typeof window === "undefined") {
    return {};
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? (JSON.parse(raw) as Record<string, string>) : {};
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

export function savePresetThumbnails(thumbnails: Record<string, string>) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(thumbnails));
}

export function presetIdForPrompt(prompt: string): string | null {
  const normalized = prompt.trim();
  return EDIT_PRESETS.find((preset) => preset.promptTemplate.trim() === normalized)?.id ?? null;
}

export function rememberPresetThumbnail(prompt: string, imageId: string) {
  const presetId = presetIdForPrompt(prompt);
  if (!presetId || !imageId) {
    return loadPresetThumbnails();
  }
  const next = { ...loadPresetThumbnails(), [presetId]: imageId };
  savePresetThumbnails(next);
  return next;
}

export function thumbnailsFromRuns(runs: RunRecord[]): Record<string, string> {
  const found: Record<string, string> = {};
  for (const run of runs) {
    const presetId = presetIdForPrompt(run.prompt || "");
    const imageId = run.output_image_id || run.pending_output_image_id;
    if (presetId && imageId && !found[presetId]) {
      found[presetId] = imageId;
    }
  }
  return found;
}
