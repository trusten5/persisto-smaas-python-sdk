from sdk.python.persisto.client import PersistoClient, PersistoNotFoundError, PersistoAuthError
import os
import time
from dotenv import load_dotenv
from uuid import uuid4
unique_ttl_content = f"This memory will self-destruct: test-{uuid4()}"


load_dotenv()

api_key = os.getenv("PERSISTO_API_KEY")
client = PersistoClient(api_key)

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
    client.query("nonexistent", "test")
except PersistoNotFoundError:
    print("✅ Caught 404")
except PersistoAuthError:
    print("❌ Invalid API key")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
