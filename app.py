import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E VISUAL
# ==========================================
st.set_page_config(page_title="Portal Comercial - MPS", page_icon="⚓", layout="wide")

st.markdown("""
    <div style="background-color:#0099dd; padding:18px 25px; border-radius:10px; margin-bottom:20px;">
        <h1 style="color:white; margin:0; font-family:sans-serif;">⚙️ MARINE POWER (MPS) - Service Inquires</h1>
        <p style="color:#e6f7ff; margin:5px 0 0 0;">Sistema Integrado de Registo e Acompanhamento de Cases Comerciais</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS COMPLETA (20 COLUNAS)
# ==========================================
def conectar_banco():
    # Novo ficheiro de base de dados já com todas as 20 colunas da folha de cálculo
    conn = sqlite3.connect("mps_service_inquires.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_inquires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_code TEXT,
            date_open TEXT,
            field TEXT,
            workshop TEXT,
            commercial_mps TEXT,
            client TEXT,
            requested_by TEXT,
            po_contact_name TEXT,
            po_email TEXT,
            po_cel_phone TEXT,
            installation TEXT,
            equip TEXT,
            equipment_type TEXT,
            maker TEXT,
            service_description TEXT,
            location TEXT,
            condition TEXT,
            status TEXT,
            valor REAL,
            notes TEXT
        )
    """)
    conn.commit()
    return conn

conn = conectar_banco()

# ==========================================
# 3. GERADOR DO MENOR CÓDIGO DISPONÍVEL NO ANO
# ==========================================
def sugerir_menor_case():
    ano_atual = date.today().year
    cursor = conn.cursor()
    cursor.execute("SELECT case_code FROM service_inquires WHERE case_code LIKE ?", (f"MPS%-{ano_atual}",))
    registos = cursor.fetchall()
    
    numeros_usados = set()
    for (codigo,) in registos:
        try:
            parte_num = codigo.upper().split("-")[0].replace("MPS", "").strip()
            numeros_usados.add(int(parte_num))
        except ValueError:
            pass
            
    # Procura o menor múltiplo de 5 disponível no ano (0005, 0010, 0015...)
    candidato = 5
    while candidato in numeros_usados:
        candidato += 5
        
    return f"MPS{candidato:04d}-{ano_atual}"

# ==========================================
# 4. FORMULÁRIO COMPLETO (ESPELHO DA PLANILHA)
# ==========================================
codigo_sugerido = sugerir_menor_case()

st.subheader("➕ Registar Novo Case (Service Inquiry)")

with st.form("form_service_inquires", clear_on_submit=True):
    
    # --- BLOCO 1: IDENTIFICAÇÃO E COMERCIAL (Colunas A até F) ---
    st.markdown("##### 📌 1. Identificação do Case e Responsável")
    c1, c2, c3, c4, c5 = st.columns([1.3, 1, 1.2, 1.5, 1.5])
    
    with c1:
        # Campo aberto (disabled=False) para permitir edição manual se necessário
        case_code = st.text_input("CASE (Automático ou Editável)", value=codigo_sugerido)
    with c2:
        date_open = st.date_input("DATE", value=date.today(), format="DD/MM/YYYY")
    with c3:
        st.write("Modalidade (`FIELD` / `WORKSHOP`)")
        chk_field = st.checkbox("FIELD (Campo)", value=True)
        chk_workshop = st.checkbox("WORKSHOP (Oficina)", value=False)
    with c4:
        opcoes_comercial = [
            "CARLOS JUNIOR", "MARCELO VIEIRA", "DANIEL OPERACIONAL", 
            "MATHEUS LIMA", "JORGE FONSECA", "NELSON BRIGIDO", "OUTRO"
        ]
        commercial_mps = st.selectbox("COMMERCIAL MPS", opcoes_comercial)
    with c5:
        client = st.text_input("CLIENT (Ex: OCEANPACT, WILSON SONS, CBO, DOF...)")

    st.divider()

    # --- BLOCO 2: CONTACTOS DO CLIENTE (Colunas G até J) ---
    st.markdown("##### 👤 2. Contactos do Cliente e P.O.")
    col_g, col_h, col_i, col_j = st.columns(4)
    
    with col_g:
        requested_by = st.text_input("REQUESTED BY (Ex: Gabriella Silva, Marcio Mathias...)")
    with col_h:
        po_contact_name = st.text_input("P.O. CONTACT NAME (Ex: Renato Vidal)")
    with col_i:
        po_email = st.text_input("P.O. E-MAIL (Ex: nome@cliente.com)")
    with col_j:
        po_cel_phone = st.text_input("P.O. CEL. PHONE (Ex: +55 21 99999-9999)")

    st.divider()

    # --- BLOCO 3: INSTALAÇÃO, EQUIPAMENTO E FABRICANTE (Colunas K até N + P) ---
    st.markdown("##### 🚢 3. Embarcação, Equipamento e Localização")
    col_k, col_l, col_m, col_n, col_p = st.columns(5)
    
    with col_k:
        installation = st.text_input("INSTALLATION (Navio / Base - Ex: ILHA DO MARAJÓ)")
    with col_l:
        equip = st.selectbox("EQUIP.", ["ENGINE", "PROP", "DECK MACH.", "Equipamentos", "OUTRO"])
    with col_m:
        equipment_type = st.text_input("EQUIPMENT TYPE (Ex: AZIMUTAL US205, MAK 8M25...)")
    with col_n:
        maker = st.text_input("MAKER (Ex: WARTSILA, KONGSBERG, MAK, KAWASAKI...)")
    with col_p:
        location = st.text_input("LOCATION (Ex: PORTO DO AÇU, ESTALEIRO RENAVE, ON BOARD...)")

    st.divider()

    # --- BLOCO 4: CONDIÇÕES COMERCIAIS E CAIXAS DE TEXTO GRANDES (Colunas O, Q, R, S, T) ---
    st.markdown("##### 📝 4. Descrição do Serviço, Status Comercial e Notas")
    
    # Caixas de texto maiores lado a lado para SERVICE DESCRIPTION e NOTES
    txt_col1, txt_col2 = st.columns(2)
    with txt_col1:
        service_description = st.text_area(
            "SERVICE DESCRIPTION (Descrição detalhada do serviço a realizar)", 
            height=120,
            placeholder="Ex: OVERHAUL AZIMUTAIS US 205 / TROCA DE SELOS DO EIXO / BOMBA INJETORA..."
        )
    with txt_col2:
        notes = st.text_area(
            "NOTES (Observações, NFs, Ref. P.O., Time Sheet, Previsões...)", 
            height=120,
            placeholder="Ex: Ref. P.O. - PRL-25-000586 (Aguardando Time Sheet) / NF 203..."
        )

    fin_col1, fin_col2, fin_col3 = st.columns(3)
    with fin_col1:
        condition = st.selectbox("CONDITION", ["PREÇO FIXO", "HH", "A DEFINIR"])
    with fin_col2:
        status = st.selectbox("STATUS", [
            "EM NEGOCIAÇÃO", "EM ANDAMENTO", "FATURAR", "FATURADO", "PERDIDO"
        ])
    with fin_col3:
        valor = st.number_input("VALOR (R$)", min_value=0.0, step=100.0, format="%.2f")

    # Botão de submissão
    salvar = st.form_submit_button("💾 Guardar Case na Base de Dados", use_container_width=True)

    if salvar:
        if case_code.strip() == "" or client.strip() == "":
            st.error("⚠️ Preencha pelo menos o código do CASE e o nome do CLIENT!")
        else:
            val_field = "X" if chk_field else ""
            val_workshop = "X" if chk_workshop else ""
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO service_inquires (
                    case_code, date_open, field, workshop, commercial_mps,
                    client, requested_by, po_contact_name, po_email, po_cel_phone,
                    installation, equip, equipment_type, maker, service_description,
                    location, condition, status, valor, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_code.strip().upper(),
                date_open.strftime("%d/%m/%Y"),
                val_field,
                val_workshop,
                commercial_mps,
                client.strip().upper(),
                requested_by.strip().upper(),
                po_contact_name.strip().upper(),
                po_email.strip().lower(),
                po_cel_phone.strip(),
                installation.strip().upper(),
                equip,
                equipment_type.strip().upper(),
                maker.strip().upper(),
                service_description.strip(),
                location.strip().upper(),
                condition,
                status,
                valor,
                notes.strip()
            ))
            conn.commit()
            st.success(f"✅ O Case **{case_code.upper()}** foi registado com sucesso!")
            st.rerun()

# ==========================================
# 5. TABELA GERAL (COM AS CORES DA PLANILHA)
# ==========================================
st.divider()
st.subheader("📊 Quadro Geral - Service Inquires")

df = pd.read_sql_query("""
    SELECT 
        case_code AS "CASE",
        date_open AS "DATE",
        field AS "FIELD",
        workshop AS "WORKSHOP",
        commercial_mps AS "COMMERCIAL MPS",
        client AS "CLIENT",
        requested_by AS "REQUESTED BY",
        po_contact_name AS "P.O. CONTACT NAME",
        po_email AS "P.O. E-MAIL",
        po_cel_phone AS "P.O. CEL. PHONE",
        installation AS "INSTALLATION",
        equip AS "EQUIP.",
        equipment_type AS "EQUIPMENT TYPE",
        maker AS "MAKER",
        service_description AS "SERVICE DESCRIPTION",
        location AS "LOCATION",
        condition AS "CONDITION",
        status AS "STATUS",
        valor AS "VALOR",
        notes AS "NOTES"
    FROM service_inquires
    ORDER BY id DESC
""", conn)

if df.empty:
    st.info("Ainda não existem cases registados nesta nova tabela. Utilize o formulário acima para adicionar o primeiro!")
else:
    # Função para aplicar as mesmas cores de STATUS da folha de cálculo original
    def colorir_status(val):
        cores = {
            "FATURADO": "background-color: #00ff00; color: black; font-weight: bold;",
            "PERDIDO": "background-color: #ff0000; color: white; font-weight: bold;",
            "FATURAR": "background-color: #000000; color: white; font-weight: bold;",
            "EM ANDAMENTO": "background-color: #ffff00; color: black; font-weight: bold;",
            "EM NEGOCIAÇÃO": "background-color: #a6a6a6; color: black; font-weight: bold;"
        }
        return cores.get(val, "")

    df_estilizado = df.style.map(colorir_status, subset=["STATUS"]).format({"VALOR": "R$ {:,.2f}"})
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)