#
# Ce code à pour objectif de résoudre l'équation non linéaire mentionnée dans le rapport
# Auteurs : Groupe 11.23
#

#Importation des packages
import math
import matplotlib.pyplot as plt
import numpy as np

#Paramètres
TauSm = 1.75757575 * 10**(-6)
TauAm = 1.6969 * 10 **(-6)

#Implémentation de la méthode des bissections (source : https://perso.uclouvain.be/vincent.legat/zouLab/util/zouShowCode.php?filename=cours10/bissection.py&cours=epl1104&action=codes&message=bissection.py)
def bissect(a,b,f,tol,nmax):
    n = 0; delta = (b-a)/2
    if (f(a)*f(b) > 0) :
        raise RuntimeError('Bad initial interval') 
 
    while (abs(delta) >= tol and n <= nmax) :
        delta = (b-a)/2; n = n + 1;
        x = a + delta;
        print(" x = %14.7e (Estimated error %13.7e at iteration %d)" % (x,abs(delta),n))
        if (f(x)*f(a) > 0) :
            a = x
        else :
            b = x
    if (n > nmax) :
        raise RuntimeError('Too much iterations') 
    return x

def toSolve(f): #Problème à résoudre
    return -(math.e**((-1)/(2*f*TauAm)))/((2*f**2*TauAm)*(1+math.e**((-1)/(2*f*TauAm)))**2) + (math.e**((-1)/(2*f*TauSm)))/((2*f**2*TauSm)*(1+math.e**((-1)/(2*f*TauSm)))**2)

def diff(f): #Fonction à optimiser
    return 6*((1/(1+math.e**(-1/(2*f*TauAm)))) - (1/(1+math.e**(-1/(2*f*TauSm)))))

print(bissect(10000 , 250000,toSolve,0.01,10000))

f = np.linspace(10 * 10**3,250 * 10**3,10000)
plt.plot(f, diff(f), label="Différence crêtes bloc 2")
plt.legend()
plt.xlabel("Frequence [Hz]")
plt.ylabel("Tension [V]")
plt.show()

