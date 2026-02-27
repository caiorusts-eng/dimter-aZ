# app.py
# Arquivo principal da aplicação com interface gráfica

# --- Importações ---
import streamlit as st
import pandas as pd
import importlib
import sys
import os
import math # Adicionado para a lógica de flexão composta

# Adiciona o diretório atual ao path para garantir que os módulos sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Módulos do seu projeto ---
from perfis import buscar_perfil, perfis_z90, perfis_z45
from calculos_solicitante.calculos_solicitante import calcular_solicitante
from calculos_Z.z_prop import calcular_zprop # Importa a função de perfil customizado

# Os módulos 'executar_calculos' serão importados dinamicamente

# --- Configuração da Página do Streamlit ---
st.set_page_config(
    page_title="Dimensionamento de Terças Z",
    page_icon="🏗️",
    layout="wide"
)

# --- CSS Personalizado para Tabelas ---
# (Este CSS será usado para as 3 tabelas)
st.markdown("""
<style>
    .table-container {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    .styled-table {
        border-collapse: collapse;
        margin-bottom: 25px; /* Espaço entre as tabelas */
        font-size: 1em;
        font-family: "Source Sans Pro", sans-serif;
        width: 100%; /* Largura total */
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.10);
    }
    .styled-table thead tr {
        background-color: #31333F;
        color: #ffffff;
        text-align: center;
    }
    .styled-table th,
    .styled-table td {
        padding: 12px 15px;
        text-align: center;
        border: 1px solid #e0e0e0; /* Borda sutil */
    }
    .styled-table tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f9f9f9; /* Cor de zebra */
    }
    .styled-table tbody tr:hover {
        background-color: #9599b8; /* Cor do hover */
    }
    .pass { color: #00703c; font-weight: bold; }
    .fail { color: #d4351c; font-weight: bold; }
    .na { color: #888; font-style: italic; }
</style>
""", unsafe_allow_html=True)


# --- Funções ---
def calcular_cb(metodo):
    """Calcula Cb com base no modelo de viga."""
    if "viga bi-apoiada" in metodo.lower():
        return 1.136363636
    elif "viga contínua" in metodo.lower():
        return 1.433121019
    return 1.0 # Valor padrão

def fmt_check(val_sd, val_rd, check):
    """Formata célula como 'Sd / Rd (✅)' com cores."""
    cor = "pass" if check == "✅" else "fail" if check == "❌" else "na"
    if check == "N/A": return "<span class='na'>N/A</span>"
    # Usa valor com sinal (sem abs) para mostrar se é positivo ou negativo (importante para sucção)
    return f"{(val_sd):.2f} / {(val_rd):.2f} <span class='{cor}'>({check})</span>"

def fmt_single(val, check):
    """Formata célula de verificação única (ex: Flexão Comp.)"""
    cor = "pass" if check == "✅" else "fail" if check == "❌" else "na"
    if check == "N/A": return "<span class='na'>N/A</span>"
    return f"{val:.3f} <span class='{cor}'>({check})</span>"

# --- FUNÇÃO DE ANÁLISE ATUALIZADA ---
def run_analysis(perfil, tipo, nome_perfil_completo, is_custom, fy, Lx, Ly, Lz, Cb, c, metodo, q_p_chapa, q_v, Ncsd, telha_trava, quadro_contraventado, tirantes, dist_tercas, ang, dim_tirante, debug=False):
    """
    Executa a análise completa para um perfil (catálogo ou customizado).
    Retorna um dicionário flat com todos os resultados e o status de verificação (booleano).
    """
    try:
        # 1. Obter propriedades e calcular solicitações
        Ix = perfil.get("Ix", 0)
        Iy = perfil.get("Iy", 0)
        q_p_terca = perfil.get("m", 0) / 100

        # --- ATUALIZADO: Captura os 11 valores de retorno ---
        Msd_x, Msd_y, q_x, q_y, flecha_x, flecha_y, q_fx, q_fy, Vsd, Fwsd_ext, Fwsd_int = calcular_solicitante(
            metodo, tirantes, Lx, Ly, dist_tercas, ang,
            q_p_terca, q_p_chapa, dim_tirante, q_v,
            Ix, Iy, debug=debug
        )

        # 2. Executar cálculos estruturais (Resistentes)
        if is_custom:
            modulo = importlib.import_module("calculos_Z.executar_calculos")
            resultados = modulo.executar_calculos(
                perfil["bf"], perfil["bw"], perfil["t"],
                fy, Lx, Ly, Lz, Cb, c, debug=debug
            )
        else:
            modulo = importlib.import_module(f"calculos_{tipo}.executar_calculos")
            resultados = modulo.executar_calculos(
                perfil, fy, Lx, Ly, Lz, Cb, c, debug=debug
            )

        # 3. Verificações ELU - Momentos
        mrd_x_esc = resultados.get('Mrd_x_esc', 0)
        mrd_y_esc = resultados.get('Mrd_y_esc', 0)
        check_x_esc = "✅" if abs(mrd_x_esc) >= abs(Msd_x) else "❌"
        check_y_esc = "✅" if abs(mrd_y_esc) >= abs(Msd_y) else "❌"
        
        # Determina quais verificações são aplicáveis
        chaves_passa_x = ["Mrd_x_esc"]
        chaves_passa_y = ["Mrd_y_esc"]

        mrd_x_flt = resultados.get('Mrd_x_flt', 0)
        mrd_y_flt = resultados.get('Mrd_y_flt', 0)
        
        # --- LÓGICA DE FLT CORRIGIDA PARA SUCÇÃO ---
        # Se a telha trava E o momento é positivo (gravidade/compressão no topo):
        # A telha trava a mesa comprimida -> FLT é contida (N/A).
        if telha_trava and Msd_x >= 0:
            check_x_flt = "N/A"
        else:
            # Se a telha NÃO trava OU se o momento é negativo (sucção/compressão na base):
            # A mesa comprimida está solta (ou travada apenas pelos tirantes) -> FLT deve ser verificada.
            check_x_flt = "✅" if abs(mrd_x_flt) >= abs(Msd_x) else "❌"
            chaves_passa_x.append("Mrd_x_flt")

        # Para o eixo Y, assumimos que a telha diafragma impede deslocamento lateral global da estrutura
        if telha_trava and Msd_x >=0:
            check_y_flt = "N/A"
        else:
            check_y_flt = "✅" if abs(mrd_y_flt) >= abs(Msd_y) else "❌"
            chaves_passa_y.append("Mrd_y_flt")
        
        mrd_x_dist = resultados.get('Mrd_x_dist', 0)
        mrd_y_dist = resultados.get('Mrd_y_dist', 0)
        if is_custom: 
            check_x_dist, check_y_dist = "N/A", "N/A"
        else:
            check_x_dist = "✅" if abs(mrd_x_dist) >= abs(Msd_x) else "❌"
            check_y_dist = "✅" if abs(mrd_y_dist) >= abs(Msd_y) else "❌"
            chaves_passa_x.append("Mrd_x_dist")
            chaves_passa_y.append("Mrd_y_dist")

        # 4. Verificações ELU - Forças
        ncrd = resultados.get('Ncrd', 0)
        ntrd = resultados.get('Ntrd', 0)
        axial_rd = 0.0
        check_axial = "N/A"
        axial_label = "AXIAL" # Label padrão
        if Ncsd < 0: # Compressão
            axial_rd = ncrd
            check_axial = "✅" if abs(ncrd) >= abs(Ncsd) else "❌"
            axial_label = "COMPRESSÃO (Nsd/Nrd)"
        elif Ncsd > 0: # Tração
            axial_rd = ntrd
            check_axial = "✅" if abs(ntrd) >= abs(Ncsd) else "❌"
            axial_label = "TRAÇÃO (Nsd/Nrd)"
        else:
             check_axial = "✅" # Se Ncsd for 0, passa
             axial_label = "AXIAL (Nsd/Nrd)"

        vrd = resultados.get('Vrd', 0)
        check_vrd = "✅" if abs(vrd) >= abs(Vsd) else "❌"
        
        fwrd_ext = resultados.get('Fwrd_ext', 0)
        fwrd_int = resultados.get('Fwrd_int', 0)
        check_fw_ext = "✅" if abs(fwrd_ext) >= abs(Fwsd_ext) else "❌"
        
        is_continua = "contínua" in metodo.lower()
        check_fw_int = "N/A"
        if is_continua:
             check_fw_int = "✅" if abs(fwrd_int) >= abs(Fwsd_int) else "❌"

        # 5. Flexão Composta (Interação N + Mx + My)
        # Deve ser calculada SEMPRE. Se Ncsd=0, torna-se verificação de Flexão Bi-axial.
        
        # Coleta os momentos resistentes válidos para a interação (em módulo)
        mrd_x_validos = [abs(mrd_x_esc)]
        # Importante: Se telha_trava=True e Msd_x < 0 (sucção), FLT foi verificado acima e deve entrar na conta.
        # A lógica "if not telha_trava" antiga estava simples demais.
        
        # Se check_x_flt não for N/A, o valor de FLT é válido e deve ser considerado se for crítico
        if check_x_flt != "N/A": 
            mrd_x_validos.append(abs(mrd_x_flt))
        
        if not is_custom: mrd_x_validos.append(abs(mrd_x_dist))
        
        mrd_y_validos = [abs(mrd_y_esc)]
        if check_y_flt != "N/A":
            mrd_y_validos.append(abs(mrd_y_flt))
        if not is_custom: mrd_y_validos.append(abs(mrd_y_dist))

        # Filtra valores > 0 para evitar erros se algum Mrd vier zerado por falha de cálculo
        mx_vals_pos = [v for v in mrd_x_validos if v > 0]
        my_vals_pos = [v for v in mrd_y_validos if v > 0]
        
        # Define o momento resistente determinante (o menor dos modos)
        min_mx = min(mx_vals_pos) if mx_vals_pos else 1e9
        min_my = min(my_vals_pos) if my_vals_pos else 1e9
        
        # Calcula o termo axial separadamente
        termo_n = 0.0
        # Só calcula a parcela axial se houver esforço normal
        if abs(Ncsd) > 0:
            rad_val = axial_rd if axial_rd > 0 else 1e9
            termo_n = (abs(Ncsd) / rad_val)
        
        # Equação de Interação: (N/Nrd) + (Mx/Mxrd) + (My/Myrd) <= 1.0
        interacao = termo_n + (abs(Msd_x) / min_mx) + (abs(Msd_y) / min_my)
        
        check_interacao = "✅" if interacao <= 1.0 else "❌"

        # 6. ELS
        lim_fx = (Lx / 180) if q_fx < 0 else (Lx / 120)
        lim_fy = (Ly / 180) if q_fy < 0 else (Ly / 120)
        check_fx = "✅" if abs(flecha_x) <= lim_fx else "❌"
        check_fy = "✅" if abs(flecha_y) <= lim_fy else "❌"
        passa_els = "✅" if (check_fx == "✅" and check_fy == "✅") else "❌"

        # 7. Flag Geral de Aprovação
        passou_geral = all([
            check_x_esc == "✅", check_y_esc == "✅",
            check_x_flt in ["✅", "N/A"], check_y_flt in ["✅", "N/A"],
            check_x_dist in ["✅", "N/A"], check_y_dist in ["✅", "N/A"],
            check_axial in ["✅", "N/A"], check_vrd == "✅",
            check_fw_ext == "✅", check_fw_int in ["✅", "N/A"],
            passa_els == "✅", check_interacao in ["✅", "N/A"]
        ])

        # 8. Construir a linha de resultado (dicionário flat)
        linha = {
            "Perfil": nome_perfil_completo,
            "passou_geral": passou_geral, # Usado para a lógica de "próximo perfil"
            
            # Tabela 1: Momentos
            "ESC (Sd/Rd)": f"Mx: {fmt_check(Msd_x, mrd_x_esc, check_x_esc)}<br>My: {fmt_check(Msd_y, mrd_y_esc, check_y_esc)}",
            "FLT (Sd/Rd)": f"Mx: {fmt_check(Msd_x, mrd_x_flt, check_x_flt)}<br>My: {fmt_check(Msd_y, mrd_y_flt, check_y_flt)}", # Removido o 'if' daqui, o check_x_flt já controla o N/A
            "DIST (Sd/Rd)": f"Mx: {fmt_check(Msd_x, mrd_x_dist, check_x_dist)}<br>My: {fmt_check(Msd_y, mrd_y_dist, check_y_dist)}" if not is_custom else "<span class='na'>N/A</span>",
            "Flexão Comp.": fmt_single(interacao, check_interacao),
            
            # Tabela 2: Forças
            "axial_label": axial_label, # Guarda o label dinâmico
            "Axial (Nsd/Nrd)": fmt_check(Ncsd, axial_rd, check_axial) if quadro_contraventado else "<span class='na'>N/A</span>",
            "Cortante (Vsd/Vrd)": fmt_check(Vsd, vrd, check_vrd),
            "Apoio Ext (Fw_sd/Fw_rd)": fmt_check(Fwsd_ext, fwrd_ext, check_fw_ext),
            "Apoio Int (Fw_sd/Fw_rd)": fmt_check(Fwsd_int, fwrd_int, check_fw_int) if is_continua else "<span class='na'>N/A</span>",

            # Tabela 3: ELS
            "Flecha X (calc/lim)": f"{flecha_x:.3f} / {lim_fx:.3f} <span class='{ 'pass' if check_fx=='✅' else 'fail' }'>({check_fx})</span>",
            "Flecha Y (calc/lim)": f"{flecha_y:.3f} / {lim_fy:.3f} <span class='{ 'pass' if check_fy=='✅' else 'fail' }'>({check_fy})</span>",
            "Resultado ELS": f"<span class='{ 'pass' if passa_els=='✅' else 'fail' }'>{passa_els}</span>"
        }
        
        return linha, passou_geral

    except Exception as e:
        st.error(f"Erro ao processar o perfil {nome_perfil_completo}: {e}")
        st.exception(e) # Mostra o erro completo no app
        return None, False


# --- Interface Gráfica ---
st.title("👨🏻‍💻 Ferramenta para Dimensionamento de Terças em Perfis Z")
with st.expander("Visualizar Propriedades dos Perfis de Catálogo (Z90 e Z45)"):
    perfis_combinados = [dict(p, Tipo='Z90') for p in perfis_z90] + [dict(p, Tipo='Z45') for p in perfis_z45]
    df_perfis = pd.DataFrame(perfis_combinados)
    # Adicionado 'ri' ao expander
    colunas_ordem = ['Tipo', 'perfil', 'A', 'm', 'bw', 'bf', 'D', 't', 'ri', 'Ix', 'Wx', 'rx', 'Iy', 'Wy', 'ry', 'J', 'Cw', 'r0', 'I1', 'I2', 'Mdist_x', 'Mdist_y']
    
    st.dataframe(
        df_perfis[[col for col in colunas_ordem if col in df_perfis.columns]].style.set_properties(**{'text-align': 'center'}).format(precision=3),
        hide_index=True,
        use_container_width=True
    )
    st.caption("*Todas as unidades dessa tabela são derivadas de centímetros.*")

with st.sidebar:
    st.image("assets/logo_ufes.png")
    st.markdown("---")
    st.header("Parâmetros de Entrada")
    
    # Debug removido da UI
    debug_mode = False 
    
    st.subheader("⚙️ Estrutura e Geometria")
    
    # --- SELEÇÃO DE AÇO (NOVIDADE) ---
    tipo_entrada_aco = st.radio("Definição do Aço", ["Aço Estrutural", "Manual"], horizontal=True, label_visibility="collapsed")
    
    if tipo_entrada_aco == "Aço Estrutural":
        # AÇO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        acos_comerciais = {
            "ASTM A36": 25.0,
            "ASTM A572 Gr.50": 34.5,
            "ASTM A570 Gr.36": 25,
            "CIVIL 300": 30.0,
            "CIVIL 350": 35.0,
            "ZAR-230": 23.0, "ZAR-250": 25.0, "ZAR-280": 28.0, "ZAR-320": 32.0, "ZAR-345": 34.5, "ZAR-400": 40.0, "ZAR-550": 55.0, "ZARBL-260": 26.0, "ZARBL-300": 30.0, "ZARBL-340": 34.0, "ZARBL-380": 38.0, "ZARBL-420": 42.0, "ZARBL-460": 46.0, "ZARBL-500": 50.0, "ZMR230": 23.0, "ZMR250": 25.0, "ZMR280": 28.0, "ZMR320": 32.0, "ZMR345": 34.5, "ZMR400": 40.0,
            
        }
        liga_selecionada = st.selectbox("Selecione a Liga", list(acos_comerciais.keys()))
        fy = acos_comerciais[liga_selecionada]
        st.info(f"Tensão de escoamento ($f_y$): **{fy:.2f} kN/cm²**")
    else:
        fy = st.number_input("Tensão de escoamento ($f_y$, kN/cm²)", 20.0, 60.0, 25.0, 0.5, "%.2f")

    Lx = st.number_input("Dist. entre tesouras ($L_x$, cm)", 100.0, value=600.0, step=50.0)
    dist_tercas = st.number_input("Dist. entre terças (cm)", 50.0, value=150.0, step=10.0)
    ang = st.slider("Inclinação da cobertura (°)", 0, 45, 10)
    c = st.number_input("Largura de contato da tesoura (c, cm)", 1.0, value=15.0, step=1.0)
    
    st.subheader("🔗 Modelo Estrutural")
    metodo = st.radio("Modelo de viga", ["Viga bi-apoiada", "Viga contínua"], index=0, horizontal=True)
    st.caption("*Para viga contínua foram considerados 2 vãos*")
    Cb = calcular_cb(metodo)
    st.metric("Coeficiente $C_b$ (Automático)", f"{Cb:.3f}")
    tirantes = st.selectbox("Nº de linhas de tirantes por vão", [0, 1, 2, 3], index=1)
    dim_tirante = st.number_input("Diâmetro dos tirantes (mm)", 1.0, value=10.0, step=0.5) if tirantes > 0 else 0
    telha_trava = st.radio("A telha funciona como travamento?", ["Sim", "Não"], index=0, horizontal=True) == "Sim"
    quadro_contraventado = st.radio("A terça faz parte do quadro contraventado?", ["Sim", "Não"], index=0, horizontal=True) == "Sim"
    Ly = Lx / (tirantes + 1) if tirantes is not None else Lx
    Lz = Ly
    st.markdown("---")
    st.subheader("⚖️ Carregamentos")
    q_p_chapa = st.number_input("Peso próprio da telha (kg/m²)", value=-5.0, step=0.5, format="%.2f") / 100
    q_v = st.number_input("Carga de vento (kN/m²)", value=-0.5, step=0.1, format="%.2f")
    Ncsd = 0.0
    if quadro_contraventado:
        # Help text atualizado
        Ncsd = st.number_input("Esforço axial de cálculo ($N_{Sd}$, kN)", value=0.0, step=0.5, format="%.2f", help="Negativo para compressão, positivo para tração.")
    st.caption("*Valores positivos para cargas gravitacionais (para baixo) e negativos para sucção (para cima).*")
    st.markdown("---")
    
    # --- SELEÇÃO DE PERFIL ATUALIZADA ---
    st.subheader("🎯 Seleção de Perfis para Análise")
    tipo_selecionado = st.radio("Selecione o tipo de perfil", ["Z90", "Z45", "Customizado"], horizontal=True, index=0)

    analise_selecionada = None
    bf_custom, bw_custom, t_custom = 0, 0, 0

    if tipo_selecionado == "Customizado":
        st.info("Insira as dimensões do perfil Z simples (sem enrijecedores).")
        bf_custom = st.number_input("Largura da mesa (bf, cm)", min_value=1.0, value=6.0, step=0.5)
        bw_custom = st.number_input("Altura da alma (d, cm)", min_value=1.0, value=15.0, step=1.0)
        t_custom = st.number_input("Espessura (t, cm)", min_value=0.1, max_value=1.0, value=0.2, step=0.01, format="%.2f")
        analise_selecionada = "Customizado" # Flag para o botão de análise
    else:
        # Catálogo Z90 ou Z45
        perfis_tipo_completo = [f"{tipo_selecionado} {p['perfil']}" for p in (perfis_z90 if tipo_selecionado == "Z90" else perfis_z45)]
        opcoes = [f"Analisar todos os {tipo_selecionado}"] + perfis_tipo_completo
        analise_selecionada = st.selectbox("Escolha os perfis a serem analisados", opcoes)

# --- Lógica do Botão Principal (Atualizada) ---
if st.sidebar.button("Analisar Perfis", type="primary", use_container_width=True):
    
    perfis_a_analisar = [] # Lista de tuplas: (perfil_obj, tipo, nome_completo, is_custom)
    is_analise_geral = False
    is_custom = False

    try:
        if analise_selecionada == "Customizado":
            is_custom = True
            is_analise_geral = False
            tipo = "Z" # Para o módulo calculos_Z
            perfil_obj = calcular_zprop(t_custom, bf_custom, bw_custom)
            nome_completo = f"Z {bw_custom*10}x{bf_custom*10}x{t_custom*10}"
            perfis_a_analisar.append((perfil_obj, tipo, nome_completo, is_custom))
        
        else: # Z90 ou Z45
            is_custom = False
            tipo = tipo_selecionado # Z90 ou Z45
            lista_catalogo = perfis_z90 if tipo == "Z90" else perfis_z45
            lista_catalogo_nomes = [f"{tipo} {p['perfil']}" for p in lista_catalogo]
            
            if analise_selecionada.startswith("Analisar todos"):
                is_analise_geral = True
                # Carrega todos os perfis para a lista de análise
                for p_nome in lista_catalogo_nomes:
                    nome_curto = p_nome.split(" ", 1)[1]
                    perfil_obj = buscar_perfil(nome_curto, lista_catalogo)
                    if perfil_obj:
                        perfis_a_analisar.append((perfil_obj, tipo, p_nome, is_custom))
            else:
                is_analise_geral = False
                # --- LÓGICA DE SUGESTÃO (CORRIGIDA) ---
                # Carrega o perfil selecionado e TODOS OS PRÓXIMOS
                try:
                    idx_inicio = lista_catalogo_nomes.index(analise_selecionada)
                    # Adiciona da seleção até o fim da lista
                    for i in range(idx_inicio, len(lista_catalogo_nomes)):
                        nome_completo_atual = lista_catalogo_nomes[i]
                        nome_curto_atual = nome_completo_atual.split(" ", 1)[1]
                        perfil_obj = buscar_perfil(nome_curto_atual, lista_catalogo)
                        if perfil_obj:
                            perfis_a_analisar.append((perfil_obj, tipo, nome_completo_atual, is_custom))
                
                except (ValueError, IndexError):
                     st.error(f"Não foi possível encontrar o perfil: {analise_selecionada}")
                     perfis_a_analisar = [] # Limpa para não executar nada


    except Exception as e:
        st.error(f"Erro ao preparar perfis para análise: {e}")

    # --- Execução da Análise ---
    if perfis_a_analisar:
        with st.spinner("Calculando... Por favor, aguarde."):
            resultados_finais = []
            
            if is_analise_geral:
                # Analisa todos e adiciona na lista
                for p_args in perfis_a_analisar:
                    # Passa o 'debug_mode'
                    resultado, passou = run_analysis(*p_args, fy, Lx, Ly, Lz, Cb, c, metodo, q_p_chapa, q_v, Ncsd, telha_trava, quadro_contraventado, tirantes, dist_tercas, ang, dim_tirante, debug=debug_mode)
                    if resultado:
                        resultados_finais.append(resultado)
            else:
                # Análise individual (ou customizado)
                primeiro_perfil_args = perfis_a_analisar[0]
                primeiro_resultado, passou = run_analysis(*primeiro_perfil_args, fy, Lx, Ly, Lz, Cb, c, metodo, q_p_chapa, q_v, Ncsd, telha_trava, quadro_contraventado, tirantes, dist_tercas, ang, dim_tirante, debug=debug_mode)
                
                if primeiro_resultado:
                    resultados_finais.append(primeiro_resultado)
                
                    if not passou and not is_custom:
                        st.warning(f"O perfil selecionado **{primeiro_perfil_args[2]}** não atende aos requisitos. Buscando a próxima opção viável...")
                        perfil_sugerido_encontrado = False
                        # Itera no *restante* da lista (que já contém os próximos)
                        for i in range(1, len(perfis_a_analisar)):
                            proximo_perfil_args = perfis_a_analisar[i]
                            resultado_sugerido, passou_sugerido = run_analysis(*proximo_perfil_args, fy, Lx, Ly, Lz, Cb, c, metodo, q_p_chapa, q_v, Ncsd, telha_trava, quadro_contraventado, tirantes, dist_tercas, ang, dim_tirante, debug=debug_mode)
                            
                            if resultado_sugerido and passou_sugerido:
                                st.success(f"**Sugestão:** O perfil **{proximo_perfil_args[2]}** é a opção seguinte que atende aos requisitos.")
                                resultados_finais.append(resultado_sugerido)
                                perfil_sugerido_encontrado = True
                                break # Para no primeiro que passar
                                
                        if not perfil_sugerido_encontrado:
                            st.error("Nenhum perfil subsequente na lista atende aos requisitos.")

            
            # --- Exibição das Tabelas (NOVO FORMATO DE 3 TABELAS) ---
            st.subheader("Tabela de Resultados")
            if resultados_finais:
                df = pd.DataFrame(resultados_finais)

                # --- Tabela 1: Momentos + Flexão Composta ---
                cols_m = ["Perfil", "ESC (Sd/Rd)", "FLT (Sd/Rd)"]
                if not is_custom: cols_m.append("DIST (Sd/Rd)")
                cols_m.append("Flexão Comp.") # Sempre adiciona agora
                
                cols_m_existentes = [col for col in cols_m if col in df.columns]
                df_m = df[cols_m_existentes]
                
                headers_m = ["PERFIL", "ESC (Sd/Rd)", "FLT (Sd/Rd)"]
                if not is_custom: headers_m.append("DIST (Sd/Rd)")
                headers_m.append("FLEXÃO COMPOSTA")
                
                df_m.columns = headers_m
                st.markdown("### Momentos Fletores (kNcm)")
                # --- ATUALIZADO: Adiciona index=False ---
                st.markdown(df_m.to_html(escape=False, index=False, classes='styled-table'), unsafe_allow_html=True)

                # --- Tabela 2: Forças ---
                cols_f = ["Perfil"]
                # --- ATUALIZADO: Label dinâmico para Axial ---
                axial_header_label = "AXIAL (Nsd/Nrd)"
                if quadro_contraventado and Ncsd != 0:
                     # Usa o label dinâmico do primeiro resultado (será o mesmo para todos)
                     axial_header_label = resultados_finais[0].get("axial_label", "AXIAL (Nsd/Nrd)")
                
                if quadro_contraventado: cols_f.append("Axial (Nsd/Nrd)")
                cols_f.extend(["Cortante (Vsd/Vrd)", "Apoio Ext (Fw_sd/Fw_rd)"])
                if "contínua" in metodo.lower():
                    cols_f.append("Apoio Int (Fw_sd/Fw_rd)")
                
                cols_f_existentes = [col for col in cols_f if col in df.columns]
                df_f = df[cols_f_existentes]

                headers_f = ["PERFIL"]
                if quadro_contraventado: headers_f.append(axial_header_label) # <-- USA O LABEL DINÂMICO
                headers_f.extend(["CORTANTE (Vsd/Vrd)", "APOIO EXT (Fwsd/Fwrd)"])
                if "contínua" in metodo.lower():
                    headers_f.append("APOIO INT (Fwsd/Fwrd)")
                
                df_f.columns = headers_f
                st.markdown("### Esforço Axial, Cortante e Força Concentrada (kN)")
                # --- ATUALIZADO: Adiciona index=False ---
                st.markdown(df_f.to_html(escape=False, index=False, classes='styled-table'), unsafe_allow_html=True)
                
                # --- Tabela 3: ELS ---
                cols_e = ["Perfil", "Flecha X (calc/lim)", "Flecha Y (calc/lim)", "Resultado ELS"]
                df_e = pd.DataFrame(resultados_finais)[cols_e]
                headers_e = ["PERFIL", "FLECHA X (Sd/Lim)", "FLECHA Y (Sd/Lim)", "RESULTADO"]
                df_e.columns = headers_e
                
                st.markdown("### Estado Limite de Serviço (Flecha em cm)")
                # --- ATUALIZADO: Adiciona index=False ---
                st.markdown(df_e.to_html(escape=False, index=False, classes='styled-table'), unsafe_allow_html=True)

            else:
                st.warning("Nenhum resultado para exibir.")



# --- Mensagem Final ---
st.markdown("---")
mensagem_final = "Os usuários desta versão educacional do programa estão livres de qualquer compromisso para usá-lo. Entretanto, nem o autor, a UFES, nem qualquer outra instituição relacionada são responsáveis pelo uso ou mau uso do programa e seus resultados. Os citados acima não possuem qualquer dever legal quando a aplicação dos resultados aqui gerados. Ademais, trata-se de uma ferramenta para auxílio no dimensionamento de terças, para a aplicação desse elemento é necessário uma avaliação estrutural minuciosa."
st.markdown(f"<p style='text-align: center; color: grey; font-size: 12px;'>{mensagem_final}</p>", unsafe_allow_html=True)