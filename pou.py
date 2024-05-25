#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from scipy.signal import find_peaks
from threading import Thread
from time import sleep
from collections import deque
from adc import *

DEQUE_MAX_LEN = 100

class Pou:
    """
    Classe pour le calcul du pouls à partir des données reçues par l'ADC

    ATTRIBUTS:
        data (deque): file d'attente des données d'oxymétrie
        Tcalcul (int): interval de rafraichissement du pouls
        is_running (bool): flag de la boucle de calcul
        fs (int): frequence d'ehcnationnage des donnees
        thread (Thread): thread de calcul du pouls en continu
    """
    
    def __init__(self, fs: int=25, interval_calcul: int=1, data=deque(maxlen=DEQUE_MAX_LEN)):
        """
        Initialise une instance de la classe Pou avec une periode de rafraichissement

        Args:
            fs (int): Fréquence d'échantillonnage en Hz. Par défaut, 25 Hz.
            interval_calcul (int): Periode de raifraichissement du pouls
            data (deque): file d'attente des donnees echantillonnees
        """
        self.data = data
        self.Tcalcul = interval_calcul
        self.is_running = False
        self.fs = fs
        self.thread = None

    def find_pouls(self) -> None:
        """
        Boucle de calcul du pouls.
        Cette methode detecte les pics dans les données echantillonnees et en deduit le pouls

        Raises:
            Exception si une erreur survient pendant le calcul du pouls
        """
        try:
            while self.is_running:
                if len(self.data) >= self.fs:
                    data = np.array(self.data) - np.mean(self.data)
                    acf = np.correlate(data, data, mode="full")[len(data)-1:]
                    peaks, _ = find_peaks(acf, height=0)
                    if peaks.size > 0:
                        pulse_rate = 1 / (peaks[0] / self.fs) * 60
                        print("Pulse Rate:", pulse_rate)
                else:
                    print("En attente de donnees")
                sleep(self.Tcalcul)
        except Exception as e:
            print("Error calculating pulse rate:", e)
   
    def start_processing(self) -> None:
        """
        Démarre le calcul du pouls en continu.

        Raises:
            Exception: Si une erreur survient lors du démarrage du thread.
        """
        try:
            self.is_running = True
            self.thread = Thread(target=self.find_pouls)
            self.thread.start()
        except Exception as e:
            print("Erreur démarrage thread sampling : ", e)

    def stop_processing(self) -> None:
        """
        Arrête le calcul du pouls en continu

        Cette méthode arrête le thread en cours d'exécution pour le calcul du pouls,
        si un tel thread est actif.
        """
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()

