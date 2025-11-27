import streamlit as st
import datetime
import pandas as pd
import locale 
from utils import load_data, save_data, load_users, save_users, PRONTUARIOS_FILE, USERS_FILE

# Tenta configurar o locale para Português (pt_BR)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')
    except locale.Error:
        pass # Mantém o locale padrão se falhar

# --- Cores Personalizadas ---
HIGHLIGHT_COLOR = "#FF69B4" # Rosa
GREEN_COLOR = "#4CAF50" # Verde para texto

# --- Funções Auxiliares ---
def calcular_idade(data_nasc_str):
    """Calcula a idade a partir da data de nascimento em formato string (AAAA-MM-DD)."""
    try:
        data_nasc = datetime.datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
        hoje = datetime.date.today()
        return hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
    except:
        return 'N/D'

# --- Funções de Autenticação (Mantidas) ---
def authenticate(username, password):
    """Verifica as credenciais do usuário."""
    users = st.session_state.users
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.current_user = username
        return True
    return False

def logout():
    """Faz o logout do usuário e recarrega os dados."""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.prontuarios = load_data(PRONTUARIOS_FILE)
    st.rerun()

# --- Gerenciamento de Estado da Sessão ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'prontuarios' not in st.session_state:
    st.session_state.prontuarios = load_data(PRONTUARIOS_FILE)
if 'users' not in st.session_state:
    st.session_state.users = load_users()
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- Layout Principal ---
if not st.session_state.logged_in:
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Usuário", key="login_user")
    password = st.sidebar.text_input("Senha", type="password", key="login_pwd")

    if st.sidebar.button("Entrar", key="login_btn"):
        if authenticate(username, password):
            st.sidebar.success("Login bem-sucedido!")
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha incorretos.")
    
    st.markdown("""
        <div style='text-align: center; line-height: 1.1;'>
            <h1 style='margin-bottom: -10px; font-size: 2.5em;'>
                <span style='font-size: 0.8em;'>🏥</span> Fisioterapeuta Aleandra
            </h1>
            <h2 style='color: #4CAF50; font-size: 1.8em; margin-top: 0;'>
                Prontuários
            </h2>
        </div>
    """, unsafe_allow_html=True)

else:
    st.sidebar.title("Menu")
    st.sidebar.markdown(f"**👤 Logado como:** <span style='color:{GREEN_COLOR};'>{st.session_state.current_user}</span>", unsafe_allow_html=True)
    if st.sidebar.button("Sair", type="secondary", key="logout_btn"):
        logout()

    st.title("🏥 Gestão de Prontuários")

    tab1, tab2, tab3 = st.tabs(["📝 Novo Prontuário", "📚 Visualizar Prontuários", "⚙️ Gerenciar Usuários"])

    # --- TAB 1: Novo Prontuário (Com Data de Atendimento) ---
    with tab1:
        st.subheader("Registrar Novo Paciente")

        # --- Definindo Limites de Data ---
        HOJE = datetime.date.today()
        DATA_MINIMA = datetime.date(1920, 1, 1) # Min: 1920
        
        with st.form("form_prontuario"):
            # CAMPOS EXISTENTES
            nome = st.text_input("Nome Completo do Paciente", key="nome_paciente")
            profissao = st.text_input("Profissão", key="profissao")
            
            # 1. DATA DE NASCIMENTO (Min: 1920 | Max: Hoje)
            data_nascimento = st.date_input(
                "Data de Nascimento", 
                value=datetime.date(2000, 1, 1),
                min_value=DATA_MINIMA, 
                max_value=HOJE,
                key="data_nasc"
            )
            
            # 2. DATA DO ATENDIMENTO (Min: 1920 | Max: Hoje)
            data_atendimento_obj = st.date_input(
                "Data do Atendimento",
                value=HOJE,
                min_value=DATA_MINIMA,
                max_value=HOJE
            )

            diagnostico = st.text_area("Diagnóstico", key="diagnostico")
            evolucao_inicial = st.text_area("Evolução Inicial (opcional)", key="evolucao_inicial")

            submit_button = st.form_submit_button("Salvar")

            if submit_button:
                if nome and data_nascimento and diagnostico:
                    
                    # Salvamos as datas no formato ISO para cálculo (AAAA-MM-DD)
                    data_atendimento_str = data_atendimento_obj.strftime("%Y-%m-%d")
                    
                    novo_prontuario = {
                        "id": len(st.session_state.prontuarios) + 1,
                        "nome": nome.strip(),
                        "data_nascimento": data_nascimento.strftime("%Y-%m-%d"), 
                        "profissao": profissao.strip(),
                        "diagnostico": diagnostico.strip(),
                        "evolucao": [
                            # Formato da EVOLUÇÃO (DD-MM-AAAA e Hora)
                            {"data": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "texto": evolucao_inicial.strip()} 
                        ] if evolucao_inicial.strip() else [],
                        
                        "data_atendimento": data_atendimento_str,
                        
                        # Formato da CRIAÇÃO (DD-MM-AAAA)
                        "data_criacao": datetime.datetime.now().strftime("%d-%m-%Y") 
                    }
                    st.session_state.prontuarios.append(novo_prontuario)
                    save_data(st.session_state.prontuarios, PRONTUARIOS_FILE)
                    st.markdown(f"**<p style='color:{HIGHLIGHT_COLOR};'>Prontuário de {nome} salvo com sucesso!</p>**", unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("Por favor, preencha Nome, Data de Nascimento e Diagnóstico.")

    # --- TAB 2: Visualizar Prontuários (Com Pandas) ---
    with tab2:
        st.subheader("Meus Prontuários")

        if not st.session_state.prontuarios:
            st.info("Nenhum prontuário registrado ainda.")
        else:
            df = pd.DataFrame(st.session_state.prontuarios)
            df['idade'] = df['data_nascimento'].apply(lambda x: calcular_idade(x))
            
            # --- FORMATAÇÃO PARA DD-MM-AAAA (EXIBIÇÃO) ---
            df['data_atendimento'] = pd.to_datetime(df['data_atendimento']).dt.strftime('%d-%m-%Y')
            df['data_nascimento'] = pd.to_datetime(df['data_nascimento']).dt.strftime('%d-%m-%Y')
            
            # Adicionamos a Data de Nascimento à exibição principal
            cols_display = ["id", "nome", "idade", "profissao", "diagnostico", "data_atendimento", "data_nascimento", "data_criacao"]
            
            # Renomeamos as colunas para o Português para exibição na tabela
            df_display = df.rename(columns={
                'data_atendimento': 'Atendimento',
                'data_criacao': 'Criação',
                'data_nascimento': 'Nascimento',
                'nome': 'Nome',
                'idade': 'Idade',
                'profissao': 'Profissão',
                'diagnostico': 'Diagnóstico'
            })
            
            st.dataframe(df_display[list(df_display.columns)], use_container_width=True)

            # --- SEÇÃO DE EXCLUSÃO ---
            st.markdown("---")
            st.subheader("🚨 Excluir Prontuário")
            
            max_id = df['id'].max()
            
            with st.form("form_excluir"):
                prontuario_id_excluir = st.number_input(
                    "Digite o ID do prontuário a ser excluído:",
                    min_value=1,
                    max_value=int(max_id),
                    step=1
                )
                btn_excluir = st.form_submit_button("Confirmar Exclusão", type="primary")

                if btn_excluir:
                    indice_para_remover = df[df['id'] == prontuario_id_excluir].index[0]
                    
                    if indice_para_remover >= 0:
                        nome_removido = df.loc[indice_para_remover, 'nome']
                        
                        # Remove do estado de sessão
                        st.session_state.prontuarios.pop(indice_para_remover)
                        
                        # Salva o estado modificado no arquivo JSON
                        save_data(st.session_state.prontuarios, PRONTUARIOS_FILE)
                        
                        st.success(f"Prontuário ID {prontuario_id_excluir} ({nome_removido}) excluído permanentemente.")
                        st.rerun()
                    else:
                        st.error(f"Prontuário com ID {prontuario_id_excluir} não encontrado.")

            # --- SEÇÃO DE DETALHES E EVOLUÇÃO ---
            st.markdown("---")
            st.subheader("🔎 Detalhes e Evolução")
            
            prontuario_selecionado = st.selectbox(
                "Selecione um prontuário para ver/editar:",
                options=df['nome'].unique(),
                key="selecionar_prontuario_edicao"
            )

            if prontuario_selecionado:
                pront = df_display[df_display['Nome'] == prontuario_selecionado].iloc[0].to_dict()

                if pront:
                    st.markdown(f"### Paciente: {pront['Nome']} <br><small>Nasc.: {pront['Nascimento']} | Profissão: {pront['Profissão']}</small>", unsafe_allow_html=True)
                    st.write(f"**Diagnóstico:** {pront['Diagnóstico']}") 

                    st.markdown("---")
                    st.write("**Histórico de Evolução:**")
                    
                    pront_original = next((p for p in st.session_state.prontuarios if p['nome'] == pront['Nome']), None)
                    
                    if pront_original and pront_original['evolucao']:
                        for ev in pront_original['evolucao']:
                            st.markdown(f"<div style='border: 1px solid {GREEN_COLOR}; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>**Data:** {ev['data']} <br>{ev['texto']}</div>", unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma evolução registrada para este paciente ainda.")
                    
                    # Formulário para adicionar nova evolução
                    with st.form(f"form_add_evolucao_{pront['id']}"):
                        nova_evolucao_texto = st.text_area("Adicionar Nova Evolução", key=f"nova_evolucao_texto_{pront['id']}")
                        
                        btn_add_evolucao = st.form_submit_button("Adicionar Evolução", type="primary") 
                        
                        if btn_add_evolucao and nova_evolucao_texto.strip():
                            # Encontra o índice original para modificação
                            idx_original = next((i for i, p in enumerate(st.session_state.prontuarios) if p['id'] == pront['ID']), -1)
                            
                            if idx_original != -1:
                                st.session_state.prontuarios[idx_original]['evolucao'].append({
                                    "data": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), # Novo formato DD-MM-AAAA
                                    "texto": nova_evolucao_texto.strip()
                                })
                                save_data(st.session_state.prontuarios, PRONTUARIOS_FILE)
                                st.markdown(f"**<p style='color:{HIGHLIGHT_COLOR};'>Evolução adicionada para {pront['Nome']}!</p>**", unsafe_allow_html=True)
                                st.rerun()

    # --- TAB 3: Gerenciar Usuários (Sem Alterações) ---
    with tab3:
        st.subheader("Gerenciamento de Usuários")
        
        if st.session_state.current_user == 'admin': 
            st.markdown(f"<span style='color:{HIGHLIGHT_COLOR};'>Usuários Ativos:</span>", unsafe_allow_html=True)
            for user, pwd in st.session_state.users.items():
                st.write(f"- **{user}**")
            
            st.markdown("---")
            
            with st.form("form_add_user"):
                st.write("Adicionar Novo Usuário:")
                new_username = st.text_input("Usuário", key="new_user")
                new_password = st.text_input("Senha", type="password", key="new_pwd")
                add_user_button = st.form_submit_button("Adicionar Usuário")

                if add_user_button:
                    if new_username and new_password:
                        if new_username not in st.session_state.users:
                            st.session_state.users[new_username] = new_password
                            save_users(st.session_state.users)
                            st.success(f"Usuário '{new_username}' adicionado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Usuário '{new_username}' já existe.")
                    else:
                        st.error("Por favor, insira usuário e senha.")
        else:
            st.warning("Funcionalidade de gerenciamento de usuários restrita ao administrador.")