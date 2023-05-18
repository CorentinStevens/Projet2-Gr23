#
# Ce code à pour objectif de simuler la tension dans le bloc 1,2 et 3 du circuit Projet II - 2022-2023
# Auteurs : Groupe 11.23
#

#Importation des packages
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.signal import argrelextrema
from scipy.optimize import minimize

#Constantes dans le circuit
Vcc = 5.5     #[V] Tension d'alimentation (Nous la mettons à 5.5V car lors des mesures effectués sur notre circuit, nous avons alimenté ce dernier en 5.5V , ceci permet une certaine cohérence pour la vérification des simulations avec la réalité)
C = 0.5 * 10**(-9)    #[F] #Capacité condensateur bloc 1
SlewRate = 7*10**6      #[V/s] #Valeur slew rate des AOP
Rbloc2 = 330            # [Ohm] Valeur de la résistance sur le bloc 2
Lsm = 0.58*10**(-3)     #[H] Inductance équivalente sans métal de la bobine
Lam = 0.56*10**(-3)     #[H] Inductance équivalente avec métal de la bobine
TauBloc3 = 0.1


#Fonctions utiles à la simulation
def deriveeCondensateur(Vcapa,Vout, tau):
    return (Vout-Vcapa)/(tau)

def deriveeBobine(Vl,L,Vbloc1): 
    return (Vbloc1-Vl)*(Rbloc2/L)

#Implémentation de la méthode de runge-kutta
def rungeKutta(V,f,h,param1,param2):
        k1 = h * f(V,param1,param2)
        k2 = h * f(V+k1/2, param1,param2)
        k3 = h * f(V+k2/2, param1,param2)
        k4 = h * f(V+k3, param1,param2)
        k = (k1+2*k2+2*k3+k4)/6
        return k

#Implémentation de la méthode des bissections
def bissect(a,b,f,tol,nmax):
    n = 0; delta = int(round((b-a/2)))
    if (f[a]*f[b] > 0) :
        raise RuntimeError('Bad initial interval') 
    
    while (abs(delta) >= tol and n <= nmax) :
        delta = int(round((b-a)/2)); n = n + 1;
        x = a + delta;
        if (f[x]*f[a] > 0) :
            a = x
        else :
            b = x
    return x

#Simulation du Slew Rate
def SlewRateSimulation(Vtheorique,Vreel,h):
    newVreel = 0
    
    if Vreel<Vtheorique:   #Real < Theorical
        newVreel = Vreel + SlewRate*h
        if Vreel>Vtheorique:
            newVreel = Vtheorique
    elif Vreel>Vtheorique:   #Real > Theorical:
        newVreel = Vreel - SlewRate*h
        if Vreel<Vtheorique:
            newVreel = Vtheorique
    else:
        newVreel = Vreel
    return newVreel

#Simulation globale des trois premiers blocs 
def simulationBlocs123(h,n, Rcapa):
    Vsortiebloc1 = np.zeros((2,n+1)) #Sortie bloc 1 [Real, Theorical]
    Vcapa1 = np.zeros(n+1) #Tension de la capacité sur le premier bloc

    Vam = np.zeros(n+1) #Initialisation tension avec métal de sortie du bloc 2
    Vsm = np.zeros(n+1) #Initialisation tension sans métal de sortie du bloc 2
    
    Vcapa2Sm = np.zeros(n+1) #Tension de la capacité sur le bloc 3, sans métal
    Vcapa2Am = np.zeros(n+1) #Tension de la capacité sur le bloc 3, avec métal
    VsortieAopBloc3Sm = np.zeros((2,n+1)) #Sortie AOP bloc 3 sans métal [Reel, Theorique]
    VsortieAopBloc3Am = np.zeros((2,n+1)) #Sortie AOP bloc 3 avec métal [Reel, Theorique]


    Vam[0], Vsm[0] = 0, 0 #Conditions initiales sur le système
    Vsortiebloc1[:,0] = np.array([Vcc,Vcc]) 
    Inversions = [] #Capture les moments où la tension est inversée sur le bloc 1

    for i in range(n):
        t = i*h

        ##########################
        ##### BLOC 1 #############
        ##########################


        #Simulation sans prise en compte de la tension de sortie du bloc 1
        if Vcapa1[i] >= (Vcc+Vsortiebloc1[0,i])/3:
            Vsortiebloc1[1,i+1] = 0
        else:
            Vsortiebloc1[1,i+1] = Vcc
            if Vsortiebloc1[1,i] == 0:
                Inversions.append(i*h)


        #Prise en compte du slewRate
        Vsortiebloc1[0,i+1] = SlewRateSimulation(Vsortiebloc1[1,i+1],Vsortiebloc1[0,i],h)


        #Simulation de la capa par rungekutta
        Vcapa1[i+1] = Vcapa1[i] +rungeKutta(Vcapa1[i], deriveeCondensateur, h, Vsortiebloc1[0,i],Rcapa*C)


        ##########################
        ##### BLOC 2 #############
        ##########################

        #Simulation de la bobine par euler
        Vsm[i+1] = Vsm[i] + rungeKutta(Vsm[i],deriveeBobine,h,Lsm,Vsortiebloc1[0,i])    #euler explicite sur la tension sans métal
        Vam[i+1] = Vam[i] + rungeKutta(Vam[i],deriveeBobine,h,Lam,Vsortiebloc1[0,i])     #euler explicite sur la tension avec métal




        ##########################
        ##### BLOC 3 #############
        ##########################
        if i*h >= (4 * np.log(3) *Rcapa*C): #On simule pas directement le bloc 3 afin que celui-ci mette moins de temps à converger vers la tension de crête avec décallage réelle (voir plots)
            #Simulation Bloc 3
            #1) Sans métal
            if Vsm[i] > Vcapa2Sm[i]:
                VsortieAopBloc3Sm[0,i+1] = Vcc
            else:
                VsortieAopBloc3Sm[0,i+1] = 0

            VsortieAopBloc3Sm[1,i+1] = SlewRateSimulation(VsortieAopBloc3Sm[0,i+1], VsortieAopBloc3Sm[1,i],h)


            if  -Vcapa2Sm[i] + VsortieAopBloc3Sm[1,i]>0.7:
                Vcapa2Sm[i+1] = Vcapa2Sm[i] +rungeKutta(Vcapa2Sm[i],deriveeCondensateur,h,Vsm[i],0.0000001)
            else:
                Vcapa2Sm[i+1] = Vcapa2Sm[i]  + rungeKutta(Vcapa2Sm[i],deriveeCondensateur,h,0,TauBloc3)

            
            #2) Avec métal
            if Vam[i] > Vcapa2Am[i]:
                    VsortieAopBloc3Am[0,i+1] = Vcc
            else:
                VsortieAopBloc3Am[0,i+1] = 0

            VsortieAopBloc3Am[1,i+1] = SlewRateSimulation(VsortieAopBloc3Am[0,i+1], VsortieAopBloc3Am[1,i],h)


            if  -Vcapa2Am[i] + VsortieAopBloc3Am[1,i]>0.7:
                Vcapa2Am[i+1] = Vam[i]
            else:
                Vcapa2Am[i+1] = Vcapa2Am[i] + rungeKutta(Vcapa2Am[i],deriveeCondensateur,h,0,TauBloc3)

    return Vsortiebloc1[0,:], Vsm, Vam, Vcapa2Sm, Vcapa2Am, Inversions, VsortieAopBloc3Sm[1,:]



#Appel de la fonction et plots en tout genre

h  = 50* 10**(-10)
n = 15 * 10**5
def toMinimize(x):
    Vb2sm,Vb2am, V1,V2 = simulationBlocs123(h,n,x)[1:5]
    return abs(np.mean(V1[-int(n/10):]) - np.mean(V2[-int(n/10):])), Vb2sm[argrelextrema(Vb2sm,np.greater)[0][-1]], Vb2am[argrelextrema(Vb2am,np.greater)[0][-1]]

#min = minimize(toMinimize,10*10**3,method='nelder-mead',options={'maxiter':50})
Rcapa = 1 * 10**3
#print(min)
Vb1,Vsm,Vam,V3sm,V3am,I,AOP = simulationBlocs123(h,n,Rcapa)

MaxLocVsm = Vsm[argrelextrema(Vsm,np.greater)[0][-1]]
MaxLocVam = Vam[argrelextrema(Vam,np.greater)[0][-1]]
#print(MaxLocVam,MaxLocVsm) 
#print(toMinimize(Rcapa))

t = np.linspace(0,h*n, num=n+1)
plt.plot(t,Vsm,color="red", label="Sortie Bloc 2")
plt.plot(t, V3sm,color="orange", label="Sortie Bloc 3")
#plt.plot(t, AOP,color="green", label="Sortie AOP")
plt.legend()
plt.show()

h  = 50* 10**(-10)
n = 15 * 10**5
def PlotDifferenceEnFontiondDeR():
    #R simulation
    Rsimulation = np.array(range(1,51)) * 300

    #Frequence simulation
    frequence = np.empty_like(Rsimulation, dtype=float)
    
    #Bloc 2
    V2smMaxs = np.empty_like(Rsimulation,dtype=float)
    V2amMaxs = np.empty_like(Rsimulation,dtype=float)

    #Bloc 3
    V3sm,V3am = np.empty_like(Rsimulation,dtype=float), np.empty_like(Rsimulation,dtype=float)

    #Comparaison experimentales
    Rexp = np.array([3,4,5,6,7.5,10,25]) * 10**3

    Fexp = np.array([274.6, 227.6,194,172.2, 146.1, 116.8, 53.4]) * 10**3

    Vsm2exp = np.array([3.8,3.896,4.15,4.35,4.58,4.85,5.407])
    Vam2exp = np.array([3.94,4.034,4.3,4.444,4.67,4.95,5.498])

    Vsm3exp = np.array([3.48,3.5,3.70,3.78,3.88,4.01,4.34])
    Vam3exp = np.array([3.52,3.55,3.75,3.835,3.92, 4.035,4.35])

    for i in tqdm(range(len(Rsimulation))):
        SimulationResult = simulationBlocs123(h,n,Rsimulation[i])
        frequence[i] = 1 / (np.diff(np.array(SimulationResult[5])))[-1]

        V2smMaxs[i] = SimulationResult[1][argrelextrema(SimulationResult[1],np.greater)[0][-1]]
        V2amMaxs[i] = SimulationResult[2][argrelextrema(SimulationResult[2],np.greater)[0][-1]]

        V3sm[i], V3am[i] = np.mean(SimulationResult[3][-int(n/10):]), np.mean(SimulationResult[4][-int(n/10):])

    #Calcul derivée de l'erreur sur le bloc 2 

    dErrorBloc2 = np.diff(V2amMaxs - V2smMaxs)/25

    optimisationB2 = bissect(5,len(Rsimulation)-5, dErrorBloc2,0.000001,100000)

    print(Rsimulation[optimisationB2])
    print((V2amMaxs - V2smMaxs)[optimisationB2])
    

    #Plot Frequences Bloc 1
    plt.plot(Rsimulation, 1/(2*np.log(2)*Rsimulation*C))
    plt.plot(Rsimulation, frequence,color="red")
    plt.scatter(Rexp,Fexp)
    plt.show()

    #Plot Sortie Bloc 2
    plt.plot(Rsimulation, V2smMaxs,color="green", label="Tension de crête bloc 2 sans métal - simulation")
    plt.plot(Rsimulation, V2amMaxs,color="blue", label="Tension de crête bloc 2 avec métal - simulation")
    
    plt.scatter(Rexp, Vsm2exp, color="green", label="Tension de crête bloc 2 sans métal - labo")
    plt.scatter(Rexp, Vam2exp, color="blue", label="Tension de crête bloc 2 avec métal - labo")
    plt.xlabel("Résistance bloc 1 [Ohm]")
    plt.ylabel("Tension de crête [V]")
    plt.legend()
    plt.show()


    #Plot ecarts bloc 2
    plt.plot(Rsimulation, V2amMaxs-V2smMaxs, label="Différence tension de crête bloc 2 - simulation")
    plt.scatter(Rexp, Vam2exp-Vsm2exp, label="Différence tension de crête bloc 2 - labo")
    plt.xlabel("Résistance bloc 1 [Ohm]")
    plt.ylabel("Différence tension de crête [V]")
    plt.legend()
    plt.show()

    #plot sortie bloc 3
    plt.plot(Rsimulation, V3sm, label="Sortie bloc 3 sans métal - simulation")
    plt.plot(Rsimulation, V3am, label="Sortie bloc 3 avec métal - simulation")

    plt.scatter(Rexp,Vsm3exp, label="Sortie bloc 3 sans métal - labo")
    plt.scatter(Rexp,Vam3exp, label="Sortie bloc 3 avec métal - labo")
    plt.xlabel("Résistance bloc 1 [Ohm]")
    plt.ylabel("Tension bloc 3 [V]")
    plt.legend()
    plt.show()

    #differences bloc 3
    plt.plot(Rsimulation, V3am-V3sm,label="Différence tension sortie bloc 3 - simulation")
    plt.scatter(Rexp,Vam3exp-Vsm3exp, label="Différence tension sortie bloc 3 - labo")
    plt.xlabel("Résistance bloc 1 [Ohm]")
    plt.ylabel("Différence tension bloc 3 [V]")
    plt.legend()
    plt.show()


