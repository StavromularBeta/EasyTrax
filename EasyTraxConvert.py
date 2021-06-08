import os.path
import errno


class EasyTraxConvert:
    """Converts data in an intermediate format to a ready to upload text file in WTX format.

    when passed a dictionary in the format
        key : [value1, value2, value3, [list1], [list2], [list3]... [listx]]
            where key is the sample name
            value1, value2, value3 are sample location code, sample date, sample time
            list1, list2, list3... listx are triplet lists of [analyte, units, value] and
                x is the total amount of analytes for each sample (can be different for each sample)

    A WTX file is produced from this information. A job dictionary, containing simple key : value pairs for
    job-level data (job number, client), is also passed. For each sample, there will be x amount of lines, where
    x is the amount of analytes analyzed for a given sample. Each line therefore represents one test on one sample.
    Samples don't have to have the same amount of lines. Some of the information in these lines will be conserved
    across the job (things like version number, lab ID, client ID). Some of the information will be conserved across
    each sample (like sample name and location code).

    There are 30 fields per line in a WTX report, delimited by the pipe character '|'. Many of these fields are
    optional. MB Labs utilizes 14 mandatory fields in these reports, and none of the optional fields. If a field is not
    being used, it must be fully delimited ('||'). The order these fields appear in is how they are identified.
    Any optional fields that come after all mandatory fields don't need to be included, and can be ignored.

    Information on what these fields are, their order, and their importance can be found in WTX_Report_Format_Doc.pdf,
    which has been included in this program for reference.

    Last Updated: 03June21, P.L.

    Attributes
    ----------
    samples_dictionary : dict
        the dictionary containing sample information. the format is given in the above pre-amble.

    job_dictionary: dict
        the dictionary containing job-level information. Currently only the job number and the client identifier.

    wtx_format_report: list
        the list where WTX formatted report lines are appended once made.

    WaterTraxRequiredFileFieldDict: dict
        a dictionary containing watertrax information that won't change from day to day, such as:
             our lab ID
             client ID's

    WaterTraxAnalyteCodeDict: dict
        a dictionary containing key : value pairs in the format Mb Labs name : [analyte code, WTX description]
            MB Labs name - what we call the analyte on our in house reports
            analyte code - the analyte code provided by watertrax for the given analyte
            WTX description - the WTX description of the analyte name, which can be found in the table of analyte codes
                (these aren't used in the program, but they are for confirmation that we've picked the right code, as
                there can be many different codes for the same analyte with different methodologies).

    WaterTraxUnitsCodeDict: dict
        a dictionary containing key : value pairs in the format unit : unit code

    date_dict:
        used to convert MB labs date formats (02 Jan 21) into WTX date formats (01022021)

    Methods
    -------
    easy_trax_convert_controller()
        called by EasyTraxTK, the main function that controls the class.

    populate_water_trax_report_list()
        creates the WTX report lines for the WTX report. Gets the hard-set values from WaterTraxRequiredFileFieldDict,
        gets the client ID using get_water_trax_client_id(), and then iterates through the samples dictionary,
        turning each triplet list of data into WTX line.

        get_water_trax_client_id()
            matches the passed 'job identifier' key in job_dictionary to a corresponding client id in
            WaterTraxRequiredFileFieldDict[6].

        convert_triplet_list(triplet_list)
            swaps out the mb labs analyte name for an analyte code, the mb labs unit name for a unit code. value isn't
            changed or looked at at this point.

        format_watertrax_date()
            formats the MB labs date format to the WTX format (02-Jan-21 to 01022021)

        format_watertrax_time()
            formats the MB labs time format to the WTX format (13:30p to 13:30)

    print_sample_dictionary_to_console()
        useful for debugging, allows you to print the sample dictionary to the console (prior to it being turned into a
        WTX report)

    generate_report_directories_and_files()
        generates the report directories and files. Reports are added to a folder called WTX_reports, and contained
        in this directory in a folder of the same name.

        mkdir_p()
            tries to make the desired directory.

        safe_open_w()
            safely opens the file in order to write to it.
    """

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
                                               6: [["BC Ferries", "BC Ferry", 11273],
                                                   ["City of Cranbrook", "Cranbrook, City", 17573],
                                                   ["City of Comox", "", 16581],
                                                   ["City of Campbell River", "", 10625],
                                                   ["North Salt Spring Waterworks District", "N. Saltspring", 16672]]
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
                                         'S2-': [320, 'Sulphide (total, as H2S)'],
                                         'T.O.C.': [387, 'Total Organic Carbon / TOC'],
                                         'T&L': [1220, 'Tannins and Lignins'],
                                         'TDS': [207, 'Total Dissolved Solids / TDS'],
                                         'TSS': [15, 'Total Suspended Solids / TSS'],
                                         'Turbidity': [219, 'Turbidity'],
                                         'UVT': [1009, 'UV Transmittance'],
                                         'pH': [228, 'pH'],
                                         'Hardness (mg/L CaCO3)': [360, 'Hardness (Total, as CaCO3)'],
                                         'TN': [744, 'Nitrogen (Total)'],
                                         'Bromate': [181, 'Bromate'],
                                         # METALS
                                         'Al': [174, 'Aluminum (Total)'],
                                         'Al-': [174, 'Aluminum (Total)'],
                                         'Sb': [176, 'Antimony (Total)'],
                                         'As': [26, 'Arsenic (Total)'],
                                         'T.As': [26, 'Arsenic (Total)'],
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
                                       '(ug/g)': 449,
                                       '(%)': 374,
                                       'pH': 115,
                                       '(TCU)': 116,
                                       '(NTU)': 114
                                       }
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
        """executes the various methods/functions in the script in the right order.

        is called in EasyTraxTK. Doesn't return anything, output is written to files
        which are saved onto the computer.
        """

        self.wtx_format_report = self.populate_water_trax_report_list()
        self.generate_report_directories_and_files()

    def populate_water_trax_report_list(self):
        """writes the lines of watertrax code.

        the 5 variables consistent in the report (version_no, transaction_purpose, mb_labs_id, client_id,
        report_id) are going to be the same for every line. We then iterate through the samples in the samples
        dictionary. There are 5 variables consistent in the sample (sample_name, sample_id, sample_location,
        sample_date, sample_time). These will be the same in every line for a particular sample.
        Finally, for each sample, we go through the triplet list [analyte, unit, value] and create a line for
        each triplet. Finally, we check for two conditions, and don't add the list if either condition is true:
        first, that the value is not '---', which indicates that there is no value for the analyte, and that this
        triplet pair is just a placeholder. The second condition checks to see if the analyte has already been
        included in the report for the sample, which can happen if analytes are included in more than one place
        on the report.

        :return: report_lines : list
            the sample dictionary for a given report converted into WTX format. """

        # below variables are the same in every line in the report
        version_no = self.WaterTraxRequiredFileFieldDict[1]
        transaction_purpose = self.WaterTraxRequiredFileFieldDict[2][0]
        mb_labs_id = self.WaterTraxRequiredFileFieldDict[4]
        client_id = self.get_water_trax_client_id()
        report_id = self.job_dictionary['job number']
        report_lines = []
        for key, value in self.samples_dictionary.items():
            # aka for each sample
            analytes_reported = []
            # below variables are the same in every line for a given sample
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
                    # for each test in the sample
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
        """matches a client identifier token to a client id in WaterTraxRequiredFileFieldDict.

         if no client ID is found, an error message is returned. Otherwise, returns a 5 digit code
         representing the client the report belongs to from the value corresponding to key : 6. """

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
        """swaps out the analyte and the unit for an analyte and unit code.

        Found in WaterTraxAnalyteCodeDict and WaterTraxUnitsCodeDict respectively. Does not alter the actual value.
        Might be a good place to check the value isn't '---' in the future.
        """
        converted_list = []
        # Eventually an error will be thrown here when the analyte or unit is not in the dictionary,
        # can then handle. 18May21
        for item in triplet_list:
            converted_list.append([self.WaterTraxAnalyteCodeDict[item[0]][0],
                                   self.WaterTraxUnitsCodeDict[item[1]],
                                   item[2]])
        return converted_list

    def format_watertrax_date(self, date_value):
        """formats our date into the correct WTX format (mmddyyy). """
        day = date_value[0:2]
        month = self.date_dict[date_value[2:5]]
        year = "20" + date_value[5:7]
        wtx_formatted_date = month + day + year
        return wtx_formatted_date

    def format_watertrax_time(self, time_value):
        """formats our time into the correct WTX format (hh:mm). """
        hour = time_value[0:2]
        minute = time_value[3:5]
        wtx_formatted_time = hour + ':' + minute
        return wtx_formatted_time

    def print_sample_dictionary_to_console(self):
        """prints the sample dictionary to the console. """
        for key, value in self.samples_dictionary.items():
            print(key)
            print(value)

    def generate_report_directories_and_files(self):
        """creates a file at a given target and names it based on the jobnumber of the report. The directory is
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
