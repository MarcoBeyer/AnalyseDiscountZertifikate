#!/usr/bin/env python3

import numpy
import random
import concurrent.futures
import numpy as np
import pandas as pd
import asyncio
import aiofiles
from aiohttp import ClientSession

download_path = 'bib2'
filename = 'Discount_Frankfurt_2019_09_30-14_20.csv'
discount_certificates = pd.read_csv(filename)
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
    elif ("J.P.Morgan" in issuerName):
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
        async with aiofiles.open(filename, 'wb') as fd:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                await fd.write(chunk)
        return await response.release()

async def download_bib(session, isin, issuername):
    url = get_url_bib(isin, issuername)
    return await download(session, url, download_path + "/" + str(isin) + ".pdf")

async def managed_download(isin_issuernames):
    async with ClientSession() as session:
        return await asyncio.gather(*(download_bib(session, isin, issuername) 
                                      for isin, issuername in isin_issuernames))

def download_multiple_isins(isin_issuernames):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(managed_download(isin_issuernames))

async def main_run(loop):
    # list of the isins and issuer of the BIB to download
    to_download = list(zip(discount_certificates['isin'], discount_certificates['issuerName']))
    #shuffle list to download from issuers in a random order
    #so the requests will not getting blocked by one issuer
    random.shuffle(to_download)
    to_download_splitted = np.array_split(to_download[0:10], num_workers)
    
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

loop = asyncio.get_event_loop()
task = loop.create_task(main_run(loop))
