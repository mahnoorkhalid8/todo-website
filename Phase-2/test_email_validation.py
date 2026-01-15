from pydantic import BaseModel, Field, ValidationError
from pydantic.networks import EmailStr

print("Testing email validation...")

class User(BaseModel):
    email: EmailStr

try:
    user = User(email='test@example.com')
    print(f"SUCCESS: Email validation works: {user.email}")
except ValidationError as e:
    print(f"ERROR: Validation error: {e}")

print("Test completed successfully!")