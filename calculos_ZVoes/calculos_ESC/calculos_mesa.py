import math

def calcular_mesa(perfil, fy, yg1):
    """Calcula as propriedades efetivas da mesa no método ESC."""

    D = perfil["D"]
    bf = perfil["bf"]
    bw = perfil["bw"]
    t = perfil["t"]

    # 📌 Cálculo das propriedades iniciais da seção
    d = D - 2 * t
    bf = bf - 4 * t
    bw = bw - 4 * t
    yg0 = yg1  # 🔹 Agora usamos `yg1` vindo do enrijecedor

    # 📌 Cálculo de lambda
    lambda_val = bf / t
    lambda_p0 = lambda_val / (0.623 * math.sqrt(20000 / fy))

    # 📌 Definir variáveis para evitar erros
    Is = None  
    Ia = None  
    yg2 = yg0  # 🔹 Definir `yg2` com um valor padrão (antes de possíveis cálculos)
    ixret2 = None
    Aef2 = perfil["A"]  # 🔹 Agora Aef2 começa com o valor da área bruta para evitar None
    lambda_p = None  # 🔹 Agora `lambda_p` sempre é definido

    if lambda_p0 < 0.673:
        bef = bf
        def_efetiva = d
    else:
        # 📌 Cálculo de Ia e Is
        Ia = min((399 * (t ** 4) * (((0.487 * lambda_p0) - 0.328) ** 3)), (t ** 4 * (56 * lambda_p0 + 5)))
        Is = (t * (d ** 3)) / 12

        # 📌 Cálculo de n e razão i/i
        n = max((0.582 - 0.122 * lambda_p0), (1 / 3))
        razao_ii = min((Is / Ia), 1)

        # 📌 Cálculo do fator k
        D_bf_ratio = D / bf
        if D_bf_ratio <= 0.25:
            k = min((3.57 * (razao_ii ** n) + 0.43), 4)
        elif 0.25 < D_bf_ratio < 0.8:
            k = min(((4.82 - 5 * D_bf_ratio) * (razao_ii ** n) + 0.43), 4)
        else:
            k = 4  

        lambda_p = lambda_val / (0.95 * math.sqrt(k * 20000 / fy))  # 🔹 Agora sempre será definido

        if lambda_p < 0.673:
            bef = bf
            # 📌 Cálculo do enrijecedor efetivo
            def_efetiva = razao_ii * d
            lret1 = d - def_efetiva
            Aret1 = t * lret1
            Aef1 = perfil["A"] - Aret1
            d1 = yg0 - (lret1/2+def_efetiva+2*t)
            y1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
            yg1 = yg0 + y1
            ixret2 = ((t * (lret1 ** 3)) / 12) + (Aret1 * (d1 ** 2))
            yg2=yg1
        else:
            # 📌 Cálculo do enrijecedor efetivo
            def_efetiva = (d * (1 - (0.22 / lambda_p)) * (1 / lambda_p)) * razao_ii
            lret1 = d - def_efetiva
            Aret1 = t * lret1
            Aef1 = perfil["A"] - Aret1
            d1 = yg0 - (lret1/2+def_efetiva+2*t)
            y1 = (d1 * Aret1) / Aef1 if Aef1 != 0 else 0
            yg1 = yg0 + y1
            ixret1 = ((t * (lret1 ** 3)) / 12) + (Aret1 * (d1 ** 2))

            # 📌 Cálculo da mesa efetiva
            bef = bf * (1 - (0.22 / lambda_p)) * (1 / lambda_p)
            bef1 = razao_ii * (bef / 2)
            bef2 = bef - bef1
            lret2 = bf - bef
            Aret2 = t * lret2
            Aef2 = Aef1 - Aret2  # 🔹 Garantimos que Aef2 seja sempre definido
            d2 = yg1 - (t / 2)
            y2 = (d2 * Aret2) / Aef2 if Aef2 != 0 else 0
            yg2 = yg1 + y2  # 🔹 Agora `yg2` sempre será definido
            ixret2 = ixret1 + ((lret2 * (t ** 3)) / 12) + (Aret2 * (d2 ** 2))

    return {
    "lambda_p": lambda_p,
    "bef": bef,
    "def_efetiva": def_efetiva,
    "yg2": yg2,
    "Aef2": Aef2,
    "ixret2": ixret2 if ixret2 is not None else 0  # 🔹 Adicionando sempre um valor válido
}

