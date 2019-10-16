#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 14:05:02 2019

@author: marco.beyer
"""
import pandas as pd
import time


def download_comdirect_discount_csv(issuer_id):
    complete_csv = None
    offset = 0

    while True:
        print("offset: " + str(offset))
        url = "https://www.comdirect.de/inf/zertifikate/selector/discount/trefferliste.csv?CAP_ABS_FROM=&CAP_ABS_TO" \
              "=&DATE_TIME_MATURITY_FROM=Range_NOW&DATE_TIME_MATURITY_FROM_CAL=&DATE_TIME_MATURITY_TO=Range_ENDLESS" \
              "&DATE_TIME_MATURITY_TO_CAL=&DISCOUNT_ASK_PCT_FROM=&DISCOUNT_ASK_PCT_TO=&ID_GROUP_ISSUER={" \
              "}&ID_NOTATION_UNDERLYING=20735&MAXIMUM_EARNING_PER_ANNUM_PCT=&OFFSET={" \
              "}&SEARCH_VALUE=&SUBCATEGORY_APPLICATION=DISCOUNT&UNDERLYING_NAME_SEARCH=DAX+Performance-Index" \
              "&keepCookie=true".format(issuer_id, offset)
        offset += 1
        downloaded_csv = pd.read_csv(url, encoding="latin-1", sep=";")
        if len(downloaded_csv) == 0:
            break
        downloaded_csv = downloaded_csv.dropna(axis="columns", how="all")
        if complete_csv is None:
            complete_csv = downloaded_csv
        else:
            complete_csv = complete_csv.append(downloaded_csv)
    return complete_csv


# Get JP. Morgan ID 54023
csv = download_comdirect_discount_csv(54023)

# Get Morgan Stanley ID 54283
csv = csv.append(download_comdirect_discount_csv(54283))

# rename and select columns
csv = csv.rename(columns = {"Fälligkeit" : "Bewertungstag"})
csv = csv[["ISIN", "Cap", "Bewertungstag", "Emittent", "Brief", "Geld"]]

timestr = time.strftime("%Y_%m_%d-%H_%M")

# Save to CSV File
csv.to_csv("Discount_Comdirect_" + timestr + ".csv", index=False)
