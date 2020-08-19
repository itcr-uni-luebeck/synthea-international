import csv
import shutil
import os

mii_filename = "../data/mii-hospitals.csv"
destination_path = "../src/main/resources/providers/"
hospitals_path = os.path.join(destination_path, "hospitals-de.csv")
primary_care_path = os.path.join(
    destination_path, "primary_care_facilities-de.csv")
urgent_care_path = os.path.join(
    destination_path, "urgent_care_facilities-de.csv")
va_path = os.path.join(destination_path, "va_facilities-de.csv")

primary_care_passthrough = ['name', 'address',
                            'city', 'state', 'zip', "phone", 'LAT', 'LON']
primary_care_static = {'hasSpecialties': False}
primary_care_blank = ["ADDICTION MEDICINE", "ADVANCED HEART FAILURE AND TRANSPLANT CARDIOLOGY", "ALLERGY/IMMUNOLOGY", "ANESTHESIOLOGY", "ANESTHESIOLOGY ASSISTANT", "AUDIOLOGIST", "CARDIAC ELECTROPHYSIOLOGY", "CARDIAC SURGERY", "CARDIOVASCULAR DISEASE (CARDIOLOGY)", "CERTIFIED NURSE MIDWIFE", "CERTIFIED REGISTERED NURSE ANESTHETIST", "CHIROPRACTIC", "CLINICAL NURSE SPECIALIST", "CLINICAL PSYCHOLOGIST", "CLINICAL SOCIAL WORKER", "COLORECTAL SURGERY (PROCTOLOGY)", "CRITICAL CARE (INTENSIVISTS)", "DENTIST", "DERMATOLOGY", "DIAGNOSTIC RADIOLOGY", "EMERGENCY MEDICINE", "ENDOCRINOLOGY", "FAMILY PRACTICE", "GASTROENTEROLOGY", "GENERAL PRACTICE", "GENERAL SURGERY", "GERIATRIC MEDICINE", "GERIATRIC PSYCHIATRY", "GYNECOLOGICAL ONCOLOGY", "HAND SURGERY", "HEMATOLOGY", "HEMATOLOGY/ONCOLOGY", "HEMATOPOIETIC CELL TRANSPLANTATION AND CELLULAR TH", "HOSPICE/PALLIATIVE CARE", "HOSPITALIST", "INFECTIOUS DISEASE", "INTERNAL MEDICINE", "INTERVENTIONAL CARDIOLOGY",
                      "INTERVENTIONAL PAIN MANAGEMENT", "INTERVENTIONAL RADIOLOGY", "MAXILLOFACIAL SURGERY", "MEDICAL ONCOLOGY", "NEPHROLOGY", "NEUROLOGY", "NEUROPSYCHIATRY", "NEUROSURGERY", "NUCLEAR MEDICINE", "NURSE PRACTITIONER", "OBSTETRICS/GYNECOLOGY", "OCCUPATIONAL THERAPY", "OPHTHALMOLOGY", "OPTOMETRY", "ORAL SURGERY", "ORTHOPEDIC SURGERY", "OSTEOPATHIC MANIPULATIVE MEDICINE", "OTOLARYNGOLOGY", "PAIN MANAGEMENT", "PATHOLOGY", "PEDIATRIC MEDICINE", "PERIPHERAL VASCULAR DISEASE", "PHYSICAL MEDICINE AND REHABILITATION", "PHYSICAL THERAPY", "PHYSICIAN ASSISTANT", "PLASTIC AND RECONSTRUCTIVE SURGERY", "PODIATRY", "PREVENTATIVE MEDICINE", "PSYCHIATRY", "PULMONARY DISEASE", "RADIATION ONCOLOGY", "REGISTERED DIETITIAN OR NUTRITION PROFESSIONAL", "RHEUMATOLOGY", "SLEEP MEDICINE", "SPEECH LANGUAGE PATHOLOGIST", "SPORTS MEDICINE", "SURGICAL ONCOLOGY", "THORACIC SURGERY", "UNDEFINED PHYSICIAN TYPE (SPECIFY)", "UROLOGY", "VASCULAR SURGERY"]
primary_care_header = primary_care_passthrough + \
    list(primary_care_static.keys()) + primary_care_blank + ["id"]

va_passthrough = ['id', 'name', 'address', 'city', 'state', 'zip',
                  "phone", 'ownership', 'emergency', 'quality', 'LAT', 'LON']
va_static = {"type": "VA Facility"}
va_blank = ["EBTPU", "PCT", "PRRP", "SIPU",
            "PTSD_DOM", "DH", "WSDTT", "SUPT", "WTRP"]
va_header = va_passthrough + list(va_static.keys()) + va_blank


def extract_passthrough(row: dict, passthrough: list):
    return {k: row[k] for k in passthrough}


def set_blank(blank: list):
    return {k: None for k in blank}


def generate_id(out_row: dict, row_id: int, id_key="id", prefix=""):
    out_row[id_key] = f"{prefix}{row_id}"


if __name__ == "__main__":
    # copy mii hospitals to hospitals
    shutil.copyfile(mii_filename, hospitals_path)
    with open(mii_filename, "r", encoding="utf8") as mii_f, \
            open(primary_care_path, "w", encoding="utf8", newline='') as pc_f, \
            open(urgent_care_path, "w", encoding="utf8", newline='') as uc_f, \
            open(va_path, "w", encoding="utf8", newline='') as va_f:
        mii = csv.DictReader(mii_f)
        pc = csv.DictWriter(pc_f, fieldnames=primary_care_header)
        # passes through row unmodified
        uc = csv.DictWriter(uc_f, fieldnames=mii.fieldnames)
        va = csv.DictWriter(va_f, fieldnames=va_header)

        pc.writeheader()
        uc.writeheader()
        va.writeheader()

        for row_id, row in enumerate(mii):
            pc_row = {}
            pc_row.update(extract_passthrough(row, primary_care_passthrough))
            pc_row.update(primary_care_static)
            pc_row.update(set_blank(primary_care_blank))
            generate_id(pc_row, row_id + 1, prefix="PCP")
            pc.writerow(pc_row)

            uc.writerow(row)

            va_row = {}
            va_row.update(extract_passthrough(row, va_passthrough))
            va_row.update(va_static)
            va_row.update(set_blank(va_blank))
            va.writerow(va_row)
