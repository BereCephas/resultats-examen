from openpyxl import load_workbook
import mysql.connector
from constants import BD
from sql_statements import select_table_statements

def extract_data_from_excel_file(data_file:str,data_worksheet:str):
    # Load the entire workbook.
    wb = load_workbook(data_file,data_only=True)

    #load workbook
    ws = wb[data_worksheet]
    all_rows = list(ws.rows)
    return all_rows

def table_exist(filename:str)->int:
    #init a connection with the BD
    cnx = mysql.connector.connect(user=BD['user'], password=BD["password"],host=BD["host"],database=BD["database"])
    cursor=cnx.cursor()
    cursor.execute(select_table_statements(filename))
    result=cursor.fetchone()
    if result==None:
        return False
    else:
        return True
    
def create_table_statement(filename: str, structure: dict) -> str:
    # Correspondance Python → SQL
    type_map = {
        int: "SMALLINT",
        str: "VARCHAR(255)"
    }

    # Construction des colonnes SQL
    columns_sql = []
    for column_name, column_type in structure.items():
        sql_type = type_map.get(column_type, "TEXT")  # fallback si type inconnu
        columns_sql.append(f"`{column_name}` {sql_type} NOT NULL")

    # Génération du code final
    query = f"""
    CREATE TABLE `{filename}` (
        {',\n        '.join(columns_sql)}
    ) ENGINE = InnoDB;
    """
    return query.strip()
