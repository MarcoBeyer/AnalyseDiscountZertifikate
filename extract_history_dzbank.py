#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 09:32:08 2019

@author: marco.beyer
"""
import camelot
import pandas as pd
import os

path = "historie_dz"
not_found = []

def extract_table(path, isin):
    #remove two columns with headings
    table = camelot.read_pdf(path)[0].df[2:]
    table.columns = table.columns = ["Datum",
                                     "Einstiegskosten", 
                                     "Ausstiegskosten",
                                     "Portfolio Transaktionskosten", 
                                     "Sonstige laufende Kosten"]
    table['ISIN'] = isin
    return table

data = pd.DataFrame()
files = os.listdir(path)
for file in files:
    try:
        print(file)
        table = extract_table(path + "/" + file, file.strip('.pdf'))
        data = data.append(table, ignore_index = True)
    except:
        print('keine Tabelle in ' + file)
        not_found.append(file)
print('Finished\n Not found:\n'+ str(not_found))
data.to_csv('history_dzbank.csv')

