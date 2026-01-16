import requests
import json

# Get the OpenAPI schema
response = requests.get("http://localhost:8000/openapi.json")
schema = response.json()

# Look for the register endpoint
register_path = schema.get("paths", {}).get("/api/auth/register", {})
register_post = register_path.get("post", {})

print("Register endpoint schema:")
print(json.dumps(register_post, indent=2))

# Check parameters
parameters = register_post.get("parameters", [])
request_body = register_post.get("requestBody", {})

print(f"\nParameters: {parameters}")
print(f"Request body: {request_body}")

if parameters:
    print("\nPROBLEM: The endpoint still expects parameters instead of a request body!")
    print("This indicates the function signature is still not properly typed.")
else:
    print("\nGOOD: The endpoint expects a request body (no parameters).")