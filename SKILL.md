---
name: tiktok-competitor-collector
description: Collect and analyze TikTok competitor-video references in bulk without bypassing platform access controls. Use when the user supplies public TikTok URLs, TikTok exports, or otherwise authorized local video files and requests a source ledger, 1- or 2-second shot slices, contact sheets, scene analysis, or Baidu Drive archiving for future legal creative reference and batch-production planning.
---

# TikTok Competitor Collector

Use this skill for reference analysis, not copying competitor content into new advertisements.

## Scope and gates

1. Accept only an on-page TikTok download, a user-supplied direct media URL, an owner-authorized export, or a local file whose rights status is recorded.
2. Do not defeat logins, CAPTCHAs, anti-bot controls, access restrictions, DRM, or paywalls. If discovery returns no accessible videos, create only the search/access report and stop acquisition.
3. Treat competitor video, voice, captions, music, logos, product packs, and creator likenesses as reference-only. Reuse scene rhythm, shot taxonomy, and generic setup ideas only.
4. Record `source_url`, creator, capture date, access method, rights status, and content-use boundary before slicing.
5. Do not treat on-screen product claims as verified facts or propagate them into a new brand script.

## Workflow

### 1. Discover and ledger

- Inspect public TikTok pages or an official API only when the user has access and the request is within the API's permitted purpose.
- Save `analysis/source-ledger.csv` before downloading. Include one row per candidate and statuses `accessible`, `not_accessible`, `downloaded`, or `rejected`.
- Do not claim discovery is complete when TikTok search or page access is blocked.

### 2. Acquire only permitted media

- Prefer the platform's visible download action when it is available.
- For an owner-authorized export or a user-provided source file, preserve it unchanged as `originals/<source-id>.mp4`.
- Use a direct media URL only when it is publicly reachable and the user has authorized the acquisition. Keep the URL in the ledger.

### 3. Slice and inspect

Use the bundled script for exact re-encoded 1- or 2-second slices:

```bash
python3 scripts/slice_video.py --source "/absolute/path/video.mp4" --source-id "pethealer_001" --source-url "https://www.tiktok.com/@creator/video/123" --creator "creator-name" --out "/absolute/path/project" --chunk-seconds 1
```

It writes `slices/`, `analysis/<source-id>.manifest.json`, and a source ledger row. Use 1 second for fast TikTok cuts; use 2 seconds only where the shot has a stable action.

Generate a contact sheet and inspect it before completion. For semantic analysis, create `analysis/<source-id>.md` with hook, scene order, shot type, framing, product reveal, actor or pet action, visible text language, pacing, and reusable generic production pattern. Never transcribe or reuse competitor copy as a new script.

### 4. Archive to Baidu Drive

Use `/baidu-drive` for every Baidu Drive action. Create this three-level destination under the approved root:

```text
竞品素材/<brand>/<YYYY-MM-DD>/
  原视频/
  1-2秒分镜/
  分析报告/
```

Upload the ledger and analysis report even when no accessible video is found. For an actual upload, reconcile local versus remote counts and retry missing-only. Report raw-video count, slice count, failures, and remaining work.

## Output boundary

Deliver paths, source count, slice count, access failures, and the Baidu Drive return links. A folder or submitted transfer is not completion until all expected files are listed remotely.
