from sdk.python.persisto.client import PersistoClient

client = PersistoClient(api_key="your-api-key")

# Save memory
print("\nSaving memory...")
save_response = client.save(
    namespace="test",
    content="The user asked for a summary of a 10-K document",
    metadata={"type": "summary", "source": "api-test"}
)
print("Save response:", save_response)

# Query memory
print("\nQuerying memory...")
query_results = client.query(
    namespace="test",
    query="What did the user ask?",
    filters={"type": "summary"},
    top_k=1
)
print("Query results:", query_results)

# Delete memory
print("\nDeleting memory...")
delete_response = client.delete(
    namespace="test",
    content="The user asked for a summary of a 10-K document"
)
print("Delete response:", delete_response)
