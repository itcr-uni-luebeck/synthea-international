import csv
import re
import numpy as np, numpy.random

zip_header = ["", "USPS", "ST", "NAME", "ZCTA5", "LAT", "LON"]
demographics_ethnic_group_header = ["WHITE", "HISPANIC", "BLACK", "ASIAN", "NATIVE", "OTHER"]
demographics_age_group_header = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18"]
demographics_income_group_header = ["00..10", "10..15", "15..25", "25..35", "35..50", "50..75", "75..100", "100..150", "150..200", "200..999"]
demographics_education_group_header = ["LESS_THAN_HS", "HS_DEGREE", "SOME_COLLEGE", "BS_DEGREE"]
demographics_header = ["ID", "COUNTY", "NAME", "STNAME", "POPESTIMATE2015", "CTYNAME", "TOT_POP", "TOT_MALE", "TOT_FEMALE"] + \
    demographics_ethnic_group_header + demographics_age_group_header + demographics_income_group_header + demographics_education_group_header

def build_multiremove_pattern(subs):
    "Simultaneously perform all substitutions on the subject string, adapted https://stackoverflow.com/a/765835"
    return '|'.join(f'({p})' for p in subs)


remove_city_name_parts = list([f", ({s})" for s in [".*[Ss]tadt",
                                                    "(gemfr.|gemeindefreies) (Gebiet|Geb.|Bezirk)",
                                                    "Flecken|Marktflecken",
                                                    "Kurort",
                                                    "(Insel|Markt|Burg|Kloster|Nationalpark|Senne)gemeinde",
                                                    "(St|M|GKSt)"]])
remove_city_name_parts_pattern = build_multiremove_pattern(
    remove_city_name_parts)

def generate_random_demographics(keys):
    random_values = np.random.dirichlet(np.ones(len(keys)), size=1).tolist()[0]
    demographics = {k : v for k, v in zip(keys, random_values)}
    return demographics


def remove_gemeindename_parts(gemeindename):
    return re.sub(remove_city_name_parts_pattern, "", gemeindename)


def bundeslandLookup(bundesland_key):
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
        "10": ("Saarland", "SN"),
        "11": ("Berlin", "BE"),
        "12": ("Brandenburg", "BB"),
        "13": ("Mecklenburg-Vorpommern", "MV"),
        "14": ("Sachsen", "SN"),
        "15": ("Sachsen-Anhalt", "ST"),
        "16": ("Thüringen", "TH")
    }.get(bundesland_key, "")


with open("../data/destatis_auszug_gv2q_2020-06-30.csv", mode='r', encoding="utf8") as source_file, \
        open("../src/main/resources/geography/zipcodes.csv", mode='w', newline='') as zipcode_file, \
        open("../src/main/resources/geography/demographics.csv", mode='w', newline='') as demographics_file:

    source_reader = csv.DictReader(source_file, delimiter=',')
    zip_writer = csv.DictWriter(
        zipcode_file, delimiter=',', fieldnames=zip_header)
    demographics_writer = csv.DictWriter(
        demographics_file, delimiter=",", fieldnames=demographics_header)

    zip_writer.writeheader()
    demographics_writer.writeheader()

    line_count = 0
    for i, row in enumerate(source_reader):
        if (not row["Gem"]):  # we only care about proper Gemeinden
            # skip Bundesländer
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
            "POPESTIMATE2015": row["Bevoelkerung_Gesamt"],
            "CTYNAME": gemeindename,
            "TOT_POP": row["Bevoelkerung_Gesamt"],
            "TOT_MALE": row["Bevoelkerung_Maennlich"],
            "TOT_FEMALE": row["Bevoelkerung_Weiblich"]
        }
        demographics_row.update(generate_random_demographics(demographics_ethnic_group_header))
        demographics_row.update(generate_random_demographics(demographics_age_group_header))
        demographics_row.update(generate_random_demographics(demographics_income_group_header))
        demographics_row.update(generate_random_demographics(demographics_education_group_header))

        demographics_writer.writerow(demographics_row)

        line_count += 1
