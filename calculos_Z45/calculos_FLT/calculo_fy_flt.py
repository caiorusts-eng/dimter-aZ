import math

def calcular_fy_flt(perfil, fy, Ly, Lz, Cb):
    """
    Calcula a minoração de fy para FLT.
    
    Parâmetros:
    - perfil: dicionário com as propriedades da seção
    - fy: tensão de escoamento original (kN/cm²)
    - Ly: comprimento destravado no eixo y (cm)
    - Lz: comprimento destravado no eixo z (cm)
    - Cb: coeficiente de modificação do momento crítico elástico

    Retorna:
    - fy_flt: tensão de escoamento minorada para FLT (kN/cm²)
    """
    
    # Propriedades do perfil necessárias
    rx = perfil["rx"]  # Raio de giração em torno de x (cm)
    ry = perfil["ry"]  # Raio de giração em torno de y (cm)
    Ix = perfil["Ix"]  # Momento de inércia principal em y (cm⁴)
    Cw = perfil["Cw"]  # Constante de empenamento (cm⁶)
    J = perfil["J"]    # Constante de torção (cm⁴)
    Wx = perfil["Wx"]  # Módulo de resistência em x (cm³)

    # Passo 1: Calcular r0
    r0 = math.sqrt(rx**2 + ry**2)

    # Passo 2: Cálculo de Ney e Nez
    Ney = (math.pi ** 2 * 20000 * Ix) / (Ly ** 2)
    Nez = (1 / r0**2) * (((math.pi ** 2 * 20000 * Cw) / (Lz ** 2)) + 7700 * J)

    # Passo 3: Cálculo de Me
    Me = 0.5 * Cb * r0 * math.sqrt(Ney * Nez)

    # Passo 4: Cálculo de lambda_p0
    lambda_p0 = math.sqrt(Wx * fy / Me)

    # Passo 5: Definir x_flt baseado em lambda_p0
    if lambda_p0 <= 0.6:
        x_flt = 1
    elif 0.6 < lambda_p0 <= 1.336:
        x_flt = 1.11 * (1 - (0.278 * lambda_p0**2))
    else:
        x_flt = 1 / (lambda_p0**2)

    # Passo 6: Minoração de fy para FLT
    fy_flt = x_flt * fy

    return max(fy_flt, 0)  # Garantir que não fique negativo
