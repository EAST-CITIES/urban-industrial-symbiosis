#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import symbiosis
import os

def test_association_table_import():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")
    association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")

    entries_with_thermal_energy = [entry for entry in symbiosis.importer.import_association_table(association_table_path) if entry.energy.thermal]

    assert(len(entries_with_thermal_energy) == 5)


test_association_table_import()
