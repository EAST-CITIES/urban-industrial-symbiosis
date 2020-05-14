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
        if len(row) > 15:
            self.lat = row[13]
            self.lon = row[14]
            self.circle = row[15]
        else:
            self.lat = None
            self.lon = None
            self.circle = None

    #TODO (later) also use geo-locations / street networks for ranking
    def get_symbiosis_potential(self, company, assoc_table, 
                                energy_flow_scaling_function_size, material_flow_scaling_function_size,
                                energy_flow_scaling_function_year, material_flow_scaling_function_year,
                                material_scoring_scheme):
        potential_energy = self.get_energy_flow_symbiosis_potential(company, assoc_table,
                                energy_flow_scaling_function_size, energy_flow_scaling_function_year)
        potential_material = self.get_material_flow_symbiosis_potential(company, assoc_table,
                                material_flow_scaling_function_size, material_flow_scaling_function_year, 
                                material_scoring_scheme)
        return (potential_energy, potential_material)

    def __str__(self):
        return "Name: %s; Sector: %s; Products: %s; ISIC v4: %s; Size: %s; Street: %s; Number: %s; Postal Code: %s; Year: %s; Website: %s, Latitude: %s, Longitude: %s, Circle Size: %s" %(self.name, self.sector, [str(p) for p in self.products], self.isic_codes, self.size, self.street, self.number, self.postal_code, self.year, self.website, self.lat, self.lon, self.circle)

    #TODO there should only be one code - else how to combine conflicting flow specifications?
    #for now: use only first code
    def get_energy_flow_symbiosis_potential(self, company, assoc_table, 
                                            energy_flow_scaling_function_size,
                                            energy_flow_scaling_function_year):
        scores = []
        for code in self.isic_codes:
            for code2 in company.isic_codes:
                scores.append(assoc_table.get(code).energy.get_energy_flow_symbiosis_potential(
                    assoc_table.get(code2).energy, energy_flow_scaling_function_size, 
                    energy_flow_scaling_function_year, self.size, company.size, self.year, company.year))
                break
            break
        #print("energy flow symbiosis potential: " + (str(scores)))
        return scores[0]

    #TODO (see energy...)
    def get_material_flow_symbiosis_potential(self, company, assoc_table,
                                            material_flow_scoring_function_size, material_flow_scoring_function_year, 
                                            material_scoring_scheme):
        scores = []
        for code in self.isic_codes:
            for code2 in company.isic_codes:
                scores.append(assoc_table.get(code).materials.get_material_flow_symbiosis_potential(assoc_table.get(code2).materials, material_flow_scoring_function_size, material_flow_scoring_function_year, 
                material_scoring_scheme, self.size, company.size, self.year, company.year))
        #print("material flow symbiosis potential: " + (str(scores)))
        return scores[0]


class EnergySymbiosisPotential:
    max_val = 9999

    def __init__(self):
        self.thermal_absolute = self.max_val
        self.thermal_relative = 0.0
        self.electrical_absolute = self.max_val
        self.electrical_relative = 0.0
        self.chemical_absolute = self.max_val
        self.chemical_relative = 0.0
        self.mechanical_absolute = self.max_val
        self.mechanical_relative = 0.0
        self.conditioned_media_absolute = self.max_val
        self.conditioned_media_relative = 0.0

    def __str__(self):
        return "Missing thermal input: %s (%.2f%% coverage)\nMissing electrical input: %s (%.2f%% coverage)\nMissing chemical input: %s (%.2f%% coverage)\nMissing mechanical input: %s (%.2f%% coverage)\nMissing conditioned media input: %s (%.2f%% coverage)\n" %(self.thermal_absolute, 100*self.thermal_relative, self.electrical_absolute, 100*self.electrical_relative, self.chemical_absolute, 100*self.chemical_relative, self.mechanical_absolute, 100*self.mechanical_relative, self.conditioned_media_absolute, 100*self.conditioned_media_relative)

    def get_score(self, accumulation_function):
        return accumulation_function([self.thermal_absolute, self.electrical_absolute, self.chemical_absolute, self.mechanical_absolute, self.conditioned_media_absolute])

    def is_empty(self):
        return 0 == sum([self.thermal_relative, self.electrical_relative, self.chemical_relative, self.mechanical_relative, self.conditioned_media_relative])

class MaterialSymbiosisPotential:
    max_val = 9999

    def __init__(self):
        self.absolute = {}
        self.relative = {}

    def __str__(self):
        string = ""
        for key in self.absolute.keys():
            string += "Missing input for %s: %s (%s coverage)\n" %(key, self.absolute.get(key), "{:.2%}".format(self.relative.get(key)))
        return string

    def add(self, key, absolute, relative):
        self.absolute[key] = absolute
        self.relative[key] = relative
    
    def get_score(self, accumulation_function):
        if self.absolute.values():
            return accumulation_function(self.absolute.values())
        else:
            return self.max_val

    def is_empty(self):
        return len(self.absolute.values()) == 0

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

        def get_energy_flow_symbiosis_potential(self, energy, weighting_function_size, weighting_function_year, 
                                                size1, size2, year1, year2):
            potential = EnergySymbiosisPotential()
            potential.thermal_absolute, potential.thermal_relative = self.get_potential(self.thermal_in, energy.thermal_out, weighting_function_size, weighting_function_year, size1, size2, year1, year2)
            potential.electrical_absolute, potential.electrical_relative = self.get_potential(self.electrical_in, energy.electrical_out, weighting_function_size, weighting_function_year, size1, size2, year1, year2)
            potential.chemical_absolute, potential.chemical_relative = self.get_potential(self.chemical_in, energy.chemical_out, weighting_function_size, weighting_function_year, size1, size2, year1, year2)
            potential.mechanical_absolute, potential.mechanical_relative = self.get_potential(self.mechanical_in, energy.mechanical_out, weighting_function_size, weighting_function_year, size1, size2, year1, year2)
            potential.conditioned_media_absolute, potential.conditioned_media_relative = self.get_potential(self.conditioned_media_in, energy.conditioned_media_out, weighting_function_size, weighting_function_year, size1, size2, year1, year2)
            return potential

        def get_potential(self, energy1_in, energy2_out, 
                            weighting_function_size, weighting_function_year, size1, size2, year1, year2):
            if energy1_in == 0:
                return 0.0, 0.0
            size_factor_1 = weighting_function_size(size1)
            size_factor_2 = weighting_function_size(size2) 
            
            div_in1_out2_abs = weighting_function_year(year1, (size_factor_1 * energy1_in)) - float(weighting_function_year(year2, (size_factor_2 * energy2_out)))
            div_in1_out2_rel = weighting_function_year(year2, (size_factor_2 * energy2_out)) / float(weighting_function_year(year1, (size_factor_1 * energy1_in)))
            return(div_in1_out2_abs, div_in1_out2_rel)


    class Material:

        def __init__(self, cells):
            self.hs_in_low = self.to_products(cells[0])
            self.hs_in_high = self.to_products(cells[1])
            self.hs_out_products = self.to_products(cells[2])
            self.hs_out_low = self.to_products(cells[3])
            self.hs_out_high = self.to_products(cells[4])

        def __str__(self):
            return "material.HS-In-Low: %s; material.HS-In-High: %s; material.HS-Out-Products: %s; material.HS-Out-Low: %s; material.HS-Out-High: %s" %([str(p) for p in self.hs_in_low], [str(p) for p in self.hs_in_high], [str(p) for p in self.hs_out_products], [str(p) for p in self.hs_out_low], [str(p) for p in self.hs_out_high])

        def to_products(self, cell):
            return [self.Product(code) for code in str(cell).split(";") if code != "None"]

        def get_score(self, scaling_function_size, scaling_function_year, product_similarity_factor, size, year, volume_factor):
            return float(scaling_function_year(year, product_similarity_factor * scaling_function_size(size) * volume_factor))

        def _get_potential(self, scaling_function_size, scaling_function_year, weighting_scheme, product1, product2, size1, size2, year1, year2, volume_factor1, volume_factor2):
            product_similarity = product1.similarity(product2)
            if not product_similarity == -1:
                score1 = self.get_score(scaling_function_size, scaling_function_year, weighting_scheme[product_similarity], size1, year1, volume_factor1)
                score2 = self.get_score(scaling_function_size, scaling_function_year, weighting_scheme[product_similarity], size2, year2, volume_factor2)
                return (score1 - score2, score2 / score1)
            return (None, None)


        #for each product: score for input and output match / overlap (also consider similarity/compatibility...)
        def get_material_flow_symbiosis_potential(self, material, scaling_function_size, scaling_function_year, 
                                                    weighting_scheme, size1, size2, year1, year2):
            potential = MaterialSymbiosisPotential()
            # hs_low == hs_high / 5
            # hs_out == hs_out_high
            # flow == flow_value * ENERGY_FLOW_SCALING_FUNCTION(size)
            for product in self.hs_in_low:
                for p in material.hs_out_low:
                    potential_abs, potential_rel = self._get_potential(scaling_function_size, scaling_function_year, weighting_scheme, product, p, size1, size2, year1, year2, 1, 1)
                    if potential_abs:
                        potential.add(product, potential_abs, potential_rel)
                #products are assumed to be mentioned in one of those categories only (e.g. either in hs_out_products or in hs_out_low or in hs_out_high)
                for p in material.hs_out_products:
                    potential_abs, potential_rel = self._get_potential(scaling_function_size, scaling_function_year, weighting_scheme, product, p, size1, size2, year1, year2, 1, 5)
                    if potential_abs:
                        potential.add(product, potential_abs, potential_rel)
                for p in material.hs_out_high:
                    potential_abs, potential_rel = self._get_potential(scaling_function_size, scaling_function_year, weighting_scheme, product, p, size1, size2, year1, year2, 1, 5)
                    if potential_abs:
                        potential.add(product, potential_abs, potential_rel)
            for product in self.hs_in_high:
                for p in material.hs_out_high:
                    potential_abs, potential_rel = self._get_potential(scaling_function_size, scaling_function_year, weighting_scheme, product, p, size1, size2, year1, year2, 5, 5)
                    if potential_abs:
                        potential.add(product, potential_abs, potential_rel)

                for p in material.hs_out_products:
                    potential_abs, potential_rel = self._get_potential(scaling_function_size, scaling_function_year, weighting_scheme, product, p, size1, size2, year1, year2, 5, 5)
                    if potential_abs:
                        potential.add(product, potential_abs, potential_rel)
                for p in material.hs_out_low:
                    potential_abs, potential_rel = self._get_potential(scaling_function_size, scaling_function_year, weighting_scheme, product, p, size1, size2, year1, year2, 5, 1)
                    if potential_abs:
                        potential.add(product, potential_abs, potential_rel)
            
            return potential

        class Product:

            def __init__(self, hs):
                #leading zeros are omitted at import: fix
                self.hs2 = None
                self.hs4 = None
                self.hs6 = None
                if len(hs) % 2:
                    hs = "0" + hs
                if len(hs) == 2:
                    self.hs2 = hs
                elif len(hs) == 4:
                    self.hs4 = hs
                    self.hs2 = hs[:2]
                elif len(hs) == 6:
                    self.hs6 = hs
                    self.hs4 = hs[:4]
                    self.hs2 = hs[:2]
                self.label = None
                self.desci4 = None
                

            def similarity(self, product):
                if self.hs6 and product.hs6 and (self.hs6 == product.hs6):
                    return 2
                elif self.hs4 and product.hs4 and (self.hs4 == product.hs4):
                    return 1
                elif self.hs2 and product.hs2 and (self.hs2 == product.hs2):
                    return 0
                return -1

            def __str__(self):
                #return "HS-2: %s (%s)" %(self.hs2, self.label)
                return "HS-2: %s; HS-4: %s; HS-6: %s" %(self.hs2, self.hs4, self.hs6)
