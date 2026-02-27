import math

def calcular_enrijecedor(perfil, fy_y_flt):
    """Calcula as propriedades do enrijecedor para o método ESC."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Cálculo das dimensões da seção
    d = D - 2 * t
    bf = bf - 4 * t
    bw = bw - 4 * t
    xg0 = (bf + 4 * t) - (t/ 2)  
    
    # 📌 Cálculo da largura efetiva do enrijecedor
    lambda_e = d/t
    k = 0.43
    lambda_pe = lambda_e / (0.95 * math.sqrt(k * 20000 / fy_y_flt)) 

    if lambda_pe < 0.673:
        def_efetiva = d
    else:
        def_efetiva = d * (1 - (0.22 / lambda_pe)) * (1 / lambda_pe)

    # 📌 Cálculo do centroide yg1
    lret1 = d - def_efetiva
    Aret1 = t * lret1
    Aef1 = perfil["A"] - Aret1
    d1 = xg0 - (t / 2)
    x1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
    xg1 = xg0 + x1

    return{
    "xg1": xg1,
    "xg0" : xg0
}
