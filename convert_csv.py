# -*- coding: utf-8 -*-

import pandas as pd

path = "bib_test_2"
import_filename_csv = 'bib-06-2020-raw.csv'
export_filename_csv = 'BIB-2020-06.csv'
export_filename_xlsx = 'BIB-2020-06.xlsx'
sheet_name = '2020-06'

data = pd.read_csv(import_filename_csv, parse_dates = ['Erstelldatum', 'Abrufdatum'])
data.to_csv(export_filename_csv, index=False)
with pd.ExcelWriter(export_filename_xlsx,
                    engine='xlsxwriter',
                    datetime_format='dd.mm.yyyy hh:mm',
                    date_format='dd.mm.yyyy') as writer:
    data.to_excel(writer, sheet_name = sheet_name, index = False)