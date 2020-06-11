import csv
import yaml

fieldnames = ["Name", "Count"]
street_data = {
    "type": ["Straße", "Str.", "Allee", "Weg"],
    "secondary": ["Apartment", "Appartement", "Stockwerk"]
}

name_data = {}


def read_file_to(filename, encoding="utf8", names=fieldnames):
    with open(filename, "r", encoding=encoding) as csv_file:
        read_data = csv.DictReader(csv_file, fieldnames=names)
        list_data = [f[names[0]] for f in read_data]
        return f"[{','.join(list_data)}]"


def dump_dict(d, indent=0):
    output = ""
    indent_string = " " * indent
    if (type(d) is dict):
        for k, v in d.items():
            output += f"{indent_string}{k}:"
            if (type(v) is dict):
                output += "\n" + dump_dict(v, indent=indent+2)
                output += "\n"
            else:
                output += f" {v}\n"   
        return output
    else:
        return f"{indent_string}{d}\n"


def dump(filename, lang_key="english"):
    with open(filename, "w", encoding="utf8") as target_file:
        whole_dict = {lang_key: name_data, "street": street_data}
        d = dump_dict(whole_dict)
        target_file.write(d)


if __name__ == "__main__":

    name_data["family"] = read_file_to("../data/names/family.csv")
    name_data["M"] = read_file_to("../data/names/male.csv")
    name_data["F"] = read_file_to("../data/names/female.csv")

    dump("../src/main/resources/names.yml")


# with open("../data/names/family.csv", "r", encoding="utf8") as fam_file:
#     fam_data = csv.DictReader(fam_file, fieldnames=fieldnames)
#     print(fam_data)
#     english_data["family"] = [f["Name"] for f in fam_data]
