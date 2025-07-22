from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.auth.models import UserModel
from api.core.security import verify_token
from api.core.seeder import seeder
from api.admin.schemas import FileUploadResponse
from openpyxl import load_workbook
import os
from typing import List

admin_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
security = HTTPBearer()

async def get_current_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication"""
    username = verify_token(credentials.credentials)
    user = UserModel.get_user_by_username(username)
    
    if not user or user['role'] not in ['admin', 'operator']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return user

@admin_router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin/login.html", {"request": request})

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user: dict = Depends(get_current_admin_user)):
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "user": current_user
    })

@admin_router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    return templates.TemplateResponse("admin/upload.html", {
        "request": request,
        "user": current_user,
        "exams": ["CEP", "BEPC", "BAC"],
        "tours": ["1er", "2nd"]
    })

@admin_router.post("/upload", response_model=FileUploadResponse)
async def upload_excel_file(
    request: Request,
    exam: str = Form(...),
    tour: str = Form(...),
    year: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_admin_user)
):
    """Upload and process Excel file"""
    try:
        # Validate file
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are allowed")
        
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File too large")
        
        # Save uploaded file temporarily
        upload_dir = "temp_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{exam}_{tour}_{year}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Load Excel file
        workbook = load_workbook(file_path)
        worksheet = workbook.active
        wb_data = list(worksheet.rows)
        
        # Generate table name
        table_name = f"resultats_{exam.upper()}_{tour}_{year}"
        
        # Process with seeder
        result = seeder(wb_data, table_name, year)
        
        # Clean up temp file
        os.remove(file_path)
        
        if result["success"]:
            return templates.TemplateResponse("admin/upload.html", {
                "request": request,
                "user": current_user,
                "exams": ["CEP", "BEPC", "BAC"],
                "tours": ["1er", "2nd"],
                "success_message": result["message"],
                "upload_result": result
            })
        else:
            return templates.TemplateResponse("admin/upload.html", {
                "request": request,
                "user": current_user,
                "exams": ["CEP", "BEPC", "BAC"],
                "tours": ["1er", "2nd"],
                "error_message": result["message"],
                "upload_result": result
            })
            
    except Exception as e:
        return templates.TemplateResponse("admin/upload.html", {
            "request": request,
            "user": current_user,
            "exams": ["CEP", "BEPC", "BAC"],
            "tours": ["1er", "2nd"],
            "error_message": f"Error processing file: {str(e)}"
        })

@admin_router.get("/users", response_class=HTMLResponse)
async def manage_users_page(request: Request, current_user: dict = Depends(get_current_admin_user)):
    """Only admin can manage users"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can manage users")
    
    users = UserModel.get_all_users()
    return templates.TemplateResponse("admin/manage_users.html", {
        "request": request,
        "user": current_user,
        "users": users
    })

@admin_router.post("/users/create")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new user (admin only)"""
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Only admin can create users")
    
    try:
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'role': role
        }
        
        UserModel.create_user(user_data)
        return RedirectResponse(url="/admin/users", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")