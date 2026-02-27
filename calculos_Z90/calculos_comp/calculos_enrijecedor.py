import math

def calcular_c_enrijecedor(perfil, sigma):
    """Calcula as propriedades do enrijecedor para o método ESC."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]
    A = perfil["A"]

    # 📌 Cálculo das dimensões da seção
    d = D - 2 * t
    bf = bf - 4 * t
    bw = bw - 4 * t
    lambda_val = d/t

    # 📌 Cálculo de lambda
    k = 0.43
    lambda_pe =  lambda_val / (0.95* math.sqrt(k * 20000/sigma))

    if lambda_pe > 0.673:
        d_efetiva = (d/lambda_pe) * (1- 0.22/lambda_pe)
    else: 
        d_efetiva = d

    # 📌 Cálculo da largura efetiva
    lret1 = d-d_efetiva
    Aret1 = lret1 * t
    Aef1 = A-Aret1

    return{
    "lambda" : lambda_pe,
    "lret" : lret1,
    "Aret" : Aret1,
    "Aef" : Aef1
    }


    
    

