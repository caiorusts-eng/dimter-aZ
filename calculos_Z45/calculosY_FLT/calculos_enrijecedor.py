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
    xg0 = (bf + 2 * t + 2*t*math.tan(math.radians(45/2)) + D *math.sin(math.radians(45))) - (t/ 2)  

    # 📌 Cálculo da largura efetiva do enrijecedor
    lambda_e = d/t
    sigma_e1 = float(fy_flt)
    sigma_e2 = (xg0 - d*math.sin(math.radians(45))) * fy_flt / xg0
    psi = sigma_e2 / sigma_e1 if sigma_e1 != 0 else 0
    k = 0.57 - 0.21 * psi + 0.07 * psi**2
    lambda_pe = lambda_e / (0.95 * math.sqrt(k * 20000 / fy_flt)) 

    if lambda_pe < 0.673:
        def_efetiva = d
        xg1=xg0
    else:
        def_efetiva = d * (1 - (0.22 / lambda_pe)) * (1 / lambda_pe)

    # 📌 Cálculo do centroide yg1
    lret1 = d - def_efetiva
    Aret1 = t * lret1
    Aef1 = perfil["A"] - Aret1
    d1 = xg0 - (lret1 / 2)
    x1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
    xg1 = xg0 + x1 - (lret1*math.sin(math.radians(45)))

    return{
    "xg1": xg1,
    "xg0" : xg0
}
