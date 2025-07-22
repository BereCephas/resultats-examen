import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.admin.routes import admin_router
from api.public.routes import public_router
from api.auth.auth import auth_router

app = FastAPI(title="Academic Results Management System")

# Static files
script_dir = os.path.dirname(__file__)
st_abs_file_path = os.path.join(script_dir, "static/")
app.mount("/static", StaticFiles(directory=st_abs_file_path), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(public_router, prefix="", tags=["Public"])

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

