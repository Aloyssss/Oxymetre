#!/usr/bin/python
# -*- coding: utf-8 -*-
from adc import *
from pou import *
from oxy import *
from gui import *

Fs = 10

def main():

    adc = Adc(fs = Fs)
    pouls = Pou(fs = Fs, data=adc.R_values)
    oxy = Oxy(R_values=adc.R_values, IR_values=adc.IR_values, fs=Fs)
    gui = Gui(data_y=adc.IR_values)

    adc.start_sampling()
    pouls.start_processing()
    oxy.start_processing()

    gui.init_window()
    gui.start_render()

    adc.stop_sampling()
    pouls.stop_processing()
    oxy.stop_processing()

if __name__ == '__main__':
    main()
