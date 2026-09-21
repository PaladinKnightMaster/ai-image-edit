#!/usr/bin/env python3
"""Scan this machine and recommend which image model to run (Ollama-style).

Usage:
    python scripts/scan_machine.py            # human-readable report
    python scripts/scan_machine.py --json     # machine-readable JSON

No server required. This is the CLI front-end for backend/app/hardware.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import hardware  # noqa: E402

_VERDICT_ICON = {
    "recommended": "[BEST]",
    "usable": "[ OK ]",
    "usable_slow": "[SLOW]",
    "needs_more_disk": "[DISK]",
    "needs_more_ram": "[ RAM]",
    "needs_gpu": "[ GPU]",
}


def _fmt_hardware(hw: dict) -> str:
    ram = hw.get("ram_gb")
    disk = hw.get("disk_free_gb")
    cpu = hw.get("cpu_brand") or "unknown CPU"
    cores = hw.get("cpu_logical")
    gpu = "CUDA GPU: yes" if hw.get("has_cuda") else "CUDA GPU: no"
    vram = hw.get("vram_gb")
    if hw.get("has_cuda") and vram:
        gpu += f" ({vram} GB VRAM)"
    ov = hw.get("openvino_devices") or []
    ov_line = ", ".join(ov) if ov else "not installed"
    lines = [
        "Machine profile",
        "-" * 60,
        f"  OS / arch     : {hw.get('os')} / {hw.get('arch')}",
        f"  CPU           : {cpu}  ({cores} logical cores)",
        f"  RAM           : {ram} GB",
        f"  {gpu}",
        f"  OpenVINO      : {ov_line}",
        f"  Disk free     : {disk} GB",
    ]
    return "\n".join(lines)


def _fmt_models(models: list[dict]) -> str:
    rows = ["", "Model recommendations (best first)", "-" * 60]
    for m in models:
        icon = _VERDICT_ICON.get(m["verdict"], "[    ]")
        caps = "/".join(m["capabilities"])
        installed = " (installed)" if m["present"] else ""
        rows.append(f"{icon} {m['label']}  <{caps}, ~{m['approx_disk_gb']:.0f} GB>{installed}")
        rows.append(f"       {m['reason']}")
        if m["downloadable"]:
            rows.append(f"       setup: {m['setup']}")
        rows.append("")
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend image models for this machine.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a report.")
    args = parser.parse_args()

    result = hardware.recommend()

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(_fmt_hardware(result["hardware"]))
    print(_fmt_models(result["models"]))
    print("=" * 60)
    print(result["summary"])
    if result["best_choice_setup"]:
        print(f"\nTo set up the best pick:\n    {result['best_choice_setup']}")
    print(
        "\nFull guide (all models, GPU/off-box options, safe removal):\n"
        "    docs/models/download-and-setup.md"
    )


if __name__ == "__main__":
    main()
