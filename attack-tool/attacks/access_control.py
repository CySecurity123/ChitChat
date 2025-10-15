import time
import random
from urllib.parse import urljoin
from config import get_log_filename, log_result
from datetime import datetime, timedelta

class AccessControlAttack:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.vulnerabilities = []

    def run(self, target_url, endpoints, log_file=None, live_log_container=None, progress_container=None):
        """
        Executa o teste de controle de acesso com logs em tempo real.
        """
        if log_file is None:
            log_file = get_log_filename("access_control")

        live_logs = []
        progress_bar, status_text = (progress_container, None) if progress_container else (None, None)
        if progress_container:
            progress_bar, status_text = progress_container

        def add_log(message, update_progress=None):
            brazil_time = datetime.now() - timedelta(hours=3)
            timestamp = brazil_time.strftime("%H:%M:%S")
            formatted_log = f"[{timestamp}] {message}"
            live_logs.append(formatted_log)
            log_result(message, log_file)
            
            if live_log_container:
                display_logs = live_logs[-15:]
                live_log_container.text_area(
                    f"📋 Logs em Tempo Real ({len(live_logs)} total):", 
                    value="\n".join(display_logs),
                    height=300,
                    key=f"live_logs_ac_{len(live_logs)}"
                )
            
            if progress_bar and update_progress is not None:
                progress_bar.progress(update_progress)
            
            if status_text:
                status_text.text(f"🔄 {message}")

        add_log("🔐 Iniciando teste de Controle de Acesso...", 0)
        
        # Verifica o status da sessão atual
        if self.session_manager.is_authenticated:
            add_log(f"ℹ️ Sessão ATUAL: Autenticada como '{self.session_manager.current_user or 'usuário desconhecido'}'.")
        else:
            add_log("ℹ️ Sessão ATUAL: Não autenticada.")

        total_endpoints = len(endpoints)
        for i, endpoint in enumerate(endpoints):
            progress = int(((i + 1) / total_endpoints) * 100)
            full_url = urljoin(target_url, endpoint)
            add_log(f"🔍 Testando endpoint ({i+1}/{total_endpoints}): {full_url}", progress)

            try:
                response = self.session_manager.session.get(full_url, allow_redirects=True, timeout=10)
                add_log(f"  -> Status: {response.status_code}, URL Final: {response.url}")

                # Lógica de detecção de vulnerabilidade
                # Cenário 1: Acesso a endpoint restrito sem autenticação
                is_vulnerable = False
                reason = ""
                if not self.session_manager.is_authenticated and response.status_code == 200:
                    # Se não estou logado e recebo 200, pode ser uma falha.
                    # Verifica se a página não é de login (falso positivo)
                    if 'login' not in response.url.lower() and 'login' not in response.text.lower():
                        is_vulnerable = True
                        reason = "Acesso concedido a endpoint restrito sem autenticação."

                # Cenário 2: Acesso a endpoint de admin como usuário não-admin
                elif self.session_manager.is_authenticated and not self.session_manager.is_admin:
                    if ('admin' in endpoint.lower() or 'painel' in endpoint.lower()) and response.status_code == 200:
                         if 'login' not in response.url.lower():
                            is_vulnerable = True
                            reason = "Acesso a endpoint de admin como usuário comum."

                if is_vulnerable:
                    add_log(f"  🚨 VULNERABILIDADE ENCONTRADA: {reason}")
                    self.vulnerabilities.append({"endpoint": full_url, "reason": reason, "status": response.status_code})
                else:
                    add_log("  ✅ Acesso parece estar controlado corretamente.")

            except Exception as e:
                add_log(f"  🔥 Erro ao testar o endpoint {full_url}: {str(e)}")
            
            time.sleep(random.uniform(0.5, 1.0))

        add_log("📊 Gerando relatório final...", 100)
        if self.vulnerabilities:
            report = f"🚨 {len(self.vulnerabilities)} vulnerabilidades de Controle de Acesso encontradas:\n\n"
            for vuln in self.vulnerabilities:
                report += f"- Endpoint: {vuln['endpoint']}\n"
                report += f"  Razão: {vuln['reason']}\n"
                report += f"  Status HTTP: {vuln['status']}\n\n"
        else:
            report = "✅ Nenhuma vulnerabilidade de Controle de Acesso encontrada nos endpoints testados."
        
        add_log("🏁 Teste de Controle de Acesso finalizado!", 100)
        return report
