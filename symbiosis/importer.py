#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl

class Company:

    def __init__(self, row):
        self.name = row[0]
        self.sector = row[1]
        self.products = [entry for entry in row[2].split("/")]
        self.isic_codes = [entry for entry in str(row[3]).split("/")]
        self.size = row[4]
        self.street = row[5]
        self.number = row[6]
        self.postal_code = row[7]
        self.year = row[8]
        self.website = row[9]

        #TODO compute using energy and material inputs and outputs
        #TODO (later) use geo-locations / street networks for ranking
        def symbiosis_potential_score(self, company):
            return None

    def __str__(self):
        return "Name: %s; Sector: %s; Products: %s; ISIC v4: %s; Size: %s; Street: %s; Number: %s; Postal Code: %s; Year: %s; Website: %s" %(self.name, self.sector, [str(p) for p in self.products], self.isic_codes, self.size, self.street, self.number, self.postal_code, self.year, self.website)


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
            self.thermal_in, self.thermal_out = self.get_input_and_output(cells[0])
            self.electrical_in, self.electrical_out = self.get_input_and_output(cells[1])
            self.chemical_in, self.chemical_out = self.get_input_and_output(cells[2])
            self.mechanical_in, self.mechanical_out = self.get_input_and_output(cells[3])
            self.conditioned_media_in, self.conditioned_media_out = self.get_input_and_output(cells[4])

        def __str__(self):
            return "energy.thermal_in: %s; energy.thermal_out: %s; energy.electrical_in: %s; energy.electrical_out: %s; energy.chemical_in: %s; energy.chemical_out: %s; energy.mechanical_in: %s; energy.mechanical_out: %s; energy.conditioned_media_in: %s; energy.conditioned_media_out: %s" %(self.thermal_in, self.thermal_out, self.electrical_in, self.electrical_out, self.chemical_in, self.chemical_out, self.mechanical_in, self.mechanical_out, self.conditioned_media_in, self.conditioned_media_out)

        def get_input_and_output(self, cell):
            if not cell:
                return (None, None)
            cell = str(cell)
            if len(cell) == 2:
                return (int(cell[0]), int(cell[1]))
            #leading zeros are ignored
            elif len(cell) == 1:
                return (0, int(cell[0]))
            else:
                raise ValueError(cell)

        #TODO matching function...
        #for each energy type: score for input and output match / overlap
        #average over all types (fixed number of types)
        #allow adding weights to different types
        def energy_flow_symbiosis_score(self, energy):
            return 0

    class Material:

        def __init__(self, cells):
            self.hs_in_low = self.to_products(cells[0])
            self.hs_in_high = self.to_products(cells[1])
            self.hs_out_products = self.to_products(cells[2])
            self.hs_out_low = self.to_products(cells[3])
            self.hs_out_high = self.to_products(cells[4])

        def __str__(self):
            return "material.HS-In-Low: %s; material.HS-In-High: %s; material.HS-Out-Products: %s; material.HS-Out-Low: %s; material.HS-Out-High: %s" %([str(p) for p in self.hs_in_low], [str(p) for p in self.hs_in_high], [str(p) for p in self.hs_out_products], [str(p) for p in self.hs_out_low], [str(p) for p in self.hs_out_high])

        def to_products(self, cell):
            return [self.Product(code) for code in str(cell).split(";")]

        #TODO matching function...
        #for each product: score for input and output match / overlap (also consider similarity/compatibility...)
        #average/sum over all products (variable number of products)
        def material_flow_symbiosis_score(self, material):
            return 0

        class Product:

            def __init__(self, hs2):
                self.hs2 = hs2
                self.hs4 = None
                self.hs6 = None
                self.label = None
                self.desci4 = None

            #TODO use graph-based similarity measure
            def similarity(self, product):
                if self.hs2 == product.hs2:
                    return 1
                return 0

            def __str__(self):
                #return "HS-2: %s (%s)" %(self.hs2, self.label)
                return "HS-2: %s" %self.hs2


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
    return [ISIC4(row) for row in association_list]

def to_Company(company_list):
    return [Company(row) for row in company_list]

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

def main(association_table_path, company_data_path):
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
    
    main(association_table_path, company_data_path)
