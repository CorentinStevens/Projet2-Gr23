# Projet II - Annexes codes

* *OptimisationAnalytique.py* : Implémentation de la méthode des bissections pour la résolution de l'équation non-linéaire dans le cadre de l'optimisation analytique des trois premiers blocs. L'équation résolue est la suivante :
<img src="https://latex.codecogs.com/gif.latex?\frac{-exp(\frac{-1}{2f\tau_{AvecMetal}})}{2f^2\tau_{AvecMetal}(1+exp(\frac{-1}{2f\tau_{AvecMetal}}))^{2}}%20+%20\frac{exp(\frac{-1}{2f\tau_{SansMetal}})}{2f^2\tau_{SansMetal}(1+exp(\frac{-1}{2f\tau_{SansMetal}}))^{2}}=0" /> 
* *SimulationsBloc1-2-3.py* : Implémentation de la méthode de Runge-Kutta, afin de simuler les trois premiers blocs, et d'optimiser ces derniers en prenant compte du slew rate sur les AOP.

* *Projet_II_Gr11-23_Arduino.ino* : Code arduino pour la gestion de notre application
