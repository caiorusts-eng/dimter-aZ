import math

def calcular_mesa(fy_flt, t, perfil_z):
    bf = perfil_z["bf"]
    yg0 = perfil_z["yg0"]
    A = perfil_z["A"]

    # 📌 Inicialização
    ixret1 = 0
    Aef1 = 0
    lret1 = 0
    Aret1 = 0

    # 📌 Cálculo de lambda
    lambda_val = bf / t
    k = 0.43
    lambda_p = lambda_val / (0.95 * math.sqrt(k * 20000 / fy_flt))

    if lambda_p < 0.673:
        bef = bf
        yg1 = yg0
    else:
        # 📌 Redução da mesa
        bef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
        lret1 = bf - bef
        Aret1 = t * lret1
        Aef1 = A - Aret1
        d1 = yg0 - (t / 2)
        y1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
        yg1 = yg0 + y1
        ixret1 = ((lret1 * t**3) / 12) + (Aret1 * d1**2)

    return {
        "lambda_p": lambda_p,
        "bef": bef,
        "yg1": yg1,
        "Aef1": Aef1,
        "ixret1": ixret1,
        "lret1": lret1,
        "Aret1": Aret1
    }
