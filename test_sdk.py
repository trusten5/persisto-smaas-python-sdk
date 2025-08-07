# test_sdk.py
from sdk.python.persisto.client import PersistoClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PERSISTO_API_KEY")

client = PersistoClient(api_key)

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

print("\nListing namespaces...")
print("Namespaces:", client.list_namespaces())
