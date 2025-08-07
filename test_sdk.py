# test_sdk.py
from sdk.python.persisto.client import PersistoClient, PersistoNotFoundError, PersistoAuthError
import os
import time
from dotenv import load_dotenv
from uuid import uuid4

unique_ttl_content = f"This memory will self-destruct: test-{uuid4()}"

load_dotenv()

api_key = os.getenv("PERSISTO_API_KEY")
client = PersistoClient(api_key)

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

# 🔹 Seed a few memories that help profile tests
print("\nSeeding profile test memories...")
client.save(namespace="profiles-test", content="The team won the soccer match in overtime.", metadata={"topic": "sports"})
client.save(namespace="profiles-test", content="We discussed quarterly revenue growth of 24% YoY.", metadata={"topic": "finance"})
client.save(namespace="profiles-test", content="New UI components were added to the design system.", metadata={"topic": "eng"})

# 🔹 Standard Save Tests
print("\nSaving memory...")
save_response = client.save(
    namespace="auth-test",
    content="This memory should be saved with auth",
    metadata={"source": "sdk-auth"}
)
print("Save response 1:", save_response)

save_response = client.save(
    namespace="demo-test",
    content="I like soccer",
    metadata={"source": "sdk-auth"}
)
print("Save response 2:", save_response)

save_response = client.save(
    namespace="auth-test",
    content="I am using auth",
    metadata={"source": "test"}
)
print("Save response 3:", save_response)

# 🔹 TTL Test
print("\nSaving short-lived memory (TTL = 3s)...")
ttl_response = client.save(
    namespace="auth-test",
    content=unique_ttl_content,
    metadata={"source": "ttl-test"},
    ttl_seconds=3
)
print("TTL save response:", ttl_response)

print("Waiting 4 seconds for TTL to expire...")
time.sleep(4)

print("Querying for expired memory...")
query_results = client.query(
    namespace="auth-test",
    query="self-destruct"
)
print("Query results (should NOT include TTL memory):", query_results)

# 🔹 Regular Query Test
print("\nQuerying memory...")
query_results = client.query(
    namespace="auth-test",
    query="What memory did I just save?"
)
print("Query results:", query_results)

# 🔷 Retrieval Profiles — smoke tests
print("\n=== Retrieval Profiles (strict | fuzzy | recency) ===")

# Use a deliberately loose query against sports content to see fuzzy bring something back even if strict is picky.
strict_res = client.query(namespace="profiles-test", query="football results", mode="strict", k=10)
print_result_label("STRICT results", strict_res)

fuzzy_res = client.query(namespace="profiles-test", query="football results", mode="fuzzy", k=20)
print_result_label("FUZZY results", fuzzy_res)

# Recency will be subtle without big time gaps; still call to ensure the parameter is accepted and returns.
recency_res = client.query(namespace="profiles-test", query="recent announcements or updates", mode="recency", k=10)
print_result_label("RECENCY results", recency_res)

# Optional: a small heuristic check (non-failing) to observe that fuzzy tends to return >= strict
try:
    strict_len = len(strict_res.get("results", []))
    fuzzy_len  = len(fuzzy_res.get("results", []))
    print(f"\nHeuristic: fuzzy count ({fuzzy_len}) vs strict count ({strict_len})")
except Exception:
    pass

# 🔹 Delete Test
print("\nDeleting memory...")
delete_response = client.delete(
    namespace="auth-test",
    metadata={"source": "sdk-auth"}
)
print("Delete response:", delete_response)

# 🔹 List Namespaces Test
print("\nListing namespaces...")
print("Namespaces:", client.list_namespaces())

print("\nListing past queries...")
queries = client.list_queries(namespace="auth-test")
for q in queries:
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


# EASY Test

print("\nControl: exact-ish match in demo-test")
print(client.query(namespace="demo-test", query="I like soccer", mode="fuzzy", k=10))

print("\nControl: semantic match in profiles-test (sports)")
print(client.query(namespace="profiles-test", query="soccer match overtime", mode="fuzzy", k=10))

print("\nControl: auth-test")
print(client.query(namespace="auth-test", query="I am using auth", mode="strict"))
