import math

def calcular_enrijecedor(perfil, fy_flt):
    """Calcula as propriedades do enrijecedor para o método ESC."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Cálculo das dimensões da seção
    d = D - (2 * t * math.tan(math.radians(45/2)))
    bf = bf - 2 * t - 2*t*math.tan(math.radians(45/2))
    bw = bw - 4 * t
    yg0 = (bw + 4 * t) / 2  

    # 📌 Cálculo da largura efetiva do enrijecedor
    lambda_e = d / t
    sigma_e1 = (yg0 - (2 * t * math.tan(math.radians(45/2)))) * fy_flt / yg0 #Avaliar
    sigma_e2 = (yg0 - d*math.sin(math.radians(45))) * fy_flt / yg0
    psi = sigma_e2 / sigma_e1 if sigma_e1 != 0 else 0
    k = 0.578 / (psi + 0.34)
    lambda_pe = lambda_e / (0.95 * math.sqrt(k * 20000 / sigma_e2)) if sigma_e2 != 0 else 0

    if lambda_pe < 0.673:
        def_efetiva = d
    else:
        def_efetiva = d * (1 - (0.22 / lambda_pe)) * (1 / lambda_pe)

    # 📌 Cálculo do centroide yg1
    lret1 = d - def_efetiva
    Aret1 = t * lret1
    Aef1 = perfil["A"] - Aret1
    d1 = yg0 - (((def_efetiva+lret1/2) *math.sin(math.radians(45))+(2 * t * math.tan(math.radians(45/2))))) 
    y1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
    yg1 = yg0 + y1

    return yg1  # 🔹 yg1 será passado para o cálculo da mesa
