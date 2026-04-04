from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, EmailStr, Field
from services.auth_service import signup_user, login_user
from database.organization_queries import create_org
from Utils.security import create_access_token, verify_access_token, get_current_user
from fastapi import Request, Depends
from services.organization_service import join_organization
from database.admin_queries import view_perms
from typing import List
app = FastAPI()

class SignupLoginRequest(BaseModel):
    email: EmailStr
    # password: str = Field(..., min_length=8, max_length=128)
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
    organization_id: int
    invite_key: str

class MakeMemberRequest(BaseModel):
    user_id: int
    invite_key: str

class MakeMemberResponse(BaseModel):
    membership_id: int
    message: str

class ViewMembersResponse(BaseModel):
    user_id: int
    role: str

@app.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupLoginRequest):
    try:
        return signup_user(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.post("/login", response_model=TokenResponse)
def login(data: SignupLoginRequest):
    try:
        return login_user(data.email, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@app.post("/organizations", response_model=OrganizationCreateResponse, status_code=status.HTTP_201_CREATED)
def createorg(data: OrganizationCreateRequest, current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        return create_org(data.name, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.post("/membership", response_model=MakeMemberResponse, status_code=status.HTTP_201_CREATED)
def makemember(data: MakeMemberRequest, current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        return join_organization(user_id, data.invite_key)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.get("/organization/{org_id}/membership", response_model=List[ViewMembersResponse])
def viewperms(org_id: int, current_user = Depends(get_current_user)):
    try:
        return view_perms(org_id)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

