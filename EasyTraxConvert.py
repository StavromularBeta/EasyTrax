class EasyTraxConvert:

    def __init__(self, samples_dictionary, job_dictionary):
        self.samples_dictionary = samples_dictionary
        self.job_dictionary = job_dictionary
        #WaterTrax File Fields
        self.WaterTraxRequiredFileFieldDict = {1: "WTX_2.0",
                                               2: ["O", "R"],
                                               4: 3393,
                                               }
        self.WaterTraxAnalyteCodeDict = {'Alkalinity': [458, 'Alkalinity (total, as CaC03)'],
                                         'Color': [225, 'Color'],
                                         'NH3-N': [175, 'Ammonia (total, as N)'],
                                         'NO3-N': [361, 'Nitrate (as N)'],
                                         'NO2-N': [199, 'Nitrite (as N)'],
                                         'Cl-': [184, 'Chloride'],
                                         'F-': [188, 'Fluoride'],
                                         'E.C.': [8, 'Conductivity'],
                                         'TKN': [689, 'Total Kjeldahl Nitrogen / TKN'],
                                         'Mn': [192, 'Manganese (total)'],
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
                                         'pH': [228, 'pH']
                                         }
        self.WaterTraxUnitsCodeDict = {'(uS/cm)': 369,
                                       '(mg/L)': 111,
                                       '(ug/L)': 390,
                                       '(%)': 374,
                                       'pH': 115
                                       }

    def easy_trax_convert_controller(self):
        self.print_sample_dictionary_to_console()

    def print_sample_dictionary_to_console(self):
        for key, value in self.samples_dictionary.items():
            print(key)
            print(value)
