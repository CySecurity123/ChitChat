import requests
import os
import pickle
from config import BASE_URL, ENDPOINTS, log_result

class SessionManager:
    def __init__(self, session_file='sessions/current_session.pkl'):
        self.session = requests.Session()
        self.is_authenticated = False
        self.is_admin = False
        self.current_user = None
        self.valid_credentials = []
        self.session_file = session_file

    def save_session(self):
        """Salva os cookies da sessão atual em um arquivo."""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'wb') as f:
                pickle.dump(self.session.cookies, f)
            print(f"Sessão salva em {self.session_file}")
            return True
        except Exception as e:
            print(f"Erro ao salvar a sessão: {e}")
            return False

    def load_session(self):
        """Carrega os cookies de um arquivo para a sessão atual."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'rb') as f:
                    self.session.cookies = pickle.load(f)
                self.is_authenticated = True  # Assume que a sessão salva é autenticada
                print(f"Sessão carregada de {self.session_file}")
                return True
            else:
                print("Nenhum arquivo de sessão encontrado para carregar.")
                return False
        except Exception as e:
            print(f"Erro ao carregar a sessão: {e}")
            return False
        
    def get_session_cookie(self, log_file):
        """Obtém cookie de sessão"""
        try:
            response = self.session.get(f"{BASE_URL}/")
            log_result(f"📊 Status da conexão: {response.status_code}", log_file)
            
            if self.session.cookies.get('PHPSESSID'):
                log_result("✅ Cookie PHPSESSID obtido", log_file)
                return True
            else:
                log_result("⚠️  PHPSESSID não encontrado", log_file)
                return False
        except Exception as e:
            log_result(f"❌ Erro na conexão: {str(e)}", log_file)
            return False
    
    def authenticate(self, username, password, log_file):
        """Tenta fazer login"""
        if not self.get_session_cookie(log_file):
            return False
            
        login_url = f"{BASE_URL}/controller/usuario.php"
        payload = {
            "Usuario": "Login",
            "Login": username,
            "Senha": password
        }
        
        try:
            response = self.session.post(login_url, data=payload, allow_redirects=True)
            
            if any(indicator in response.text for indicator in ["Bem-vindo", "Home"]):
                self.is_authenticated = True
                self.current_user = username
                
                # Verificar se é admin
                if "admin" in response.text.lower():
                    self.is_admin = True
                
                log_result(f"✅ Login bem-sucedido: {username}:{password}", log_file)
                self.save_session() # Salva a sessão automaticamente após o sucesso
                return True
            else:
                log_result(f"❌ Login falhou: {username}:{password}", log_file)
                return False
                
        except Exception as e:
            log_result(f"🔥 Erro na autenticação: {str(e)}", log_file)
            return False
    
    def test_endpoint(self, endpoint_name, log_file, custom_params=None):
        """Testa acesso a um endpoint específico"""
        if endpoint_name not in ENDPOINTS:
            return False, None
            
        endpoint = ENDPOINTS[endpoint_name]
        url = f"{BASE_URL}{endpoint['url']}"
        params = custom_params or endpoint['params']
        
        try:
            if endpoint['method'] == 'POST':
                response = self.session.post(url, data=params, allow_redirects=True)
            else:
                response = self.session.get(url, params=params, allow_redirects=True)
            
            log_result(f"📥 Testado {endpoint_name}: Status {response.status_code}", log_file)
            return True, response
            
        except Exception as e:
            log_result(f"🔥 Erro ao testar {endpoint_name}: {str(e)}", log_file)
            return False, None
    
    def logout(self, log_file):
        """Faz logout e remove o arquivo de sessão"""
        self.session.cookies.clear()
        self.is_authenticated = False
        self.is_admin = False
        self.current_user = None
        log_result("👋 Sessão encerrada", log_file)
        
        # Remove o arquivo de sessão ao fazer logout
        if os.path.exists(self.session_file):
            try:
                os.remove(self.session_file)
                print(f"Arquivo de sessão {self.session_file} removido.")
            except Exception as e:
                print(f"Erro ao remover arquivo de sessão: {e}")