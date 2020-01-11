#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections
import model
import importer


def get_data(association_table_path, company_data_path):
    return importer.import_data(association_table_path, company_data_path)

def get_pairwise_scores(assoc_table, company_data):
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
    return collections.OrderedDict(sorted(res.items()))

def pretty_print(score_dict):
    for key, val in score_dict.items():
        print("\n")
        print(key)
        for v in val:
            print("%s --- %s" %(v[0].name, v[1].name))

if __name__=="__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "data")
    company_data_path = os.path.join(data_path, "20191216_Unternehmensverzeichnis_Toydata_2.xlsx")
    association_table_path = os.path.join(data_path, "20191216_Association_Table_2.xlsx")
    
    assoc_table, company_data = get_data(association_table_path, company_data_path)
    pretty_print(get_pairwise_scores(assoc_table, company_data))

