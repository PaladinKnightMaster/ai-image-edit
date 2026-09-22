import type { Page, Route } from "@playwright/test";

const BACKEND = "http://127.0.0.1:8000";

/** 1x1 PNG */
export const TINY_PNG_BASE64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";

export const MOCK_MODELS = [
  {
    id: "sdxl-openvino",
    label: "SDXL 1.0 (OpenVINO)",
    capabilities: ["t2i", "edit"],
    present: true,
    edit_input_limit: 1,
    defaults: { steps: 12, width: 1024, height: 1024, strength: 0.65 },
    review_mode: null
  },
  {
    id: "flux2-klein-9b-gguf",
    label: "FLUX.2 klein 9B (GGUF) - fast",
    capabilities: ["t2i", "edit"],
    present: true,
    edit_input_limit: 1,
    defaults: { steps: 4, width: 768, height: 768 },
    review_mode: "manual"
  }
];

export const MOCK_SYSTEM = {
  profile: "cpu-balanced",
  profile_reason: "manual",
  hardware: { has_cuda: false, vram_gb: null, ram_gb: 64, device_name: null },
  defaults: { width: 1024, height: 1024, steps: 24 },
  limits: { max_width: 2048, max_height: 2048, max_steps: 50 },
  memory: { attention_slicing: true, vae_slicing: true, vae_tiling: false },
  storage: {
    total_bytes: 1_000_000,
    images_bytes: 500_000,
    flux_outputs_bytes: 0,
    db_bytes: 10_000,
    disk_free_bytes: 100_000_000_000
  }
};

export const MOCK_HARDWARE = {
  hardware: {
    has_cuda: false,
    ram_gb: 64,
    disk_free_gb: 100,
    openvino_devices: ["CPU"],
    has_openvino: true
  },
  models: [
    {
      id: "sdxl-openvino",
      label: "SDXL 1.0 (OpenVINO, Intel-optimized)",
      engine: "openvino",
      capabilities: ["t2i", "edit"],
      approx_disk_gb: 7,
      verdict: "recommended",
      verdict_label: "Recommended",
      reason: "Runs efficiently on this CPU (Intel-optimized path).",
      downloadable: true,
      present: true,
      setup: "hf download …",
      docs: "docs/models/download-and-setup.md#sdxl-openvino",
      notes: "Primary local CPU lane."
    },
    {
      id: "flux2-klein-9b-gguf",
      label: "FLUX.2 klein 9B (GGUF)",
      engine: "stable-diffusion.cpp",
      capabilities: ["t2i", "edit"],
      approx_disk_gb: 12,
      verdict: "usable_slow",
      verdict_label: "Usable (slow)",
      reason: "Runs on CPU but is very slow.",
      downloadable: true,
      present: true,
      setup: "fetch script",
      docs: "docs/models/download-and-setup.md#flux2-klein-9b-gguf",
      notes: "Optional draft."
    }
  ],
  best_choice: "sdxl-openvino",
  best_choice_setup: "hf download …",
  summary: "Best local pick for this machine: SDXL 1.0 (OpenVINO, Intel-optimized) (t2i/edit)."
};

export const MOCK_HISTORY_RUN = {
  id: "run-hist-1",
  job_id: "job-hist-1",
  model_id: "sdxl-openvino",
  prompt: "prior portrait",
  seed: 1,
  steps: 8,
  output_image_id: "img-base-1",
  status: "succeeded",
  created_at: 1_700_000_000
};

async function json(route: Route, body: unknown, status = 200) {
  await route.fulfill({
    status,
    contentType: "application/json",
    body: JSON.stringify(body)
  });
}

/**
 * Deterministic non-model API surface for /chat product-flow tests.
 * No real inference; edit submit returns a job that is immediately succeeded on poll.
 */
export async function installChatApiMocks(page: Page) {
  await page.route(`${BACKEND}/ready`, (route) =>
    json(route, { ready: true, status: "ready", details: { message: "ok" } })
  );
  await page.route(`${BACKEND}/api/system`, (route) => json(route, MOCK_SYSTEM));
  await page.route(`${BACKEND}/api/hardware`, (route) => json(route, MOCK_HARDWARE));
  await page.route(`${BACKEND}/api/models`, (route) => json(route, MOCK_MODELS));
  await page.route(`${BACKEND}/api/runs**`, async (route) => {
    if (route.request().method() === "GET") {
      await json(route, [MOCK_HISTORY_RUN]);
      return;
    }
    await json(route, { deleted: 0 });
  });
  await page.route(`${BACKEND}/api/jobs/edit`, async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }
    await json(route, { job_id: "job-edit-1" });
  });
  await page.route(`${BACKEND}/api/jobs/t2i`, async (route) => {
    if (route.request().method() !== "POST") {
      await route.fallback();
      return;
    }
    await json(route, { job_id: "job-t2i-1" });
  });
  await page.route(`${BACKEND}/api/jobs/job-edit-1`, (route) =>
    json(route, {
      id: "job-edit-1",
      status: "succeeded",
      stage: "complete",
      progress_percent: 100,
      run: {
        ...MOCK_HISTORY_RUN,
        id: "run-edit-1",
        job_id: "job-edit-1",
        output_image_id: "img-out-1",
        prompt: "Retouch this portrait"
      }
    })
  );
  await page.route(`${BACKEND}/api/jobs/job-edit-1/events`, async (route) => {
    // Minimal SSE: immediate result so UI does not wait on a live worker.
    const body = [
      "event: status",
      `data: ${JSON.stringify({ status: "running", stage: "running" })}`,
      "",
      "event: result",
      `data: ${JSON.stringify({ output_image_id: "img-out-1", last_activity_at: Date.now() })}`,
      "",
      ""
    ].join("\n");
    await route.fulfill({
      status: 200,
      contentType: "text/event-stream",
      headers: {
        "Cache-Control": "no-cache",
        Connection: "keep-alive"
      },
      body
    });
  });
  await page.route(`${BACKEND}/api/images/**`, async (route) => {
    const url = route.request().url();
    if (url.endsWith("/meta")) {
      await json(route, { width: 1, height: 1, content_type: "image/png" });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "image/png",
      body: Buffer.from(TINY_PNG_BASE64, "base64")
    });
  });
}

export { BACKEND };
