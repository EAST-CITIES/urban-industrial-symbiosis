#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import collections
import importer
import sys
import operator
from functools import reduce
from optparse import OptionParser

STANDARD_SIZE = 100.0
STANDARD_YEAR = 1950
ENERGY_FLOW_SCALING_FUNCTION_SIZE = lambda x:float(x) / STANDARD_SIZE
MATERIAL_FLOW_SCALING_FUNCTION_SIZE = lambda x:float(x) / STANDARD_SIZE
#reduce energy value by 0.35% for each year after standard year
ENERGY_FLOW_SCALING_FUNCTION_YEAR = lambda year,value:value - (value * ((year - STANDARD_YEAR) * 0.35) / 100.0)
MATERIAL_FLOW_SCALING_FUNCTION_YEAR = lambda year,value:value - (value * ((year - STANDARD_YEAR) * 0.35) / 100.0)
MATERIAL_SCORING_SCHEME = [1.0, 0.3]
#ACCUMULATION_FUNCTION = lambda x:reduce(operator.__sub__, x)
#ACCUMULATION_FUNCTION = max
#absolute numbers are capped at 0: more than 100% coverage should not yield bonus (absolute scores denote differences between need and coverage)
ACCUMULATION_FUNCTION = lambda x:reduce(operator.__add__, [max(y,0) for y in x])

#def accumulate(scores):
#    return sum([max(score,0) for score in scores])

def get_user_input():
    parser = OptionParser()
    parser.add_option("-c", "--company_data_path", dest="company_data_path",
                  help="path to file containing company data", metavar="FILENAME_COMPANIES")
    parser.add_option("-a", "--association_table_path", dest="association_table_path",
                  help="path to file containing association tables")
    parser.add_option("-e", "--energy_flow_scaling_function_size", dest="energy_flow_scaling_function_size", help="function determining the impact of the company size on energy flows")
    parser.add_option("-m", "--material_flow_scaling_function_size", dest="material_flow_scaling_function_size", help="function determining the impact of the company size on material flows")
    parser.add_option("-y", "--energy_flow_scaling_function_year", dest="energy_flow_scaling_function_year", help="function determining the impact of the company year of establishment on energy flows")
    parser.add_option("-z", "--material_flow_scaling_function_year", dest="material_flow_scaling_function_year", help="function determining the impact of the company year of establishment on material flows")
    parser.add_option("-s", "--scoring_scheme_material", dest="material_scoring_scheme", help="scores for material input and output overlaps: [equal products, similar products]")
    parser.add_option("-f", "--function_score_accumulation", dest="accumulation_function", help="function to accumulate symbiosis potential scores into final score")

    global ENERGY_FLOW_SCALING_FUNCTION_SIZE
    global ENERGY_FLOW_SCALING_FUNCTION_YEAR
    global MATERIAL_FLOW_SCALING_FUNCTION_SIZE
    global MATERIAL_FLOW_SCALING_FUNCTION_YEAR
    global MATERIAL_SCORING_SCHEME
    global ACCUMULATION_FUNCTION

    (options, args) = parser.parse_args()
    if not options.company_data_path:
        parser.error('path to file containing company data not given')
    if not options.association_table_path:
        parser.error('path to file containing association tables not given')
    if not options.energy_flow_scaling_function_size:
        print("energy_flow_scaling_function_size not given - using %s" %ENERGY_FLOW_SCALING_FUNCTION_SIZE)
    else:
        ENERGY_FLOW_SCALING_FUNCTION_SIZE = eval(options.energy_flow_scaling_function_size)
    if not options.material_flow_scaling_function_size:
        print("material_flow_scaling_function_size not given - using %s" %MATERIAL_FLOW_SCALING_FUNCTION_SIZE)
    else:
        MATERIAL_FLOW_SCALING_FUNCTION_SIZE = eval(options.material_flow_scaling_function_size)
    if not options.material_flow_scaling_function_year:
        print("material_flow_scaling_function_year not given - using %s" %MATERIAL_FLOW_SCALING_FUNCTION_YEAR)
    else:
        MATERIAL_FLOW_SCALING_FUNCTION_YEAR = eval(options.material_flow_scaling_function_year)
    if not options.energy_flow_scaling_function_year:
        print("energy_flow_scaling_function_year not given - using %s" %ENERGY_FLOW_SCALING_FUNCTION_YEAR)
    else:
        ENERGY_FLOW_SCALING_FUNCTION_YEAR = eval(options.energy_flow_scaling_function_year)
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
            score_vec_energy_abs, score_vec_energy_rel, score_vec_material_abs, score_vec_material_rel = c1.get_symbiosis_potential(c2, assoc_table,
                                        ENERGY_FLOW_SCALING_FUNCTION_SIZE, MATERIAL_FLOW_SCALING_FUNCTION_SIZE, 
                                        ENERGY_FLOW_SCALING_FUNCTION_YEAR,
                                        MATERIAL_FLOW_SCALING_FUNCTION_YEAR,
                                        MATERIAL_SCORING_SCHEME)
            if not score_vec_energy_abs:
                #sum of empty list (== no potential) is 0
                score_energy_abs = sys.maxsize
            else:
                #print(score_vec_energy_abs)
                score_energy_abs = ACCUMULATION_FUNCTION(score_vec_energy_abs)
            if not score_vec_material_abs:
                score_material_abs = sys.maxsize
            else:
                score_material_abs = ACCUMULATION_FUNCTION(score_vec_material_abs)

            #absolute numbers: score denotes difference, the smaller the better (less than 0 no bonus)
            #relative numbers: score denotes percentage of coverage, the higher the better (more than 1 no bonus)
            vals_energy = res_energy.get(score_energy_abs, [])
            vals_material = res_material.get(score_material_abs, [])
            vals_energy.append((c1, c2, score_vec_energy_abs, score_vec_energy_rel))
            vals_material.append((c1, c2, score_vec_material_abs, score_vec_material_rel))
            res_energy[score_energy_abs] = vals_energy
            res_material[score_material_abs] = vals_material
            checked.add((c1.name, c2.name))
            #checked.add((c2.name, c1.name))
    return (collections.OrderedDict(sorted(res_energy.items())), collections.OrderedDict(sorted(res_material.items())))

def pretty_print(score_dict):
    for key, val in score_dict.items():
        print("\n")
        if not key == sys.maxsize:
            print("Divergence: %s" %key)
        for v in val:
            if not v[2] and not v[3]:
                print("%s --- %s\n%s\n" %(v[0].name, v[1].name, "(no symbiosis potential)"))
            else:    
                print("%s --- %s\n%s\n%s\n" %(v[0].name, v[1].name, v[2], v[3]))


def main():
    assoc_table, company_data = get_data(get_user_input())
    energy_scores, material_scores = get_pairwise_scores(assoc_table, company_data)
    print("ENERGY SYMBIOSIS:\n")
    pretty_print(energy_scores)
    print("\n\t\t\t+++\t\t\t\n")
    print("MATERIAL SYMBIOSIS:\n")
    pretty_print(material_scores)


if __name__=="__main__":
    main() 
