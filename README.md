---
title: Oxymétrie de pouls sur Raspberry Pi
author: Aloys Réant, Baptiste Millet
---

# Note d'application : Oxymétrie de pouls sur Raspberry Pi
## Présentation générale
Le but de ce projet est de concevoir un programme capable d’échantillonner, de traiter et d’afficher des données d’oxymétrie. Pour achever ceci, le programme utilise plusieurs threads. Chaque thread est dédié à une tâche. Le projet ne comporte qu’un script et 4 classes.

## Matériel utilisé
* Capteur d'oxymétrie
* Carte d'acquisition comportant un filtre et un amplificateur
* Convertisseur analogique numérique MCP3204
* Raspberry Pi 3

## Description du logiciel
### `main.py`
Le fichier `main.py` coordonne l'acquisition des données, le calcul de la fréquence cardiaque, le calcul de la saturation en oxygène et l'affichage graphique en utilisant les classes définies dans les fichiers `adc.py`, `pou.py`, `oxy.py`, et `gui.py`.

#### Dépendances : 
- `Adc` : Classe pour l'acquisition de données d'un ADC via SPI.
- `Pou` : Classe pour le calcul de la fréquence cardiaque à partir des données d'oxymétrie.
- `Oxy` : Classe pour le calcul de la saturation en oxygène à partir des données de l'ADC.
- `Gui` : Classe pour l'interface graphique utilisant DearPyGui pour afficher les données.

#### Constantes : 
`Fs` : Fréquence d'échantillonnage en Hz (10 Hz par défaut).

#### `main() -> None`
La fonction `main()` initialise et coordonne l'exécution des différentes tâches. Elle suit les étapes suivantes :
* Création des instances des classes pour l'acquisition de données, le traitement du pouls, la mesure de l'oxygène et l'affichage graphique.
* Démarrage des tâches d'acquisition de données, de traitement et d'affichage en parallèle.
* Initialisation de l'interface graphique et démarrage de l'affichage en temps réel.
* Arrêt ordonné des tâches après la fermeture de l'interface graphique.

### `adc.py`
Ce script Python est conçu pour l'acquisition de données à partir d'un convertisseur analogique-numérique (ADC) via le protocole Serial Peripheral Interface (SPI) sur un Raspberry Pi. Il utilise la bibliothèque `spidev` pour la communication SPI et la bibliothèque `threading` pour l'exécution concurrente de tâches.

#### Dépendances : 
- `spidev`: Utilisé pour la communication SPI avec l'ADC.
- `threading`: Utilisé pour exécuter des tâches en arrière-plan.
- `time`: Utilisé pour créer des pauses dans le traitement des données.
- `collections.deque`: Utilisé pour stocker les données de manière efficace dans des files (deques).
- `gpiozero.LED`: Utilisé pour contrôler une LED via GPIO.

#### Constantes : 
* `DEQUE_MAX_LEN` : Longueur maximale des files d'attente pour stocker les valeurs mesurées.
* `SPI_BUS` : Numéro du bus SPI.
* `SPI_DEVICE` : Numéro du périphérique SPI.
* `SPI_MAX_SPEED` : Vitesse maximale du bus SPI.
* `LED_GPIO_PIN` : Numéro du GPIO utilisé pour contrôler la LED du capteur.

#### Classe `Adc` : 
La classe `Adc` encapsule les fonctionnalités liées à l'acquisition de données ADC.

##### Attributs

- `Te` (float): Période d'échantillonnage en secondes.
- `R_values` (deque): File d'attente pour stocker les valeurs mesurées du canal R.
- `IR_values` (deque): File d'attente pour stocker les valeurs mesurées du canal IR.
- `thread` (Thread): Thread pour l'acquisition de données en continu.
- `is_running` (bool): Drapeau indiquant si le thread d'échantillonnage est en cours d'exécution.
- `spi_bus`: Interface pour le bus SPI.
- `rir_led`: Interface pour le contrôle de la LED du capteur.

##### Méthodes

`__init__(self, fs: int) -> None`
Le constructeur initialise les attributs de la classe avec la fréquence d'échantillonnage spécifiée, les files d'attente pour les données, et initialise les interfaces SPI et GPIO.

`spi_init(self) -> None`
Cette méthode initialise l'interface du bus SPI pour la communication avec le convertisseur ADC MCP3204. En cas d'erreur, elle affiche un message d'erreur.

`rir_init(self) -> None`
Cette méthode initialise la sortie GPIO pour le contrôle de la LED du capteur. En cas d'erreur, elle affiche un message d'erreur.

`read_adc(self) -> float`
Cette méthode lit les valeurs de tension du convertisseur ADC via SPI et les convertit en volts. En cas d'erreur, elle affiche un message d'erreur et retourne `None`.

`sample(self) -> None`
Méthode pour l'acquisition de données en continu. Cette méthode lit les valeurs du canal R et du canal IR alternativement, puis les stocke dans la file d'attente correspondante.

`start_sampling(self) -> None`
Cette méthode démarre un thread qui exécute la méthode `sample`. Elle initialise `is_running` à `True` et crée un nouveau thread. En cas d'erreur, elle affiche un message d'erreur.

`stop_sampling(self) -> None`
Cette méthode arrête le thread d'échantillonnage en définissant `is_running` à `False` et en rejoignant le thread pour s'assurer qu'il s'arrête correctement.

#### Utilisation : 
Pour utiliser cette classe, vous devez suivre les étapes suivantes :

```python
    from adc import Adc 
    # Créer une instance de la classe Adc avec une fréquence d'échantillonnage de 25 Hz 
    adc = Adc(fs=25) 
    # Démarrer l'acquisition de données 
    adc.start_sampling() 
    # Attendre un certain temps pour acquérir des données (ex: 10 secondes) 
    time.sleep(10) 
    # Arrêter l'acquisition de données 
    adc.stop_sampling() 
    # Afficher les valeurs acquises  
    print("R_values:", list(adc.R_values)) 
    print("IR_values:", list(adc.IR_values))
```

### `pou.py`
Ce script Python est conçu pour calculer le pouls à partir de données oxymétriques acquises par un ADC. Il utilise des méthodes de traitement du signal pour détecter les pics dans les données et déduire le rythme cardiaque.

#### Dépendances : 
-   `numpy`: Utilisé pour les calculs numériques, comme la moyenne et l'autocorrélation des données.
-   `scipy.signal.find_peaks`: Utilisé pour détecter les pics dans les données.
-   `threading.Thread`: Utilisé pour exécuter des tâches en arrière-plan.
-   `time.sleep`: Utilisé pour créer des pauses dans le traitement des données.
-   `collections.deque`: Utilisé pour stocker les données de manière efficace dans des files (deques).
-   `adc`: Importé pour les données provenant du convertisseur analogique-numérique (ce fichier est présumé exister).

#### Constantes : 
`DEQUE_MAX_LEN` : Longueur maximale de la file d'attente pour stocker les données oxymétriques.

#### Classe `Pou` :
La classe `Pou` encapsule les fonctionnalités de calcul du pouls.

##### Attributs : 
- `data` (deque): File d'attente pour stocker les données d'oxymétrie.
- `Tcalcul` (int): Intervalle de temps entre les calculs du pouls.
- `is_running` (bool): Drapeau indiquant si le thread de traitement est en cours d'exécution.
- `fs` (int): Fréquence d'échantillonnage des données.
- `thread` (Thread): Thread pour le traitement continu des données et le calcul du pouls.

##### Méthode : 
`__init__(self, fs: int=25, interval_calcul: int=1, data=deque(maxlen=DEQUE_MAX_LEN)) -> None`
Le constructeur initialise les attributs de la classe avec la fréquence d'échantillonnage, l'intervalle de calcul et la file pour les données d'oxymétrie.

`find_pouls(self) -> None`
Cette méthode calcule le pouls en continu tant que `is_running` est `True`. Les étapes de calcul incluent :

1.  Vérification que la file de données contient suffisamment de données.
2.  Calcul de la moyenne et de l'autocorrélation des données.
3.  Détection des pics dans l'autocorrélation.
4.  Calcul du pouls à partir des pics détectés.
5.  Affichage de la valeur du pouls ou d'un message d'attente de données.

En cas d'erreur, elle affiche un message d'erreur.

`start_processing(self) -> None`
Cette méthode démarre un thread qui exécute la méthode `find_pouls`. Elle initialise `is_running` à `True` et crée un nouveau thread.

`stop_processing(self) -> None`
Cette méthode arrête le thread de traitement en définissant `is_running` à `False` et en rejoignant le thread pour s'assurer qu'il s'arrête correctement.

#### Utilisation : 
Pour utiliser cette classe, vous devez suivre les étapes suivantes :

```python
    from pou import Pou 
    # Créer une instance de la classe 
    Pou pou = Pou() 
    # Démarrer le traitement des données 
    pou.start_processing() 
    # Ajouter des données d'exemple (simulées ici pour illustration)  
    import random 
    for _ in  range(100): 
	    pou.data.append(random.uniform(0.9, 1.1)) 
	    sleep(0.04) # Simuler un intervalle de temps entre les échantillons  
	# Arrêter le traitement des données 
	pou.stop_processing()
```

### `oxy.py`
Ce script Python est conçu pour calculer la saturation en oxygène (SpO2) à partir des données capturées par un capteur physiologique connecté à un Raspberry Pi. Il utilise les valeurs mesurées des canaux R (rouge) et IR (infrarouge) provenant du capteur pour estimer la SpO2 à l'aide d'algorithmes de traitement de signal.

#### Dépendances : 
- `threading.Thread`: Utilisé pour exécuter des tâches en arrière-plan.
- `numpy`: Utilisé pour les calculs statistiques sur les données.
- `time.sleep`: Utilisé pour créer des pauses dans le traitement des données.
- `collections.deque`: Utilisé pour stocker les données de manière efficace dans des files (deques).

#### Constantes : 
`fs` : Fréquence d'échantillonnage des données oxymétriques en Hz.

#### Classe `Oxy` : 
La classe `Oxy` encapsule les fonctionnalités de calcul de la SpO2.

##### Attributs : 
* `R_values` : File d'attente pour stocker les valeurs mesurées du canal R.
* `IR_values` : File d'attente pour stocker les valeurs mesurées du canal IR.
* `Tcalcul` : Période de rafraîchissement du calcul de la SpO2.
* `is_running` : Indicateur pour la boucle de calcul.
* `thread` : Thread pour le calcul de la SpO2 en continu.
* `fs` : Fréquence d'échantillonnage des données ADC.

##### Méthodes : 
`__init__(self, R_values=deque(maxlen=DEQUE_MAX_LEN), IR_values=deque(maxlen=DEQUE_MAX_LEN), fs=25, interval_calcul=1) -> None`
Le constructeur initialise les attributs de la classe avec les files pour les valeurs R et IR, la fréquence d'échantillonnage et l'intervalle de calcul.

`find_spo2(self) -> None`
Cette méthode calcule la SpO2 en continu tant que `is_running` est `True`. Les étapes de calcul incluent :

1.  Vérification que les files R et IR contiennent suffisamment de données.
2.  Calcul des valeurs moyennes, des amplitudes AC et des ratios R/IR.
3.  Calcul de la SpO2 à partir des ratios.
4.  Affichage de la valeur de SpO2 ou d'un message d'attente de données.
5.  Pause de la durée de `Tcalcul`.

En cas d'erreur, elle affiche un message d'erreur.

`start_processing(self) -> None`
Cette méthode démarre un thread qui exécute la méthode `find_spo2`. Elle initialise `is_running` à `True` et crée un nouveau thread.

`stop_processing(self) -> None`
Cette méthode arrête le thread de traitement en définissant `is_running` à `False` et en rejoignant le thread pour s'assurer qu'il s'arrête correctement.

#### Utilisation : 
Le code suivant est un exemple d'utilisation de la classe `Oxy.py` : 

```python
    # Créer une instance de la classe 
    Oxy oxy = Oxy() 
    # Démarrer le traitement des données 
    oxy.start_processing() 
    # Ajouter des données d'exemple (simulées ici pour illustration)  
    import random 
    for _ in  range(100): 
	    oxy.R_values.append(random.uniform(0.9, 1.1)) 
	    oxy.IR_values.append(random.uniform(0.8, 1.2)) 
	    sleep(0.04) # Simuler un intervalle de temps entre les échantillons  
	# Arrêter le traitement des données 
	oxy.stop_processing()
```

### `gui.py`
Le fichier `gui.py` contient une classe `Gui` qui utilise la bibliothèque `dearpygui` pour créer une interface graphique permettant de visualiser des données en temps réel. Cette documentation détaille chaque composant de la classe `Gui`, ses méthodes et son utilisation.

#### Dépendances :
Le fichier `gui.py` dépend des bibliothèques suivantes :

- `dearpygui.dearpygui` : Utilisé pour créer et gérer l'interface graphique.
- `time` : Utilisé pour obtenir l'heure actuelle.
- `collections.deque` : Utilisé pour stocker les données de manière efficace.

#### Constantes : 
- `DEQUE_MAX_LEN` définit la taille maximale des deques `data_x` et `data_y`, limitant ainsi le nombre de points stockés pour l'affichage.

#### Classe `Gui` :
La classe `Gui` encapsule les fonctionnalités d'affichage.

##### Attributs : 
- `start_button`: Booléen indiquant si le bouton de démarrage est activé ou désactivé.
- `data_y`: File (deque) pour stocker les données de l'axe Y.
- `data_x`: File (deque) pour stocker les données de l'axe X.

##### Méthode : 
`__init__(self, data_y=deque(maxlen=DEQUE_MAX_LEN), data_x=deque(maxlen=DEQUE_MAX_LEN)) -> None`
Le constructeur initialise les attributs de la classe et crée le contexte Dear PyGui.

`__del__(self) -> None`
Le destructeur détruit le contexte Dear PyGui et affiche la fenêtre de débogage.

`toggle_button(self, sender, data) -> None`
Cette méthode est appelée lorsqu'on clique sur le bouton de démarrage/arrêt. Elle bascule l'état du bouton et met à jour son étiquette en conséquence.

`update_plot(self) -> None`
Cette méthode met à jour le graphique avec les nouvelles données des axes X et Y. Si la case à cocher "Auto-fit x-axis limits" est activée, elle ajuste les limites de l'axe X pour s'adapter aux nouvelles données.

`init_window(self) -> None`
Cette méthode initialise la fenêtre de l'interface graphique. Elle crée un bouton de démarrage/arrêt, un graphique et une case à cocher pour l'ajustement automatique des limites de l'axe X.

`start_render(self) -> None`
Cette méthode démarre la boucle de rendu Dear PyGui. Tant que Dear PyGui est en cours d'exécution, elle ajoute les nouvelles données de temps aux axes X et Y et met à jour le graphique si le bouton de démarrage est activé.

#### Utilisation : 
Voici un exemple d'utilisation de la classe `Gui.py` : 

```python
    from gui import Gui 
    # Créer une instance de la classe 
    Gui gui = Gui() 
    # Initialiser la fenêtre 
    gui.init_window() 
    # Démarrer la boucle de rendu 
    gui.start_render()
```
