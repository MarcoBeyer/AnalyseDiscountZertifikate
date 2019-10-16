#!/usr/bin/env python3

import os
import numpy
import random
import concurrent.futures
import numpy as np
import pandas as pd
import asyncio
import aiofiles
from aiohttp import ClientSession, TCPConnector

download_path = 'bib'
filename = 'Discount_Frankfurt_2019_09_30-14_20.csv'
num_workers = 10

def get_url_bib(isin, issuerName):
    # BNP Paribas Emissions- und Handelsgesellschaft mbH
    if ("BNP" in issuerName):
        return "https://kid.bnpparibas.com/{}_DE.pdf".format(isin)
    # Citigroup
    elif ("Citigroup" in issuerName):
        return "https://priipskids.smarttra.de/citi/{}_latest_de_DE.pdf".format(isin)
    # Commerzbank AG
    elif ("Commerzbank" in issuerName):
        return "https://www.certificates.commerzbank.com/webforms/Products/KidDownload.aspx?ISIN={}&market=de-DE".format(
            isin)
    # DZ BANK AG Deutsche Zentral-Genossenschaftsbank
    elif ("DZ BANK" in issuerName):
        return "https://www.bib-service.dzbank.de/bib/{}-de-DE.pdf".format(isin)
    # Deutsche Bank AG
    elif ("Deutsche Bank" in issuerName):
        return "https://www.xmarkets.db.com/DE/DE/KID/{}".format(isin)
    # Goldman, Sachs & Co. Wertpapier GmbH
    elif ("Goldman Sachs" in issuerName):
        return "https://www.gspriips.eu/?isin={}&lang=DE&cnt=DE".format(isin)
    # HSBC Trinkaus & Burkhardt AG
    elif ("HSBC" in issuerName):
        return "https://kid.hsbc-zertifikate.de/DE/{}.pdf".format(isin)
    # J.P Morgan
    elif ("J.P. Morgan" in issuerName):
        return "https://priips.jpmorgan.com/priips/document/{}/DE/pop".format(isin)
    # Landesbank Baden-Württemberg
    elif ("Landesbank Baden-Württemberg" in issuerName):
        return "http://www.lbbw-zertifikate.de/kid/{}".format(isin)
    # Morgan Stanley & Co. International plc
    elif ("Morgan Stanley" in issuerName):
        return "https://www.morganstanley.com/ied/etp-server/webapp/svc/document/downloadKID?isin={}&country=DE&language=DE&internal=false".format(
            isin)
    # Société Générale Effekten GmbH
    elif ("Société Générale" in issuerName):
        return "http://kid.sgmarkets.com/isin/{}/ger".format(isin)
    # UBS AG
    elif ("UBS AG" in issuerName):
        return "https://kid.ubs.com/product/generate_pdf?id_type=isin&id_value={}&locale=de_DE&channel_key=554af-d8b923-by4560-r854br".format(isin)
    # UniCredit Bank AG
    elif ("UniCredit" in issuerName):
        return "https://www.onemarkets.de/kid/{}/de".format(isin)
    # Vontobel Financial Products GmbH
    elif ("Vontobel" in issuerName):
        return "https://derinet.vontobel.ch/api/kid?isin={}&language=de".format(isin)
    else:
        print("Emittent zu ISIN {} nicht gefunden".format(isin))


async def download(session, url, filename):
    async with session.get(url) as response:
        if response.status == 200:
            async with aiofiles.open(filename, 'wb') as fd:
                content = await response.read()
                await fd.write(content)
        else:
            async with aiofiles.open("log.txt", 'a') as fd:
                fd.write("Status " + str(response.status) + " for url: " + url + "\n")

async def download_bib(session, isin, issuername):
    url = get_url_bib(isin, issuername)
    return await download(session, url, download_path + "/" + str(isin) + ".pdf")

async def managed_download(isin_issuernames):
    # max connections per thread to one host
    connector = TCPConnector(limit_per_host=1, limit = 10)
    async with ClientSession(connector = connector) as session:
        return await asyncio.gather(*(download_bib(session, isin, issuername) 
                                      for isin, issuername in isin_issuernames))

def download_multiple_isins(isin_issuernames):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(managed_download(isin_issuernames))

async def main_run(loop):
    discount_certificates = pd.read_csv(filename)
    # get already downloaded files
    files = os.listdir(download_path)
    #remove all rows with already downloaded KID
    discount_certificates = discount_certificates[~discount_certificates['ISIN'].isin([s.strip('.pdf') for s in files])]
    # list of the isins and issuer of the BIB to download
    to_download = list(zip(discount_certificates['ISIN'], discount_certificates['Emittent']))
    #shuffle list to download from issuers in a random order
    #so the requests will not getting blocked by one issuer
    random.shuffle(to_download)
    to_download_splitted = np.array_split(to_download, num_workers)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = num_workers) as executor:
        futures = [
            loop.run_in_executor(
                executor, 
                download_multiple_isins, 
                to_download_part
            )
            for to_download_part in to_download_splitted
        ]
        for response in await asyncio.gather(*futures):
            pass

asyncio.run(main_run())

#debug
#main_loop = asyncio.get_event_loop()
#task = main_loop.create_task(main_run(main_loop))