import json
import os
import requests

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

BASE_URL = "https://api.kie.ai/api/v1/jobs"


def headers():
    return {
        "Authorization": f"Bearer {os.environ['KIE_API_KEY']}",
        "Content-Type": "application/json",
    }


@login_required
@ensure_csrf_cookie
def ai_page(request):
    return render(request, "ai/generator.html")


@login_required
@require_POST
def generate_image(request):
    try:
        body = json.loads(request.body)
        prompt = body.get("prompt", "").strip()
    except (ValueError, AttributeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not prompt or len(prompt) > 2000:
        return JsonResponse(
            {"error": "Prompt must contain 1–2000 characters"},
            status=400
        )

    try:
        response = requests.post(
            f"{BASE_URL}/createTask",
            headers=headers(),
            json={
                "model": "flux1-kontext",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "jpeg"
                }
            },
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 200:
            return JsonResponse(
                {"error": "Kie.ai rejected the request"},
                status=502
            )

        task_id = data["data"]["taskId"]

        # Production: save task_id and request.user
        # in the database to verify task ownership.

        return JsonResponse({"task_id": task_id})

    except (requests.RequestException, ValueError, KeyError):
        return JsonResponse(
            {"error": "Could not start generation"},
            status=502
        )


@login_required
@require_GET
def generation_status(request):
    task_id = request.GET.get("task_id", "")

    if not task_id:
        return JsonResponse({"error": "Missing task ID"}, status=400)

    # Production: verify this task belongs to request.user.

    try:
        response = requests.get(
            f"{BASE_URL}/recordInfo",
            headers=headers(),
            params={"taskId": task_id},
            timeout=20
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != 200:
            return JsonResponse(
                {"error": "Status lookup failed"},
                status=502
            )

        task = data["data"]
        state = task.get("state")

        if state == "success":
            raw = task.get("resultJson") or "{}"
            result = json.loads(raw) if isinstance(raw, str) else raw
            urls = result.get("resultUrls", [])

            return JsonResponse({
                "status": "success",
                "image_url": urls[0] if urls else None
            })

        if state == "fail":
            return JsonResponse({
                "status": "failed",
                "error": task.get("failMsg") or "Generation failed"
            })

        return JsonResponse({"status": "generating"})

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return JsonResponse(
            {"error": "Could not check generation"},
            status=502
        )






import ipaddress
import json
import os
import socket
from urllib.parse import urlparse

import requests

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import ImageGeneration


KIE_BASE_URL = "https://api.kie.ai/api/v1/jobs"
DAILY_LIMIT = 5


def kie_headers():
    api_key = os.environ.get("KIE_API_KEY")

    if not api_key:
        raise ValueError("KIE_API_KEY is not configured")

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def daily_usage(user):
    return ImageGeneration.objects.filter(
        user=user,
        created_at__date=timezone.localdate(),
    ).count()


@login_required
@ensure_csrf_cookie
def ai_page(request):
    history = ImageGeneration.objects.filter(
        user=request.user
    )[:30]

    return render(request, "ai/generator.html", {
        "history": history,
        "remaining": max(0, DAILY_LIMIT - daily_usage(request.user)),
    })


@login_required
@require_POST
def generate_image(request):
    try:
        data = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid JSON"}, status=400
        )

    prompt = data.get("prompt", "")

    if not isinstance(prompt, str):
        return JsonResponse(
            {"error": "Prompt must be text"}, status=400
        )

    prompt = prompt.strip()

    if not prompt or len(prompt) > 2000:
        return JsonResponse(
            {"error": "Prompt must contain 1-2000 characters"},
            status=400,
        )

    # Lock user row to prevent simultaneous requests
    # bypassing the daily quota.
    with transaction.atomic():
        from django.contrib.auth import get_user_model

        get_user_model().objects.select_for_update().get(
            pk=request.user.pk
        )

        if daily_usage(request.user) >= DAILY_LIMIT:
            return JsonResponse(
                {"error": "Daily limit reached (5 images)."},
                status=429,
            )

        active = ImageGeneration.objects.filter(
            user=request.user,
            status=ImageGeneration.Status.PENDING,
        ).exists()

        if active:
            return JsonResponse(
                {"error": "Finish your current generation first."},
                status=429,
            )

        generation = ImageGeneration.objects.create(
            user=request.user,
            prompt=prompt,
        )

    try:
        response = requests.post(
            f"{KIE_BASE_URL}/createTask",
            headers=kie_headers(),
            json={
                "model": "flux1-kontext",
                "input": {
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "jpeg",
                },
            },
            timeout=25,
        )
        response.raise_for_status()
        result = response.json()

        task_id = (result.get("data") or {}).get("taskId")

        if result.get("code") != 200 or not task_id:
            raise ValueError(
                result.get("msg") or "Kie.ai rejected the request"
            )

        generation.task_id = task_id
        generation.save(update_fields=["task_id"])

        return JsonResponse({
            "task_id": task_id,
            "generation_id": generation.id,
        })

    except (requests.RequestException, ValueError, TypeError):
        # An upstream timeout may occur after Kie.ai has
        # accepted the job, so billing is not necessarily reversed.
        generation.status = ImageGeneration.Status.FAILED
        generation.error_message = "Could not confirm AI task creation"
        generation.save(
            update_fields=["status", "error_message"]
        )
        return JsonResponse(
            {"error": "Could not start generation."},
            status=502,
        )


@login_required
@require_GET
def generation_status(request):
    task_id = request.GET.get("task_id", "")

    generation = get_object_or_404(
        ImageGeneration,
        user=request.user,
        task_id=task_id,
    )

    if generation.status == ImageGeneration.Status.SUCCESS:
        return JsonResponse({
            "status": "success",
            "image_url": generation.image_url,
        })

    if generation.status == ImageGeneration.Status.FAILED:
        return JsonResponse({
            "status": "failed",
            "error": generation.error_message,
        })

    try:
        response = requests.get(
            f"{KIE_BASE_URL}/recordInfo",
            headers=kie_headers(),
            params={"taskId": generation.task_id},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 200:
            raise ValueError("Invalid Kie.ai response")

        info = result.get("data") or {}
        state = info.get("state")

        if state == "success":
            raw_result = info.get("resultJson") or "{}"
            output = (
                json.loads(raw_result)
                if isinstance(raw_result, str)
                else raw_result
            )

            urls = output.get("resultUrls") or []

            if not urls:
                raise ValueError("No generated image returned")

            generation.status = ImageGeneration.Status.SUCCESS
            generation.image_url = urls[0]
            generation.save(
                update_fields=["status", "image_url"]
            )

            return JsonResponse({
                "status": "success",
                "image_url": generation.image_url,
            })

        if state == "fail":
            generation.status = ImageGeneration.Status.FAILED
            generation.error_message = (
                info.get("failMsg") or "Generation failed"
            )
            generation.save(
                update_fields=["status", "error_message"]
            )
            return JsonResponse({
                "status": "failed",
                "error": generation.error_message,
            })

        return JsonResponse({"status": "pending"})

    except (requests.RequestException, ValueError, TypeError):
        # Temporary polling errors should not destroy the task.
        return JsonResponse(
            {"error": "Status temporarily unavailable"},
            status=503,
        )


@login_required
@require_GET
def generation_history(request):
    generations = ImageGeneration.objects.filter(
        user=request.user
    )[:30]

    return JsonResponse({
        "items": [
            {
                "id": item.id,
                "prompt": item.prompt,
                "status": item.status,
                "image_url": item.image_url,
                "created_at": item.created_at.isoformat(),
            }
            for item in generations
        ],
        "remaining": max(
            0, DAILY_LIMIT - daily_usage(request.user)
        ),
    })


@login_required
@require_GET
def download_image(request, pk):
    generation = get_object_or_404(
        ImageGeneration,
        pk=pk,
        user=request.user,
        status=ImageGeneration.Status.SUCCESS,
    )

    if not generation.image_url:
        raise Http404("Image unavailable")

    # Only allow explicitly trusted image CDN hosts.
    allowed_hosts = {
        host.strip().lower()
        for host in os.environ.get(
            "KIE_IMAGE_HOSTS", ""
        ).split(",")
        if host.strip()
    }

    parsed = urlparse(generation.image_url)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.lower() not in allowed_hosts
        or parsed.port not in (None, 443)
        or parsed.username
        or parsed.password
    ):
        return HttpResponse(
            "Image host is not allowed",
            status=400,
        )

    # Reject hosts resolving to private or local addresses.
    try:
        addresses = socket.getaddrinfo(
            parsed.hostname, 443, type=socket.SOCK_STREAM
        )
        if not addresses or any(
            not ipaddress.ip_address(addr[4][0]).is_global
            for addr in addresses
        ):
            return HttpResponse(
                "Unsafe image address", status=400
            )
    except (OSError, ValueError):
        return HttpResponse(
            "Image address unavailable", status=502
        )

    try:
        upstream = requests.get(
            generation.image_url,
            timeout=20,
            allow_redirects=False,
        )
        upstream.raise_for_status()

        content_type = upstream.headers.get(
            "Content-Type", ""
        ).split(";")[0].lower()

        if content_type not in (
            "image/jpeg", "image/png", "image/webp"
        ):
            return HttpResponse(
                "Invalid image type", status=502
            )

        if len(upstream.content) > 15 * 1024 * 1024:
            return HttpResponse(
                "Image too large", status=413
            )

        extension = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
        }[content_type]

        response = HttpResponse(
            upstream.content,
            content_type=content_type,
        )
        response["Content-Disposition"] = (
            f'attachment; filename="ai-image-{pk}.{extension}"'
        )
        return response

    except requests.RequestException:
        return HttpResponse(
            "Download failed", status=502
        )
