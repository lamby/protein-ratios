# -*- coding: utf-8 -*-

import re

from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose

re_names = [re.compile(x, re.IGNORECASE) for x in (
    r'\s+$',
    r'>$',
    r'-$',
    r'[\d\.,]+\s*(k?g|m?l|litre|ltr?)-?$',
    r'(\d+g?|twin)\s*(pack|slices|sachets|x|can)$',
    r'\s+(x)$',
)]

re_protein                  = re.compile(r'([\d\.]+)\s*g?', re.IGNORECASE)
re_protein_label            = re.compile(r'^Protein', re.IGNORECASE)

re_calories                 = re.compile(r'([\d\.]+)\s*k?cal', re.IGNORECASE)
re_calories_raw             = re.compile(r'([\d\.]+)\s*(?:k?cal)?$', re.IGNORECASE)

re_calorie_label            = re.compile(r'^Energy', re.IGNORECASE)
re_calorie_label_raw        = re.compile(r'k?cal', re.IGNORECASE)
re_calorie_label_continue   = re.compile(r'^-', re.IGNORECASE)

def load_name(val):
    while True:
        for pattern in re_names:
            val, count = pattern.subn('', val)

            if count:
                break
        else:
            break

    return val

def load_protein_per_100_kcal(elem):
    table = []

    try:
        if elem.css('caption::text').extract()[0] != "Nutrition":
            return
    except IndexError:
        return

    for idx, th in enumerate(elem.css('thead th::text')[1:]):
        serving = th.extract()

        if serving == "-":
            continue

        column = []
        for y in elem.css('tbody tr'):
            key = y.css('th::text')[0].extract()

            # Also extract empty values
            values = [''.join(z.css('::text').extract()) for z in y.css('td')]

            try:
                value = values[idx]
            except IndexError:
                value = ''

            column.append((key, value))

        table.append((serving, column))

    result = []
    for serving, x in table:
        if 'RI' in serving:
            continue

        protein = _parse_protein(x)
        calories = _parse_calories(x)

        if protein and calories:
            result.append(100. * protein / calories)

    return result

class ProductLoader(ItemLoader):
    default_output_processor = TakeFirst()

    name_in = MapCompose(load_name)
    price_in = MapCompose(lambda x: x.replace(u'\xa3', ''))
    protein_per_100_kcal_in = MapCompose(load_protein_per_100_kcal)

def _parse_protein(data):
    for k, v in data:
        if re_protein_label.search(k):
            raw = v
            break
    else:
        return

    # Some products use commas instead of periods
    raw = raw.replace(',', '.')

    # Some products have double dots.
    raw = raw.replace('..', '.')

    # Ignore "less than"; it's probably too low anyway (eg. "< 0.5g")
    if raw.startswith('<'):
        return

    m = re_protein.search(raw)

    if m is None:
        return

    return float(m.group(1))

def _parse_calories(data):
    val = None

    flag = False
    for k, v in data:
        if re_calorie_label_raw.search(k):
            m = re_calories_raw.search(v)
            if m is not None:
                val = float(m.group(1))
                break

        # Calories can be split onto the next line with a "-" label
        if re_calorie_label.search(k) or \
                (flag and re_calorie_label_continue.search(k)):
            m = re_calories.search(v)

            if m is not None:
                val = float(m.group(1))
                break
        flag = bool(re_calorie_label.search(k))

    # Ignore low values
    if val <= 10:
        return

    return val
