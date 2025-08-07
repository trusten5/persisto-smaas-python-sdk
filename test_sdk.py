# test_sdk.py
from sdk.python.persisto.client import PersistoClient

client = PersistoClient(api_key="your-api-key")

API_KEY = "<key>"

client = PersistoClient(api_key=API_KEY)

print("\nSaving memory...")
save_response = client.save(
    namespace="auth-test",
    content="This memory should be saved with auth",
    metadata={"source": "sdk-auth"}
)
print("Save response:", save_response)

print("\nQuerying memory...")
query_results = client.query(
    namespace="auth-test",
    query="What memory did I just save?"
)
print("Query results:", query_results)

print("\nDeleting memory...")
delete_response = client.delete(
    namespace="auth-test",
    metadata={"source": "sdk-auth"}
)
print("Delete response:", delete_response)

