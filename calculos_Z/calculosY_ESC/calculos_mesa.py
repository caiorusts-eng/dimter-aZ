import math

def calcular_mesa(perfil_z, t, fy):
    """Calcula as propriedades efetivas da mesa no método ESC."""

    xg0 = perfil_z["xg0"]
    bf = perfil_z["bf"]
    bw = perfil_z["bw"]
    A = perfil_z["A"]

    # 📌 Cálculo de lambda
    sigma_2 = (xg0-bf)*fy/xg0
    psi = sigma_2/fy
    k = 0.57 - 0.21*psi + 0.07*psi**2
    lambda_val = bf / t
    lambda_p = lambda_val / (0.95 * math.sqrt(k*20000 /fy))

    x1=0

    if lambda_p < 0.673:
            bef = bf
            xg1=xg0
            Aef1 = A
            iyret1 = 0
    else:  
            # 📌 Cálculo da mesa efetiva
            bef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
            lret1 = bf - bef
            Aret1 = t * lret1
            Aef1 = A - Aret1  # 🔹 Garantimos que Aef1 seja sempre definido
            d1 = xg0 - lret1*0.5
            x1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
            xg1 = xg0 + x1 - lret1 # 🔹 Agora `xg2` sempre será definido
            iyret1 = ((t * (lret1 ** 3)) / 12) + (Aret1 * (d1 ** 2))

    return {
    "lambda": lambda_val,
    "k" : k,
    "lambda_p": lambda_p,
    "bef": bef,
    "xg1": xg1,
    "Aef1": Aef1,
    "x1" : x1,
    "iyret1": iyret1 if iyret1 is not None else 0  # 🔹 Adicionando sempre um valor válido
}



