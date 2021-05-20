import os.path
import errno


class EasyTraxConvert:

    def __init__(self, samples_dictionary, job_dictionary):
        self.samples_dictionary = samples_dictionary
        self.job_dictionary = job_dictionary
        self.wtx_format_report = []
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
                                                   ["North Salt Spring Waterworks District", "", 16672]]
                                               }
        self.WaterTraxAnalyteCodeDict = {
                                         # MISCELLANEOUS
                                         'Alkalinity': [458, 'Alkalinity (total, as CaC03)'],
                                         'Colour': [225, 'Color'],
                                         'NH3-N': [175, 'Ammonia (total, as N)'],
                                         'NO3-N': [361, 'Nitrate (as N)'],
                                         'NO2-N': [199, 'Nitrite (as N)'],
                                         'Cl-': [184, 'Chloride'],
                                         'F-': [188, 'Fluoride'],
                                         'E.C.': [8, 'Conductivity'],
                                         'TKN': [689, 'Total Kjeldahl Nitrogen / TKN'],
                                         'Ortho-PO43--': [748, 'o-Phosphate (as P)'],
                                         'Ortho-PO43--P': [748, 'o-Phosphate (as P)'],
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
                                         'TN': [744, 'Nitrogen (Total)'],
                                         # METALS
                                         'Al': [174, 'Aluminum (Total)'],
                                         'Al-': [174, 'Aluminum (Total)'],
                                         'Sb': [176, 'Antimony (Total)'],
                                         'As': [26, 'Arsenic (Total)'],
                                         'Ba': [178, 'Barium (Total)'],
                                         'Be': [179, 'Beryllium (Total)'],
                                         'B': [180, 'Boron (Total)'],
                                         'Ca': [150, 'Calcium (Total)'],
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
                                       'pH': 115,
                                       '(TCU)': 116,
                                       '(NTU)': 114
                                       }
        self.WaterTraxReportList = []
        self.date_dict = {'Jan': '01',
                          'Feb': '02',
                          'Mar': '03',
                          'Apr': '04',
                          'May': '05',
                          'Jun': '06',
                          'Jul': '07',
                          'Aug': '08',
                          'Sep': '09',
                          'Oct': '10',
                          'Nov': '11',
                          'Dec': '12'}

    def easy_trax_convert_controller(self):
        self.wtx_format_report = self.populate_water_trax_report_list()
        self.generate_report_directories_and_files()

    def populate_water_trax_report_list(self):
        version_no = self.WaterTraxRequiredFileFieldDict[1]
        transaction_purpose = self.WaterTraxRequiredFileFieldDict[2][0]
        mb_labs_id = self.WaterTraxRequiredFileFieldDict[4]
        client_id = self.get_water_trax_client_id()
        report_id = self.job_dictionary['job number']
        report_lines = []
        for key, value in self.samples_dictionary.items():
            analytes_reported = []
            sample_name = key
            sample_id = sample_name.split(" ")[0]
            if sample_name == 'Lab Blank':
                pass
            else:
                sample_location = value[0]
                sample_date = self.format_watertrax_date(value[1])
                sample_time = self.format_watertrax_time(value[2])
                triplet_list = self.convert_triplet_list(value[3:])
                for value_triplet in triplet_list:
                    analyte_code = value_triplet[0]
                    unit_code = value_triplet[1]
                    value = value_triplet[2]
                    wtx_format_line = str(version_no) + '|' + str(transaction_purpose) + '|F|' + str(mb_labs_id) +\
                        '||' + str(client_id) + '|' + str(sample_location) + '|' + str(report_id) + 'T||' +\
                        self.job_dictionary['job number'] + '-' + str(sample_id) +\
                        '||' + str(sample_date) + '|' + str(sample_time) + '|||' + str(analyte_code) +\
                        '|' + str(value) + '|' + str(unit_code)
                    if value == '---':
                        pass
                    elif analyte_code in analytes_reported:
                        pass
                    else:
                        report_lines.append(wtx_format_line)
                        analytes_reported.append(analyte_code)
        return report_lines

    def get_water_trax_client_id(self):
        client_identifier = self.job_dictionary['client identifier']
        value_to_return = ""
        for item in self.WaterTraxRequiredFileFieldDict[6]:
            if item[1] == client_identifier:
                value_to_return = item[2]
        if value_to_return == "":
            return "No client ID"
        else:
            return value_to_return

    def convert_triplet_list(self, triplet_list):
        converted_list = []
        # Eventually an error will be thrown here when the analyte or unit is not in the dictionary,
        # can then handle. 18May21
        for item in triplet_list:
            converted_list.append([self.WaterTraxAnalyteCodeDict[item[0]][0],
                                   self.WaterTraxUnitsCodeDict[item[1]],
                                   item[2]])
        return converted_list

    def format_watertrax_date(self, date_value):
        day = date_value[0:2]
        month = self.date_dict[date_value[2:5]]
        year = "20" + date_value[5:7]
        wtx_formatted_date = month + day + year
        return wtx_formatted_date

    def format_watertrax_time(self, time_value):
        hour = time_value[0:2]
        minute = time_value[3:5]
        wtx_formatted_time = hour + ':' + minute
        return wtx_formatted_time

    def print_sample_dictionary_to_console(self):
        for key, value in self.samples_dictionary.items():
            print(key)
            print(value)

    def generate_report_directories_and_files(self):
        """creates a file at a given target and names it based on the key in finished_reports_dictionary - the key will
        be the 6 digit job number for multi sample reports, and the -XX number for single reports. The directory is
        always named using the 6 digit job number. """
        target = r'T:\ANALYST WORK FILES\Peter\EasyTrax\WTX_reports\ '
        try:
            jobnumber = str(self.job_dictionary['job number'])
            filename = target[:-1] + jobnumber[0:7] + '\\' + jobnumber + '.txt'
            filename = filename.replace('/', '-')
            with self.safe_open_w(filename) as f:
                for item in self.wtx_format_report:
                    f.write(item)
                    f.write('\n')
        except OSError:
            pass

    def mkdir_p(self, path):
        """tries to make the directory."""
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def safe_open_w(self, path):
        """ Open "path" for writing, creating any parent directories as needed. """
        self.mkdir_p(os.path.dirname(path))
        return open(path, 'w')
