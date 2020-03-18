#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
from io import StringIO
from datetime import datetime
from dateutil.parser import parse
import pandas as pd

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams


errors = []
#path = "D:/Zertifikate/2020-02"
path = "bib_test_2"

def pdf_to_text(path):
    with open(path, 'rb') as file:
        # PDFMiner boilerplate
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        device = TextConverter(rsrcmgr, sio, codec='utf-8', 
                               laparams=LAParams(line_margin=100, 
                                                 word_margin=0.4))
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # get text from file
        for page in PDFPage.get_pages(file):
            interpreter.process_page(page)
        # Get text from StringIO
        text = sio.getvalue()
        # close objects
        device.close()
        sio.close()
    return text


def extract_creation_date(text):
    #Morgan Stanley
    creation_date = re.sub(r' *Uhr', '', text)
    creation_date = re.sub(r'Ortszeit Frankfurt am Main', '', creation_date)
    creation_date = re.sub(r'Authority\ndes Produkts', '\nErstellungszeit', creation_date)
    creation_date = re.search(
            "(Herstellers des Produkts|Letzte Aktualisierung|datum|Erstellungszeit|Stand:|Überarbeitung des)[^0-9]*([0-9]*[0-9][.]*[^0-9]*["
            "0-9.]+)(?!.*Letzte Aktualisierung)",
            creation_date, re.IGNORECASE|re.MULTILINE).group(2)
    creation_date = normalize_date(creation_date)    
    return creation_date

def normalize_local_string_to_float(string):
    # remove dots
    string = string.replace('.', '')
    # replace , with dots
    string = string.replace(',','.')
    # replace - with 0.00
    string = string.replace(r'^-$', '0.00')
    #replace .- with .0
    string = string.replace('.–', '.0')
    return float(string)
    
def extract_total_costs(text):
    total_costs = re.sub(r'Anlage EUR 10.000,00\n*', '', text)
    total_costs = re.sub(r'Szenarien\n', '', total_costs)

    total_costs = re.search(
        r"(?<!EUR  )(?<!Haltedauer \(Fälligkeit\)\n)(?<!- )(?<!-)(?<!\)\)\n)(?<!0\n)(?<!EUR\n)(?<!EUR )"
        r"(einlösen|Gesamtkosten)\n*((EUR )*[0-9,-]+( EUR)*[^AG]*)", 
        total_costs, re.MULTILINE).group(2)
    # cleanup costs
    total_costs = total_costs.replace(' ', '\n').replace('EUR', '').replace('\n\n', '\n').strip("\n\r")
    total_costs = total_costs.split('\n')
    for i in range(len(total_costs)):
        total_costs[i] = normalize_local_string_to_float(total_costs[i])
    return total_costs

def extract_relative_total_costs(text):
    # cleanup of special cases for easier regex
    relative_total_costs = re.sub(r'[0-9,.–-]+ EUR\n*','', text)
    relative_total_costs = re.sub(r' %','%', relative_total_costs)
    relative_total_costs = re.sub(r'EUR [0-9,.–-]+\n*','', relative_total_costs)
    relative_total_costs = re.sub(r'Gesamtkosten\n*','', relative_total_costs)
    relative_total_costs = re.sub(r'\n[\n]+','\n', relative_total_costs)
    #Societe Generale
    relative_total_costs = re.sub(r'proJahr','\nHaltedauer einlösen\n', relative_total_costs)    
    relative_total_costs = re.sub(r'.*\(Fälligkeit\)* *\n','', relative_total_costs)       
    relative_total_costs = re.sub(r'Auswirkung[en]* *\n* *auf[^0-9-]*\n*', '\nHaltedauer einlösen', relative_total_costs)
    relative_total_costs = re.sub(r'[^0-9][0-9] Jahr[^0-9H\n-]*\n','', relative_total_costs)
    relative_total_costs = re.sub(r'.*Wenn Sie[^0-9\n-]*\n*','', relative_total_costs)
    relative_total_costs = re.sub(r'Anlage *\n*Szenarien','\nHaltedauer einlösen', relative_total_costs)
    relative_total_costs = re.sub(r'einlösen *\n*Szenarien','\nHaltedauer einlösen', relative_total_costs)
    relative_total_costs = re.sub(r'Haltedauer *\n*Szenarien','\nHaltedauer einlösen', relative_total_costs)
    # Goldman Sachs
    relative_total_costs = re.sub(r'Anlage auswirken werden.\nSzenarien','\nHaltedauer einlösen', relative_total_costs)
    # Morgan Stanley
    relative_total_costs = re.sub(r'Anlage: *Szenarien','\nHaltedauer einlösen', relative_total_costs)
    # DZ
    relative_total_costs = re.sub(r'.*Zeitverlauf *\n*Szenarien','\nHaltedauer einlösen', relative_total_costs)

    # HSBC
    relative_total_costs = re.sub(r'Anlage *\n*Szenario\n','\nHaltedauer einlösen', relative_total_costs)
    # UBS
    relative_total_costs = re.sub(r'Empfohlene *\n*Szenarien','\nHaltedauer einlösen', relative_total_costs)
    # LBBW
    relative_total_costs = re.sub(r'Rendite \(RIY\) pro Jahr','\nHaltedauer einlösen', relative_total_costs)

    relative_total_costs = re.search(
        r"(?<!%\n)("
        r"Haltedauer einlösen)"
        r" *\n?([0-9,\n%-]+%)",
        relative_total_costs, re.MULTILINE).group(2)

    relative_total_costs = relative_total_costs.replace('%', ' ').replace(' ', '\n')
    relative_total_costs = re.sub(r'\n+', '\n', relative_total_costs)
    relative_total_costs = relative_total_costs.strip("\n\r").split('\n')
    for i in range(len(relative_total_costs)):
        relative_total_costs[i] = normalize_local_string_to_float(relative_total_costs[i])
    return relative_total_costs
      
def normalize_date(date_string):
    date_string = date_string.replace('Januar', 'Jan')
    date_string = date_string.replace('Februar', 'Feb')
    date_string = date_string.replace('März', 'Mar')
    date_string = date_string.replace('April', 'Apr')
    date_string = date_string.replace('Mai', 'May')
    date_string = date_string.replace('Juni', 'Jun')
    date_string = date_string.replace('Juli', 'Jul')
    date_string = date_string.replace('August', 'Aug')
    date_string = date_string.replace('September', 'Sep')
    date_string = date_string.replace('Oktober', 'Oct')
    date_string = date_string.replace('November', 'Nov')
    date_string = date_string.replace('Dezember', 'Dec')
    date_string = date_string.replace('Mrz', 'Mar')
    date_string = date_string.replace('Mai', 'May')
    date_string = date_string.replace('Okt', 'Oct')
    date_string = date_string.replace('Dez', 'Dec')
    date = parse(date_string, ignoretz = True, dayfirst = True)
    return date

def extract_bib_informations(text):
    values = {}
    
    # Erstelldatum
    values['Erstelldatum'] = extract_creation_date(text)

    # Gesamtkosten
    # TODO return dict/list
    total_costs = extract_total_costs(text)
    for i in range(len(total_costs)):
        values['Gesamtkosten_' + str(i)] = total_costs[len(total_costs) - 1 - i]
        
    # Relative Gesamtkosten
    relative_total_costs = extract_relative_total_costs(text)
    for i in range(len(relative_total_costs)):
        values['Relative_Gesamtkosten_' + str(i)] = relative_total_costs[len(relative_total_costs) - 1 - i]
    
    return values

data = pd.DataFrame()
files = os.listdir(path)
EXTEND = True
if EXTEND:
    data = pd.read_csv("BIB-2020-02.csv")
    isins = data['ISIN'] + '.pdf'
    isins = isins.unique()
    isins = set(isins)
    files = list(set(files) - set(isins))

i = 0
for file in files:
    i += 1
    print(str(i) + '/' + str(len(files)))
    print(file)
    try:
        file='DE000DC5X7A7.pdf'
        text = pdf_to_text(path + "/" + file)
        # Text bereinigen
        text = text.replace('p. a.', '')
        text = text.replace('\x0c', '')
        text = re.sub(r'Seite [0-9]', '', text)
        text = re.sub(r'DocID:[^\n]*', '' , text)
        #remove empty lines
        text = re.sub(r'^\n', '', text, flags=re.MULTILINE)

        informations = extract_bib_informations(text)
        informations['ISIN'] = file.strip('.pdf')
        informations['Abrufdatum'] = datetime.fromtimestamp(os.path.getmtime(path + "/" + file))
        print(informations)
        data = data.append(informations, ignore_index=True)
    except Exception as e: 
        print(e)
        errors.append(file)
        print('Error in File ' + file)
data['Abrufdatum'] = pd.to_datetime(data['Abrufdatum'])
data.to_csv('BIB-2020-02.csv', index=False)

with pd.ExcelWriter("BIB-2020-02.xlsx",
                    engine='xlsxwriter',
                    datetime_format='mm.dd.yyyy hh:mm',
                    date_format='dd.mm.yyyy') as writer:
    data.to_excel(writer, sheet_name = '2020-02', index = False)
print(errors)