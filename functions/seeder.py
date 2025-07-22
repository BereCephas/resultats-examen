import mysql.connector
import random 
from sql_statements import seed_statement
from utils import extract_data_from_excel_file,table_exist,create_table_statement
from constants import BD,result_table_structure

# extract data from the excel file
wb_data=extract_data_from_excel_file("excel-files\\samples\\resultats_bac_2025.xlsx","CENTRE LISTE GLE")

# function to fill the BD with Data
def seeder(wb_data: list, filename):
    # init a connection with the BD
    cnx = mysql.connector.connect(
        user=BD['user'], 
        password=BD["password"],
        host=BD["host"],
        database=BD["database"]
    )
    cursor = cnx.cursor()
    
    try:
        # --- seed with the excel file data---
        
        # verify if the tables already exist
        if table_exist(filename):
            print({"message": "table already exist"})
            return False
        else:
            # create the table
            query = create_table_statement(filename, result_table_structure)
            cursor.execute(query)
            
            # Pull information from specific cells.
            for row in wb_data[1:]:
                numero_pv = row[9].value
                etablissement = row[3].value
                centre_composition = row[6].value
                nom = row[10].value
                prenom = row[11].value
                # ---fake data---
                status = random.randint(0, 2)
                if status==0 or status==1:
                    mention = 0
                mention = random.randint(0, 5)
                # generate a row object
                row_object = {
                    "table_name": filename,
                    "pv_number": numero_pv,
                    "etablissement": etablissement,
                    "centre_composition": centre_composition,
                    "nom": nom,
                    "prenom": prenom,
                    "statut": status,
                    "mention": mention
                }
                
                query = seed_statement(row_object)
                cursor.execute(query, (
                    row_object["pv_number"],
                    row_object["etablissement"],
                    row_object["centre_composition"],
                    row_object["nom"],
                    row_object["prenom"],
                    row_object["statut"],
                    row_object["mention"]
                ))
            
            # Validate all changements
            cnx.commit()
            print("-------Work Done-------")
            return True
            
    except mysql.connector.Error as err:
        print(f"Erreur MySQL: {err}")
        cnx.rollback()  #stop changements in case of error
        return False
    except Exception as e:
        print(f"Erreur générale: {e}")
        cnx.rollback()
        return False
    finally:
        # close the connection
        cursor.close()
        cnx.close()


seeder(wb_data,"resultats_2025_1er_tour")