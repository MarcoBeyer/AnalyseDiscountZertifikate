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
import re
import os

def pdf_to_text(path):
    with open(path, 'rb') as file:
        # PDFMiner boilerplate
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        device = TextConverter(rsrcmgr, sio, codec='utf-8', laparams=LAParams(line_margin=100))
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
    #Risikoklasse
    risikoklasse = re.search(r"in[^d]*die[^R]*Risikoklasse[^0-7]*([0-7])", text, re.MULTILINE).group(1)
    print(risikoklasse)
    #Einstiegskosten
    einstiegskosten = re.search(r"(Einmalige Kosten|Einstiegskosten)[^0-9-]*([0-9,-]+)", text, re.MULTILINE).group(2)
    #Ausstiegskosten
    ausstiegskosten = re.search(r"(inbegriffenen Kosten|Ausstiegskosten)(?!.*\n*Einstiegskosten)[^,][^0-9-]*([0-9,-]+)", text, re.MULTILINE).group(2)
    #Erstelldatum
    erstelldatum = re.search(r"(Letzte Aktualisierung|datum|Erstellungszeit|Stand:)[^0-9]*([0-9]*[0-9][.]*[^0-9]*[0-9.]+)(?!.*Letzte Aktualisierung)", text, re.IGNORECASE | re.MULTILINE).group(2)
    return text

files = os.listdir("bib")
for file in files:
    print(file)
    text = pdf_to_text("bib/" + file)
    informations = extract_bib_informations(text)

