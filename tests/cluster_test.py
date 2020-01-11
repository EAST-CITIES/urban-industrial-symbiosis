#!/usr/bin/env python
# -*- coding: utf-8 -*-

from context import cluster
import os

data_path = os.path.join(os.path.dirname(__file__), "..", "data")
company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata_2.xlsx")
association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")

def test_pairwise_scores():
    assoc_table, company_data = cluster.get_data(association_table_path, company_data_path)
    cluster.pretty_print(cluster.get_pairwise_scores(assoc_table, company_data))


test_pairwise_scores()
