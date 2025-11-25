import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

st.set_page_config(
    page_title="Judicial Process Verification",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://judicial-verification-api:8000/v1"

st.title("Judicial Process Verification System")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # Detect if running in Docker
    import os
    in_docker = os.path.exists('/.dockerenv')
    default_url = "http://judicial-verification-api:8000/v1" if in_docker else "http://localhost:8000/v1"
    
    api_url = st.text_input(
        "API URL",
        value=default_url,
        help="Base URL for the verification API"
    )
    st.markdown("---")
    st.info(
        "This application verifies judicial processes against company policies. "
        "Enter process details and submit for analysis."
    )

# Main content
tab1, tab2 = st.tabs(["Verificação", "Testar Dados"])

with tab1:
    st.subheader("Informações do Processo")
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        numero_processo = st.text_input(
            "Número do Processo",
            placeholder="0001234-56.2023.4.05.8100"
        )
        classe = st.text_input(
            "Classe",
            placeholder="Cumprimento de Sentença contra a Fazenda Pública"
        )
        orgao_julgador = st.text_input(
            "Órgão Julgador",
            placeholder="19ª VARA FEDERAL - SOBRAL/CE"
        )
        esfera = st.selectbox(
            "Esfera Judiciária",
            ["Federal", "Estadual", "Trabalhista"]
        )
    
    with col2:
        assunto = st.text_input(
            "Assunto",
            placeholder="Rural (Art. 48/51)"
        )
        valor_condenacao = st.number_input(
            "Valor da Condenação (R$)",
            min_value=0.0,
            step=100.0
        )
        siglaTribunal = st.text_input(
            "Sigla do Tribunal",
            placeholder="TRF5"
        )
        justica_gratuita = st.checkbox("Justiça Gratuita")
    
    # Additional information
    st.markdown("---")
    st.subheader("Informações Adicionais")
    
    col1, col2 = st.columns(2)
    with col1:
        sigilo = st.checkbox("Sigilo de Justiça")
        ultima_distribuicao = st.date_input("Data da Última Distribuição")
    
    with col2:
        honorarios_contratuais = st.number_input(
            "Honorários Contratuais (R$)",
            min_value=0.0,
            step=100.0,
            value=0.0
        )
        honorarios_periciais = st.number_input(
            "Honorários Periciais (R$)",
            min_value=0.0,
            step=100.0,
            value=0.0
        )
    
    honorarios_sucumbenciais = st.number_input(
        "Honorários Sucumbenciais (R$)",
        min_value=0.0,
        step=100.0,
        value=0.0
    )
    
    # Documents and Movements
    st.markdown("---")
    st.subheader("Documentos")
    
    num_docs = st.number_input("Número de Documentos", min_value=0, max_value=10, value=1)
    documentos = []
    
    for i in range(num_docs):
        with st.expander(f"Documento {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                doc_id = st.text_input(f"ID do Documento {i+1}", value=f"DOC-1-{i+1}")
                doc_nome = st.text_input(f"Nome do Documento {i+1}", placeholder="Sentença de Mérito")
            with col2:
                doc_data = st.date_input(f"Data de Entrega {i+1}", key=f"doc_date_{i}")
                doc_hora = st.time_input(f"Hora de Entrega {i+1}", key=f"doc_time_{i}")
            
            doc_texto = st.text_area(
                f"Conteúdo do Documento {i+1}",
                placeholder="Digite o conteúdo do documento.",
                height=100,
                key=f"doc_text_{i}"
            )
            
            if doc_id and doc_nome and doc_texto:
                from datetime import datetime
                doc_datetime = datetime.combine(doc_data, doc_hora)
                documentos.append({
                    "id": doc_id,
                    "dataHoraJuntada": doc_datetime.isoformat(),
                    "nome": doc_nome,
                    "texto": doc_texto
                })
    
    # Movements
    st.markdown("---")
    st.subheader("Movimentos")
    
    num_movimentos = st.number_input("Número de Movimentos", min_value=0, max_value=10, value=1)
    movimentos = []
    
    for i in range(num_movimentos):
        with st.expander(f"Movimento {i+1}"):
            col1, col2 = st.columns(2)
            with col1:
                mov_data = st.date_input(f"Data do Movimento {i+1}", key=f"mov_date_{i}")
                mov_hora = st.time_input(f"Hora do Movimento {i+1}", key=f"mov_time_{i}")
            with col2:
                mov_desc = st.text_input(
                    f"Descrição do Movimento {i+1}",
                    placeholder="Iniciado cumprimento definitivo...",
                    key=f"mov_desc_{i}"
                )
            
            if mov_desc:
                from datetime import datetime
                mov_datetime = datetime.combine(mov_data, mov_hora)
                movimentos.append({
                    "dataHora": mov_datetime.isoformat(),
                    "descricao": mov_desc
                })
    
    # Submit button
    st.markdown("---")
    
    if st.button("Verificar Processo", type="primary", use_container_width=True):
        if not numero_processo:
            st.error("O número do processo é obrigatório")
        elif not documentos:
            st.warning("Pelo menos um documento é obrigatório")
        else:
            # Build request payload
            payload = {
                "process": {
                    "numeroProcesso": numero_processo,
                    "classe": classe,
                    "orgaoJulgador": orgao_julgador,
                    "ultimaDistribuicao": datetime.combine(ultima_distribuicao, datetime.min.time()).isoformat(),
                    "assunto": assunto,
                    "segredoJustica": sigilo,
                    "justicaGratuita": justica_gratuita,
                    "siglaTribunal": siglaTribunal,
                    "esfera": esfera,
                    "documentos": documentos,
                    "movimentos": movimentos,
                    "valorCondenacao": valor_condenacao if valor_condenacao > 0 else None,
                    "honorarios": {
                        "contratuais": honorarios_contratuais if honorarios_contratuais > 0 else None,
                        "periciais": honorarios_periciais if honorarios_periciais > 0 else None,
                        "sucumbenciais": honorarios_sucumbenciais if honorarios_sucumbenciais > 0 else None
                    }
                }
            }
            
            try:
                with st.spinner("Verifying process..."):
                    response = requests.post(
                        f"{api_url}/verify",
                        json=payload,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display result
                    decision = result.get("decision", "unknown")
                    
                    # Color coding
                    if decision == "approved":
                        st.success(f"Decision: **APPROVED**")
                    elif decision == "rejected":
                        st.error(f"Decision: **REJECTED**")
                    else:
                        st.warning(f"Decision: **INCOMPLETE**")
                    
                    st.markdown("---")
                    
                    # Rationale
                    st.subheader("Rationale")
                    st.info(result.get("rationale", "No rationale provided"))
                    
                    # References
                    st.subheader("Policy References")
                    references = result.get("references", [])
                    
                    for ref in references:
                        with st.expander(f"Policy {ref['policy_id']}"):
                            st.write(ref.get("explanation", "No explanation"))
                    
                    # Full response
                    with st.expander("Full Response"):
                        st.json(result)
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.json(response.json())
            
            except requests.exceptions.ConnectionError:
                st.error(f"Connection Error: Cannot reach API at {api_url}")
                st.info("Make sure the API is running on the configured URL")
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Test Data")
    st.markdown("Use the test data below to quickly populate the form")
    
    test_process_1 = {
        "numeroProcesso": "0001234-56.2023.4.05.8100",
        "classe": "Cumprimento de Sentença contra a Fazenda Pública",
        "orgaoJulgador": "19ª VARA FEDERAL - SOBRAL/CE",
        "ultimaDistribuicao": "2024-11-18T23:15:44.130Z",
        "assunto": "Rural (Art. 48/51)",
        "segredoJustica": False,
        "justicaGratuita": True,
        "siglaTribunal": "TRF5",
        "esfera": "Federal",
        "documentos": [
            {
                "id": "DOC-1-1",
                "dataHoraJuntada": "2023-09-10T10:12:05.000",
                "nome": "Sentença de Mérito",
                "texto": "PODER JUDICIÁRIO - Sentença favorável ao autor..."
            },
            {
                "id": "DOC-1-2",
                "dataHoraJuntada": "2023-12-12T09:05:30.000",
                "nome": "Certidão de Trânsito em Julgado",
                "texto": "CERTIDÃO - Certifico que a sentença transitou em julgado..."
            }
        ],
        "movimentos": [
            {
                "dataHora": "2024-01-20T11:22:33.000",
                "descricao": "Iniciado cumprimento definitivo de sentença."
            }
        ],
        "valorCondenacao": 67592,
        "honorarios": {
            "contratuais": 6000,
            "periciais": 1200,
            "sucumbenciais": 3000
        }
    }
    
    st.json(test_process_1)
    
    if st.button("Copy to Clipboard"):
        st.code(json.dumps(test_process_1, indent=2))

