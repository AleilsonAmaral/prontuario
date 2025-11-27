import streamlit as st
import datetime
import pandas as pd
from utils import load_data, save_data, load_users, save_users, PRONTUARIOS_FILE, USERS_FILE

# --- Configuração da Página ---
st.set_page_config(
    page_title="Prontuário Médico",
    page_icon="🏥",
    layout="centered"
)

# --- Cores Personalizadas ---
HIGHLIGHT_COLOR = "#FF69B4" # Rosa

# --- Gerenciamento de Estado da Sessão ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'prontuarios' not in st.session_state:
    st.session_state.prontuarios = load_data(PRONTUARIOS_FILE)
if 'users' not in st.session_state:
    st.session_state.users = load_users()
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- Funções de Autenticação ---
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
    st.sidebar.markdown(f"**👤 Logado como:** <span style='color:#4CAF50;'>{st.session_state.current_user}</span>", unsafe_allow_html=True)
    if st.sidebar.button("Sair", type="secondary", key="logout_btn"):
        logout()

    st.title("🏥 Gestão de Prontuários")

    tab1, tab2, tab3 = st.tabs(["📝 Novo Prontuário", "📚 Visualizar Prontuários", "⚙️ Gerenciar Usuários"])

    # --- TAB 1: Novo Prontuário (Sem Alterações) ---
    with tab1:
        st.subheader("Registrar Novo Paciente")

        with st.form("form_prontuario"):
            nome = st.text_input("Nome Completo do Paciente", key="nome_paciente")
            data_nascimento = st.date_input("Data de Nascimento", key="data_nasc", max_value=datetime.date.today())
            profissao = st.text_input("Profissão", key="profissao")
            diagnostico = st.text_area("Diagnóstico", key="diagnostico")
            
            evolucao_inicial = st.text_area("Evolução Inicial (opcional)", key="evolucao_inicial")

            submit_button = st.form_submit_button("Salvar Prontuário")

            if submit_button:
                if nome and data_nascimento and diagnostico:
                    novo_prontuario = {
                        "id": len(st.session_state.prontuarios) + 1,
                        "nome": nome.strip(),
                        "data_nascimento": data_nascimento.strftime("%Y-%m-%d"),
                        "profissao": profissao.strip(),
                        "diagnostico": diagnostico.strip(),
                        "evolucao": [
                            {"data": datetime.date.today().strftime("%Y-%m-%d %H:%M:%S"), "texto": evolucao_inicial.strip()}
                        ] if evolucao_inicial.strip() else [],
                        "data_criacao": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.prontuarios.append(novo_prontuario)
                    save_data(st.session_state.prontuarios, PRONTUARIOS_FILE)
                    st.markdown(f"**<p style='color:{HIGHLIGHT_COLOR};'>Prontuário de {nome} salvo com sucesso!</p>**", unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.error("Por favor, preencha Nome, Data de Nascimento e Diagnóstico.")

    # --- TAB 2: Visualizar Prontuários (Com Exclusão) ---
    with tab2:
        st.subheader("Meus Prontuários")

        if not st.session_state.prontuarios:
            st.info("Nenhum prontuário registrado ainda.")
        else:
            df = pd.DataFrame(st.session_state.prontuarios)
            df['idade'] = df['data_nascimento'].apply(lambda x: datetime.date.today().year - datetime.datetime.strptime(x, "%Y-%m-%d").year)
            
            cols_display = ["id", "nome", "idade", "profissao", "diagnostico", "data_criacao"]
            st.dataframe(df[cols_display], use_container_width=True)

            # --- SEÇÃO DE EXCLUSÃO ---
            st.markdown("---")
            st.subheader("🚨 Excluir Prontuário")
            
            # Garante que há IDs para excluir (mínimo 1)
            max_id = max(p['id'] for p in st.session_state.prontuarios)
            
            with st.form("form_excluir"):
                prontuario_id_excluir = st.number_input(
                    "Digite o ID do prontuário a ser excluído:",
                    min_value=1,
                    max_value=max_id,
                    step=1
                )
                btn_excluir = st.form_submit_button("Confirmar Exclusão", type="primary")

                if btn_excluir:
                    # Encontra o índice na lista de estado de sessão
                    indice_para_remover = -1
                    for i, pront in enumerate(st.session_state.prontuarios):
                        if pront['id'] == prontuario_id_excluir:
                            indice_para_remover = i
                            break

                    if indice_para_remover != -1:
                        # Remove o item da lista
                        nome_removido = st.session_state.prontuarios[indice_para_remover]['nome']
                        st.session_state.prontuarios.pop(indice_para_remover)
                        
                        # Salva o estado modificado no arquivo JSON
                        save_data(st.session_state.prontuarios, PRONTUARIOS_FILE)
                        
                        st.success(f"Prontuário ID {prontuario_id_excluir} ({nome_removido}) excluído permanentemente.")
                        st.rerun() # Recarrega para atualizar a tabela
                    else:
                        st.error(f"Prontuário com ID {prontuario_id_excluir} não encontrado.")

            # --- SEÇÃO DE DETALHES E EVOLUÇÃO (Movemos para baixo) ---
            st.markdown("---")
            st.subheader("🔎 Detalhes e Evolução")
            
            prontuario_selecionado = st.selectbox(
                "Selecione um prontuário para ver/editar:",
                options=df['nome'].unique(),
                key="selecionar_prontuario_edicao"
            )

            if prontuario_selecionado:
                pront_idx = df[df['nome'] == prontuario_selecionado].index[0]
                pront = st.session_state.prontuarios[pront_idx]

                st.markdown(f"### Paciente: {pront['nome']} <br><small>Nasc.: {pront['data_nascimento']} | Profissão: {pront['profissao']}</small>", unsafe_allow_html=True)
                st.write(f"**Diagnóstico:** {pront['diagnostico']}")

                st.markdown("---")
                st.write("**Histórico de Evolução:**")
                if pront['evolucao']:
                    for ev in pront['evolucao']:
                        st.markdown(f"<div style='border: 1px solid #4CAF50; padding: 10px; border-radius: 5px; margin-bottom: 5px;'>**Data:** {ev['data']} <br>{ev['texto']}</div>", unsafe_allow_html=True)
                else:
                    st.info("Nenhuma evolução registrada para este paciente ainda.")
                
                # Formulário para adicionar nova evolução
                with st.form(f"form_add_evolucao_{pront['id']}"):
                    nova_evolucao_texto = st.text_area("Adicionar Nova Evolução", key=f"nova_evolucao_texto_{pront['id']}")
                    
                    btn_add_evolucao = st.form_submit_button("Adicionar Evolução", type="primary") 
                    
                    if btn_add_evolucao and nova_evolucao_texto.strip():
                        pront['evolucao'].append({
                            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "texto": nova_evolucao_texto.strip()
                        })
                        save_data(st.session_state.prontuarios, PRONTUARIOS_FILE)
                        st.markdown(f"**<p style='color:{HIGHLIGHT_COLOR};'>Evolução adicionada para {pront['nome']}!</p>**", unsafe_allow_html=True)
                        st.rerun()

    # --- TAB 3: Gerenciar Usuários (Sem Alterações) ---
    with tab3:
        st.subheader("Gerenciamento de Usuários")
        
        if st.session_state.current_user == 'admin': 
            st.markdown(f"<span style='color:#FF69B4;'>Usuários Ativos:</span>", unsafe_allow_html=True)
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