import os
from datetime import datetime, timedelta, timezone

# --- Configurações Globais ---
BASE_URL = "http://web:80"
LOG_DIR = "/app/logs"
SLEEP_INTERVAL = 1
TARGET_USERNAME = "admin"

# Criar diretório de logs
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_filename(test_type="attack"):
    """Gera um nome de arquivo de log com timestamp"""
    utc_minu_3 = timezone(timedelta(hours=-3))
    timestamp = datetime.now(utc_minu_3).strftime("%Y%m%d_%H%M%S")
    return os.path.join(LOG_DIR, f"{test_type}_{timestamp}.log")

def log_result(message, log_file):
    """Escreve uma mensagem no arquivo de log e no console"""
    utc_minu_3 = timezone(timedelta(hours=-3))
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(f"[{datetime.now(utc_minu_3).strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

# Endpoints para testar
ENDPOINTS = {
    "login": {
        "url": "/controller/usuario.php",
        "method": "POST",
        "params": {"Usuario": "Login", "Login": "", "Senha": ""},
        "success_indicators": ["Bem-vindo", "Home"],
        "failure_indicators": ["Usuário ou senha inválidos"]
    },
    "search": {
        "url": "/view/post.php",
        "method": "GET",
        "params": {"msg": ""},
        "success_indicators": [],
        "failure_indicators": []
    },
    "profile": {
        "url": "/view/perfil.php",
        "method": "GET",
        "params": {"id": "1"},
        "success_indicators": ["Perfil"],
        "failure_indicators": ["Acesso negado"]
    },
    "admin": {
        "url": "/view/admin_panel.php",
        "method": "GET",
        "params": {},
        "success_indicators": ["Admin", "Painel"],
        "failure_indicators": ["Acesso negado", "Login"]
    }
}

data = get_log_filename()
print(data)
log_result("aaaaaaa", data)
print("aaaaaaaaaaa")
