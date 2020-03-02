#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections
import importer
from optparse import OptionParser

STANDARD_SIZE = 100.0
ENERGY_FLOW_SCALING_FUNCTION = lambda x:float(x) / STANDARD_SIZE
MATERIAL_FLOW_SCALING_FUNCTION = lambda x:float(x) / STANDARD_SIZE
ENERGY_SCORING_SCHEME = [1.0, 0.5, 0.3]
MATERIAL_SCORING_SCHEME = [1.0, 0.3]
ACCUMULATION_FUNCTION = sum
ENERGY_BUCKETS = [2, 5]

def get_user_input():
    parser = OptionParser()
    parser.add_option("-c", "--company_data_path", dest="company_data_path",
                  help="path to file containing company data", metavar="FILENAME_COMPANIES")
    parser.add_option("-a", "--association_table_path", dest="association_table_path",
                  help="path to file containing association tables")
    parser.add_option("-e", "--energy_flow_scaling_function", dest="energy_flow_scaling_function", help="function determining the impact of the company size on energy flows")
    parser.add_option("-b", "--energy_flow_buckets", dest="energy_flow_buckets", help="buckets for different energy flow potential scores (how close do scores have to be in order to be treated as similar?): [upper boundary for closest score (exclusive), upper boundary for medium score (exclusive)]")
    parser.add_option("-m", "--material_flow_scaling_function", dest="material_flow_scaling_function", help="function determining the impact of the company size on material flows")
    parser.add_option("-s", "--scoring_scheme_energy", dest="energy_scoring_scheme", help="scores for energy input and output overlaps: [exact match input and output, divergence of 1, divergence of 2]")
    parser.add_option("-t", "--scoring_scheme_material", dest="material_scoring_scheme", help="scores for material input and output overlaps: [equal products, similar products]")
    parser.add_option("-f", "--function_score_accumulation", dest="accumulation_function", help="function to accumulate symbiosis potential scores into final score")

    global ENERGY_FLOW_SCALING_FUNCTION
    global MATERIAL_FLOW_SCALING_FUNCTION
    global ENERGY_SCORING_SCHEME
    global MATERIAL_SCORING_SCHEME
    global ACCUMULATION_FUNCTION
    global ENERGY_BUCKETS

    (options, args) = parser.parse_args()
    if not options.company_data_path:
        parser.error('path to file containing company data not given')
    if not options.association_table_path:
        parser.error('path to file containing association tables not given')
    if not options.energy_flow_scaling_function:
        print("energy_flow_scaling_function not given - using %s" %ENERGY_FLOW_SCALING_FUNCTION)
    else:
        ENERGY_FLOW_SCALING_FUNCTION = eval(options.energy_flow_scaling_function)
    if not options.energy_flow_buckets:
        print("energy_flow_buckets not given - using %s" %ENERGY_BUCKETS)
    else:
        ENERGY_BUCKETS = eval(options.energy_flow_buckets)
    if not options.material_flow_scaling_function:
        print("material_flow_scaling_function not given - using %s" %MATERIAL_FLOW_SCALING_FUNCTION)
    else:
        MATERIAL_FLOW_SCALING_FUNCTION = eval(options.material_flow_scaling_function)
    if not options.energy_scoring_scheme:
        print("scoring_scheme_energy not given - using %s" %ENERGY_SCORING_SCHEME)
    else:
        ENERGY_SCORING_SCHEME = eval(options.energy_scoring_scheme)
    if not options.material_scoring_scheme:
        print("scoring_scheme_material not given - using %s" %MATERIAL_SCORING_SCHEME)
    else:
        MATERIAL_SCORING_SCHEME = eval(options.material_scoring_scheme)
    if not options.accumulation_function:
        print("function_score_accumulation not given - using %s" %ACCUMULATION_FUNCTION)
    else:
        ACCUMULATION_FUNCTION = eval(options.accumulation_function)
    return (options.association_table_path, options.company_data_path)

def get_data(file_paths):
    return importer.import_data(file_paths[0], file_paths[1])

def get_pairwise_scores(assoc_table, company_data):
    checked = set([])
    res_energy = {}
    res_material = {}
    for i in range(len(company_data)):
        c1 = company_data[i]
        for j in range(len(company_data)):
            c2 = company_data[j]
            # don't match entries with themselves
            if (c1.name == c2.name):
                continue
            if (c1.name, c2.name) in checked:
                continue
            score_vec_energy, score_vec_material = c1.get_symbiosis_potential(c2, assoc_table,
                                        ENERGY_FLOW_SCALING_FUNCTION, MATERIAL_FLOW_SCALING_FUNCTION, 
                                        ENERGY_SCORING_SCHEME, MATERIAL_SCORING_SCHEME,
                                        ENERGY_BUCKETS)
            if not score_vec_energy:
                #sum of empty list (== no potential) is 0
                score_energy = -1000
            else:
                score_energy = ACCUMULATION_FUNCTION(score_vec_energy)
            if not score_vec_material:
                score_material = -1000
            else:
                score_material = ACCUMULATION_FUNCTION(score_vec_material)

            vals_energy = res_energy.get(score_energy, [])
            vals_material = res_material.get(score_material, [])
            vals_energy.append((c1, c2))
            vals_material.append((c1, c2))
            res_energy[score_energy] = vals_energy
            res_material[score_material] = vals_material
            checked.add((c1.name, c2.name))
            checked.add((c2.name, c1.name))
    return (collections.OrderedDict(sorted(res_energy.items())), collections.OrderedDict(sorted(res_material.items())))

def pretty_print(score_dict):
    for key, val in score_dict.items():
        print("\n")
        print(key)
        for v in val:
            print("%s --- %s" %(v[0].name, v[1].name))


def main():
    assoc_table, company_data = get_data(get_user_input())
    for score_dict in get_pairwise_scores(assoc_table, company_data):
        pretty_print(score_dict)
        print("\n\t\t\t+++\t\t\t\n")


if __name__=="__main__":
    main()    
