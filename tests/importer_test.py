#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from context import symbiosis
from context import model
from context import importer
import os

data_path = os.path.join(os.path.dirname(__file__), "..", "data")
company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata_2.xlsx")
association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")

def test_association_table_import():
    entries = importer.import_association_table(association_table_path)  
    entries_with_thermal_energy = [entry for entry in entries if entry.energy.thermal_out]
    assert(len(entries_with_thermal_energy) == 5)

    entries_with_chemical_energy_out = [entry for entry in entries if entry.energy.chemical_out]
    assert(len(entries_with_chemical_energy_out) == 0)
    
    entries_with_chemical_energy_in = [entry for entry in entries if entry.energy.chemical_in]
    assert(len(entries_with_chemical_energy_in) == 3)


def test_import_data():
    assoc_table, company_data = importer.import_data(association_table_path, company_data_path)
    for company in company_data:
        print(company)

test_import_data()
test_association_table_import()
