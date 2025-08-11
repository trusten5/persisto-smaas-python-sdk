# test_profiles.py
import os
import sys
import time
from uuid import uuid4
from dotenv import load_dotenv

DEBUG_SHOW_RAW = True  # show kwargs and a peek at raw responses

# ----------------------------
# SDK import
# ----------------------------
try:
    from persisto.client import PersistoClient
except Exception as e:
    print("Failed to import PersistoClient. Check your SDK path.\n", e)
    sys.exit(1)

# ----------------------------
# Profiles (for printing only)
# ----------------------------

class _P:
    def __init__(self, name, min_sim):
        self.name = name
        self.min_sim = min_sim
DEFAULT_PROFILES = {
    "strict": _P("strict", 0.55),
    "fuzzy":  _P("fuzzy", 0.25),
    "recency": _P("recency", 0.30),
}

# ----------------------------
# Helpers
# ----------------------------
def extract_results(resp):
    if resp is None:
        return []
    if isinstance(resp, list):
        return resp
    if isinstance(resp, dict):
        if isinstance(resp.get("results"), list):
            return resp["results"]
        if isinstance(resp.get("matches"), list):
            return resp["matches"]
        data = resp.get("data")
        if isinstance(data, dict):
            if isinstance(data.get("results"), list):
                return data["results"]
            if isinstance(data.get("matches"), list):
                return data["matches"]
    return []

def top_content(row):
    return row.get("content") or row.get("text") or row.get("chunk") or str(row)

def top_score(row):
    return row.get("similarity") or row.get("score")

def print_profile_result(profile_name, query_label, query_text, resp, show_example=False):
    rows = extract_results(resp)
    print(f"\n[{profile_name.upper()}] {query_label} → \"{query_text}\"")
    print(f"- count: {len(rows)}")
    if rows:
        t = rows[0]
        score = top_score(t)
        print(f"- top.similarity: {score:.4f}" if isinstance(score, (int, float)) else f"- top.similarity: {score}")
        print(f"- top.content: {top_content(t)[:200]}")
        if show_example and len(rows) > 1:
            print(f"- 2nd.content: {top_content(rows[1])[:200]}")

def run_query(client, *, namespace, query, mode=None, k=5, metadata=None):
    kwargs = dict(namespace=namespace, query=query, k=k)
    if mode is not None:
        kwargs["mode"] = mode
    if metadata:
        kwargs["metadata"] = metadata
    if DEBUG_SHOW_RAW:
        print("  KWARGS:", kwargs)
    resp = client.query(**kwargs)
    if DEBUG_SHOW_RAW:
        if isinstance(resp, dict):
            print("  RAW resp keys:", list(resp.keys()))
        elif isinstance(resp, list):
            print(f"  RAW resp: list(len={len(resp)}) sample:", resp[:1])
        else:
            print("  RAW resp type:", type(resp))
    return resp

def must_env(var_name: str) -> str:
    v = os.getenv(var_name)
    if not v:
        print(f"Missing required environment variable: {var_name}")
        sys.exit(1)
    return v

def safe_save(client, **kwargs):
    try:
        res = client.save(**kwargs)
        ok = bool(res) and (not isinstance(res, dict) or "error" not in res)
        if not ok:
            print("⚠️  Save returned non-ok payload:", res)
        return res
    except Exception as e:
        print("❌ Save raised an exception:", e)
        return None

def sanity_query(client, namespace: str):
    print("\n=== Quick control queries (should return something) ===")
    try:
        r1 = client.query(namespace=namespace, query="I like soccer", mode="fuzzy", k=10)
        print_profile_result("fuzzy", "control-1", "I like soccer", r1)
        r2 = client.query(namespace=namespace, query="soccer match overtime", mode="fuzzy", k=10)
        print_profile_result("fuzzy", "control-2", "soccer match overtime", r2)
    except Exception as e:
        print("Control queries failed:", e)

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    load_dotenv()
    api_key = must_env("PERSISTO_API_KEY")
    client = PersistoClient(api_key)

    # fresh namespace per run
    ns = f"profiles-test-{uuid4().hex[:8]}"

    print("\n=== Seeding retrieval profile test data ===")
    safe_save(client, namespace=ns, content="The team won the soccer match in overtime.", metadata={"topic": "sports"})
    safe_save(client, namespace=ns, content="We discussed quarterly revenue growth of 24% YoY.", metadata={"topic": "finance"})
    safe_save(client, namespace=ns, content="New UI components were added to the design system.", metadata={"topic": "eng"})

    recent_content = f"Breaking news in soccer: {uuid4()}"
    print("\nSaving recency test memory (TTL = 60s)...")
    safe_save(client, namespace=ns, content=recent_content, metadata={"topic": "sports"}, ttl_seconds=60)

    # let embeddings/indexing catch up if async
    time.sleep(2)

    # sanity
    sanity_query(client, ns)

    # direct mode comparison on known-good string
    print("\n=== Direct mode comparison on 'soccer match overtime' ===")
    for mode in ["strict", "fuzzy", "recency"]:
        try:
            resp = run_query(client, namespace=ns, query="soccer match overtime", mode=mode, k=5)
            print_profile_result(mode, "exact", "soccer match overtime", resp)
        except Exception as e:
            print(f"direct {mode} failed:", e)

    # probes
    queries = {
        "far":   "football results",
        "close": "soccer match results",
        "exact": "soccer match overtime",  # proven-good
    }

    # profile diagnostics (note: thresholds live server-side; we only pass mode)
    print("\n=== Running profile diagnostics ===")
    for profile_name, profile in DEFAULT_PROFILES.items():
        print(f"\n--- Profile: {profile_name.upper()} ---")
        min_sim = getattr(profile, "min_sim", None)
        print(f"min_sim (server-defined): {min_sim}")
        filters = getattr(profile, "filters", None) or getattr(profile, "metadata_filters", None)
        if filters:
            print(f"filters (server-defined): {filters}")

        for q_label, q_text in queries.items():
            try:
                resp = run_query(client, namespace=ns, query=q_text, mode=profile_name, k=5)
                print_profile_result(profile_name, q_label, q_text, resp)
            except Exception as e:
                print(f"{profile_name} query failed ({q_label}):", e)

    # heuristic
    try:
        strict_close = extract_results(run_query(client, namespace=ns, query=queries["close"], mode="strict", k=5))
        fuzzy_close  = extract_results(run_query(client, namespace=ns, query=queries["close"], mode="fuzzy", k=5))
        print(f"\nHeuristic: fuzzy close-count ({len(fuzzy_close)}) vs strict close-count ({len(strict_close)})")
    except Exception as e:
        print(f"Heuristic check failed: {e}")

    # recency checks
    print("\nRecency profile should boost most recent memory...")
    try:
        recency_res_exact  = run_query(client, namespace=ns, query=recent_content, mode="recency", k=3)
        print_profile_result("recency", "recent exact", recent_content, recency_res_exact, show_example=True)

        recency_res_soccer = run_query(client, namespace=ns, query="soccer", mode="recency", k=3)
        print_profile_result("recency", "recent soccer", "soccer", recency_res_soccer, show_example=True)

        rows = extract_results(recency_res_soccer)
        recent_hit = any(top_content(r).startswith("Breaking news in soccer:") for r in rows)
        print(f"- recent_hit_in_topk: {recent_hit}")
    except Exception as e:
        print("Recency check failed:", e)

    print("\n✅ Retrieval profile test complete.")
