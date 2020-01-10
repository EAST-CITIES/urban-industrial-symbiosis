#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import openpyxl
import collections

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

    #return vector with scores for energy and material input and output overlaps
    #TODO (later) also use geo-locations / street networks for ranking
    def get_symbiosis_potential(self, company, assoc_table):
        potential = self.get_energy_flow_symbiosis_potential(company, assoc_table)
        potential.extend(self.get_material_flow_symbiosis_potential(company, assoc_table))
        return potential

    def __str__(self):
        return "Name: %s; Sector: %s; Products: %s; ISIC v4: %s; Size: %s; Street: %s; Number: %s; Postal Code: %s; Year: %s; Website: %s" %(self.name, self.sector, [str(p) for p in self.products], self.isic_codes, self.size, self.street, self.number, self.postal_code, self.year, self.website)

    #TODO there should only be one code - else how to combine conflicting flow specifications?
    #for now: use only first code
    def get_energy_flow_symbiosis_potential(self, company, assoc_table):
        scores = [0]
        for code in self.isic_codes:
            for code2 in company.isic_codes:
                scores.extend(assoc_table.get(code).energy.get_energy_flow_symbiosis_potential(assoc_table.get(code2).energy))
                break
            break
        #print("energy flow symbiosis potential: " + (str(scores)))
        return scores

    def get_material_flow_symbiosis_potential(self, company, assoc_table):
        scores = [0]
        for code in self.isic_codes:
            for code2 in company.isic_codes:
                scores.extend(assoc_table.get(code).materials.get_material_flow_symbiosis_potential(assoc_table.get(code2).materials))
        #print("material flow symbiosis potential: " + (str(scores)))
        return scores

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
                #return (None, None)
                return (0,0)
            cell = str(cell)
            if len(cell) == 2:
                return (int(cell[0]), int(cell[1]))
            #leading zeros are ignored
            elif len(cell) == 1:
                return (0, int(cell[0]))
            else:
                raise ValueError(cell)

        #for each energy type: score for input and output match / overlap
        #TODO allow adding weights to different types?
        def get_energy_flow_symbiosis_score(self, energy):
            return sum(self. get_energy_flow_symbiosis_potential(energy))

        #weighting_schema: [exact match input and output: 1; divergence of 1: 0.5; divergence of 2: 0.3]
        def get_energy_flow_symbiosis_potential(self, energy, weighting_scheme = [1.0, 0.5, 0.3]):
            return [self.get_potential(self.thermal_in, energy.thermal_out, self.thermal_out, energy.thermal_in, weighting_scheme), self.get_potential(self.electrical_in, energy.electrical_out, self.electrical_out, energy.electrical_in, weighting_scheme), self.get_potential(self.chemical_in, energy.chemical_out, self.chemical_out, energy.chemical_in, weighting_scheme), self.get_potential(self.mechanical_in, energy.mechanical_out, self.mechanical_out, energy.mechanical_in, weighting_scheme), self.get_potential(self.conditioned_media_in, energy.conditioned_media_out, self.conditioned_media_out, energy.conditioned_media_in, weighting_scheme)]

        def get_potential(self, energy1_in, energy2_out, energy1_out, energy2_in, weighting_scheme):
            if energy1_in + energy2_out + energy1_out + energy2_in == 0:
                return 0
            p = 0
            div_in1_out2 = abs(energy1_in - energy2_out)
            if div_in1_out2 == 0:
                p = weighting_scheme[0]
            elif div_in1_out2 == 1:
                p = weighting_scheme[1]
            elif div_in1_out2 == 2:
                p = weighting_scheme[2]

            div_in2_out1 = abs(energy1_out - energy2_in)
            if div_in2_out1 == 0:
                p += weighting_scheme[0]
            elif div_in2_out1 == 1:
                p += weighting_scheme[1]
            elif div_in2_out1 == 2:
                p += weighting_scheme[2]
            return p


    class Material:

        def __init__(self, cells):
            self.hs_in_low = self.to_products(cells[0])
            self.hs_in_high = self.to_products(cells[1])
            self.hs_out_products = self.to_products(cells[2])
            self.hs_out_low = self.to_products(cells[3])
            self.hs_out_high = self.to_products(cells[4])

        def __str__(self):
            return "material.HS-In-Low: %s; material.HS-In-High: %s; material.HS-Out-Products: %s; material.HS-Out-Low: %s; material.HS-Out-High: %s" %([str(p) for p in self.hs_in_low], [str(p) for p in self.hs_in_high], [str(p) for p in self.hs_out_products], [str(p) for p in self.hs_out_low], [str(p) for p in self.hs_out_high])

        #TODO add leading 0 if only one digit?
        def to_products(self, cell):
            return [self.Product(code) for code in str(cell).split(";") if code != "None"]

        #for each product: score for input and output match / overlap (also consider similarity/compatibility...)
        #weighting_scheme: [perfect_match(product and volume), partial_match (similar product, same volume), product_match (different volume), minimal_match (similar product, different volume)]
        def get_material_flow_symbiosis_potential(self, material, weighting_scheme = [1, 0.3, 0.5, 0.1]):
        #def get_product_matches(self, material, weighting_scheme):
            matches = []
            for product in self.hs_in_low:
                for p in material.hs_out_low:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0])
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1])
                for p in material.hs_out_products:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[2]) 
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[3])
                for p in material.hs_out_high:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[2]) 
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[3])

            for product in self.hs_in_high:
                for p in material.hs_out_high:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0])
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1])
                for p in material.hs_out_products:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0])
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1])
                for p in material.hs_out_low:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[2]) 
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[3])
            return matches

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
                else:
                    try:
                        if self.hs2[0] == product.hs2[1]:
                            return 0.5
                    except IndexError:
                        return 0
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
