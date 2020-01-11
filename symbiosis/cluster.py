#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections
import model
import importer
from optparse import OptionParser


def get_user_input():
    parser = OptionParser()
    parser.add_option("-c", "--company_data_path", dest="company_data_path",
                  help="path to file containing company data", metavar="FILENAME_COMPANIES")
    parser.add_option("-a", "--association_table_path", dest="association_table_path",
                  help="path to file containing association tables")

    (options, args) = parser.parse_args()
    if not options.company_data_path:
        parser.error('path to file containing company data not given')
    if not options.association_table_path:
        parser.error('path to file containing association tables not given')
    return (options.association_table_path, options.company_data_path)

def get_data(file_paths):
    return importer.import_data(file_paths[0], file_paths[1])

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

def main():
    assoc_table, company_data = get_data(get_user_input())
    pretty_print(get_pairwise_scores(assoc_table, company_data))


if __name__=="__main__":
    main()    
