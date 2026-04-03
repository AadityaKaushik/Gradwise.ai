from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr
from services.auth_service import signup_user, login_user
from database.organization_queries import create_org
from Utils.security import create_access_token, verify_access_token, get_current_user
from fastapi import Request, Depends

app = FastAPI()

class SignupLoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupResponse(BaseModel):
    message: str
    user_id: int

class TokenResponse(BaseModel):
    message: str
    token: str
    token_type: str = "bearer"
    user_id: int

class OrganizationCreateRequest(BaseModel):
    name: str

class OrganizationCreateResponse(BaseModel):
    message: str
    org_id: int

@app.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupLoginRequest):
    return signup_user(data.email, data.password)

@app.post("/login", response_model=TokenResponse)
def login(data: SignupLoginRequest):
    return login_user(data.email, data.password)

@app.post("/organizations")
def createorg(
    data: OrganizationCreateRequest,
    current_user = Depends(get_current_user)
):
    user_id = current_user["user_id"]
    org = create_org(data.name, user_id)
    return {
        "message": "Organization created",
        "organization": org
    }

