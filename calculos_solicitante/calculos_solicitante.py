import math

def calcular_solicitante(metodo, tirantes, Lx, Ly, dist_terças, ang, q_p_terça, q_p_chapa, dim_tirante, q_v, Ix, Iy, debug=False):
    print("\n🧩 [DEBUG] Iniciando cálculo de solicitante...") if debug else None

    # Conversões
    Lx_m = Lx / 100  # cm -> m
    Ly_m = Ly / 100
    dist_terças_m = dist_terças / 100
    
    # --- Carga dos tirantes ---
    # Considera o peso dos tirantes como carga pontual distribuída na terça
    comp_tirante = tirantes * (math.sqrt( (Lx_m/(tirantes+1))**2 + dist_terças_m**2)) + dist_terças_m
    peso_esp = 7850  # kg/m³
    dim_tirante_m = dim_tirante / 1000  # mm -> m
    # Carga negativa (gravidade para baixo)
    q_p_tirante = -1 * tirantes *(((math.pi * dim_tirante_m**2) / 4) * comp_tirante * peso_esp / (100 * Lx_m)) #em kN/m

    # --- Cargas principais ---
    # Convenção Sugerida:
    # Cargas Gravitacionais (Peso, Sobrecarga) devem entrar negativas (para baixo)
    # Cargas de Vento (Sucção) devem entrar positivas (para cima) ou vice-versa, desde que opostas.
    
    # IMPORTANTE: Verifique se q_p_chapa e q_p_terça estão chegando com o sinal correto.
    # Assumindo que no app.py:
    # - Gravidade é input positivo (+)
    # - Sucção é input negativo (-)
    # Vamos ajustar os sinais aqui para garantir que Gravidade aponte para baixo (negativo no eixo local Y se inclinado)
    
        
    # NOTA: O código original usava uma lógica de decomposição específica. 
    # Vou manter a lógica original de decomposição mas corrigir a seleção do MAX.
    
    q_v_x = q_v * dist_terças_m # Carga de vento linear (positivo ou negativo)
    q_p_chapa_kNm = q_p_chapa * dist_terças_m

    # Decomposição (Eixo X = Perpendicular à alma / Eixo Y = Paralelo à alma)
    # q_p_kx = Carga permanente no eixo X (Perpendicular)
    # ATENÇÃO: Somamos peso da terça + chapa + tirante. Todos devem ter mesmo sinal (Gravidade).
    # O código original tinha (-q_p_terça + q_p_chapa ...). Se chapa for positivo e terça negativo, eles se subtraem!
    # CORREÇÃO DE SINAL DA GRAVIDADE: Forçamos tudo para "baixo"
    carga_perm_total = -1 * (abs(q_p_terça) + abs(q_p_chapa_kNm) + abs(q_p_tirante))
    
    q_p_kx = carga_perm_total * math.cos(math.radians(ang))
    q_p_ky = carga_perm_total * math.sin(math.radians(ang))

    # Sobrecarga (Sempre vertical para baixo -> Projetada)
    q_sc_total = -0.25 * dist_terças_m # 0.25 kN/m² norma
    q_sc_x = q_sc_total * math.cos(math.radians(ang))
    q_sc_y = q_sc_total * math.sin(math.radians(ang))

    # --- Coeficientes (NBR 8800 / 14762) ---
    g_p, g_sc, g_v = 1.25, 1.5, 1.4
    psi_sc, psi_v = 0.8, 0.6

    # --- Combinações de carga (ELU) ---
    # Comb 1: 1.25 Perm + 1.5 Sobrecarga
    q_x_1 = g_p * q_p_kx + g_sc * q_sc_x
    q_y_1 = g_p * q_p_ky + g_sc * q_sc_y
    
    # Comb 2: 1.25 Perm + 1.4 Vento (Vento Principal)
    q_x_2 = g_p * q_p_kx + g_v * q_v_x
    q_y_2 = g_p * q_p_ky
    
    # Comb 3: 1.0 Perm + 1.4 Vento (Sucção pura - PP favorável)
    # IMPORTANTE: Aqui o PP não é majorado por 1.25, usa-se 1.0 pois ele ajuda a combater a sucção
    q_x_3 = 1.0 * q_p_kx + g_v * q_v_x
    q_y_3 = 1.0 * q_p_ky
    
    # Comb 4: Perm + Sobrecarga (Principal) + Vento (Secundário)
    q_x_4 = g_p * q_p_kx + g_sc * q_sc_x + g_v * psi_v * q_v_x
    q_y_4 = g_p * q_p_ky + g_sc * q_sc_y
    
    # Comb 5: Perm + Vento (Principal) + Sobrecarga (Secundária)
    q_x_5 = g_p * q_p_kx + g_v * q_v_x + g_sc * psi_sc * q_sc_x
    q_y_5 = g_p * q_p_ky + g_sc * q_sc_y

    # --- SELEÇÃO DA CARGA CRÍTICA (CORRIGIDO) ---
    # key=abs pega o valor com maior módulo, mas MANTÉM O SINAL original.
    # Se a sucção (positiva/negativa oposta) vencer, q_x terá o sinal do vento.
    q_x = max(q_x_1, q_x_2, q_x_3, q_x_4, q_x_5, key=abs)
    q_y = max(q_y_1, q_y_2, q_y_3, q_y_4, q_y_5, key=abs)

    if debug:
        print(f"\n📊 Combinações críticas:")
        print(f" - q_x escolhido = {q_x:.5f} kN/m")
        print(f" - q_y escolhido = {q_y:.5f} kN/m")

    # --- Cálculo dos momentos ---
    # Fórmula base: M = q * L^2 / 8
    # Se q_x for negativo (gravidade), Mdx será negativo (compressão embaixo? depende do referencial).
    # O código original usava M = -q... para inverter.
    # Vamos manter a física: 
    # Se q for para baixo (-), Momento flete para baixo (traciona embaixo).
    # Se q for para cima (+) (Sucção), Momento flete para cima (traciona em cima).
    
    if metodo.lower() == "viga bi-apoiada":
        tipo_viga = "bi-apoiada"
        # Mdx = -qL²/8. 
        # Se q é negativo (gravidade), M vira Positivo. 
        # Se q é positivo (sucção), M vira Negativo. (CORRETO)
        Mdx_cal = -q_x * Lx_m**2 / 8 
        Mdy_cal = -q_y * (Lx_m/(tirantes+1))**2 / 8 # Assumindo tirantes em Y
        
        # Define Positivo e Negativo para o dimensionamento
        Mdx_pos = Mdx_cal if Mdx_cal > 0 else 0
        Mdx_neg = Mdx_cal if Mdx_cal < 0 else 0
        
        # Para Y, geralmente tirantes reduzem o vão.
        # Mas vamos seguir a lógica original de coeficientes se houver tirantes
        if tirantes == 0:
             Mdy_pos = q_y * Ly_m**2 / 8 # Logica antiga estava invertida? Vamos padronizar
             Mdy_neg = 0
        else:
             # Mantendo coeficientes originais do seu código para tirantes
             Mdy_pos = abs(9 * q_y * Ly_m**2 / 128)
             Mdy_neg = -abs(q_y * Ly_m**2 / 8)

    elif metodo.lower() == "viga contínua":
        tipo_viga = "contínua"
        # Na contínua, temos momento no apoio (negativo p/ gravidade) e no vão (positivo p/ gravidade)
        # Se q_x for negativo (gravidade): Apoio (-), Vão (+)
        # Se q_x for positivo (sucção): Apoio (+), Vão (-)
        
        # Coeficientes conservadores para 2 vãos:
        # Apoio: qL²/8
        # Vão: 9qL²/128
        
        m_apoio =  q_x * Lx_m**2 / 8  # Se q negativo -> M negativo. Se q positivo -> M positivo.
        m_vao = -9 * q_x * Lx_m**2 / 128 # Se q negativo -> M positivo.
        
        # Separa para verificação
        Mdx_pos = max(m_apoio, m_vao, 0)
        Mdx_neg = min(m_apoio, m_vao, 0)
        
        # Para eixo Y (Mdy)
        # Mantendo seus coeficientes de tirantes originais
        if tirantes == 0:
            Mdy_pos = 9 * abs(q_y) * Ly_m**2 / 128
            Mdy_neg = -abs(q_y) * Ly_m**2 / 8
        elif tirantes == 1:
            Mdy_pos = 121 * abs(q_y) * Ly_m**2 / 1568
            Mdy_neg = -3 * abs(q_y) * Ly_m**2 / 28
        elif tirantes == 2:
            Mdy_pos = 1681 * abs(q_y) * Ly_m**2 / 21632
            Mdy_neg = -11 * abs(q_y) * Ly_m**2 / 104
        elif tirantes == 3:
            Mdy_pos = 23409 * abs(q_y) * Ly_m**2 / 301088
            Mdy_neg = -41 * abs(q_y) * Ly_m**2 / 388
        else:
            Mdy_pos, Mdy_neg = 0, 0

    else:
        raise ValueError("Método inválido.")

    # --- Força concentrada e Cortante (Usa magnitude, pois sinal não importa tanto pra Vrd) ---
    q_x_mag = abs(q_x)
    if "contínua" in metodo.lower():
        Fwsd_int = 1.25 * q_x_mag * Lx_m
        Fwsd_ext = 0.375 * q_x_mag * Lx_m
        Vsd = 0.625 * q_x_mag * Lx_m
    else: 
        Fwsd_ext = (q_x_mag * Lx_m) / 2
        Vsd = (q_x_mag * Lx_m) / 2
        Fwsd_int = 0.0

    # Seleção final do momento solicitante (Pega o pior caso: Positivo ou Negativo)
    # Se Mdx_neg tiver módulo maior (sucção forte), Msd_x será negativo.
    Msd_x = 100 * (Mdx_pos if abs(Mdx_pos) >= abs(Mdx_neg) else Mdx_neg)
    Msd_y = 100 * (Mdy_pos if abs(Mdy_pos) >= abs(Mdy_neg) else Mdy_neg)

    # --- ELS (Flechas) ---
    psi_sc1, psi_v1 = 0.7, 0.3
    # Combinações ELS também precisam respeitar sinais
    # q_p é negativo (gravidade)
    # q_v é positivo/negativo (vento)
    
    q_els_grav = q_p_kx
    q_els_sc = q_sc_x
    q_els_vento = q_v_x
    
    q_fx_1 = q_els_grav + q_els_vento + psi_sc1 * q_els_sc
    q_fx_2 = q_els_grav + q_els_sc + psi_v1 * q_els_vento
    q_fx_3 = q_els_grav + q_els_vento
    q_fx_4 = q_els_grav + q_els_sc
    
    # Seleciona maior magnitude ELS
    q_fx = max(q_fx_1, q_fx_2, q_fx_3, q_fx_4, key=abs)
    q_fy = q_p_ky + q_sc_y 

    # Cálculo Flecha (usa magnitude abs para não dar flecha negativa na verificação simples)
    if "contínua" in metodo.lower():
        flecha_x = (abs(q_fx)/100)*(Lx**4)/(185*20000*Ix)
        flecha_y = (abs(q_fy)/100) * (Ly**4)/(185*20000*Iy)
    else:
        flecha_x = (5 * abs(q_fx/100) * (Lx**4))/(384*20000*Ix)
        flecha_y = (5 * abs(q_fy/100) * (Ly**4))/(384*20000*Iy)

    # Retorna os valores (Msd_x e Msd_y podem ser negativos agora!)
    return Msd_x, Msd_y, q_x, q_y, flecha_x, flecha_y, q_fx, q_fy, Vsd, Fwsd_ext, Fwsd_int