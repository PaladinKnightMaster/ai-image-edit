import type { EditPreset } from "./types";

export const EDIT_PRESETS: EditPreset[] = [
  {
    id: "headshot-cleanup",
    name: "Headshot Cleanup",
    description: "Tidy small distractions while keeping the portrait realistic and professional.",
    promptTemplate:
      "Clean up this headshot while preserving identity. Reduce stray hairs and temporary blemishes, even skin tone gently, keep pores and natural texture, maintain crisp eyes and hair detail, and keep the result realistic and believable.",
    compatibleModes: ["edit"],
    draftDefaults: {
      steps: 12,
      guidanceScale: 4.2,
      trueCfgScale: 1.2,
      strength: 0.5
    },
    benchmarkReview: {
      primaryCases: ["edit-001-headshot-cleanup"],
      reviewFocus: ["identity_preservation", "skin_realism", "hair_detail", "artifact_absence"],
      watchouts: ["waxy skin", "hairline drift", "cleanup spill into the background"]
    }
  },
  {
    id: "natural-skin-retouch",
    name: "Natural Skin Retouch",
    description: "Softly refine skin and tone without drifting into plastic or over-smoothed results.",
    promptTemplate:
      "Retouch this portrait with a natural editorial finish. Soften uneven skin gently, reduce harsh shadows under the eyes, keep pores and natural texture, preserve facial structure and identity, and avoid over-smoothed or airbrushed skin.",
    compatibleModes: ["edit"],
    draftDefaults: {
      steps: 12,
      guidanceScale: 4.0,
      trueCfgScale: 1.15,
      strength: 0.48
    },
    benchmarkReview: {
      primaryCases: ["edit-001-headshot-cleanup"],
      secondaryCases: ["edit-002-studio-relight"],
      reviewFocus: ["identity_preservation", "skin_realism", "eye_detail", "artifact_absence"],
      watchouts: ["plastic skin", "flattened facial structure", "under-eye cleanup that erases texture"]
    }
  },
  {
    id: "studio-relight",
    name: "Studio Relight",
    description: "Shift the portrait toward a cleaner, more intentional studio lighting setup.",
    promptTemplate:
      "Relight this portrait as if it were captured in a controlled studio setup. Keep identity unchanged, lift the subject slightly from the background, balance highlights and shadows, add clean directional light, and keep skin tone natural and realistic.",
    compatibleModes: ["edit"],
    draftDefaults: {
      steps: 12,
      guidanceScale: 4.6,
      trueCfgScale: 1.25,
      strength: 0.58
    },
    benchmarkReview: {
      primaryCases: ["edit-002-studio-relight", "ref-001-softbox-relight"],
      reviewFocus: ["identity_preservation", "lighting_coherence", "skin_realism", "eye_detail"],
      watchouts: ["lighting from conflicting directions", "over-brightened skin", "lost eye contrast"]
    }
  },
  {
    id: "background-simplify",
    name: "Background Simplify",
    description: "Reduce background clutter so the subject reads more clearly.",
    promptTemplate:
      "Simplify the background around the portrait while preserving the subject exactly. Reduce distractions, keep edges clean around hair and shoulders, maintain natural depth, and make the portrait feel cleaner and more focused without looking cut out.",
    compatibleModes: ["edit"],
    draftDefaults: {
      steps: 12,
      guidanceScale: 4.3,
      trueCfgScale: 1.2,
      strength: 0.56
    },
    benchmarkReview: {
      primaryCases: ["edit-003-background-simplify"],
      reviewFocus: ["identity_preservation", "background_cleanliness", "hair_detail", "artifact_absence"],
      watchouts: ["hair-edge tearing", "cutout feel", "background smear near shoulders"]
    }
  },
  {
    id: "fashion-portrait",
    name: "Fashion Portrait",
    description: "Push styling, polish, and contrast toward a stronger editorial portrait look.",
    promptTemplate:
      "Refine this portrait toward a polished fashion-editorial look. Keep identity intact, sharpen styling details, improve fabric and hair definition, add clean contrast, preserve realistic skin, and keep the result premium rather than surreal.",
    compatibleModes: ["edit"],
    draftDefaults: {
      steps: 14,
      guidanceScale: 4.8,
      trueCfgScale: 1.3,
      strength: 0.6
    },
    benchmarkReview: {
      primaryCases: ["ref-002-editorial-look-transfer"],
      secondaryCases: ["edit-002-studio-relight"],
      reviewFocus: [
        "identity_preservation",
        "skin_realism",
        "lighting_coherence",
        "prompt_or_instruction_adherence"
      ],
      watchouts: [
        "editorial styling that drifts identity",
        "airbrushed skin",
        "color grading that breaks believable lighting"
      ]
    }
  },
  {
    id: "multi-angle-portrait",
    name: "Multi-Angle Portrait",
    description: "Keep identity stable while steering toward a reference-guided portrait direction.",
    promptTemplate:
      "Use the base portrait as the primary identity source and keep the face consistent while refining the image toward a cohesive portrait look. Preserve facial structure, skin realism, and hair detail, and keep lighting and styling coherent across the final result.",
    compatibleModes: ["edit"],
    draftDefaults: {
      steps: 14,
      guidanceScale: 4.5,
      trueCfgScale: 1.25,
      strength: 0.58
    },
    benchmarkReview: {
      primaryCases: ["ref-003-pose-and-crop-guidance"],
      secondaryCases: ["ref-001-softbox-relight"],
      reviewFocus: [
        "identity_preservation",
        "prompt_or_instruction_adherence",
        "artifact_absence",
        "lighting_coherence"
      ],
      watchouts: ["facial drift", "warped anatomy", "background perspective breaks"]
    },
    note: "Works best when you also provide an optional second reference image."
  }
];
