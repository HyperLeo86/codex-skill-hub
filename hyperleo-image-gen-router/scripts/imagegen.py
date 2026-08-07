#!/usr/bin/env python3
"""image-gen-router: route and call the user's image generation APIs.

Providers:
  - dashscope: 阿里通义万相（qwen-image-2.0-pro / z-image-turbo / wan2.7-image-pro）
  - ark: 火山方舟（doubao-seedream-5-0-pro-260628）

Credentials come from environment variables: DASHSCOPE_API_KEY, ARK_API_KEY.

Usage:
  python3 imagegen.py "prompt" [--provider dashscope|ark] [--model NAME]
        [--size 1024x1024] [-o output.png] [--dry-run]
  python3 imagegen.py --list
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

DASHSCOPE_BASE = "https://dashscope.aliyuncs.com"
ARK_BASE = "https://ark.cn-beijing.volces.com/api/v3"

PROVIDERS = [
    {
        "id": "dashscope",
        "name": "阿里通义万相 DashScope",
        "env": "DASHSCOPE_API_KEY",
        "key_url": "https://bailian.console.aliyun.com（API-KEY 管理）",
        "models": {
            "qwen-image-2.0-pro": {"kind": "dashscope_sync"},
            "z-image-turbo": {"kind": "dashscope_sync"},
            "wan2.7-image-pro": {"kind": "dashscope_async"},
        },
    },
    {
        "id": "ark",
        "name": "火山方舟 ARK",
        "env": "ARK_API_KEY",
        "key_url": "https://console.volcengine.com/ark（API Key 管理）",
        "models": {
            "doubao-seedream-5-0-pro-260628": {"kind": "ark"},
        },
    },
]

TASK_HINTS = [
    (r"快|便宜|草稿|draft|fast|cheap|turbo", "z-image-turbo"),
    (r"写实|照片|摄影|photo|photoreal|realistic", "doubao-seedream-5-0-pro-260628"),
    (r"卡通|插画|扁平|动漫|cartoon|illustration|flat|anime|可爱", "qwen-image-2.0-pro"),
    (r"高清|专业|高质量|pro|premium|4k", "wan2.7-image-pro"),
]

DEFAULT_MODEL = "qwen-image-2.0-pro"


def http_json(url, payload=None, headers=None, timeout=180, method="POST"):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            return json.loads(body)
        except Exception:
            return {"http": exc.code, "body": body[:500]}
    except Exception as exc:
        return {"error": str(exc)}


def bearer(key):
    return {"Authorization": f"Bearer {key}"}


def extract_image_url(resp):
    out = resp.get("output", {})
    for result in out.get("results", []):
        if result.get("url"):
            return result["url"]
        if result.get("image"):
            return result["image"]
    for choice in out.get("choices", []):
        for item in choice.get("message", {}).get("content", []):
            if item.get("image"):
                return item["image"]
    return None


def call_dashscope_sync(model, prompt, size, key, timeout):
    url = f"{DASHSCOPE_BASE}/api/v1/services/aigc/multimodal-generation/generation"
    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": [{"text": prompt}]}]},
        "parameters": {"size": size.replace("x", "*")},
    }
    if model == "z-image-turbo":
        payload["parameters"]["prompt_extend"] = False
    resp = http_json(url, payload, bearer(key), timeout)
    image = extract_image_url(resp)
    if not image:
        raise RuntimeError(f"no image in response: {json.dumps(resp, ensure_ascii=False)[:400]}")
    return image


def call_dashscope_async(model, prompt, size, key, timeout):
    submit_url = f"{DASHSCOPE_BASE}/api/v1/services/aigc/image-generation/generation"
    payload = {
        "model": model,
        "input": {"prompt": prompt},
        "parameters": {"size": size.replace("x", "*"), "n": 1, "watermark": False},
    }
    headers = bearer(key)
    headers["X-DashScope-Async"] = "enable"
    resp = http_json(submit_url, payload, headers, timeout)
    task_id = (resp.get("output") or {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"no task_id: {json.dumps(resp, ensure_ascii=False)[:400]}")
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(5)
        status_resp = http_json(
            f"{DASHSCOPE_BASE}/api/v1/tasks/{task_id}",
            None,
            bearer(key),
            timeout,
            method="GET",
        )
        status = (status_resp.get("output") or {}).get("task_status", "")
        if status == "SUCCEEDED":
            image = extract_image_url(status_resp)
            if not image:
                raise RuntimeError("task succeeded but no image returned")
            return image
        if status in ("FAILED", "CANCELED"):
            raise RuntimeError(f"task {status}: {json.dumps(status_resp, ensure_ascii=False)[:400]}")
    raise RuntimeError(f"async task {task_id} timed out after {timeout}s")


def call_ark(model, prompt, size, key, timeout):
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "watermark": False,
        "response_format": "url",
    }
    resp = http_json(f"{ARK_BASE}/images/generations", payload, bearer(key), timeout)
    data = resp.get("data") or []
    if not data:
        raise RuntimeError(f"empty data: {json.dumps(resp, ensure_ascii=False)[:400]}")
    item = data[0]
    if item.get("url"):
        return item["url"]
    if item.get("b64_json"):
        return f"data:image/png;base64,{item['b64_json']}"
    raise RuntimeError(f"no url/b64 in response: {json.dumps(resp, ensure_ascii=False)[:400]}")


HANDLERS = {
    "dashscope_sync": call_dashscope_sync,
    "dashscope_async": call_dashscope_async,
    "ark": call_ark,
}


def available_providers():
    return [p for p in PROVIDERS if os.environ.get(p["env"])]


def pick_model(provider, prompt):
    low = prompt.lower()
    for pattern, model in TASK_HINTS:
        if re.search(pattern, low) and model in provider["models"]:
            return model
    if DEFAULT_MODEL in provider["models"]:
        return DEFAULT_MODEL
    return next(iter(provider["models"]))


def route(args, providers):
    if args.model:
        for p in providers:
            if args.model in p["models"]:
                return p, args.model, "用户显式指定模型"
        sys.exit(f"ERROR: 模型 {args.model} 未注册或对应提供方未配置 Key")
    if args.provider:
        for p in providers:
            if p["id"] == args.provider:
                return p, pick_model(p, args.prompt), "用户指定提供方，模型按任务类型选择"
        sys.exit(f"ERROR: 提供方 {args.provider} 未注册或未配置 Key")
    low = args.prompt.lower()
    for pattern, model in TASK_HINTS:
        if re.search(pattern, low):
            for p in providers:
                if model in p["models"]:
                    return p, model, f"命中任务类型规则「{pattern}」"
    for p in providers:
        if DEFAULT_MODEL in p["models"]:
            return p, DEFAULT_MODEL, "默认模型"
    p = providers[0]
    return p, pick_model(p, args.prompt), "回退到首个可用提供方"


def download(image_ref, output, timeout):
    if image_ref.startswith("data:image"):
        b64 = image_ref.split(",", 1)[1]
        data = base64.b64decode(b64)
    elif image_ref.startswith("http"):
        with urllib.request.urlopen(image_ref, timeout=timeout) as resp:
            data = resp.read()
    else:
        raise RuntimeError(f"unsupported image reference: {image_ref[:60]}")
    ext = ".png"
    if data[:3] == b"\xff\xd8\xff":
        ext = ".jpg"
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        ext = ".png"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        ext = ".webp"
    if not os.path.splitext(output)[1]:
        output += ext
    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with open(output, "wb") as f:
        f.write(data)
    return os.path.abspath(output), len(data)


def print_guidance():
    print("未检测到任何生图 API Key。请先配置以下任一环境变量：")
    for p in PROVIDERS:
        print(f"  - {p['env']}: {p['name']} → {p['key_url']}")


def main():
    parser = argparse.ArgumentParser(description="Route and call the user's image generation APIs")
    parser.add_argument("prompt", nargs="?", help="image description")
    parser.add_argument("-p", "--provider", help="dashscope | ark")
    parser.add_argument("-m", "--model", help="model id, e.g. qwen-image-2.0-pro")
    parser.add_argument("-s", "--size", default="1024x1024", help="output size")
    parser.add_argument("-o", "--output", default="generated_image", help="output file path")
    parser.add_argument("--timeout", type=int, default=180, help="request timeout seconds")
    parser.add_argument("--dry-run", action="store_true", help="print route only")
    parser.add_argument("--list", action="store_true", help="list registered providers and models")
    args = parser.parse_args()

    if args.list:
        for p in PROVIDERS:
            marker = "可用" if os.environ.get(p["env"]) else "未配置"
            models = ", ".join(p["models"])
            print(f"[{marker}] {p['id']} ({p['env']}) -> {models}")
        return 0

    if not args.prompt:
        parser.error("prompt is required (or use --list)")

    providers = available_providers()
    if not providers:
        print_guidance()
        return 1

    primary, model, reason = route(args, providers)
    print(f"route: provider={primary['id']} model={model}\nreason: {reason}")
    if args.dry_run:
        return 0

    explicit = bool(args.provider or args.model)
    candidates = [(primary, model)]
    if not explicit:
        for p in providers:
            if p["id"] != primary["id"]:
                candidates.append((p, pick_model(p, args.prompt)))

    failures = []
    for p, m in candidates:
        key = os.environ[p["env"]]
        kind = p["models"][m]["kind"]
        size = args.size if p["id"] == "ark" else args.size
        try:
            image_ref = HANDLERS[kind](m, args.prompt, size, key, args.timeout)
            output, size_bytes = download(image_ref, args.output, args.timeout)
        except Exception as exc:
            failures.append(f"{p['id']}/{m}: {exc}")
            continue
        print(f"provider={p['id']}\nmodel={m}\nsaved={output} ({size_bytes} bytes)")
        return 0

    print("ERROR: 所有候选调用均失败：")
    for f in failures:
        print(f"  - {f}")
    print("建议：检查 Key 配额/权限，换 --provider/--model，或稍后重试。")
    return 2


if __name__ == "__main__":
    sys.exit(main())
