import math

def calcular_c_mesa(perfil_z, sigma):
    """Calcula as propriedades do enrijecedor para o método ESC."""

    bf = perfil_z["bf"]
    bw = perfil_z["bw"]
    t = perfil_z["t"]
    A = perfil_z["A"]

    # 📌 Cálculo das dimensões da seção
    lambda_val = bf/t

    # 📌 Cálculo de lambda
    k = 0.43
    lambda_p =  lambda_val / (0.95* math.sqrt(k * 20000/sigma))

    # 📌 Cálculo da largura efetiva `bc_ef`
    if lambda_p < 0.673:
        bf_ef = bf
    else:
        bf_ef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
    
    # 📌 Cálculo das áreas reduzidas e centróides
    lret1 = bf - bf_ef
    Aret1 = t * lret1
    Aef1 = A - Aret1

    return {
        "lambda" : lambda_p,
        "lret1": lret1,
        "Aret1": Aret1,
        "Aef1": Aef1
    }



    