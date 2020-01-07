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

    def __init__(self):
        self.code = ""
        self.description = ""
        self.energy = ""
        self.materials = ""
        self.mobility = ""
        self.equipment = ""
        self.abilities = ""

    class Energy:
        
        def __init__(self):
            self.thermal = ""
            self.electrical = ""
            self.chemical = ""
            self.mechanical = ""
            self.conditioned_media = ""

    class Material:

        def __init__(self):
            self.hs_in_low = ""
            self.hs_in_high = ""
            self.hs_out_low = ""
            self.hs_out_high = ""
            self.hs_out_products = ""


def import_company_data(filename):
    pass

def import_association_table(filename):
    association_data, hs_overview, hs_codes, concordance = parse(filename)
    import_associations(association_data)

def import_associations(association_data):
    pass
    
# import xlsx sheets:
# 1) NACE REV.2 - ISIC REV.4 associations
# 2) HS_Overview
# 3) HS_Codes
# 4) HS_ISICv4 Concordance
def parse(filename):
    wb = openpyxl.load_workbook(filename)
    print("importing %s" %filename)
    print(wb.sheetnames)
    return [sheet for sheet in wb]

if __name__=="__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")
    company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata.xlsx")
    association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")
    
    import_association_table(association_table_path)
    import_company_data(company_data_path)
