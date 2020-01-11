#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl
import collections
import model

def import_company_data(filename):
    company_data = parse(filename)[0]
    rows = []
    r = 0
    for row in company_data.rows:
        #ignore header
        if r < 2:
            r += 1
            continue
        c = 0
        for cell in row:
            if not cell.value:
                continue
            elif c < 1:
                rows.append([])
            rows[-1].append(cell.value)
            c += 1
        r += 1
    return rows

def to_dict(isic_rows):
    return {isic.code:isic for isic in isic_rows}

def to_ISIC(association_list):
    return [model.ISIC4(row) for row in association_list]

def to_Company(company_list):
    return [model.Company(row) for row in company_list]

def import_association_table(filename):
    association_data, hs_overview, hs_codes, concordance = parse(filename)
    #TODO import remaining sheets
    return to_ISIC(import_associations(association_data))

def import_associations(association_data):
    rows = []
    r = 0
    for row in association_data.rows:
        if r < 13:
            r += 1
            continue

        rows.append([])

        c = 0
        for cell in row:
            if c < 1:
                c += 1
                continue
            elif c > 15:
                break
            rows[-1].append(cell.value)
            c += 1
        r += 1
    return rows
    
# import xlsx sheets:
# 1) NACE REV.2 - ISIC REV.4 associations
# 2) HS_Overview
# 3) HS_Codes
# 4) HS_ISICv4 Concordance
def parse(filename):
    wb = openpyxl.load_workbook(filename, read_only=True)
    print("importing %s" %filename)
    print(wb.sheetnames)
    return [sheet for sheet in wb]

def get_isic_data(assoc_table, company):
    return [assoc_table.get(code) for code in company.isic_codes]

def import_data(association_table_path, company_data_path):
    assoc_table = to_dict(import_association_table(association_table_path))
    company_data = to_Company(import_company_data(company_data_path))
    for company in company_data:
        print(company)
        for isic in get_isic_data(assoc_table, company):
            print(isic)
    return (assoc_table, company_data)


if __name__=="__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")
    company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata_2.xlsx")
    association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")
    
    assoc_table, company_data = import_data(association_table_path, company_data_path)

    checked = set([])
    res = {}
    for i in range(len(company_data)):
        c1 = company_data[i]
        for j in range(len(company_data)):
            c2 = company_data[j]
            #TODO necessary?
            if (c1.name == c2.name):
                continue
            if (c1.name, c2.name) in checked:
                continue
            score = sum(c1.get_symbiosis_potential(c2, assoc_table))
            vals = res.get(score, [])
            vals.append((c1, c2))
            res[score] = vals
            checked.add((c1.name, c2.name))
            checked.add((c2.name, c1.name))

    for key, val in collections.OrderedDict(sorted(res.items())).items():
        print("\n")
        print(key)
        for v in val:
            print("%s --- %s" %(v[0].name, v[1].name))
