#!/usr/bin/env python3
"""Create exact 1- or 2-second reference slices and a provenance manifest."""

import argparse
import csv
import json
import math
import shutil
import subprocess
from datetime import date
from pathlib import Path


def run(command: list[str]) -> str:
    return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()


def duration_seconds(source: Path) -> float:
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(source)]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--chunk-seconds", required=True, choices=(1, 2), type=int)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--creator", default="")
    parser.add_argument("--rights-status", default="unknown_reference_only")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.source.is_file():
        raise SystemExit(f"source not found: {args.source}")
    if not args.source_id.replace("_", "").replace("-", "").isalnum():
        raise SystemExit("source-id must contain only letters, numbers, _ or -")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise SystemExit("ffmpeg and ffprobe are required")

    total = duration_seconds(args.source)
    pieces = math.ceil(total / args.chunk_seconds)
    out = args.out.resolve()
    slices = out / "slices"
    analysis = out / "analysis"
    slices.mkdir(parents=True, exist_ok=True)
    analysis.mkdir(parents=True, exist_ok=True)
    manifest = {"source_id": args.source_id, "source_file": str(args.source.resolve()), "source_url": args.source_url, "creator": args.creator, "rights_status": args.rights_status, "use_boundary": "reference_only_no_republication_or_copying", "captured_on": date.today().isoformat(), "duration_seconds": round(total, 3), "chunk_seconds": args.chunk_seconds, "slices": []}

    for index in range(pieces):
        clip_start = index * args.chunk_seconds
        clip_duration = min(args.chunk_seconds, total - clip_start)
        name = f"{args.source_id}_{index + 1:03d}_{clip_start:07.3f}-{clip_start + clip_duration:07.3f}.mp4"
        destination = slices / name
        manifest["slices"].append({"file": f"slices/{name}", "start": clip_start, "duration": round(clip_duration, 3)})
        if not args.dry_run:
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.source), "-ss", f"{clip_start:.3f}", "-t", f"{clip_duration:.3f}", "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-movflags", "+faststart", str(destination)], check=True)

    manifest_path = analysis / f"{args.source_id}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ledger = analysis / "source-ledger.csv"
    new_ledger = not ledger.exists()
    with ledger.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_id", "source_url", "creator", "rights_status", "status", "duration_seconds", "slice_count"])
        if new_ledger:
            writer.writeheader()
        writer.writerow({"source_id": args.source_id, "source_url": args.source_url, "creator": args.creator, "rights_status": args.rights_status, "status": "sliced" if not args.dry_run else "planned", "duration_seconds": round(total, 3), "slice_count": pieces})
    print(json.dumps({"manifest": str(manifest_path), "slice_count": pieces, "dry_run": args.dry_run}, ensure_ascii=False))


if __name__ == "__main__":
    main()
