class EasyTraxConvert:

    def __init__(self, samples_dictionary, job_dictionary):
        self.samples_dictionary = samples_dictionary
        self.job_dictionary = job_dictionary
        #WaterTrax File Fields
        self.WaterTraxRequiredFileFieldDict = {
                                               # 1) Version No.
                                               1: "WTX_2.0",
                                               # 2) Transactional Purpose (Original or Replacement report?)
                                               2: ["O", "R"],
                                               # 4) WTX Lab ID
                                               4: 3393,
                                               # 6) WTX Client ID
                                               6: [["BC Ferries", "", 11273],
                                                   ["City of Cranbrook", "Cranbrook, City", 17573],
                                                   ["City of Comox", "", 16581],
                                                   ["City of Campbell River", "", 10625],
                                                   ["North Salt Spring Waterworks District", "", 16672]],
                                               # 8) Report ID (Job number)
                                               8: "",
                                               # 10) Sample ID (Job number -1,2,3 etc.)
                                               10: [],
                                               }
        self.WaterTraxAnalyteCodeDict = {
                                         # MISCELLANEOUS
                                         'Alkalinity': [458, 'Alkalinity (total, as CaC03)'],
                                         'Color': [225, 'Color'],
                                         'NH3-N': [175, 'Ammonia (total, as N)'],
                                         'NO3-N': [361, 'Nitrate (as N)'],
                                         'NO2-N': [199, 'Nitrite (as N)'],
                                         'Cl-': [184, 'Chloride'],
                                         'F-': [188, 'Fluoride'],
                                         'E.C.': [8, 'Conductivity'],
                                         'TKN': [689, 'Total Kjeldahl Nitrogen / TKN'],
                                         'Ortho-PO43--': [748, 'o-Phosphate (as P)'],
                                         'TPO43--P': [3507, 'Phosphate (total, as P)'],
                                         'D.TPO43--P': [3508, 'Phosphate (dissolved, as P)'],
                                         'SO42-': [205, 'Sulphate'],
                                         'T.O.C.': [387, 'Total Organic Carbon / TOC'],
                                         'T&L': [1220, 'Tannins and Lignins'],
                                         'TDS': [207, 'Total Dissolved Solids / TDS'],
                                         'TSS': [15, 'Total Suspended Solids / TSS'],
                                         'Turbidity': [219, 'Turbidity'],
                                         'UVT': [1009, 'UV Transmittance'],
                                         'pH': [228, 'pH'],
                                         'Hardness (mg/L CaCO3)': [360, 'Hardness (Total, as CaCO3)'],
                                         # METALS
                                         'Al': [174, 'Aluminum (Total)'],
                                         'Sb': [176, 'Antimony (Total)'],
                                         'As': [26, 'Arsenic (Total)'],
                                         'Ba': [178, 'Barium (Total)'],
                                         'Be': [179, 'Beryllium (Total)'],
                                         'B': [180, 'Boron (Total)'],
                                         'Cd': [182, 'Cadmium (Total)'],
                                         'Cr': [186, 'Chromium (Total)'],
                                         'Co': [542, 'Cobalt (Total)'],
                                         'Cu': [187, 'Copper (Total)'],
                                         'Au': [1399, 'Gold (Total)'],
                                         'Fe': [189, 'Iron (Total)'],
                                         'La': [1400, 'Lanthanum (total)'],
                                         'Pb': [191, 'Lead (Total)'],
                                         'Mg': [327, 'Magnesium (Total)'],
                                         'Mn': [192, 'Manganese (Total)'],
                                         'Hg': [193, 'Mercury (Total)'],
                                         'Mo': [194, 'Molybdenum (Total)'],
                                         'Ni': [195, 'Nickel (Total)'],
                                         'P': [640, 'Phosphorus (Total)'],
                                         'K': [514, 'Potassium (Total)'],
                                         'Sc': [1401, 'Scandium (Total)'],
                                         'Se': [201, 'Selenium (Total)'],
                                         'Si': [737, 'Silicon (Total, as Si)'],
                                         'Ag': [202, 'Silver (Total)'],
                                         'Na': [203, 'Sodium (Total)'],
                                         'Sr': [697, 'Strontium (Total)'],
                                         'Sn': [703, 'Tin (Total)'],
                                         'Ti': [705, 'Titanium (Total)'],
                                         'W': [1010, 'Tungsten (Total)'],
                                         'V': [414, 'Vanadium (Total)'],
                                         'Zn': [210, 'Zinc (Total)']
                                         }
        self.WaterTraxUnitsCodeDict = {
                                       # UNITS
                                       '(uS/cm)': 369,
                                       '(mg/L)': 111,
                                       '(ug/L)': 390,
                                       '(%)': 374,
                                       'pH': 115
                                       }
        self.WaterTraxReportList = []

    def easy_trax_convert_controller(self):
        self.print_sample_dictionary_to_console()
        self.populate_water_trax_report_list()

    def print_sample_dictionary_to_console(self):
        for key, value in self.job_dictionary.items():
            print(key)
            print(value)
        for key, value in self.samples_dictionary.items():
            print(key)
            print(value)

    def populate_water_trax_report_list(self):
        version_no = self.WaterTraxRequiredFileFieldDict[1]
        # transaction purpose - first index for original, second index for replacement
        transaction_purpose = self.WaterTraxRequiredFileFieldDict[2][0]
        mb_labs_id = self.WaterTraxRequiredFileFieldDict[4]

