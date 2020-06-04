# coding: latin-1

import csv

def addAbbr(bundesland):
	switcher = {
        "Brandenburg": "Brandenburg,BB,",
        "Berlin":"Berlin,BE",
        "Baden-Württemberg":"Baden-Württemberg,BW",
        "Bayern":"Bayern,BY",
        "Bremen":"Bremen,HB",
        "Hessen":"Hessen,HE",
        "Hamburg":"Hamburg,HH",
        "Mecklenburg-Vorpommern":"Mecklenburg-Vorpommern,MV",
        "Niedersachsen":"Niedersachsen,NI",
        "Nordrhein-Westfalen":"Nordrhein-Westfalen,NW",
        "Rheinland-Pfalz":"Rheinland-Pfalz,RP",
        "Schleswig-Holstein":"Schleswig-Holstein,SH",
        "Saarland":"Saarland,SN",
        "Sachsen":"Sachsen,SN",
        "Sachsen-Anhalt":"Sachsen-Anhalt,ST",
        "Thüringen":"Thüringen,TH"}
	return switcher.get(bundesland, "")

plz_lookup = {}

with open('../data/zuordnung_plz_ort.csv', mode='r') as plz_file:
	plz_reader = csv.reader(plz_file, delimiter=';')
	line_count = 0
	for row in plz_reader:
		if line_count > 0:
			print("".join(row))
			plz_lookup[row[2]]=addAbbr(row[3])
			line_count+=1
		else:
			line_count+=1

with open('../data/postleitzahlen-deutschland.csv', mode='r') as source_file:
	with open('../src/main/resources/geography/zipcodes.csv', 'w') as target_file:
		source_reader = csv.reader(source_file, delimiter=';')
		line_count = 0
		for row in source_reader:
			if line_count == 0:
				target_file.write(",USPS,ST,NAME,ZCTA5,LAT,LON\n")
				line_count+=1
			else:
				#,USPS,ST,NAME,ZCTA5,LAT,LON
				#1,Brandenburg,BB,Potsdam,14467, XX, XX,

				if len(row[3]) == 4:
					row[3]="0"+row[3]

				if not row[3] in plz_lookup.keys():
					continue

				if len(row[0]) > 0:
					lat_lon = row[0].rstrip().split(",")
					target_file.write("%s,%s,%s,%s,%s,%s \n" % (str(line_count),plz_lookup[row[3]],row[2],row[3],lat_lon[0],lat_lon[1]))
				print(row[0].split(","))
				line_count+=1
	print("Print line: %s" % (str(line_count)))
	target_file.close()

