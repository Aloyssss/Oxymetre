#!/usr/bin/python
# -*- coding: utf-8 -*-

"""    IMPORTS    """
import spidev
import threading
import time
from collections import deque
from gpiozero import LED

"""    VARIABLES GLOBALES    """
DEQUE_MAX_LEN = 100
SPI_BUS = 0
SPI_DEVICE = 0
SPI_MAX_SPEED = 100000
LED_GPIO_PIN = 2

"""    CLASSE    """
class Adc:
    """
    Classe pour l'acquisition de données d'un ADC via SPI.

    ATTRIBUTS:
        Te (float): Période d'échantillonnage en secondes.
        R_values (deque): File d'attente pour stocker les valeurs mesurées du canal R.
        IR_values (deque): File d'attente pour stocker les valeurs mesurées du canal IR.
        thread (Thread): Thread pour l'acquisition de données en continu.
        is_running (bool): flag de la boucle d'echantillonnage
        spi_bus: Interface pour le bus SPI.
        rir_led: Interface pour le controle de la LED du capteur.
    """
    
    def __init__(self, fs: int) -> None:
        """
        Initialise une instance de la classe Adc avec une fréquence d'échantillonnage spécifiée.

        Args:
            fs (float): Fréquence d'échantillonnage en Hz. Par défaut, 25 Hz.
        """
        self.Te: float = 1/fs
        self.R_values = deque(maxlen=DEQUE_MAX_LEN)
        self.IR_values = deque(maxlen=DEQUE_MAX_LEN)
        self.thread = None
        self.is_running = False
        self.spi_bus = None
        self.rir_led = None
        self.spi_init()
        self.rir_init()

    def spi_init(self) -> None:
        """
        Initialise l'interface du bus SPI pour la communication avec le convertisseur ADC.

        Raises:
            Exception: Si une erreur survient lors de l'initialisation du bus SPI.
        """
        try:
            self.spi_bus = spidev.SpiDev()
            self.spi_bus.open(0, 0)
            self.spi_bus.max_speed_hz = 100000
        except Exception as e:
            print("Erreur initialisation bus spi : ", e)
        
    def rir_init(self) -> None:
        """
        Initialise la sortie GPIO pour le controle de la LED du capteur

        Raises:
            Exception: Si une erreur survient lors de l'initialisation de la LED.
        """
        try:
            self.rir_led = LED(LED_GPIO_PIN)
            self.rir_led.off()
        except Exception as e:
            print("Erreur initialisation gpio : ", e)
   
    def read_adc(self) -> float:
        """
        Lit les valeurs de tension du convertisseur analogique-numérique (ADC).

        Returns:
            float: La valeur de tension mesurée en volts, ou None en cas d'erreur de lecture.
        """
        try:
            r = self.spi_bus.xfer2([6, 0, 0])
            d = (r[1] << 8) + r[2]
            u = d*5/4095
            return u
        except Exception as e:
            print("Erreur lecture adc : ", e)
            return None
    
    def sample(self) -> None:
        """
        Méthode exécutée en boucle pour l'acquisition de données en continu.

        Cette méthode lit les valeurs du canal R et du canal IR de manière alternative,
        puis les stocke dans les filet d'attente correspondants.
        """
        while(self.is_running):
            self.rir_led.on()
            self.R_values.append(self.read_adc())
            self.rir_led.off()
            self.IR_values.append(self.read_adc())
            time.sleep(self.Te)

    def start_sampling(self) -> None:
        """
        Démarre l'acquisition de données en continu.

        Raises:
            Exception: Si une erreur survient lors du démarrage du thread pour l'échantillonnage.
        """
        try:
            self.is_running = True
            self.thread = threading.Thread(target=self.sample)
            self.thread.start()
        except Exception as e:
            print("Erreur démarrage thread sampling : ", e)

    def stop_sampling(self) -> None:
        """
        Arrête l'acquisition de données en continu.

        Cette méthode arrête le thread en cours d'exécution pour l'échantillonnage,
        si un tel thread est actif.
        """
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()



    

    

