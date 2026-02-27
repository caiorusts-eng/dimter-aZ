import math

def calcular_zprop(t, bf, bw,):
    # 📌 Cálculo das propriedades iniciais da seção
    rm = 1.5 * t
    u1 = 1.571 * rm
    bf = bf - 2 * t
    bm = (bf + 2 * t) - t
    bw = bw - 4 * t
    bwm = bw - t
    yg0 = (bw + 4 * t) / 2
    xg0 = (bf + 1.5 *t)
    A = t * (bw + 2*bf + 2*u1)
    Ix = 2*t * (0.042*bw**3 + bf*(0.5*bw + rm)**2 + 2*u1*(0.5*bw + 0.637*rm)**2 + 0.298*rm**3)
    Wx = Ix/yg0
    Iy = 2*t * (bf*(0.5*bf + rm)**2 + 0.083*bf**3 + 0.505*rm**3 + u1*(bf + 1.637*rm)**2)
    Wy = Iy/xg0
    Ixy = 2*t * (bf*(0.5*bw + rm)*(0.5*bf + rm) + 0.5*rm**3 + 0.285*bw*rm**2 + u1*(bf + 1.637*rm)*(0.5*bw + 0.637*rm))
    I1 = ((Ix + Iy) / 2) + (( (Ix - Iy) / 2)**2 + Ixy**2)**0.5
    I2 = ((Ix + Iy) / 2) - (( (Ix - Iy) / 2)**2 + Ixy**2)**0.5
    J = 0.333*t**3 * (bw + 2 * bf)
    rx = math.sqrt(Ix/A)
    ry = math.sqrt(Iy/A)
    Cw = (t / 12) * ( (bwm**2 * bm**3 * (2*bwm + bm)) / (bwm + 2*bm) )

    perfil_z = {
        "perfil Z": f"{(bw+4*t)*10}x{(bf+2*t)*10}x{10*t:.2f}", # Nome do perfil customizado
        "bw": bw,
        "bf": bf,
        "t": t,
        "rm": rm, "u1": u1, "bf": bf, "bm": bm, "bw": bw, "bwm": bwm, "rx": rx, "ry": ry, 
        "yg0": yg0, "xg0": xg0, "A": A, "Ix": Ix, "Wx": Wx, "Wy": Wy, "Iy": Iy, "I1": I1, "I2": I2, "J": J, "Cw": Cw,
        "m": (A * 7850) / 10000 # Massa em kg/m (densidade do aço ~7850 kg/m³)
    }

    return perfil_z