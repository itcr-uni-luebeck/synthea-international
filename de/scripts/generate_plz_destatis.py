import csv
import re
import numpy as np, numpy.random

rng = numpy.random.default_rng()

def build_multiremove_pattern(subs):
    "Simultaneously perform all substitutions on the subject string, adapted https://stackoverflow.com/a/765835"
    return '|'.join(f'({p})' for p in subs)

def generate_random_demographics(keys, round_digits=5):
    """generate entirely random demographics summing up to one, for the provided keys"""
    random_values = np.random.dirichlet(np.ones(len(keys)), size=1).tolist()[0]
    demographics = {k : round(v, round_digits) for k, v in zip(keys, random_values)}
    return demographics


def remove_gemeindename_parts(gemeindename):
    """remove parts from the gemeindename that are not desired in the output,
    for example 'Stadt' or 'Marktflecken'"""
    return re.sub(remove_city_name_parts_pattern, "", gemeindename)

def read_population_statistics(age_group_header, representation='list'):
    """read the cleaned-up population statistic table downloaded from destatis and parse it to the
    required reprensentation (one of 'array'/'numpy', 'dict' or 'list')"""
    def parse_row(row):
        """helper function to parse the row"""
        if representation == 'array' or representation=="numpy":
            return np.array([float(row[k]) for k in age_group_header])
        elif representation == 'dict':
            return {k : float(row[k]) for k in age_group_header}
        else:
            return [float(row[k]) for k in age_group_header]
    with open("../data/destatis_12411-0012_aufbereitung.CSV", "r", encoding="utf8") as pop_file:
        csv_data = csv.DictReader(pop_file, delimiter=",")
        pop_data = {row["Bundesland"] : parse_row(row) for row in csv_data}
        return pop_data

def warp_population_statistics(population_statistics_numpy, bundesland_name, group_header, jitter_factor=0.25, round_digits=5):
    """retrieve the population statistics available by bundesland and apply random jitter to it
    the jitter_factor is used as a percentage. By default, all values will be warped by lambda 
    in [-25%, 25%] of the minimum of the entire distribution -> so that no values will be below 0"""
    stat = population_statistics_numpy[bundesland_name]
    maximum = jitter_factor * stat.min()
    minimum = maximum * -1
    offsets = rng.uniform(low=minimum, high=maximum, size=stat.shape)
    warped = stat + offsets
    normed = warped / warped.sum()
    as_dict = {k: round(v, round_digits) for k, v in zip(group_header, normed)}
    return as_dict


def bundeslandLookup(bundesland_key):
    """map bundesland keys in the gv2q dataset to strings and abbreviations"""
    return {
        "01": ("Schleswig-Holstein", "SH"),
        "02": ("Hamburg", "HH"),
        "03": ("Niedersachsen", "NI"),
        "04": ("Bremen", "HB"),
        "05": ("Nordrhein-Westfalen", "NW"),
        "06": ("Hessen", "HE"),
        "07": ("Rheinland-Pfalz", "RP"),
        "08": ("Baden-Württemberg", "BW"),
        "09": ("Bayern", "BY"),
        "10": ("Saarland", "SL"),
        "11": ("Berlin", "BE"),
        "12": ("Brandenburg", "BB"),
        "13": ("Mecklenburg-Vorpommern", "MV"),
        "14": ("Sachsen", "SN"),
        "15": ("Sachsen-Anhalt", "ST"),
        "16": ("Thüringen", "TH")
    }.get(bundesland_key, "")

def parse_to_number(data : str, to_int=True):
    """parse numbers in the GV2Q dataset to integers/floats"""
    data = data.replace(" ", "").replace(",", ".").strip()
    if to_int:
        return int(data)
    else:
        return float(data)

def generate_population_demographics(row, round_digits=8):
    """take the (absolute) population demographics in the GV2Q dataset and calculate the
    ratio of male and female inhabitants"""
    total = parse_to_number(row["Bevoelkerung_Gesamt"])

    male_abs = parse_to_number(row["Bevoelkerung_Maennlich"])
    male_rel = float(male_abs) / float(total)
    female_abs = parse_to_number(row["Bevoelkerung_Weiblich"])
    female_rel = float(female_abs) / float(total)

    return {
        "POPESTIMATE2015": total,
        "TOT_POP": total,
        "TOT_MALE": round(male_rel, round_digits),
        "TOT_FEMALE": round(female_rel, round_digits)
    }

if __name__ == "__main__":
    zip_header = ["", "USPS", "ST", "NAME", "ZCTA5", "LAT", "LON"]
    demographics_ethnic_group_header = ["WHITE", "HISPANIC", "BLACK", "ASIAN", "NATIVE", "OTHER"]
    demographics_age_group_header = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
    demographics_income_group_header = ["00..10", "10..15", "15..25", "25..35", "35..50", "50..75", "75..100", "100..150", "150..200", "200..999"]
    demographics_education_group_header = ["LESS_THAN_HS", "HS_DEGREE", "SOME_COLLEGE", "BS_DEGREE"]
    demographics_header = ["ID", "COUNTY", "NAME", "STNAME", "POPESTIMATE2015", "CTYNAME", "TOT_POP", "TOT_MALE", "TOT_FEMALE"] + \
        demographics_ethnic_group_header + demographics_age_group_header + demographics_income_group_header + demographics_education_group_header

    remove_city_name_parts_pattern = build_multiremove_pattern([f", ({s})" for s in [".*[Ss]tadt",
                                                        "(gemfr.|gemeindefreies) ?(Gebiet|Geb.|Bezirk)",
                                                        "Flecken|Marktflecken",
                                                        "Kurort",
                                                        "(Insel|Markt|Burg|Kloster|Nationalpark|Senne)gemeinde",
                                                        "(St|M|GKSt)"]])

    population_statistics_numpy = read_population_statistics(demographics_age_group_header, representation="numpy")
    population_statistics_dict = read_population_statistics(demographics_age_group_header, representation="dict")

    with open("../data/destatis_auszug_gv2q_2020-06-30.csv", mode='r', encoding="utf8") as source_file, \
            open("../src/main/resources/geography/zipcodes.csv", mode='w', newline='', encoding="utf8") as zipcode_file, \
            open("../src/main/resources/geography/demographics.csv", mode='w', newline='', encoding="utf8") as demographics_file:

        source_reader = csv.DictReader(source_file, delimiter=',')
        zip_writer = csv.DictWriter(
            zipcode_file, delimiter=',', fieldnames=zip_header)
        demographics_writer = csv.DictWriter(
            demographics_file, delimiter=",", fieldnames=demographics_header)

        zip_writer.writeheader()
        demographics_writer.writeheader()

        line_count = 0
        for i, row in enumerate(source_reader):
            if not row["Gem"]:  # we only care about proper Gemeinden
                # skip Bundesländer
                continue
            if row["Bevoelkerung_Gesamt"].strip() == "0" :
                # there are some officially uninhabited areas in DE,
                # for example Sachsenwald, SH
                continue

            bundesland_key = row["Land"]
            bundesland_name, bundesland_abbrev = bundeslandLookup(bundesland_key)

            gemeindename = remove_gemeindename_parts(row["Gemeindename"])

            zip_row = {k: v for k, v in zip(zip_header, [
                # use the AGS as the row number in the CSV file, because this column is not used in Synthea
                row["AGS"],
                bundesland_name,
                bundesland_abbrev,
                gemeindename,
                row["PLZ"],
                row["Laengengrad"].replace(",", "."),
                row["Breitengrad"].replace(",", "."),
            ])}
            zip_writer.writerow(zip_row)

            demographics_row = {
                "ID": line_count, "COUNTY": line_count,
                "NAME": gemeindename, "STNAME": bundesland_name,
                "CTYNAME": gemeindename,
            }

            demographics_row.update(generate_population_demographics(row))
            demographics_row.update(generate_random_demographics(demographics_ethnic_group_header))
            
            warped_age_groups = warp_population_statistics(population_statistics_numpy, bundesland_name, demographics_age_group_header)
            demographics_row.update(warped_age_groups)

            demographics_row.update(generate_random_demographics(demographics_income_group_header))
            demographics_row.update(generate_random_demographics(demographics_education_group_header))

            demographics_writer.writerow(demographics_row)

            line_count += 1
