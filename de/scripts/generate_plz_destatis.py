import csv
import re

zip_header = ["", "USPS", "ST", "NAME", "ZCTA5", "LAT", "LON"]
demographics_header = []


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

    zip_writer.writeheader()

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

        line_count += 1
