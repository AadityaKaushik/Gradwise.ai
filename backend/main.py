from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr, Field
from services.auth_service import signup_user, login_user
from database.organization_queries import create_org
from Utils.security import create_access_token, verify_access_token, get_current_user
from fastapi import Request, Depends
from services.organization_service import join_organization

app = FastAPI()

class SignupLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

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
    organization_id: int
    invite_key: str

class MakeMemberRequest(BaseModel):
    user_id: int
    invite_key: str

class MakeMemberResponse(BaseModel):
    membership_id: int
    message: str

@app.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupLoginRequest):
    return signup_user(data.email, data.password)

@app.post("/login", response_model=TokenResponse)
def login(data: SignupLoginRequest):
    return login_user(data.email, data.password)

@app.post("/organizations", response_model=OrganizationCreateResponse, status_code=status.HTTP_201_CREATED)
def createorg(data: OrganizationCreateRequest, current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return create_org(data.name, user_id)

@app.post("/membership", response_model=MakeMemberResponse, status_code=status.HTTP_201_CREATED)
def makemember(data: MakeMemberRequest, current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    return join_organization(user_id, data.invite_key)

# @app.get("/organization/{org_id}/membership")