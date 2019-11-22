# -*- coding: utf-8 -*-
"""
Ein Skript um zwei CSV Dateien zu kombinieren
@author: marco.beyer
"""
import pandas as pd

path_csv_1 = "Daten/Discount_Frankfurt_2019_10_16-19_39.csv"
path_csv_2 = "Daten/Discount_Comdirect_2019_10_16-19_40.csv"
path_combined = "Daten/Discount_Certificates.csv"

csv_1 = pd.read_csv(path_csv_1)
csv_2 = pd.read_csv(path_csv_2)

csv = csv_1.append(csv_2)

# Save to CSV File
csv.to_csv(path_combined, index=False)
