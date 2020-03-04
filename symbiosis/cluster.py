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
MATERIAL_SCORING_SCHEME = [1.0, 5.0, 10.0]
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
    parser.add_option("-s", "--scoring_scheme_material", dest="material_scoring_scheme", help="factor for material input and output overlaps: [equal HS2 codes, equal HS4 codes, equal HS6 codes]")
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
            energy_symbiosis_potential, material_symbiosis_potential = c1.get_symbiosis_potential(c2, assoc_table,
                                        ENERGY_FLOW_SCALING_FUNCTION_SIZE, MATERIAL_FLOW_SCALING_FUNCTION_SIZE, 
                                        ENERGY_FLOW_SCALING_FUNCTION_YEAR,
                                        MATERIAL_FLOW_SCALING_FUNCTION_YEAR,
                                        MATERIAL_SCORING_SCHEME)
            checked.add((c1.name, c2.name))
            #checked.add((c2.name, c1.name))
            associations = res_energy.get(c1.name, {})
            associations[c2.name] = energy_symbiosis_potential
            res_energy[c1.name] = associations
            associations = res_material.get(c1.name, {})
            associations[c2.name] = material_symbiosis_potential
            res_material[c1.name] = associations
    return (res_energy, res_material)

def pretty_print(score_dict):
    rank = 1
    for n_matches, pair_dict in score_dict.items():
        #print("Number of matches: %s" %n_matches)
        for divergence, company_pair_list in pair_dict.items():
            for company_pair in company_pair_list:
                company1, company2, potential1, potential2 = company_pair
                if potential1.is_empty() and potential2.is_empty():
                    continue
                print("\nRank: %s" %rank)
                print("%s +++ %s" %(company1, company2))
                print("Required inputs vs. outputs divergence score: %s\n" %divergence)
                print("%s --> %s" %(company1, company2))
                print(potential1)
                print("%s --> %s" %(company2, company1))
                print(potential2)
                rank += 1

def rank_energy_symbiosis_potentials(energy_dict):
    d = {}
    ranked = set([])
    for company1, associations_dict in energy_dict.items():
        for company2 in associations_dict.keys():
            if company1+company2 in ranked:
                continue
            potential = associations_dict.get(company2)
            n_overlaps1 = sum([1 for e in [potential.thermal_relative, potential.electrical_relative, potential.chemical_relative, potential.mechanical_relative, potential.conditioned_media_relative] if e != 0.0])
            score_energy_abs = potential.get_score(ACCUMULATION_FUNCTION)
            #get score for pairing of other direction
            potential2 = energy_dict.get(company2).get(company1)
            n_overlaps2 = sum([1 for e in [potential2.thermal_relative, potential2.electrical_relative, potential2.chemical_relative, potential2.mechanical_relative, potential2.conditioned_media_relative] if e != 0.0])
            score_energy_abs2 = potential2.get_score(ACCUMULATION_FUNCTION)
            #first rank according to number of matches
            #then rank according to absolute numbers (sum up; the lower the score the better)
            n_overlaps = n_overlaps1 + n_overlaps2
            score_energy = score_energy_abs + score_energy_abs2
            vals = d.get(n_overlaps, {})
            vals2 = vals.get(score_energy, [])
            vals2.append((company1, company2, potential, potential2))
            vals[score_energy] = vals2
            d[n_overlaps] = collections.OrderedDict(sorted(vals.items()))
            ranked.add(company1+company2)
            ranked.add(company2+company1)
    
    return collections.OrderedDict(sorted(d.items(), reverse=True))

def rank_material_symbiosis_potentials(material_dict):
    d = {}
    ranked = set([])
    for company1, associations_dict in material_dict.items():
        for company2 in associations_dict.keys():
            if company1+company2 in ranked:
                continue
            potential = associations_dict.get(company2)
            n_overlaps1 = sum([1 for e in potential.relative.values() if e != 0.0])
            score_material_abs = potential.get_score(ACCUMULATION_FUNCTION)
            #get score for pairing of other direction
            potential2 = material_dict.get(company2).get(company1)
            n_overlaps2 = sum([1 for e in potential2.relative.values() if e != 0.0])
            score_material_abs2 = potential2.get_score(ACCUMULATION_FUNCTION)
            #first rank according to number of matches
            #then rank according to absolute numbers (sum up; the lower the score the better)
            n_overlaps = n_overlaps1 + n_overlaps2
            score_material = score_material_abs + score_material_abs2
            vals = d.get(n_overlaps, {})
            vals2 = vals.get(score_material, [])
            vals2.append((company1, company2, potential, potential2))
            vals[score_material] = vals2
            d[n_overlaps] = collections.OrderedDict(sorted(vals.items()))
            ranked.add(company1+company2)
            ranked.add(company2+company1)
    
    return collections.OrderedDict(sorted(d.items(), reverse=True))


def main():
    assoc_table, company_data = get_data(get_user_input())
    energy_scores, material_scores = get_pairwise_scores(assoc_table, company_data)
    print("ENERGY SYMBIOSIS:\n")
    pretty_print(rank_energy_symbiosis_potentials(energy_scores))
    print("\n\t\t\t+++\t\t\t\n")
    print("MATERIAL SYMBIOSIS:\n")
    pretty_print(rank_material_symbiosis_potentials(material_scores))


if __name__=="__main__":
    main() 
