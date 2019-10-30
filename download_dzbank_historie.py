#!/usr/bin/env python3

import os
import numpy
import concurrent.futures
import numpy as np
import pandas as pd
import asyncio
import aiofiles
from aiohttp import ClientSession, TCPConnector

download_path = 'historie_dz'
filename = 'Discount_Certificates.csv'
num_workers = 10

async def download(session, url, filename):
    async with session.get(url) as response:
        if response.status == 200:
            async with aiofiles.open(filename, 'wb') as fd:
                content = await response.read()
                await fd.write(content)
        else:
            print("Status " + str(response.status) + " for url: " + url + "\n")
            await response.release()
            
async def download_history(session, isin):
    url = "https://www.dzbank-derivate.de/product/detail/ksh/isin/{}".format(isin)
    return await download(session, url, download_path + "/" + str(isin) + ".pdf")

async def managed_download(isins):
    # max connections per thread to one host
    connector = TCPConnector(limit_per_host=1, limit = 10)

    async with ClientSession(connector = connector) as session:
        return await asyncio.gather(*(download_history(session, isin)
                                      for isin in isins))

def download_multiple_isins(isins):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(managed_download(isins))

async def main_run():
    discount_certificates = pd.read_csv(filename)
    # get already downloaded files
    files = os.listdir(download_path)
    #filter by issuername
    discount_certificates = discount_certificates[discount_certificates['Emittent'] == "DZ BANK AG"]
    #remove all rows with already downloaded KID
    discount_certificates = discount_certificates[~discount_certificates['ISIN'].isin([s.strip('.pdf') for s in files])]
    # list of the isins and issuer of the BIB to download
    to_download = discount_certificates['ISIN'].to_list()
    print(str(len(to_download)) + " files are left to download")
    to_download_splitted = np.array_split(to_download, num_workers)
    loop = asyncio.get_event_loop()
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
