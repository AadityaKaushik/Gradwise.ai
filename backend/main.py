from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from services.auth_service import signup_user, login_user
app = FastAPI()

class SignupLoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupLoginResponse(BaseModel):
    message: str
    user_id: int

class OrganizationCreateRequest(BaseModel):
    name: str
    user_id: int

@app.post("/signup")
def signup(data: SignupLoginRequest):
    return signup_user(data.email, data.password)

@app.post("/login")
def login(data: SignupLoginRequest):
    return login_user(data.email, data.password)

