import math

def calcular_c_alma(perfil, sigma, Aef2):
    """Calcula as propriedades do enrijecedor para o método ESC."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Cálculo das dimensões da seção
    d = D - 2 * t
    bf = bf - 4 * t
    bw = bw - 4 * t
    lambda_val = bw/t

    # 📌 Cálculo de lambda
    k = 4
    lambda_p =  lambda_val / (0.95* math.sqrt(k * 20000/sigma))

    # 📌 Cálculo da largura efetiva `bc_ef`
    if lambda_p < 0.673:
        bw_ef = bw
    else:
        bw_ef = bw * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
    
    # 📌 Cálculo das áreas reduzidas e centróides
    lret3 = bw - bw_ef
    Aret3 = t * lret3
    Aef3 = Aef2 - Aret3

    return {
        "lambda" : lambda_p,
        "lret3": lret3,
        "Aret3": Aret3,
        "Aef3": Aef3
    }



    