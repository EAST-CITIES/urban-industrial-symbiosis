#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Company:

    def __init__(self, row):
        self.name = row[0].replace("\n", " ")
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
    def get_symbiosis_potential(self, company, assoc_table, 
                                energy_flow_scaling_function, material_flow_scaling_function,
                                material_scoring_scheme):
        potential_energy = self.get_energy_flow_symbiosis_potential(company, assoc_table,
                                energy_flow_scaling_function)
        potential_material = self.get_material_flow_symbiosis_potential(company, assoc_table,
                                material_flow_scaling_function, material_scoring_scheme)
        return (potential_energy, potential_material)

    def __str__(self):
        return "Name: %s; Sector: %s; Products: %s; ISIC v4: %s; Size: %s; Street: %s; Number: %s; Postal Code: %s; Year: %s; Website: %s" %(self.name, self.sector, [str(p) for p in self.products], self.isic_codes, self.size, self.street, self.number, self.postal_code, self.year, self.website)

    #TODO there should only be one code - else how to combine conflicting flow specifications?
    #for now: use only first code
    def get_energy_flow_symbiosis_potential(self, company, assoc_table, 
                                            energy_flow_scaling_function):
        scores = []
        for code in self.isic_codes:
            for code2 in company.isic_codes:
                scores.extend(assoc_table.get(code).energy.get_energy_flow_symbiosis_potential(
                    assoc_table.get(code2).energy, energy_flow_scaling_function, 
                    self.size, company.size))
                break
            break
        #print("energy flow symbiosis potential: " + (str(scores)))
        return scores

    #TODO (see energy...)
    def get_material_flow_symbiosis_potential(self, company, assoc_table,
                                            material_flow_scoring_function, material_scoring_scheme):
        scores = []
        for code in self.isic_codes:
            for code2 in company.isic_codes:
                scores.extend(assoc_table.get(code).materials.get_material_flow_symbiosis_potential(assoc_table.get(code2).materials, material_flow_scoring_function, material_scoring_scheme, self.size, company.size))
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

        def get_energy_flow_symbiosis_potential(self, energy, weighting_function, size1, size2):
            return [score for score in [self.get_potential(self.thermal_in, energy.thermal_out, self.thermal_out, energy.thermal_in, weighting_function, size1, size2), 
                    self.get_potential(self.electrical_in, energy.electrical_out, self.electrical_out, energy.electrical_in, weighting_function, size1, size2), 
                    self.get_potential(self.chemical_in, energy.chemical_out, self.chemical_out, energy.chemical_in, weighting_function, size1, size2), 
                    self.get_potential(self.mechanical_in, energy.mechanical_out, self.mechanical_out, energy.mechanical_in, weighting_function, size1, size2), 
                    self.get_potential(self.conditioned_media_in, energy.conditioned_media_out, self.conditioned_media_out, energy.conditioned_media_in, weighting_function, size1, size2)] if score]

        def get_potential(self, energy1_in, energy2_out, energy1_out, energy2_in, 
                            weighting_function, size1, size2):
            if energy1_in + energy2_out + energy1_out + energy2_in == 0:
                return None
            size_factor_1 = weighting_function(size1)
            size_factor_2 = weighting_function(size2)
            
            div_in1_out2 = -1 * abs((size_factor_1 * energy1_in) - size_factor_2 * energy2_out)
            div_in2_out1 = -1 * abs((size_factor_1 * energy1_out) - size_factor_2 * energy2_in)

            #return the better of the two scores (direction of the flow does not matter for the score)
            return max(div_in1_out2, div_in2_out1)


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
        def get_material_flow_symbiosis_potential(self, material, scaling_function, weighting_scheme, size1, size2):
            matches = []
            # hs_low == hs_high / 5
            # hs_out == hs_out_high
            # flow == flow_value * ENERGY_FLOW_SCALING_FUNCTION(size)
            
            for product in self.hs_in_low:
                for p in material.hs_out_low:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0] * abs((scaling_function(size1) - scaling_function(size2))))
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1] * abs((scaling_function(size1) - scaling_function(size2))))

                for p in material.hs_out_products:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0] * abs((scaling_function(size1) - scaling_function(size2) * 5)))
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1] * abs((scaling_function(size1) - scaling_function(size2) * 5)))

                for p in material.hs_out_high:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0] * abs((scaling_function(size1) - scaling_function(size2) * 5)))
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1] * abs((scaling_function(size1) - scaling_function(size2) * 5)))

            for product in self.hs_in_high:
                for p in material.hs_out_high:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0] * abs((scaling_function(size1) - scaling_function(size2))))
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1] * abs((scaling_function(size1) - scaling_function(size2))))
                for p in material.hs_out_products:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0] * abs((scaling_function(size1) - scaling_function(size2))))
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1] * abs((scaling_function(size1) - scaling_function(size2))))
                for p in material.hs_out_low:
                    if product.similarity(p) == 1:
                        matches.append(weighting_scheme[0] * abs((scaling_function(size1) * 5 - scaling_function(size2)))) 
                    elif product.similarity(p) == 0.5:
                        matches.append(weighting_scheme[1] * abs((scaling_function(size1) * 5 - scaling_function(size2)))) 
            return [score * -1 for score in matches] #the numbers are the differences; but the scale should be: the higher the better (smaller differences are better)

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
