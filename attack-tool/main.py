#!/usr/bin/env python3
import streamlit as st
import sys
import os
import time
import pandas as pd
from datetime import datetime, timedelta
import glob
import threading

# Seus imports originais
from config import log_result, get_log_filename
from session_manager import SessionManager
from attacks.brute_force import BruteForceAttack
from attacks.sql_injection import SQLInjectionAttack
from attacks.xss import XSSAttack
from attacks.access_control import AccessControlAttack

class WebSecurityTester:
    def __init__(self):
        # Garante que o session_manager seja persistente durante a sessão do Streamlit
        if 'session_manager' not in st.session_state:
            st.session_state.session_manager = SessionManager()
        self.session_manager = st.session_state.session_manager

    def run_attack(self, attack_type, target_url, params, live_log_container=None, progress_container=None):
        """Função genérica para executar ataques com logs em tempo real."""
        result = None
        success_count = 0
        attempts = 0

        # Passa o session_manager compartilhado para cada ataque
        if attack_type == "Brute Force":
            attack = BruteForceAttack(self.session_manager)
            usernames = params.get('usernames', [])
            passwords = params.get('passwords', [])
            attempts = len(usernames) * len(passwords)
            
            log_file = get_log_filename()
            result = attack.run(target_url, usernames, passwords, 
                              max_attempts=params.get('max_attempts', 50),
                              delay=params.get('delay', 1.0),
                              log_file=log_file,
                              live_log_container=live_log_container,
                              progress_container=progress_container)
            # Após o ataque, a sessão já é salva automaticamente no authenticate bem-sucedido
            success_count = len(attack.valid_credentials)
            st.session_state.last_log_file = log_file

        elif attack_type == "SQL Injection":
            attack = SQLInjectionAttack(self.session_manager)
            payloads = params.get('payloads', None)
            
            log_file = get_log_filename()
            result = attack.run(target_url, payloads, 
                              log_file=log_file,
                              live_log_container=live_log_container,
                              progress_container=progress_container)
            
            # Usar contagem real de tentativas
            attempts = attack.total_attempts
            success_count = len(attack.vulnerabilities)
            st.session_state.last_log_file = log_file

        elif attack_type == "XSS":
            attack = XSSAttack(self.session_manager)
            payloads = params.get('payloads', None)
            log_file = get_log_filename()
            
            # O método run agora retorna uma tupla (relatório, total_de_testes)
            result, attempts = attack.run(target_url, payloads, log_file=log_file,
                                          live_log_container=live_log_container,
                                          progress_container=progress_container)
            
            success_count = len(attack.vulnerabilities)
            st.session_state.last_log_file = log_file

        elif attack_type == "Access Control":
            attack = AccessControlAttack(self.session_manager)
            endpoints = params.get('endpoints', [])
            attempts = len(endpoints)
            log_file = get_log_filename()
            result = attack.run(target_url, endpoints, log_file=log_file,
                              live_log_container=live_log_container,
                              progress_container=progress_container)
            success_count = len(attack.vulnerabilities)
            st.session_state.last_log_file = log_file

        else:
            result = "Ataque não suportado."
        
        if not result:
            result = "Nenhum resultado detalhado retornado, mas o ataque foi executado."

        return {
            "result": result,
            "attempts": attempts,
            "success_count": success_count,
            "log_file": st.session_state.get('last_log_file', '')
        }

def initialize_session_state():
    """Inicializa o session state com valores padrão"""
    if 'attack_executed' not in st.session_state:
        st.session_state.attack_executed = False
    if 'attack_result' not in st.session_state:
        st.session_state.attack_result = None
    if 'last_log_file' not in st.session_state:
        st.session_state.last_log_file = ''
    if 'live_logs' not in st.session_state:
        st.session_state.live_logs = []
    if 'attack_in_progress' not in st.session_state:
        st.session_state.attack_in_progress = False

def find_log_files():
    """Encontra todos os arquivos de log na pasta logs"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(project_root, "logs")
    
    if not os.path.exists(log_dir):
        return []
    
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return log_files

def display_logs():
    """Função separada para exibir logs sem reexecutar ataque"""
    st.subheader("📄 Logs Salvos:")
    
    log_files = find_log_files()
    
    if log_files:
        if len(log_files) > 1:
            selected_log = st.selectbox(
                "Selecione o arquivo de log:",
                log_files,
                format_func=lambda x: f"{os.path.basename(x)} ({(datetime.fromtimestamp(os.path.getmtime(x)) - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M:%S')})",
                key="log_selector"
            )
        else:
            selected_log = log_files[0]
        
        try:
            with open(selected_log, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            
            file_info = os.stat(selected_log)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Arquivo", os.path.basename(selected_log))
            with col2:
                st.metric("📏 Linhas", len(logs))
            with col3:
                st.metric("📅 Modificado", (datetime.fromtimestamp(file_info.st_mtime) - timedelta(hours=3)).strftime('%H:%M:%S'))
            
            show_all = st.checkbox("Mostrar todos os logs", value=False, key="show_all_logs")
            
            if show_all:
                display_logs_content = logs
            else:
                display_logs_content = logs[-20:] if len(logs) > 20 else logs
                if len(logs) > 20:
                    st.info(f"Mostrando os últimos 20 logs de {len(logs)} total.")
            
            log_data = []
            for i, line in enumerate(display_logs_content):
                line = line.strip()
                if line:
                    if line.startswith('[') and ']' in line:
                        timestamp_end = line.find(']')
                        timestamp = line[1:timestamp_end]
                        message = line[timestamp_end + 2:]
                    else:
                        timestamp = f"Linha {i+1}"
                        message = line
                    
                    log_data.append({
                        "⏰ Timestamp": timestamp,
                        "📝 Mensagem": message
                    })

            if log_data:
                with st.container():
                    # Tabela de logs
                    df = pd.DataFrame(log_data)
                    st.dataframe(df, use_container_width=True, height=300)

                    # Botões em uma linha compacta
                    col1, col2, col3 = st.columns([1, 1, 1])

                    with col1:
                        st.download_button(
                            label="📥 Baixar",
                            data="\n".join(logs),
                            file_name=os.path.basename(selected_log),
                            mime="text/plain",
                            key="download_log",
                            use_container_width=True
                        )

                    with col2:
                        if st.button("🔄 Atualizar", key="refresh_logs", use_container_width=True):
                            st.rerun()

                    with col3:
                        if st.button("❌ Deletar", key="delete_log", use_container_width=True):
                            try:
                                os.remove(selected_log)
                                st.success("Arquivo deletado!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
            else:
                st.warning("O arquivo de log está vazio.")
                
            with st.expander("📋 Ver Log Bruto"):
                st.text_area(
                    "Conteúdo completo:",
                    value="\n".join(logs),
                    height=200,
                    key="raw_log_view"
                )
        
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {e}")
    
    else:
        st.warning("⚠️ Nenhum arquivo de log encontrado.")
        with st.expander("🔍 Debug"):
            project_root = os.path.dirname(os.path.abspath(__file__))
            log_dir = os.path.join(project_root, "logs")
            st.write(f"**Pasta esperada:** `{log_dir}`")
            st.write(f"**Existe:** {os.path.exists(log_dir)}")

def main():
    st.set_page_config(page_title="Web Security Tester", page_icon="🔒", layout="wide")
    
    initialize_session_state()
    
    # Instancia o tester para ter acesso ao session_manager
    tester = WebSecurityTester()

    st.title("🔒 Web Security Tester - Ferramenta de Testes de Segurança")
    st.markdown("Bem-vindo! Esta é uma interface web para testar vulnerabilidades em sites. **Use apenas em ambientes autorizados.**")
    
    st.sidebar.header("Menu de Opções")
    attack_options = ["Brute Force", "SQL Injection", "XSS", "Access Control"]
    selected_attack = st.sidebar.selectbox("Selecione o tipo de ataque:", attack_options)
    
    # Opções de sessão na sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Gerenciamento de Sessão")
    load_session = st.sidebar.checkbox("Carregar sessão salva", help="Reutiliza a sessão de um login anterior bem-sucedido.")
    if st.sidebar.button("Limpar sessão salva", key="clear_session_file"):
        session_file = tester.session_manager.session_file
        if os.path.exists(session_file):
            os.remove(session_file)
            st.sidebar.success("Arquivo de sessão limpo!")
            time.sleep(1)
            st.rerun()
        else:
            st.sidebar.info("Nenhuma sessão salva para limpar.")

    st.sidebar.markdown("---")

    target_url = st.text_input("URL Alvo (ex: http://web:80)", 
                              value="http://web:80/controller/usuario.php")
    
    # Campos específicos por ataque
    params = {}
    if selected_attack == "Brute Force":
        st.subheader("⚡ Configurações para Brute Force")
        col1, col2 = st.columns(2)
        with col1:
            usernames = st.text_area("Lista de usernames (um por linha)", 
                                   value="admin\nuser\ntest\nroot\nadministrator")
        with col2:
            passwords = st.text_area("Lista de passwords (um por linha)", 
                                   value="password\n123456\nadmin\nroot\npassword123")
        params['usernames'] = [u.strip() for u in usernames.split('\n') if u.strip()]
        params['passwords'] = [p.strip() for p in passwords.split('\n') if p.strip()]
        
        with st.expander("⚙️ Configurações Avançadas"):
            max_attempts = st.number_input("Máximo de tentativas", min_value=1, max_value=1000, value=50)
            delay = st.slider("Delay entre tentativas (segundos)", 0.1, 5.0, 1.0, 0.1)
            params['max_attempts'] = max_attempts
            params['delay'] = delay
    
    elif selected_attack == "SQL Injection":
        st.subheader("💉 Configurações para SQL Injection")
        
        # Opção para usar payloads padrão ou customizados
        use_default_sql = st.checkbox("Usar payloads padrão de SQL Injection (recomendado)", value=True, key="default_sql")
        
        if use_default_sql:
            # Mostrar preview dos payloads padrão
            with st.expander("👁️ Ver payloads padrão que serão testados"):
                # Instancia temporariamente para pegar os payloads
                temp_attack = SQLInjectionAttack(None)
                payload_categories = temp_attack.get_default_sql_payloads()
                for category, payloads in payload_categories.items():
                    st.write(f"**Categoria: {category.replace('_', ' ').title()}**")
                    for p in payloads[:3]: # Mostra até 3 por categoria
                        st.code(p)
                    if len(payloads) > 3:
                        st.caption(f"... e mais {len(payloads) - 3}")

            params['payloads'] = None  # Usar padrão
        else:
            # Payloads customizados
            payloads = st.text_area(
                "Payloads SQL (um por linha)", 
                value="' OR '1'='1\n--\nadmin' --\n' UNION SELECT 1,2,3--",
                height=150
            )
            params['payloads'] = [p.strip() for p in payloads.split('\n') if p.strip()]
    
    elif selected_attack == "XSS":
        st.subheader("🎭 Configurações para XSS")
        use_default_xss = st.checkbox("Usar payloads padrão de XSS (recomendado)", value=True, key="default_xss")

        if use_default_xss:
            with st.expander("👁️ Ver payloads padrão de XSS"):
                temp_attack = XSSAttack(None)
                for p in temp_attack.get_xss_payloads():
                    st.code(p)
            params['payloads'] = None
        else:
            payloads = st.text_area("Payloads XSS (um por linha)", 
                                   value="<script>alert('XSS')</script>\n<img src='x' onerror='alert(1)'>",
                                   height=150)
            params['payloads'] = [p.strip() for p in payloads.split('\n') if p.strip()]

    elif selected_attack == "Access Control":
        st.subheader("🚪 Configurações para Controle de Acesso")
        endpoints = st.text_area("Endpoints a testar (um por linha, ex: /admin/dashboard.php)", 
                                value="/view/admin/dashboard.php\n/view/user/details.php?id=1\n/logout.php",
                                height=150)
        params['endpoints'] = [e.strip() for e in endpoints.split('\n') if e.strip()]
    
    # Verificar se ataque está em progresso e mostrar aviso
    if st.session_state.attack_in_progress:
        st.warning("⚡ **Ataque em andamento!** Aguarde a conclusão antes de executar outro ataque.")

    # Botão para executar
    button_clicked = st.button(
        f"🚀 Executar {selected_attack}" if not st.session_state.attack_in_progress else "⏳ Executando...", 
        type="primary", 
        key="execute_attack",
        disabled=st.session_state.attack_in_progress,
        help="Clique para iniciar o ataque" if not st.session_state.attack_in_progress else "Aguarde o ataque atual terminar"
    )

    if button_clicked and not st.session_state.attack_in_progress:
        if not target_url:
            st.error("❌ Por favor, forneça uma URL válida.")
        elif not any(params.values()) and selected_attack != "SQL Injection":
            st.error("❌ Por favor, forneça parâmetros para o ataque.")
        elif selected_attack == "SQL Injection" and not use_default_sql and not params.get('payloads'):
            st.error("❌ Por favor, forneça payloads SQL ou use os padrão.")
        elif selected_attack == "XSS" and not use_default_xss and not params.get('payloads'):
            st.error("❌ Por favor, forneça payloads XSS ou use os padrão.")
        else:
            # Marcar que ataque está em progresso IMEDIATAMENTE
            st.session_state.attack_in_progress = True
            
            # Carregar sessão se solicitado
            if load_session:
                if tester.session_manager.load_session():
                    st.toast("✅ Sessão carregada com sucesso!", icon="🎉")
                else:
                    st.toast("⚠️ Não foi possível carregar a sessão. Iniciando uma nova.", icon="🤷")
            
            # Forçar atualização da interface
            st.rerun()

    # Se o ataque está em progresso, executar o ataque
    if st.session_state.attack_in_progress and not st.session_state.get('attack_executing', False):
        # Evitar execução dupla
        st.session_state.attack_executing = True
        
        # Container principal para toda a seção de logs em tempo real
        realtime_section = st.empty()
        
        with realtime_section.container():
            st.subheader("📺 Logs em Tempo Real:")
            live_log_container = st.empty()
        
        # Container para progresso
        st.subheader("📊 Progresso do Ataque:")
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("🚀 Iniciando ataque...")
        
        # Executar ataque
        attack_result = tester.run_attack(
            selected_attack, 
            target_url, 
            params, 
            live_log_container=live_log_container,
            progress_container=(progress_bar, status_text)
        )
        
        # Finalizar progresso
        progress_bar.progress(100)
        status_text.text("✅ Ataque concluído!")
        
        # Marcar que ataque terminou
        st.session_state.attack_in_progress = False
        st.session_state.attack_executing = False
        
        # Salvar resultado no session state
        st.session_state.attack_result = attack_result
        st.session_state.attack_executed = True
        
        st.success("🎉 Ataque executado com sucesso!")
        
        # Limpar toda a seção de logs em tempo real após execução
        time.sleep(2)
        realtime_section.empty()
        
        # Forçar atualização da interface para mostrar o botão desbloqueado
        st.rerun()    
    
    # Exibir resultados se ataque foi executado
    if st.session_state.attack_executed and st.session_state.attack_result and not st.session_state.attack_in_progress:
        attack_result = st.session_state.attack_result
        
        st.subheader("📊 Resultados Detalhados:")
        if attack_result["result"]:
            with st.expander("Ver detalhes completos", expanded=True):
                st.code(attack_result["result"], language="text")
        
        # Gráfico de resultados
        if attack_result["attempts"] > 0:
            st.subheader("📈 Resumo em Gráfico:")
            col1, col2 = st.columns(2)
            
            with col1:
                data = pd.DataFrame({
                    "Métrica": ["Tentativas", "Sucessos"],
                    "Valor": [attack_result["attempts"], attack_result["success_count"]]
                })
                st.bar_chart(data.set_index("Métrica"))
            
            with col2:
                st.metric("Total de Tentativas", attack_result["attempts"])
                st.metric("Sucessos", attack_result["success_count"], 
                         delta=f"{(attack_result['success_count']/attack_result['attempts']*100):.1f}% taxa de sucesso")
    
    # Separador visual
    st.markdown("---")
    
    # Exibir logs salvos (só se não estiver executando ataque)
    if not st.session_state.attack_in_progress:
        display_logs()
    
    # Botão para limpar resultados
    if st.session_state.attack_executed and not st.session_state.attack_in_progress:
        if st.button("🧹 Limpar Resultados", key="clear_results"):
            st.session_state.attack_executed = False
            st.session_state.attack_result = None
            st.session_state.live_logs = []
            st.rerun()
    
    # Sidebar com informações
    st.sidebar.markdown("---")

    # Status na sidebar
    if st.session_state.attack_in_progress:
        st.sidebar.warning("⚡ Ataque em andamento...")
    elif st.session_state.attack_executed:
        st.sidebar.success("✅ Ataque concluído")

if __name__ == "__main__":
    main()