#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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


def extract_bib_informations(text):
    values = {}
    # Risikoklasse
    risikoklasse = re.search(r"in[^d]*die[^R]*Risikoklasse[^0-7]*([0-7])", 
                             text).group(1)
    values['risikoklasse'] = risikoklasse
    # Einstiegskosten
    einstiegskosten = re.search(
        r"(Einmalige Kosten|Einstiegskosten|inbegriffenen Kosten.|"
        r"Auswirkung der im Preis bereits inbegriffenen \n)[^0-9-]*([0-9,-]+)",
        text).group(2)
    values['einstiegskosten'] = einstiegskosten
    
    # Ausstiegskosten
    ausstiegskosten = re.search(
        r"(?<!Einstiegskosten\n)(?<!im Preis bereits )(?<!und )(inbegriffenen Kosten|Ausstiegskosten|Einmalige "
        r"Kosten\nweniger.)(?!.*\n*Einstiegskosten)[^,0-9-]*[^0-9-]*([0-9,-]+)",
        text).group(2)
    values['ausstiegskosten'] = ausstiegskosten
    
    # Erstelldatum
    erstelldatum = re.search(
        r"(Letzte Aktualisierung|datum|Erstellungszeit|Stand:|Überarbeitung des)[^0-9]*([0-9]*[0-9][.]*[^0-9]*["
        r"0-9.]+)(?!.*Letzte Aktualisierung)",
        text, re.IGNORECASE).group(2)
    values['erstelldatum'] = erstelldatum
    
    # Bezugsverhältnis
    bezugsverhaeltnis = re.search(
        r"((?<!dem |das )Bezugsverhältnis|Das Ergebnis wird mit)[^0-9.]*([0-9.,]* (Indexpunkte|EUR)\n|[0-9.]*\n)*(["
        r"0-9,]+)",
        text, re.MULTILINE).group(4)
    values['bezugsverhaeltnis'] = bezugsverhaeltnis
    
    # Fälligkeitsdatum
    faelligkeitsdatum = re.sub(r'-','', text)
    faelligkeitsdatum = re.sub(r' \(Fälligkeit\)', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r' /', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r':', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r'0,01\n', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r'Euro \(EUR\)\n', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r'Bewertungstag\n[^\n]*\n', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r'Ausgabe/Zahltag\nFälligkeitstag\n[^\n]*\n', 'Fälligkeitstag\n', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r' \(Fäl', '', faelligkeitsdatum)
    faelligkeitsdatum = re.sub(r'Bezugsverhältnis\n', '', faelligkeitsdatum)
    if("Der 5. Geschäftstag nach dem" in text):
        faelligkeitsdatum = None
    else:
        faelligkeitsdatum = re.search(
                r"(Rückzahlungstermin|voraussichtich spätestens der|Fälligkeitstag\n|Einlösungstermin\n|Am )[\n]*([0-9]*[0-9][.]*[^0-9]*[0-9.]+)",
                faelligkeitsdatum).group(2)
    values['faelligkeitsdatum'] = faelligkeitsdatum
    
    # Gesamtkosten
    gesamtkosten = re.search(
        r"(?<!EUR  )(?<!Haltedauer \(Fälligkeit\)\n)(?<!- )(?<!-)(?<!\)\)\n)(?<!0\n)(?<!EUR\n)(?<!EUR )"
        r"(Szenarien|einlösen|Gesamtkosten)\n*((EUR )*[0-9,-]+( EUR)*[^AG]*)", 
        text).group(2)
    # remove new lines add the end
    gesamtkosten = gesamtkosten.replace(' ', '\n').replace('EUR', '').replace('\n\n', '\n').strip("\n\r").split('\n')
    for i in range(len(gesamtkosten)):
        values['gesamtkosten_' + str(i)] = gesamtkosten[len(gesamtkosten) - 1 - i]
    
    # Relative Gesamtkosten
    # cleanup of special cases for easier regex
    relative_gesamtkosten = re.sub(r'[0-9,.–-]+ EUR','\n', text)
    relative_gesamtkosten = re.sub(r'Gesamtkosten','', relative_gesamtkosten)
    relative_gesamtkosten = re.sub(r'\n[\n]+','\n', relative_gesamtkosten)
    relative_gesamtkosten = re.search(
        r"(?<!%\n)(Auswirkung auf die Rendite|Auswirkung auf die Rendite \(RIY\)|Auswirkung auf die Rendite \(RIY\) "
        r"pro|Auswirkung auf die Rendite \(RIY\) pro Jahr|Auswirkungen auf die Rendite \("
        r"RIY\)|einlösen\nSzenarien\n|Auswirkung \nauf|Auswirkungen auf die Rendite \(RIY\) "
        r"pro Jahr) *\n*([0-9,%\n-]+[^A-Za-z\.(]*)",
        relative_gesamtkosten).group(2)
    relative_gesamtkosten = relative_gesamtkosten.replace('%', '').replace(' ', '\n').replace('\n\n', '\n').strip(
        "\n\r").split('\n')
    for i in range(len(relative_gesamtkosten)):
        values['relative_gesamtkosten_' + str(i)] = relative_gesamtkosten[len(relative_gesamtkosten) - 1 - i]
    print(relative_gesamtkosten)

    # Mittleres Szenario
    #cleanup of special cases for easier regex
    mittleres_szenario = re.sub(r' EUR','\n', text)
    mittleres_szenario = re.sub(r'EUR ','', mittleres_szenario)
    mittleres_szenario = re.sub(r'\n[\n]+','\n', mittleres_szenario)
    mittleres_szenario = re.sub(r',–', '', mittleres_szenario)
    mittleres_szenario = re.sub(r'[ ]?(Was|Sie|nach|Abzug|der|Kosten|erhalten|könn[t]?en)[ ]?\n?', '', mittleres_szenario)
    mittleres_szenario = re.sub(r'[0-9,-]*%\n', '', mittleres_szenario)
    mittleres_szenario = re.search(
        r"(Mittleres[ ]*(Szenario)?[\n]*([0-9.,]+[\n]*)+|([0-9.,]+[\n]*)+Mittleres[ ]*Szenario)",
        mittleres_szenario).group(1)
    mittleres_szenario = mittleres_szenario.replace(' ', '')\
                        .replace('Mittleres', '')\
                        .replace('Szenario', '')\
                        .strip("\n\r")\
                        .split('\n')
    if("Deutsche Bank AG" in text):
        for i in range(len(mittleres_szenario)):
            values['mittleres_szenario_' + str(i)] = mittleres_szenario[i]
    else:
        for i in range(len(mittleres_szenario)):
            values['mittleres_szenario_' + str(i)] = mittleres_szenario[len(mittleres_szenario) - 1 - i]
    return values


data = pd.DataFrame()
files = os.listdir(path)
i = 0
for file in files:
    i += 1
    print(str(i) + '/' + str(len(files)))
    print(file)
    try:
        #file='DE000HX65D37.pdf'
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
        print(informations)
        data = data.append(informations, ignore_index=True)
    except:
        errors.append(file)
        print('Error in File ' + file)
data.to_csv('BIB_Informationen_12_12.csv', index=False)
print(errors)
