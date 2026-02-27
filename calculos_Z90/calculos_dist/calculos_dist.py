import math

def calcular_dist(perfil, fy):
    
    Mdist_x = perfil["Mdist_x"] 
    Wx = perfil ["Wx"]

    lambda_dist = math.sqrt(Wx * fy /(Mdist_x))

    if lambda_dist < 0.673:
        Mrd_x_dist = Wx * fy /1.1
    else:
        Mrd_x_dist = (1- (0.22/lambda_dist)) * Wx * fy /(1.1 *lambda_dist)

    return Mrd_x_dist
