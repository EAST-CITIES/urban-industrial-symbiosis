#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import symbiosis
import os

data_path = os.path.join(os.path.dirname(__file__), "..", "data")
company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata_2.xlsx")
association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")

def test_association_table_import():
    entries_with_thermal_energy = [entry for entry in symbiosis.importer.import_association_table(association_table_path) if entry.energy.thermal_out]

    assert(len(entries_with_thermal_energy) == 5)


def test_main():
    assoc_table, company_data = symbiosis.importer.import_data(association_table_path, company_data_path)
    for company in company_data:
        print(company)

test_association_table_import()
test_main()
