# core/llm_client.py
import os, time, httpx

BASE_URL = (
    os.getenv("OLLAMA_BASE_URL")
    or os.getenv("OPENAI_BASE_URL")
    or "http://localhost:11434"
).rstrip("/")

API_KEY  = os.getenv("OPENAI_API_KEY", "ollama")  # Ollama không check key
HTTP_TIMEOUT_SEC = float(os.getenv("HTTP_TIMEOUT_SEC", "600"))
HTTP_RETRIES     = int(os.getenv("HTTP_RETRIES", "2"))
HTTP_BACKOFF_SEC = float(os.getenv("HTTP_RETRY_BACKOFF", "2.0"))
DEBUG_EMBED      = os.getenv("DEBUG_EMBED", "0") == "1"

def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    }

def _client():
    return httpx.Client(
        timeout=httpx.Timeout(connect=HTTP_TIMEOUT_SEC, read=HTTP_TIMEOUT_SEC, write=HTTP_TIMEOUT_SEC, pool=None),
        http2=False,
    )

def chat(messages, model=None, max_tokens=256, temperature=0.0):
    mdl = model or os.getenv("LLM_MODEL", "qwen2.5:3b-instruct")
    url = f"{BASE_URL}/v1/chat/completions"
    payload = {"model": mdl, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}

    last_err = None
    for attempt in range(HTTP_RETRIES + 1):
        try:
            with _client() as client:
                r = client.post(url, headers=_headers(), json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            last_err = e
            if attempt < HTTP_RETRIES:
                time.sleep(HTTP_BACKOFF_SEC * (attempt + 1))
            else:
                raise last_err

def _normalize_embeddings_payload(data):
    if data is None:
        return []
    if isinstance(data, dict) and isinstance(data.get("embedding"), list):
        return [data["embedding"]]
    if isinstance(data, dict) and isinstance(data.get("embeddings"), list):
        embs = data["embeddings"]
        if embs and isinstance(embs[0], list):
            return embs
        if embs and isinstance(embs[0], dict) and "embedding" in embs[0]:
            return [e["embedding"] for e in embs]
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [e.get("embedding") for e in data["data"]]
    if isinstance(data, list) and data and isinstance(data[0], dict) and "embedding" in data[0]:
        return [e["embedding"] for e in data]
    return []

def embed_ollama(texts, model=None):
    """
    Ưu tiên Ollama native /api/embeddings (prompt),
    nếu 404 thì fallback sang OpenAI-compatible /v1/embeddings (input).
    """
    mdl = model or os.getenv("EMBED_MODEL", "nomic-embed-text")
    base = BASE_URL

    outs = []
    last_err = None

    for t in texts:
        # 1) thử native
        payload_native = {"model": mdl, "prompt": t}
        url_native = f"{base}/api/embeddings"

        # 2) fallback openai-compatible
        payload_oai = {"model": mdl, "input": t}
        url_oai = f"{base}/v1/embeddings"

        for attempt in range(HTTP_RETRIES + 1):
            try:
                with _client() as client:
                    r = client.post(url_native, headers=_headers(), json=payload_native)
                if r.status_code == 404:
                    # thử openai-compatible
                    with _client() as client:
                        r2 = client.post(url_oai, headers=_headers(), json=payload_oai)
                    r2.raise_for_status()
                    data = r2.json()
                    # dạng OpenAI: {"data":[{"embedding":[...]}]}
                    emb_list = data.get("data", [])
                    if not emb_list:
                        raise RuntimeError(f"Empty embedding (v1) for model={mdl}")
                    emb = emb_list[0].get("embedding")
                else:
                    r.raise_for_status()
                    data = r.json()
                    emb = data.get("embedding")

                if not isinstance(emb, list) or not emb or not isinstance(emb[0], (int, float)):
                    raise RuntimeError(f"Embeddings malformed for model={mdl}")
                outs.append(emb)
                break
            except Exception as e:
                last_err = e
                if attempt < HTTP_RETRIES:
                    time.sleep(HTTP_BACKOFF_SEC * (attempt + 1))
                else:
                    raise last_err

    return outs
