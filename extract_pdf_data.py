#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 09:32:08 2019

@author: marco.beyer
"""
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
import pandas as pd

import re
import os

errors = []
path = "bib"


def pdf_to_text(path):
    with open(path, 'rb') as file:
        # PDFMiner boilerplate
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        device = TextConverter(rsrcmgr, sio, codec='utf-8', laparams=LAParams(line_margin=100, word_margin=0.4))
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


def extract_bib_informations(text):
    values = {}
    # Risikoklasse
    risikoklasse = re.search(r"in[^d]*die[^R]*Risikoklasse[^0-7]*([0-7])", text, re.MULTILINE).group(1)
    values['risikoklasse'] = risikoklasse
    # Einstiegskosten
    einstiegskosten = re.search(
        r"(Einmalige Kosten|Einstiegskosten|inbegriffenen Kosten.|Auswirkung der im Preis bereits inbegriffenen \n)["
        r"^0-9-]*([0-9,-]+)",
        text, re.MULTILINE).group(2)
    values['einstiegskosten'] = einstiegskosten
    # Ausstiegskosten
    ausstiegskosten = re.search(
        r"(?<!Einstiegskosten\n)(?<!im Preis bereits )(?<!und )(inbegriffenen Kosten|Ausstiegskosten|Einmalige "
        r"Kosten\nweniger.)(?!.*\n*Einstiegskosten)[^,0-9-]*[^0-9-]*([0-9,-]+)",
        text, re.MULTILINE).group(2)
    values['ausstiegskosten'] = ausstiegskosten
    # Erstelldatum
    erstelldatum = re.search(
        r"(Letzte Aktualisierung|datum|Erstellungszeit|Stand:|Überarbeitung des)[^0-9]*([0-9]*[0-9][.]*[^0-9]*["
        r"0-9.]+)(?!.*Letzte Aktualisierung)",
        text, re.IGNORECASE | re.MULTILINE).group(2)
    values['erstelldatum'] = erstelldatum
    # Bezugsverhältnis
    bezugsverhaeltnis = re.search(
        r"((?<!dem |das )Bezugsverhältnis|Das Ergebnis wird mit)[^0-9.]*([0-9.,]* (Indexpunkte|EUR)\n|[0-9.]*\n)*(["
        r"0-9,]+)",
        text, re.MULTILINE).group(4)
    values['bezugsverhaeltnis'] = bezugsverhaeltnis
    gesamtkosten = re.search(
        r"(?<!EUR\n)(?<!EUR  )(?<!Haltedauer \(Fälligkeit\)\n)(?<!- )(?<!-)(?<!\)\)\n)(?<!0\n)(?<!EUR )("
        r"Gesamtkosten|Szenarien|einlösen)\n*(?!Gesamtkosten)((EUR )*[0-9,-]+( EUR)*[^AG]*)",
        text, re.MULTILINE).group(2)
    # remove new lines add the end
    gesamtkosten = gesamtkosten.replace(' ', '\n').replace('EUR', '').replace('\n\n', '\n').strip("\n\r").split('\n')
    for i in range(len(gesamtkosten)):
        values['gesamtkosten_' + str(i)] = gesamtkosten[len(gesamtkosten) - 1 - i]
    relative_gesamtkosten = re.search(
        r"(?<!%\n)(Auswirkung auf die Rendite|Auswirkung auf die Rendite \(RIY\)|Auswirkung auf die Rendite \(RIY\) "
        r"pro|Auswirkung auf die Rendite \(RIY\) pro Jahr|Auswirkungen auf die Rendite \("
        r"RIY\)|EUR\nGesamtkosten\nAuswirkung auf die Rendite \(RIY\) pro Jahr|EUR\nGesamtkosten|Auswirkung "
        r"\n*auf|Auswirkungen auf die Rendite \(RIY\) pro Jahr) *\n*([0-9,%\n-]+[^A-Za-z\.(]*)",
        text, re.MULTILINE).group(2)
    relative_gesamtkosten = relative_gesamtkosten.replace('%', '').replace(' ', '\n').replace('\n\n', '\n').strip(
        "\n\r").split('\n')
    for i in range(len(relative_gesamtkosten)):
        values['relative_gesamtkosten_' + str(i)] = relative_gesamtkosten[len(relative_gesamtkosten) - 1 - i]
    return values


data = pd.DataFrame()
files = os.listdir(path)
i = 0
for file in files:
    i += 1
    print(str(i) + '/' + str(len(files)))
    print(file)
    try:
        # file='DE000VS043B2.pdf'
        text = pdf_to_text(path + "/" + file).replace('p. a.', '')
        informations = extract_bib_informations(text)
        informations['ISIN'] = file.strip('.pdf')
        data = data.append(informations, ignore_index=True)
    except:
        errors.append(file)
        print('Error in File ' + file)
data.to_csv('BIB_Informationen_neu.csv', index=False)
print(errors)
