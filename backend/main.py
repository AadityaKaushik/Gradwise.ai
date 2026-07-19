from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, EmailStr, Field
from services.auth_service import signup_user, login_user
from database.organization_queries import create_org
from Utils.security import create_access_token, verify_access_token, get_current_user, require_org_admin
from fastapi import Request, Depends
from services.organization_service import join_organization
from database.admin_queries import view_perms
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ViewMembersResponse(BaseModel):
    user_id: int
    role: str
    status: str

class ChangePerms(BaseModel):
    user_id: int
    role: str

class ChangePermsResponse(BaseModel):
    membership_id: int
    role: str
    message: str


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

class OrganizationListItem(BaseModel):
    organization_id: int
    role: str
    status: str
    name: str
    invite_key: str

@app.get("/organizations", response_model=List[OrganizationListItem])
def listorgs(current_user = Depends(get_current_user)):
    from services.organization_service import get_organizations
    user_id = current_user["user_id"]
    return get_organizations(user_id)

@app.post("/membership", response_model=MakeMemberResponse, status_code=status.HTTP_201_CREATED)
def makemember(data: MakeMemberRequest, current_user = Depends(get_current_user)):
    user_id = current_user["user_id"]
    try:
        return join_organization(user_id, data.invite_key)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.get("/organization/{org_id}/membership", response_model=List[ViewMembersResponse])
def viewperms(org_id: int, current_user = Depends(require_org_admin)):
    try:
        return view_perms(org_id)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.patch("/organization/{org_id}/membership", response_model=ChangePermsResponse)
def changeperms(org_id: int, data: ChangePerms, current_user = Depends(require_org_admin)):
    from database.admin_queries import update_membership_role
    try:
        return update_membership_role(org_id, data.user_id, data.role.upper())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Include New Routers ──────────────────────────────────────────────

from routes.academic_router import router as academic_router
from routes.people_router import router as people_router
from routes.teaching_router import router as teaching_router
from routes.assessment_router import router as assessment_router
from routes.attendance_router import router as attendance_router
from routes.results_router import router as results_router

app.include_router(academic_router)
app.include_router(people_router)
app.include_router(teaching_router)
app.include_router(assessment_router)
app.include_router(attendance_router)
app.include_router(results_router)
