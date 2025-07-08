from constants import BD

tables_structure={
    "table_name":str,
    "pv_number":int,
    "etablissement":str,
    "centre_composition":str,
    "nom":str,
    "prenom":str,
    "statut":int,
    "mention":int
}


def filter_by_pv_number_statement(pv_number:int):
    query=f"SELECT * FROM resultats_2025_1er_tour WHERE numero_pv = {pv_number};"
    return query

def seed_statement(tables_structures:dict ):
    table_name = tables_structures["table_name"]
    # delete the table_name to the columns to add
    columns = [col for col in tables_structure if col != "table_name"]
    
    # sql request with %s placeholders
    query = f"""
    INSERT INTO {table_name} ({', '.join(columns)})
    VALUES ({', '.join(['%s'] * len(columns))});
    """
    return query

def select_table_statements(filename:str)->str:
    query=f"""SELECT table_name 
    FROM information_schema.tables 
    WHERE table_name = '{filename}';"""
    return query

