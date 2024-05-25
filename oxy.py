#!/usr/bin/python
# -*- coding: utf-8 -*-

"""    IMPORTS    """
from threading import Thread
import numpy as np
from time import sleep
from collections import deque

"""    VARIABLES GLOBALES    """
DEQUE_MAX_LEN = 100

"""    CLASSE    """
class Oxy:
    """
    Classe pour le calcul du pouls à partir des données de l'adc

    ATTRIBUTS:
        R_values (deque): File d'attente pour stocker les valeurs mesurées du canal R.
        IR_values (deque): File d'attente pour stocker les valeurs mesurées du canal IR.
        is_running (bool): flag de marche/arret du thread
        thread (Thread): Thread pour le traitement de données en continu.
        Tcalcul (float): 
    """
    def __init__(self, R_values=deque(maxlen=DEQUE_MAX_LEN), IR_values=deque(maxlen=DEQUE_MAX_LEN), fs=25, interval_calcul=1):
        self.R_values = R_values
        self.IR_values = IR_values
        self.Tcalcul = interval_calcul
        self.is_running = False
        self.thread= None
        self.fs = fs

    def find_spo2(self):
        try:
            while self.is_running:
                if len(self.R_values) >= self.fs and len(self.IR_values) >= self.fs:
                    R_mean = np.mean(self.R_values)
                    IR_mean = np.mean(self.IR_values)
                    R_AC = max(self.R_values) - min(self.R_values)
                    IR_AC = max(self.IR_values) - min(self.IR_values)
                    R_ratio = R_AC / R_mean
                    IR_ratio = IR_AC / IR_mean
                    spo2 = 110 - 25 * (R_ratio / IR_ratio)
                    print("SPO2:", spo2)
                else:
                    print("En attente de données.")
                sleep(self.Tcalcul)
        except Exception as e:
            print("Erreur calcul du SPO2:", e)

    
    '''
    Démarre un thread qui appelle la fonction d'echantillonnage
    '''
    def start_processing(self):
        try:
            self.is_running = True
            self.thread = Thread(target=self.find_spo2)
            self.thread.start()
        except Exception as e:
            print("Erreur démarrage thread sampling : ", e)

    '''
    Detruit le thread d'echantillonnage et sauvegarde les donnees
    '''
    def stop_processing(self):

        self.is_running = False
        self.thread.join()
