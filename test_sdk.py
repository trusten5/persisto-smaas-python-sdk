# test_sdk.py

from sdk.python.persisto.client import PersistoClient

# Step 1: Init client
client = PersistoClient(api_key="demo-key", base_url="http://localhost:8000")

# Step 2: Save memory
save_response = client.save(
    namespace="demo-namespace",
    content="The user asked for a summary of a 10-K document",
    metadata={"source": "api-test", "type": "summary"}
)
print("Save response:", save_response)

# Step 3: Query memory
query_results = client.query(
    namespace="demo-namespace",
    query="What did the user request?",
    filters={"type": "summary"}
)
print("Query results:", query_results)
