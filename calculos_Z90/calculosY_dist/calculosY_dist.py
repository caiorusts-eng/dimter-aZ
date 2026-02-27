import math

def calcularY_dist(perfil, fy):
    
    Mdist_y = perfil["Mdist_y"] 
    Wy = perfil ["Wy"]

    lambda_dist = math.sqrt(Wy * fy /(Mdist_y))

    if lambda_dist < 0.673:
        Mrd_y_dist = Wy * fy /1.1
    else:
        Mrd_y_dist = (1- (0.22/lambda_dist)) * Wy * fy /(1.1 *lambda_dist)

    return Mrd_y_dist
