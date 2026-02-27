import math

def calcular_fy_y_flt(perfil, fy, Lx, Lz):
    """
    Calcula a minoração de fy para FLT e retorna um dicionário com os valores calculados.
    """

    # Propriedades do perfil necessárias
    rx = perfil["rx"]  
    ry = perfil["ry"]  
    I1 = perfil["I1"]  
    Cw = perfil["Cw"]  
    J = perfil["J"]    
    Wy = perfil["Wy"] 

    # Passo 1: Calcular r0
    r0 = float(math.sqrt(rx**2 + ry**2))

    # Passo 2: Cálculo de Nex e Nez
    Nex = float(((math.pi ** 2) * 20000 * I1) / (Lx ** 2))
    Nez = float((1 / r0**2) * ((((math.pi ** 2) * 20000 * Cw) / (Lz ** 2)) + 7700 * J))


    # Passo 3: Cálculo de Me
    Me = float((-1 * Nex) * (-1 * math.sqrt((r0**2) * (Nez / Nex))))

    # Passo 4: Cálculo de lambda_p0
    lambda_p0 = float(math.sqrt(Wy * fy / Me))
    
    # Passo 5: Definir x_flt baseado em lambda_p0
    if lambda_p0 <= 0.6:
        x_flt = 1
    elif 0.6 < lambda_p0 < 1.336:
        x_flt = float(1.11 * (1 - 0.278 * lambda_p0**2))
    else:
        x_flt = float(1 / (lambda_p0**2))

    # Passo 6: Minoração de fy para FLT
    fy_y_flt = float(x_flt * fy)

    return{
    "x_flt" : x_flt,
    "fy_y_flt" : fy_y_flt
    }

