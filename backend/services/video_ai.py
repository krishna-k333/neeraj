"""
AI video generation client — Kie.ai Gemini Omni Video model.
Generates product showcase videos from catalog images in 9:16 Reels format.
"""
import httpx
import asyncio
from config import settings

VIDEO_AI_BASE = "https://api.kie.ai"


async def generate_video(
    image_url: str,
    prompt: str,
    duration: str = "8",
) -> dict:
    """
    Start a video generation job.
    Returns {"taskId": ...} to poll for completion.
    """
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            f"{VIDEO_AI_BASE}/api/v1/jobs/createTask",
            headers={
                "Authorization": f"Bearer {settings.VIDEO_AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gemini-omni-video",
                "input": {
                    "prompt": prompt,
                    "image_urls": [image_url],
                    "duration": duration,
                    "aspect_ratio": "9:16",
                    "resolution": "720p",
                },
            }
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"Kie.ai createTask failed: {data.get('msg')}")
        return data["data"]


async def get_video_status(task_id: str) -> dict:
    """Poll task status. Returns the raw `data` object (state: waiting/success/fail)."""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            f"{VIDEO_AI_BASE}/api/v1/jobs/recordInfo",
            params={"taskId": task_id},
            headers={"Authorization": f"Bearer {settings.VIDEO_AI_API_KEY}"}
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"Kie.ai recordInfo failed: {data.get('msg')}")
        return data["data"]


async def wait_for_video(task_id: str, max_wait: int = 300) -> str | None:
    """Poll until video is ready. Returns output URL or None on timeout/failure."""
    import json

    for _ in range(max_wait // 10):
        await asyncio.sleep(10)
        status = await get_video_status(task_id)
        state = status.get("state")
        if state == "success":
            result = json.loads(status.get("resultJson") or "{}")
            urls = result.get("resultUrls") or []
            return urls[0] if urls else None
        if state == "fail":
            return None
    return None
