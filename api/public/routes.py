import os
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.database import DatabaseConnection, sanitize_table_name, sanitize_input
from typing import Optional, Dict, Any
from datetime import datetime
public_router = APIRouter()
# Static files and templates directory 

script_dir = os.getcwd()
st_abs_file_path = os.path.join(script_dir, "templates/")
templates = Jinja2Templates(directory=f"{st_abs_file_path}")

@public_router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "exams": ["CEP", "BEPC", "BAC"],
        "tours": ["1er", "2nd"]
    })

@public_router.post("/search-result")
async def search_result(
    request: Request,
    exam: str = Form(...),
    tour: str = Form(...),
    pv_number: str = Form(...),
):
    """Search for student result by PV number"""
    try:
        # Sanitize inputs
        exam = sanitize_input(exam)
        tour = sanitize_input(tour)
        pv_number = sanitize_input(pv_number)
        year = datetime.now().year
        
        # Generate table name
        table_name = f"resultats_{exam.lower()}_{year}_{tour}_tour"
        
        # Validate table name
        sanitize_table_name(exam, tour)  # This will raise exception if invalid
        
        # Search in database
        result = await get_student_result(table_name, pv_number)
        
        if result:
            return templates.TemplateResponse("result.html", {
                "request": request,
                "result": result,
                "found": True
            })
        else:
            return templates.TemplateResponse("result.html", {
                "request": request,
                "found": False,
                "message": "Aucun résultat trouvé pour ce numéro PV"
            })
            
    except ValueError as e:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "found": False,
            "error": str(e)
        })
    except Exception as e:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "found": False,
            "error": "Erreur lors de la recherche"
        })


async def get_student_result(table_name: str, pv_number: str) -> Optional[Dict[str, Any]]:
    try:
        # Obtenez le gestionnaire de contexte
        connection_manager = DatabaseConnection.get_connection()
        
        with connection_manager as conn:
            # 1. Vérifier que la table existe
            with conn.cursor(dictionary=True) as cursor:
                table_check_query = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
                AND TABLE_TYPE = 'BASE TABLE'
                """
                cursor.execute(table_check_query, (table_name,))
                table_exists = cursor.fetchone()
                # Consume any remaining results
                while cursor.nextset():
                    pass
                
                if not table_exists:
                    print(f"Table {table_name} does not exist")
                    return None
            
            # 2. Vérifier que la colonne 'pv_number' existe
            with conn.cursor(dictionary=True) as cursor:
                column_check_query = """
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
                AND COLUMN_NAME = 'pv_number'
                """
                cursor.execute(column_check_query, (table_name,))
                column_exists = cursor.fetchone()
                # Consume any remaining results
                while cursor.nextset():
                    pass
                
                if not column_exists:
                    print(f"Column 'pv_number' missing in table {table_name}")
                    return None
            
            # 3. Exécuter la requête principale
            with conn.cursor(dictionary=True) as cursor:
                main_query = f"""
                SELECT pv_number, etablissement, centre_composition, 
                       nom, prenom, statut, mention
                FROM `{table_name}`
                WHERE pv_number = %s
                """
                cursor.execute(main_query, (pv_number,))
                result = cursor.fetchone()
                # Consume any remaining results
                while cursor.nextset():
                    pass
                return result
                
    except Exception as e:
        import traceback
        error_msg = f"🚨 Database error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None

# Status and mention mapping for templates
@public_router.get("/api/mappings")
async def get_mappings():
    """Get status and mention mappings for frontend"""
    return {
        "status": {
            0: "Échec",
            1: "Admis",
            2: "Absent"
        },
        "mention": {
            0: "Sans mention",
            1: "Passable",
            2: "Assez Bien",
            3: "Bien",
            4: "Très Bien",
            5: "Excellent"
        }
    }