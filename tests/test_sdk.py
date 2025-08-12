# test_sdk.py
from persisto.client import PersistoClient, PersistoNotFoundError, PersistoAuthError
import os
import time
from dotenv import load_dotenv
from uuid import uuid4

class _P:
    def __init__(self, name, min_sim):
        self.name = name
        self.min_sim = min_sim
DEFAULT_PROFILES = {
    "strict": _P("strict", 0.55),
    "fuzzy":  _P("fuzzy", 0.25),
    "recency": _P("recency", 0.30),
}

load_dotenv()
api_key = os.getenv("PERSISTO_API_KEY")
client = PersistoClient(api_key)

# Unique TTL memory
unique_ttl_content = f"This memory will self-destruct: test-{uuid4()}"

def print_result_label(label, res):
    print(f"\n{label}")
    if isinstance(res, dict) and "results" in res:
        print(f"- count: {len(res['results'])}")
        if res["results"]:
            top = res["results"][0]
            sim = top.get("similarity")
            print(f"- top.similarity: {sim:.4f}" if isinstance(sim, (int, float)) else f"- top.similarity: {sim}")
            print(f"- top.content: {top.get('content')[:120]}")
    else:
        print(res)

# print("\nCleaning up old test data...")
# client.delete(namespace="profiles-test", metadata={"topic": "sports"})
# client.delete(namespace="auth-test", metadata={"source": "sdk-auth"})
# client.delete(namespace="demo-test", metadata={"source": "sdk-auth"})

# 🔹 Seed memories
print("\nSeeding profile test memories...")
client.save(namespace="profiles-test", content="The team won the soccer match in overtime.", metadata={"topic": "sports"})
client.save(namespace="profiles-test", content="We discussed quarterly revenue growth of 24% YoY.", metadata={"topic": "finance"})
client.save(namespace="profiles-test", content="New UI components were added to the design system.", metadata={"topic": "eng"})

print("\nSaving memory...")
print("Save response 1:", client.save(namespace="auth-test", content="This memory should be saved with auth", metadata={"source": "sdk-auth"}))
print("Save response 2:", client.save(namespace="demo-test", content="I like soccer", metadata={"source": "sdk-auth"}))
print("Save response 3:", client.save(namespace="auth-test", content="I am using auth", metadata={"source": "test"}))

# 🔹 TTL Test
print("\nSaving short-lived memory (TTL = 3s)...")
print("TTL save response:", client.save(namespace="auth-test", content=unique_ttl_content, metadata={"source": "ttl-test"}, ttl_seconds=3))
print("Waiting 4 seconds for TTL to expire...")
time.sleep(4)

print("Querying for expired memory...")
print("Query results (should NOT include TTL memory):", client.query(namespace="auth-test", query="self-destruct"))

# 🔹 Regular Query Test
print("\nQuerying memory...")
print("Query results:", client.query(namespace="auth-test", query="What memory did I just save?"))

# 🔷 Retrieval Profiles — diagnostic version
print("\n=== Retrieval Profiles Diagnostic ===")
test_queries = {
    "far": "football results",      # likely below fuzzy threshold
    "close": "soccer match results" # likely above fuzzy threshold
}

for profile_name, profile in DEFAULT_PROFILES.items():
    print(f"\n--- Profile: {profile_name.upper()} ---")
    print(f"min_sim = {profile.min_sim}")

    for q_label, q_text in test_queries.items():
        res = client.query(namespace="profiles-test", query=q_text, mode=profile_name, k=10)
        print_result_label(f"{profile_name.upper()} | {q_label} query: \"{q_text}\"", res)

# Heuristic fuzzy vs strict length
try:
    strict_close = len(client.query(namespace="profiles-test", query=test_queries["close"], mode="strict").get("results", []))
    fuzzy_close = len(client.query(namespace="profiles-test", query=test_queries["close"], mode="fuzzy").get("results", []))
    print(f"\nHeuristic: fuzzy close-count ({fuzzy_close}) vs strict close-count ({strict_close})")
except Exception:
    pass

# 🔹 Delete Test
print("\nDeleting memory...")
print("Delete response:", client.delete(namespace="auth-test", metadata={"source": "sdk-auth"}))

# 🔹 List Namespaces Test
print("\nListing namespaces...")
print("Namespaces:", client.list_namespaces())

print("\nListing past queries...")
for q in client.list_queries(namespace="auth-test"):
    print(q)

try:
    print("\nTesting nonexistent query (should raise 404)...")
    client.query(namespace="nonexistent", query="test")
except PersistoNotFoundError:
    print("✅ Caught 404")
except PersistoAuthError:
    print("❌ Invalid API key")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

# EASY Controls
print("\nControl: exact-ish match in demo-test")
print(client.query(namespace="demo-test", query="I like soccer", mode="fuzzy", k=10))

print("\nControl: semantic match in profiles-test (sports)")
print(client.query(namespace="profiles-test", query="soccer match overtime", mode="fuzzy", k=10))

print("\nControl: auth-test")
print(client.query(namespace="auth-test", query="I am using auth", mode="strict"))
