import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any
import time


st.set_page_config(
    page_title="Verificador de Processos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://llm-engine-api:8000"

st.markdown("""
<style>
    .stTabs [role="tablist"] {
        gap: 2px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def fetch_health():
    """Check API health."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def verify_process(processo_data: Dict[str, Any]):
    """Send process for verification."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/verify/",
            json=processo_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com API: {str(e)}")
        return None


def get_analytics():
    """Get analytics data."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/analytics/summary",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except:
        return None


def get_processes():
    """List verified processes."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/process/",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except:
        return []


st.markdown("# Verificador de Processos Judiciais")
st.markdown("---")

if not fetch_health():
    st.error("API is not available. Please ensure the server is running at http://localhost:8000")
    st.stop()

st.success("API connected")

with st.sidebar:
    st.header("Menu")
    page = st.radio(
        "Selecione uma página:",
        ["Verificador", "Histórico", "Analytics", "Documentação"]
    )

if page == "Verificador":
    st.header("Verificação de Processo")
    st.write("Insira os dados do processo judicial para análise automática")
    
    with st.form("processo_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            numero_processo = st.text_input(
                "Número do Processo",
                placeholder="0004587-00.2021.4.05.8100"
            )
            classe = st.text_input(
                "Classe",
                placeholder="Cumprimento de Sentença contra a Fazenda Pública"
            )
            orgao_julgador = st.text_input(
                "Órgão Julgador",
                placeholder="19ª VARA FEDERAL - SOBRAL/CE"
            )
            assunto = st.text_input(
                "Assunto",
                placeholder="Rural (Art. 48/51)"
            )
        
        with col2:
            siglaTribunal = st.text_input(
                "Sigla do Tribunal",
                placeholder="TRF5"
            )
            esfera = st.selectbox(
                "Esfera",
                ["Federal", "Estadual", "Trabalhista"]
            )
            valor_condenacao = st.number_input(
                "Valor da Condenação (R$)",
                min_value=0.0,
                step=100.0
            )
            segredo_justica = st.checkbox("Sigilo de Justiça")
        
        justica_gratuita = st.checkbox("Justiça Gratuita")
        
        st.subheader("Documentos")
        st.write("Adicione documentos do processo (opcional)")
        
        documentos = []
        if st.checkbox("Adicionar documento"):
            doc_nome = st.text_input("Nome do documento")
            doc_texto = st.text_area("Texto do documento")
            if doc_nome and doc_texto:
                documentos.append({
                    "id": "DOC-1",
                    "dataHoraJuntada": datetime.utcnow().isoformat(),
                    "nome": doc_nome,
                    "texto": doc_texto
                })
        
        submitted = st.form_submit_button("Verificar Processo", type="primary")
        
        if submitted:
            if not numero_processo:
                st.error("Número do processo é obrigatório")
            else:
                with st.spinner("Verificando processo..."):
                    processo_data = {
                        "numeroProcesso": numero_processo,
                        "classe": classe,
                        "orgaoJulgador": orgao_julgador,
                        "ultimaDistribuicao": datetime.utcnow().isoformat(),
                        "assunto": assunto,
                        "segredoJustica": segredo_justica,
                        "justicaGratuita": justica_gratuita,
                        "siglaTribunal": siglaTribunal,
                        "esfera": esfera,
                        "valorCondenacao": valor_condenacao,
                        "documentos": documentos
                    }
                    
                    resultado = verify_process(processo_data)
                    
                    if resultado:
                        st.success("✓ Verificação concluída!")
                        
                        decision = resultado.get("decision", "unknown")
                        
                        if decision == "approved":
                            st.success(f"Decisão: APROVADO")
                            color = "green"
                        elif decision == "rejected":
                            st.error(f"Decisão: REJEITADO")
                            color = "red"
                        else:
                            st.warning(f"Decisão: INCOMPLETO")
                            color = "orange"
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Decisão", decision.upper())
                        with col2:
                            st.metric("Confiança", f"{resultado.get('confidence', 0):.1%}")
                        with col3:
                            st.metric("Tempo", f"{resultado.get('processingTimeMs', 0)}ms")
                        
                        st.subheader("Justificativa")
                        st.write(resultado.get("rationale", "Sem justificativa"))
                        
                        st.subheader("Políticas Citadas")
                        citations = resultado.get("citations", [])
                        if citations:
                            # Display citations as badges using markdown
                            badges = " ".join([f"`{str(c)}`" for c in citations])
                            st.markdown(badges)
                        else:
                            st.info("Nenhuma política específica citada")
                        
                        # Exibir JSON completo
                        with st.expander("Ver resposta completa (JSON)"):
                            st.json(resultado)


elif page == "Histórico":
    st.header("Histórico de Verificações")
    
    col1, col2 = st.columns(2)
    with col1:
        decision_filter = st.selectbox(
            "Filtrar por decisão:",
            ["Todas", "approved", "rejected", "incomplete"]
        )
    with col2:
        limit = st.slider("Mostrar últimas N verificações:", 10, 100, 20)
    
    processes = get_processes()
    
    if not processes:
        st.info("Nenhuma verificação realizada ainda")
    else:
        if decision_filter != "Todas":
            processes = [p for p in processes if p.get("decision") == decision_filter]
        
        processes = processes[:limit]
        
        st.write(f"Mostrando {len(processes)} verificação(ões)")
        
        for proc in processes:
            with st.expander(f"{proc.get('numeroProcesso')} - {proc.get('decision').upper()}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Processo", proc.get("numeroProcesso"))
                with col2:
                    st.metric("Decisão", proc.get("decision").upper())
                with col3:
                    st.metric("Confiança", f"{proc.get('confidence', 0):.1%}")
                
                st.write("**Justificativa:**")
                st.write(proc.get("rationale"))
                
                st.write("**Políticas:**")
                citations = proc.get("citations", [])
                if citations:
                    badges = " ".join([f"`{str(c)}`" for c in citations])
                    st.markdown(badges)
                else:
                    st.info("Nenhuma política citada")


elif page == "Analytics":
    st.header("Dashboard Analytics")
    
    analytics = get_analytics()
    
    if analytics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total de Verificações",
                analytics.get("total_verificacoes", 0)
            )
        with col2:
            st.metric(
                "Taxa de Aprovação",
                f"{analytics.get('taxa_aprovacao_percentual', 0):.1f}%"
            )
        with col3:
            st.metric(
                "Processos Aprovados",
                analytics.get("aprovados", 0)
            )
        with col4:
            st.metric(
                "Tempo Médio",
                f"{analytics.get('tempo_medio_processamento_ms', 0):.0f}ms"
            )
        
        st.subheader("Políticas Mais Impactantes")
        if analytics.get("politicas_mais_citadas"):
            for policy in analytics.get("politicas_mais_citadas", []):
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.metric(policy["id"], policy["usos"])
                with col2:
                    st.write(f"**{policy['titulo']}**")
        else:
            st.info("Sem dados de políticas ainda")
    else:
        st.error("Erro ao carregar analytics")


elif page == "Documentação":
    st.header("Documentação da API")
    
    st.markdown("""
    ## Endpoints Disponíveis
    
    ### Verificação
    - `POST /verify/` - Verifica um processo
    - `POST /verify/batch` - Verifica múltiplos processos
    
    ### Consulta
    - `GET /process/{numero_processo}` - Histórico de um processo
    - `GET /process/` - Lista processos com filtros
    
    ### Analytics
    - `GET /analytics/summary` - Resumo analítico
    - `GET /analytics/policies-usage` - Uso de políticas
    - `GET /analytics/decision-distribution` - Distribuição de decisões
    - `GET /analytics/processing-time` - Estatísticas de tempo
    
    ### Health
    - `GET /health` - Status da aplicação
    
    ## Políticas de Negócio
    
    POL-1: Só compramos crédito de processos transitados em julgado e em fase de execução
    POL-2: Exigir valor de condenação informado
    POL-3: Valor de condenação < R$ 1.000,00 → não compra
    POL-4: Condenações na esfera trabalhista → não compra
    POL-5: Óbito do autor sem habilitação no inventário → não compra
    POL-6: Substabelecimento sem reserva de poderes → não compra
    POL-7: Informar honorários contratuais, periciais e sucumbenciais quando existirem
    POL-8: Se faltar documento essencial → incomplete
    """)
    
    st.subheader("Documentação Interativa")
    st.write("Acesse a documentação Swagger em: http://localhost:8000/docs")
    st.write("Ou ReDoc em: http://localhost:8000/redoc")