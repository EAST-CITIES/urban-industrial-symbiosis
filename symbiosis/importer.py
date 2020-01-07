#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl

class Company:

    def __init__(self):
        self.name = ""
        self.sector = ""
        self.products = []
        self.isic_codes = []
        self.size = ""
        self.street = ""
        self.number = ""
        self.postal_code = ""
        self.year = ""
        self.website = ""

class ISIC4:

    def __init__(self, row):
        self.code = row[0]
        self.description = row[1]
        self.energy = self.Energy(row[2:7])
        self.materials = self.Material(row[7:12])
        self.mobility = row[12]
        self.equipment = row[13]
        self.abilities = row[14]

    def __str__(self):
        return "Code: %s; Description: %s; %s; %s, Mobility: %s; Equipment: %s; Abilities: %s" %(self.code, self.description, self.energy, self.materials, self.mobility, self.equipment, self.abilities)

    class Energy:
        
        def __init__(self, cells):
            self.thermal = cells[0]
            self.electrical = cells[1]
            self.chemical = cells[2]
            self.mechanical = cells[3]
            self.conditioned_media = cells[4]

        def __str__(self):
            return "energy.thermal: %s; energy.electrical: %s; energy.chemical: %s; energy.mechanical: %s; energy.conditioned_media: %s" %(self.thermal, self.electrical, self.chemical, self.mechanical, self.conditioned_media)

    class Material:

        def __init__(self, cells):
            self.hs_in_low = cells[0]
            self.hs_in_high = cells[1]
            self.hs_out_products = cells[2]
            self.hs_out_low = cells[3]
            self.hs_out_high = cells[4]

        def __str__(self):
            return "material.HS-In-Low: %s; material.HS-In-High: %s; material.HS-Out-Products: %s; material.HS-Out-Low: %s; material.HS-Out-High: %s" %(self.hs_in_low, self.hs_in_high, self.hs_out_products, self.hs_out_low, self.hs_out_high)

def import_company_data(filename):
    pass

def to_ISIC(association_list):
    return [ISIC4(row) for row in association_list]

def import_association_table(filename):
    association_data, hs_overview, hs_codes, concordance = parse(filename)
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

if __name__=="__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")
    company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata.xlsx")
    association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")
    
    for entry in import_association_table(association_table_path):
        if entry.energy.thermal:
            print(str(entry))
    import_company_data(company_data_path)
