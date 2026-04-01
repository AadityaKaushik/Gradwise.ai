from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr
from services.auth_service import signup_user, login_user
from database.organization_queries import create_org
from Utils.security import create_access_token, verify_access_token
app = FastAPI()

class SignupLoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupResponse(BaseModel):
    message: str
    user_id: int

class TokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user_id: int

class OrganizationCreateRequest(BaseModel):
    name: str
    user_id: int

class OrganizationCreateResponse(BaseModel):
    mesage: str
    org_id: int

@app.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupLoginRequest):
    return signup_user(data.email, data.password)

@app.post("/login", response_model=TokenResponse)
def login(data: SignupLoginRequest):
    return login_user(data.email, data.password)

# @app.post("/organization", reponse_model=OrganizationCreateResponse)
# def createorg(data: OrganizationCreateRequest):
#     create
#     return create_org(data.name, data.user_id)

