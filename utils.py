import json
import os

DATA_DIR = "data"
PRONTUARIOS_FILE = os.path.join(DATA_DIR, "prontuarios.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

def load_data(file_path):
    """Carrega dados de um arquivo JSON."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Se o arquivo não existir ou estiver vazio, cria-o com uma lista vazia
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4) 
        return []

    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return [] # Retorna lista vazia se o arquivo estiver corrompido

def save_data(data, file_path):
    """Salva dados em um arquivo JSON."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_users():
    """Carrega usuários do arquivo JSON."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Se o arquivo de usuários não existir ou estiver vazio, cria-o com um usuário padrão
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        default_user = {"admin": "senha123"}
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_user, f, ensure_ascii=False, indent=4)
        return default_user
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            users = json.load(f)
            if not isinstance(users, dict): 
                return {}
            return users
        except json.JSONDecodeError:
            return {} 

def save_users(users):
    """Salva usuários no arquivo JSON."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)