import mysql.connector
import random
from typing import List, Dict, Any
from api.database import DatabaseConnection
from api.config import settings

def table_exists(table_name: str) -> bool:
    """Check if table exists in database"""
    with DatabaseConnection.get_connection() as conn:
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*)
        FROM information_schema.tables 
        WHERE table_schema = %s AND table_name = %s
        """
        cursor.execute(query, (settings.DB_NAME, table_name))
        result = cursor.fetchone()
        return result[0] > 0

def create_results_table(table_name: str) -> str:
    """Generate CREATE TABLE statement for results"""
    return f"""
    CREATE TABLE `{table_name}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pv_number VARCHAR(20) NOT NULL UNIQUE,
        etablissement VARCHAR(255) NOT NULL,
        centre_composition VARCHAR(255) NOT NULL,
        nom VARCHAR(100) NOT NULL,
        prenom VARCHAR(100) NOT NULL,
        statut TINYINT NOT NULL DEFAULT 0 COMMENT '0=Failed, 1=Passed, 2=Absent',
        mention TINYINT NOT NULL DEFAULT 0 COMMENT '0=None, 1=Passable, 2=Assez Bien, 3=Bien, 4=Très Bien, 5=Excellent',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_pv_number (pv_number),
        INDEX idx_nom_prenom (nom, prenom),
        INDEX idx_etablissement (etablissement)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """

def seeder(wb_data: List, table_name: str, year: str) -> Dict[str, Any]:
    """
    Fill database with Excel data
    Returns processing results
    """
    results = {
        "success": False,
        "table_name": table_name,
        "records_processed": 0,
        "records_inserted": 0,
        "errors": [],
        "message": ""
    }
    
    with DatabaseConnection.get_connection() as conn:
        cursor = conn.cursor()
        
        try:
            # Check if table exists
            if table_exists(table_name):
                results["message"] = "Table already exists"
                results["success"] = False
                return results
            
            # Create table
            create_query = create_results_table(table_name)
            cursor.execute(create_query)
            
            # Process data (skip header row)
            for i, row in enumerate(wb_data[1:], start=2):
                try:
                    # Skip empty rows
                    if not row[9].value or row[9].value == "":
                        continue
                    
                    # Extract data
                    pv_number = str(row[9].value).strip()
                    etablissement = str(row[3].value).strip() if row[3].value else ""
                    centre_composition = str(row[6].value).strip() if row[6].value else ""
                    nom = str(row[10].value).strip() if row[10].value else ""
                    prenom = str(row[11].value).strip() if row[11].value else ""
                    
                    # Generate random status and mention for demo
                    # In real scenario, these would come from Excel
                    statut = random.randint(0, 2)
                    mention = random.randint(0, 5) if statut == 1 else 0
                    
                    # Insert into database
                    insert_query = f"""
                    INSERT INTO `{table_name}` 
                    (pv_number, etablissement, centre_composition, nom, prenom, statut, mention)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_query, (
                        pv_number, etablissement, centre_composition,
                        nom, prenom, statut, mention
                    ))
                    
                    results["records_inserted"] += 1
                    results["records_processed"] += 1
                    
                except Exception as e:
                    results["errors"].append(f"Row {i}: {str(e)}")
                    results["records_processed"] += 1
            
            # Commit all changes
            conn.commit()
            results["success"] = True
            results["message"] = f"Successfully processed {results['records_inserted']} records"
            
        except mysql.connector.Error as err:
            conn.rollback()
            results["message"] = f"Database error: {str(err)}"
            results["errors"].append(str(err))
        except Exception as e:
            conn.rollback()
            results["message"] = f"General error: {str(e)}"
            results["errors"].append(str(e))
        
        return results