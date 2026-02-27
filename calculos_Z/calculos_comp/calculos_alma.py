import math

def calcular_c_alma(perfil_z, sigma, Aef2):
    """Calcula as propriedades do enrijecedor para o método ESC."""

    bf = perfil_z["bf"]
    bw = perfil_z["bw"]
    t = perfil_z["t"]

    # 📌 Cálculo das dimensões da seção
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
    lret2 = bw - bw_ef
    Aret2 = t * lret2
    Aef2 = Aef2 - Aret2

    return {
        "lambda" : lambda_p,
        "lret2": lret2,
        "Aret2": Aret2,
        "Aef2": Aef2
    }



    