import csv
import json
import openpyxl
import re
import pyodbc

connection_string = 'DSN=dev_independencia;UID=henriquefroeder;PWD=Froeder@'

#o nome precisa ser o mesmo, pq tá fixo
xlsx_filename = "POP2022_Municipios_20230622.xlsx"
csv_filename = "censo.csv"
tabela_banco = "censo"

def get_odbc_connection():
    return pyodbc.connect(connection_string)

try:
    connection = get_odbc_connection()    
    cursor = connection.cursor()
    
    verificaSeExiste = f"SELECT 1 FROM censo WHERE 1=0"
    
    try:
        cursor.execute(verificaSeExiste)
        print(f"A tabela 'censo' já existe. Não é necessário criá-la.")
    except pyodbc.ProgrammingError:
    
        # cria a tabela
        create_table_query = """
        CREATE TABLE censo (
          ID INTEGER NOT NULL DEFAULT AUTOINCREMENT PRIMARY KEY,
          UF VARCHAR(2),
          COD_UF VARCHAR(10),
          COD_MUNIC VARCHAR(10),
          NOMEDOMUNICIPIO VARCHAR(100),
          POPULACAO VARCHAR(20)
        )
        """

        cursor.execute(create_table_query)    
        connection.commit()
        print("Tabela 'censo' criada com sucesso.")    
        
    cursor.close()
    connection.close()
    
except pyodbc.Error as e:
    print("Erro")

workbook = openpyxl.load_workbook(xlsx_filename, read_only=True)
worksheet = workbook.active

#aqui transforma o arquivo que tem os dados que é xlsx para csv
with open(csv_filename, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for row in worksheet.iter_rows(values_only=True):
        if len(row) == 5:
            csv_writer.writerow(row)

# pega uma linha do arquivo csv e coloca nesse data que é uma lista de linhas do arquivo
data = []
with open(csv_filename, 'r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:        
        data.append(row)

# transforma os dados do csv para um formato mais aceitavel do json
connection = get_odbc_connection()    
conexao = connection.cursor()
formatted_data = {}
for row in data:
    uf = row["UF"]
    cod_uf = int(float(row["COD.UF"]))
    cod_municipio = int(float(row["COD.MUNIC"]))
    nome_municipio = row["NOMEDOMUNICÍPIO"]
    #essa população tem algumas coisas que sujam mais os dados com (1), . e , ai foi feito esse regex que tira tudo e transforma em int
    populacao = re.sub(r'\([^)]*\)', '', row["POPULAÇÃO"])
    populacao = re.sub(r'[^\d,]', '', populacao)
    populacao = int(populacao.replace(',', ''))
    
    #quando vai criar o arquivo json e formatar ele já vai ser inserido no banco    
    insert_query = f"INSERT INTO {tabela_banco} (UF, COD_UF, COD_MUNIC, NOMEDOMUNICIPIO, POPULACAO) VALUES (?, ?, ?, ?, ?)"
    conexao.execute(insert_query, (uf, cod_uf, cod_municipio, nome_municipio, populacao))
    connection.commit()

    #cria a estrutura principal, onde fica o estado e depois adiciona os municipios
    if uf not in formatted_data:
        formatted_data[uf] = {
            "uf": uf,
            "cod_uf": cod_uf,
            "municipios": []
        }

    formatted_data[uf]["municipios"].append({
        "cod_municipio": cod_municipio,
        "nome_municipio": nome_municipio,
        "populacao": populacao
    })
conexao.close()
connection.close()
# cria o json
json_filename = "censo.json"


with open(json_filename, 'w') as json_file:
    json.dump(list(formatted_data.values()), json_file, indent=2)
