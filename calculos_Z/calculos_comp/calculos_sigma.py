import math

def calcular_sigma(perfil_z, fy, Lx, Ly, Lz):
    # Propriedades do perfil necessárias
    I1 = perfil_z["I1"]
    I2 = perfil_z["I2"]
    J = perfil_z["J"]
    Cw = perfil_z["Cw"]
    bf = perfil_z["bf"]
    bw = perfil_z["bw"]
    t = perfil_z["t"]
    A = perfil_z["A"]
    rx=perfil_z["rx"]
    ry=perfil_z["ry"]


    # 📌 Cálculo das propriedades iniciais da seção
    r0 = float(math.sqrt(rx**2 + ry**2))

    # 📌 Cálculo das cargas críticas de Euler
    Nex_c = float(((math.pi ** 2) * 20000 * I1) / (Lx ** 2))
    Ney_c = float((math.pi ** 2) * 20000 * I2 / (Ly ** 2))
    Nez_c = float((1 / r0**2) * ((((math.pi ** 2) * 20000 * Cw) / (Lz ** 2)) + 7700 * J))
    Ne_c = min(Nex_c, Ney_c, Nez_c)

    # 📌 Cálculo da tensão de trabalho para compressão
    lambdac0= math.sqrt(A*fy/Ne_c)
    if lambdac0<=1.5:
        x = 0.658**(lambdac0**2)
    else:
        x = 0.877 / (lambdac0**2)
    sigma = x*fy

    return{
    "Nex":Nex_c,
    "Ney" : Ney_c,
    "Nez" : Nez_c,
    "lambda" : lambdac0,
    "x" : x,
    "sigma": sigma
    }

    


