class EasyTraxParse:
    """Parses text files generated by the DOS program FirstChoice, prepares data for conversion to WTX format.

    Final reports can be generated by the current MB Labs LIMS system in text format.

    These files contain data displayed vertically (analytes going down the page, samples across), and horizontally
    (analytes going across the page, samples going down). Both data types can be handled together or independently.

    sample metadata is not present in vertically displayed files, so backup sample metadata is gathered from the
    report headers.

    This file parses reports, extracts sample metadata and data from report headers and data tables, and combines
    them all together in one universal data format that is handled by EasyTraxConvert.

    Last Updated: 09June2021, P.L.

    Attributes
    ----------
    job_number : str
        the job number of the report being converted.

    mb_file : list(str)
        the contents of the text file being converted, line by line, in a list.

    mb_file_split_lines : list(list(str))
        each line split based on spaces (ex. ['hello          world I           am',] -> [['hello','world','I','am'],]

    sample_list_indexes : list(int)
        the indexes of each sub list in fc_file_split_lines that have the string 'SAMPLE' at the beginning of the list.
        these are the start points of the horizontal data tables.

    analyte_list_indexes : list(int)
        the indexes of each sub list in fc_file_split_lines that have the string 'ELEMENTS' at the beginning of the
        list. These are the start points of the vertical data tables.

    backup_sample_list_indexes : list(int)
        the indexes of each sub list in fc_file_split_lines that have the string 'Samples:' at the beginning of the
        list. These are the start points of the header sample metadata.

    backup_line_split_by_sample : list(list)
        the individual samples in the header sample metadata, in a list of lists.

    job_dictionary : dict{}
        contains information pertaining to the overall job, like the job number.

    samples_dictionary : dict{}
        contains information pertaining to the samples. Format in this dict is:
        key: sample name (str)
        value: sample locator code, date, time, list of lists (each sub list is a triplet, [analyte, unit, value])

    metal_triplets_dictionary : dict{}
        contains information pertaining to the vertically formatted (analytes down, samples across) samples.
        Temporarily stored in this dictionary, then added to the samples_dictionary. Format:
        key: sample ID (str)
        value: list of data triplets [[analyte, unit, value],[analyte, unit, value],...]

    parse_log : string
        log of the conversion process, various errors can change string, returned after conversion is completed.

    Methods
    -------
    * `easy_trax_parse_controller()` -
        executes the various methods/functions in the script in the right order.

    * `split_lines_by_spacing()` -
        converts each line in self.fc_file into a list, split by spaces.

    * `get_client_name_and_jobnumber()` -
        gets the client name and the job number from the first line of the text file. Jobnumber is also passed to class
        as a parameter (forgot, wrote this unnecessary bit of code, too lazy to delete).

        * `get_job_number_from_first_line(list_to_check)` -
            finds the job number in the first line.

    * `look_for_anchor_indexes_in_split_lines()` -
        looks for the string 'SAMPLE' in the list of lines, adds those indices to self.sample_list_indices.
        looks for the string 'Samples:' in the list of lines, adds those indices to self.backup_sample_list_indices.
        looks for the string 'ELEMENTS' in the list of lines, adds those indices to self.analyte_list_indexes.

    * `pre_generate_backup_samples_dictionary_entries()` -
        if there are any indexes in self.backup_sample_list_indexes, then this method will take them and parse
        the sample header metadata into trimmed lists, consisting of [sample id, name1, ... namex, code, date, time]

    * `use_sample_indexes_to_get_sample_data()` -
        iterates through the indexes in sample_list_indexes, and uses them to fill samples_dictionary with data.

        * `get_analye_information(item)` -
            access the line above the sample index passed, which has the analyte information. Occasionally there
            is a 0 at the start of this line (for whatever reason). If this 0 is found, it's removed.

        * `get_units_information(item)` -
            accesses the line corresponding to the sample index passed. This line has the unit information. Removes
            the first three items in the line, which are the strings 'SAMPLE', 'DATE', and 'TIME'.

        * `get_samples_data(item)` -
            starts at the line at index + 2. This is the first sample line. Grabs each sample line until the sample
            name is "Lab Blank" (note, this wouldn't work if "Lab Blank" wasn't the last sample in the data table,
            and may need to be changed in the future for large jobs that might not necessarily have "Lab Blank" as the
            last sample for a given data table).

        * `split_samples_into_name_and_information(samples, analyte_information)` -
            takes list of samples created by get_samples_data, and, using the analyte_information, splits the sample
            lines into the two lists - one has the name, date, and time for the sample, and the other list has analyte
            values.

        * `generate_samples_dictionary_entries(samples_binary_list)` -
            goes through the various sample names in the samples_binary_list and uses them to make keys in the
            samples_dictionary.

        * `generate_data_triplets(analyte_information, units, samples_binary_list)` -
            matches analye names, units, and values for each analyte, for each sample, and adds data triplets to
            the samples_dictionary under the correct sample name.

    * `generate_backup_samples_dictionary_entries()` -
        takes the lists generated by pre_generate_backup_samples_dictionary_entries and converts them into appropriate
        key: value pairs in samples_dictionary, if the sample is not already in there.

    * `qc_check_for_samples_dictionary_keys_after_backups_made()` -
        checks to see if there are any sample dictionary keys after the backups are made

    * `use_analyte_indexes_to_get_sample_data()`
        iterates through the indexes in analyte_list_indexes, and uses them to fill metal_triplets_dictionary with data.

    * `qc_check_for_metal_triplets_dictionary_keys_after_analyte_indexes()` -
        checks to see if there are analyte indexes available but no metal triplet dictionary keys.

    * `combine_metal_triplet_dictionary_with_samples_dictionary()`
        matches the sample ID keys in metal_triplets_dictionary to sample ID + name keys in samples_dictionary. Once
        matched, adds data in metal_triplets_dictionary to samples_dictionary.
        """

    def __init__(self, job_number, fc_file):
        """
        Parameters
        ----------
        job_number: str
            the job number for the job being converted
        fc_file: str
            the FirstChoice text file being parsed, in string format.
        """

        self.job_number = job_number
        self.mb_file = fc_file
        self.mb_file_split_lines = []
        self.sample_list_indexes = []
        self.backup_sample_list_indexes = []
        self.backup_line_split_by_sample = []
        self.analyte_list_indexes = []
        self.job_dictionary = {}
        self.samples_dictionary = {}
        self.metal_triplets_dictionary = {}
        self.parse_log = ""

    def easy_trax_parse_controller(self):
        """executes the various methods/functions in the script in the right order.

        Is called in EasyTraxTK. Returns the samples_dictionary and job_dictionary to EasyTraxTK
        for passing to the converter.

        Returns
        -------
        samples_dictionary : dict
            dictionary where all sample level information is held.

        job_dictionary : dict
            dictionary where all job level information is held.
        """

        # split up the whole file line by line
        self.split_lines_by_spacing()
        # extract the client name and job number
        self.get_client_name_and_jobnumber()
        # collect anchor indexes
        self.look_for_anchor_indexes_in_split_lines()
        # pre-generate backup sample metadata if there is sample header info
        if self.backup_sample_list_indexes:
            self.pre_generate_backup_samples_dictionary_entries()
        # process the horizontal data tables
        self.use_sample_indexes_to_get_sample_data()
        # create entries of any samples not covered in the horizontal data tables
        self.generate_backup_samples_dictionary_entries()
        # checks for empty samples_dictionary keys, if it is still empty, nothing is going to be written to file.
        self.qc_check_for_samples_dictionary_keys_after_backups_made()
        # finally, process the ICP data files, having dealt with the sample metadata
        self.use_analyte_indexes_to_get_sample_data()
        # checks to see if the metal triplets dictionary has keys, if there are none, ICP data won't be written.
        self.qc_check_for_metal_triplets_dictionary_keys_after_analyte_indexes()
        # combine the metal triplets with the rest of the data triplets
        self.combine_metal_triplet_dictionary_with_samples_dictionary()
        # return the properly formatted intermediate data, ready for conversion
        return self.samples_dictionary, self.job_dictionary, self.parse_log

    def split_lines_by_spacing(self):
        """ converts each line in self.mb_file into a list, split by spaces.
        """

        for item in self.mb_file:
            self.mb_file_split_lines.append(item.split())

    def get_client_name_and_jobnumber(self):
        """gets the client name and the job number from the first line of the text file.

        Jobnumber is also passed to class as a parameter
        (forgot, wrote this unnecessary bit of code, too lazy to delete). """

        # if you leave a blank line before the start of the header, will need to access self.fc_file_split_lines[1][0:2]
        # otherwise, you want to access the first line.
        self.job_dictionary['client identifier'] = " ".join(self.mb_file_split_lines[0][0:2])
        self.job_dictionary['job number'] = self.get_job_number_from_first_line(self.mb_file_split_lines[0])

    def get_job_number_from_first_line(self, list_to_check):
        """finds the job number in the first line.

        checks to see if there is a 'pg X' after the job number. Checks by seeing if the length of the last element is
        7. If it is, it's assumed to be the job number. If it isn't, it's assumed to be the 'pg X' designator, and it
        is also assumed that the list element before it is the job number.

        Parameters
        ----------
        list_to_check : list
            the list to check - the first line of the file, split by space, in list form.

        Returns
        -------
        list_to_check[n] : string
            where n = -1 or -2. The item at index n will be the jobnumber in string form. """

        if len(list_to_check[-1]) == 7:
            return list_to_check[-1]
        else:
            return list_to_check[-2]

    def look_for_anchor_indexes_in_split_lines(self):
        """ looks for anchor indices in the split lines. Adds them to the relevant list. 3 types of anchors.

        first filters out empty lines.

        If a line has something in it, checks to see if the first index is 'SAMPLE'.

        If it is, adds the index of the line to sample_list_indexes. These indexes are used to parse
        horizontal data tables. Uses counter, otherwise will get first instance of list in mb_file_split_lines,
        which can be an issue with tables of the same size, same units, same samples.

        Then checks if the first index is 'Samples:'. If it is, adds the index to backup_sample_list_indexes.

        These indexes are used to parse sample metadata from the header part of the report (name, date, location, etc).
        This information is generally taken from horizontal data tables, and then the ICP data tables piggyback.
        If there are no horizontal data tables, or if there are samples in vertical data tables that aren't present
        in horizontal data tables, we need a second way to get sample metadata. That's what the backup is for.

        Finally checks if the first index is 'ELEMENTS'.

        If it is, adds the index to analyte_list_indexes. These indexes are used to parse vertical ICP style
        data tables.

        At the end of the method, there is functionality to report to the log the amount of data tables picked up,
        and a warning message that fires if you have ICP tables and no backup sample metadata. """

        counter = 0
        for item in self.mb_file_split_lines:
            if len(item) > 0:
                if item[0] == 'SAMPLE':
                    self.sample_list_indexes.append(counter)
                elif item[0] == 'Samples:':
                    self.backup_sample_list_indexes.append(counter)
                elif item[0] == 'ELEMENTS':
                    self.analyte_list_indexes.append(counter)
                else:
                    pass
            counter += 1
        # Error handling
        self.parse_log += '\nThere are ' + str(len(self.sample_list_indexes)) + ' horizontal data tables, \n' +\
            'and ' + str(len(self.analyte_list_indexes)) + ' vertical ICP data tables in this file.\n'
        if len(self.sample_list_indexes) == 0:
            if len(self.backup_sample_list_indexes) == 0:
                self.parse_log += '\nThere is no backup sample data to accompany the ICP data. This build will fail.\n'

    def pre_generate_backup_samples_dictionary_entries(self):
        """generates backup samples dictionary metadata entries, so that ICP formatted data can be properly assigned.

        there may be many indexes, we only need one as all the sample lists should be the same. Will have to deal with
        this if this is not the case in the future (09June21).

        empty_list is used to determine when we've come to a gap in the page, which means we are no longer reading in
        our sample information.

        Once a gap is hit, it's assumed that we've reached the end of the header. We then collapse all the lists of
        lines into one long list. We iterate through this list.

        The first time we hit a parenthesis ')', we know were at the start of a sample. Once we hit another parenthesis,
        we know we are at the start of the next sample.

        This logic is used to split the information up into segments where the last three items will be location code,
        date, and time, the first item will be the sample number, and the remaining indexes when combined in order
        are the sample name. """

        # once we hit a gap in the file, empty_list will be set to true, and we will know we are at the end of the
        # sample information.
        empty_list = False
        # the line that 'Samples: ' is on.
        backup_sample_list_index = self.backup_sample_list_indexes[0]
        backup_sample_lines = []
        while not empty_list:
            backup_samples_line = self.mb_file_split_lines[backup_sample_list_index]
            if len(backup_samples_line) == 0:
                empty_list = True
            else:
                backup_sample_lines.append(backup_samples_line)
                backup_sample_list_index += 1
        # collapsing the lines (which may have more than one sample, or may have one sample) into one list.
        backup_sample_lines = [item for sublist in backup_sample_lines for item in sublist]
        # if keep adding is False, we have hit the next sample, so stops adding
        # starts as false so we don't add all the extra info before the first sample
        # first parenthesis encountered then turns keep_adding to True
        # then we add up the first sample information
        # second parenthesis if keep_adding is true will trigger an appending and a clearing of single_sample
        # keep_adding will now always be true
        keep_adding = False
        single_sample = []
        for item in backup_sample_lines:
            if ')' in item:
                # either the first sample or not
                if keep_adding:
                    # past the first sample
                    self.backup_line_split_by_sample.append(single_sample)
                    single_sample = [item]
                else:
                    # the first sample
                    single_sample.append(item)
                    keep_adding = True
            else:
                # sample information
                if keep_adding:
                    # will only be false prior to hitting the first sample
                    single_sample.append(item)
        self.backup_line_split_by_sample.append(single_sample)

    def use_sample_indexes_to_get_sample_data(self):
        """ iterates through the indexes in sample_list_indexes, and uses them to fill samples_dictionary with data.

        sort of a controller function, mostly calls other functions in the correct order. Each sample index represents
        a data table that needs to be 'harvested'. for data table, the analyte names, units, and values are isolated,
        and then re-assembled in an intermediate format that we use to make the WTX files. """

        for item in self.sample_list_indexes:
            # each item is an index.
            analyte_information = self.get_analyte_information(item)
            units = self.get_units_information(item)
            samples = self.get_samples_data(item)
            samples_binary_list = self.split_samples_into_name_and_information(samples,
                                                                               analyte_information)
            self.generate_samples_dictionary_entries(samples_binary_list)
            self.generate_data_triplets(analyte_information, units, samples_binary_list)

    def get_analyte_information(self, sample_index):
        """gets analyte information from line above sample index.

        sometimes there is a 0 at the start of this line, not sure why. If so, this method removes this character.

        Returns
        -------
        analyte_information : list
            list containing analyte information."""

        analyte_information = self.mb_file_split_lines[sample_index - 1]
        if analyte_information[0] == '0':
            analyte_information = analyte_information[1:]
        return analyte_information

    def get_units_information(self, sample_index):
        """gets units information from line of the sample index.

        removes the first three elements of the list, which are the strings 'sample', 'date', and 'time'.

        Returns
        -------
        units : list
            list containing units information."""

        units = self.mb_file_split_lines[sample_index]
        units = units[3:]
        return units

    def get_samples_data(self, sample_index):
        """returns the lines of data in the horizontal sample tables.

        first line is two indexes ahead of the sample index. While there is information on subsequent lines, lines
        are added to the samples variable (a list). if a line is blank, it signifies the end of the data table, at
        which point the while loop is exited and the sample lines are returned.

        Parameters
        ----------
        sample_index : int
            index in the list of lists representing the mb labs file corresponding to a horizontal data table

        Returns
        -------
        samples : list
            list of list containing lines of the horizontal data table in question
        """

        samples = []
        item_index = sample_index + 2
        blank_counter = 0
        while blank_counter == 0:
            sample = self.mb_file_split_lines[item_index]
            if len(sample) > 0:
                samples.append(sample)
                item_index += 1
            else:
                blank_counter += 1
        return samples

    def split_samples_into_name_and_information(self, samples, analyte_information):
        """splits raw sample lines into two lists - one containing sample name info, and one containing analyte info.

        iterates through samples. First checks to see if sample is a blank, and if so, handles accordingly (no date
        or time).

        If the sample is not a blank, we find the index the sample values start at/ the name information
        ends at. This is equal to the length of the samples list - the length of the analyte_information list (because
        there will be one analyte identifier per value). Uses this to slice off the sample name, location code,
        date, time, and isolate them. If no sampling location is detected, then 'no location' is inserted instead
        (without a sampling location, we can't upload to WaterTrax, so this would be a fatal error).

        Returns
        -------
        sample_name_date_time, sample_information : [list, list]
            2 membered list, first member being a list of sample info, the second being a list of values.
        """

        sample_name_date_time = []
        sample_information = []
        for item in samples:
            if item[0] + " " + item[1] == 'Lab Blank':
                sample_name = item[0] + " " + item[1]
                sample_name_date_time.append([sample_name])
                sample_information.append(item[2:])
            else:
                index_samples_start_at = len(item) - len(analyte_information)
                sample_name_date_time_list = item[:index_samples_start_at]
                # sample_name_date_time_list = [name, sampling location (hopefully), date, time]
                sample_time = sample_name_date_time_list.pop()
                # sample_name_date_time_list = [name, sampling location (hopefully), date]
                sample_date = sample_name_date_time_list.pop()
                # sample_name_date_time_list = [name, sampling location (hopefully)]
                sampling_information = sample_name_date_time_list[-1]
                sampling_information_check = self.check_to_see_if_bad_location_code(sampling_information)
                if sampling_information_check is True:
                    # i.e. if the last item in the sample_name_date_time_list has a length of 5 with at least one int
                    sampling_information = sample_name_date_time_list.pop()
                else:
                    # otherwise, we don't have a sampling location.
                    # all sampling locations have a length of 5 and contain numbers. It's possible a sample name could
                    # meet that criteria (imagine a sample called room1). In which case, it would be erroneously
                    # considered a sample location.
                    sampling_information = 'no location'
                sample_name = " ".join(sample_name_date_time_list)
                sample_name_date_time.append([sample_name, sampling_information, sample_date, sample_time])
                sample_information.append(item[index_samples_start_at:])
        return [sample_name_date_time, sample_information]

    def check_to_see_if_bad_location_code(self, sampling_information):
        # checks for sampling information. All i can do is look for 5 character sequences with at least 1 number
        # and assume that's the sampling location.
        check_for_digits = False
        if len(sampling_information) == 5:
            for sub_item in sampling_information:
                if sub_item.isdigit():
                    check_for_digits = True
        return check_for_digits

    def generate_samples_dictionary_entries(self, samples_binary_list):
        """creates the keys (sample name) in sample dictionary, populates with sample metadata (location, date, time)

        iterates through the items in the first list in each binary list in samples_binary_list. If the key is already
        in the dictionary, we pass (there will n copies of each name in samples_binary_list, with n being the amount
        of horizontal data tables existing in the parsed document).

        if the length of the item is 1, it's a blank, because a sample has a name, location, date, and time. Otherwise,
        the item is assumed to be a sample, and handled accordingly. """

        for item in samples_binary_list[0]:
            if len(item) == 1:
                # is assumed to be a lab blank
                if item[0] in self.samples_dictionary:
                    pass
                else:
                    self.samples_dictionary[item[0]] = ["no location", "no date", "no time"]
            else:
                # is assumed to be a sample
                if item[0] in self.samples_dictionary:
                    pass
                else:
                    self.samples_dictionary[item[0]] = [item[1], item[2], item[3]]

    def generate_data_triplets(self, analyte_information, units, samples_binary_list):
        """ generates data triplets [analyte, unit, value] and adds via the sample name key to the samples dictionary

        iterates through the samples_binary_list[0]. Keeps track of the index using sample_number_index so it can access
        the right list in samples_binary_list[1]. Needs to be a separate unit index and item index because some analytes
        (so far all I've found is pH, but I believe there are others) don't have units. Assembles data triplets, and
        appends them to the list values in samples dictionary.

        Raises
        ------
        IndexError
            issue with a horizontal data table is causing an index mismatch. """

        sample_number_index = 0
        # so we can access the right spot in samples_binary_list[1].
        for item in samples_binary_list[0]:
            unit_index = 0
            # keeps track of where we are in the unit index
            item_index = 0
            # will be the same as the unit index, except where there are no units for a given analyte. In which case,
            # there will be a mismatch (x units will not equal n values), and we need two counters to account for that.
            sample_name_and_dict_key = item[0]
            # this will be the same as the keys now in samples dictionary
            try:
                for subitem in analyte_information:
                    analyte_name = subitem
                    if analyte_name == 'pH':
                        analyte_unit = 'pH'
                        # rather than grabbing units from the units list, we make a custom analyte_unit.
                    else:
                        analyte_unit = units[unit_index]
                        # all other analytes other than pH (so far, 28May21) will have a unit
                        unit_index += 1
                    value = samples_binary_list[1][sample_number_index][item_index]
                    self.samples_dictionary[sample_name_and_dict_key].append([analyte_name, analyte_unit, value])
                    # appending, value is a list.
                    item_index += 1
                sample_number_index += 1
            except IndexError:
                self.parse_log += "\nAt least one horizontal data table has issues preventing\n" +\
                                  "it from being parsed properly.\n\n" +\
                                  "Potential Issues:\n" +\
                                  "1) There is a space in an analyte name, like 'Domoic Acid'.\n" +\
                                  "turn the spaces into underscores, and try again.\n"

    def generate_backup_samples_dictionary_entries(self):
        """generates the backup sample dictionary metadata if no horizontal tables are in the report.

        first looks at whether we have any samples dictionary keys already.

        There are two options that require backup metadata - either there are no horizontal tables,
        or there are samples that exist in vertical data tables that don't exist in subsequent horizontal
        data tables in the file.

        Checks to see if there are any backup sample indices to work on - sometimes, when there is only
        horizontal data in the report, the admin staff don't add in the samples line.

        Each sublist corresponds to a sample. The first two characters of the first item in the sublist
        will be the sample number if the sample is between 10-99. Otherwise, the sample will fail an int
        check because the second character will be a parenthesis, at which point we take just the first character.

        We then check if we already have information on the particular sample. If we don't, we make a new
        samples dictionary entry, and now the ICP data has somewhere to go. """

        # has default because if there are no keys at all, we won't be able to iterate through anything
        # at "for item in samples_dictionary_keys":, and because we're just using this list for matching
        # purposes, 'default' won't get used for anything.
        samples_dictionary_keys = ['default']
        for key in self.samples_dictionary.keys():
            samples_dictionary_keys.append(key)
        if self.backup_line_split_by_sample:
            # there will be a list of lists, so the first if statement will always fire
            # if we went straight to the second statement, we'd get an index not found error if there was nothing
            # doing the above if statement first avoids that
            if self.backup_line_split_by_sample[0]:
                for sublist in self.backup_line_split_by_sample:
                    # below deals with the sample number being either one or two digits
                    sample_number = sublist[0][0:2]
                    try:
                        if int(sample_number):
                            pass
                    except ValueError:
                        sample_number = sublist[0][0:1]
                    sample_already_present = False
                    # if we already have the sample, no need to re-create the entry
                    for item in samples_dictionary_keys:
                        if sample_number in item:
                            sample_already_present = True
                        else:
                            pass
                    # will still be false if we haven't found the sample
                    if not sample_already_present:
                        # making the entry
                        time = sublist.pop()
                        date = sublist.pop()
                        location_code = sublist.pop()
                        location_code_check = self.check_to_see_if_bad_location_code(location_code)
                        if not location_code_check:
                            self.parse_log += '\nBad location code identifier. Code is either longer than\n' +\
                                '5 letters, or doesnt contain a number. WTX file will likely contain errors.\n'
                        sublist[0] = sample_number
                        new_key = ' '.join(sublist)
                        self.samples_dictionary[new_key] = [location_code, date, time]

    def use_analyte_indexes_to_get_sample_data(self):
        """ generates data triplets from ICP data and appends them to the appropriate existing key in samples dict

         iterates through the analyte_list indexes, which are the starting indexes of the ICP tables contained in the
         file being parsed.

         Trims off parts of the data table we don't need (mainly regulatory limit information, which
         WaterTrax doesn't require).

         Analyte rows are read up to a pre-determined amount (total_amount_of_analytes).

         For each sample in the table, a key is made in metal_triplets_dictionary. We then go through the analyte rows
         we read off, and add data triplets from these rows to the relevant keys in metal_triplets_dictionary.

         If the value is below the LOQ (or LOD, not entirely sure how the lab does it), then we will write "<(x)",
         where x is the LOD. We switch these for 'ND', which is what WaterTrax requires (aka non-detect).

         Once metal_triplets_dictionary is populated, it is combined with sample_dictionary using
         self.combine_metal_triplet_dictionary_with_samples_dictionary. """

        for item in self.analyte_list_indexes:
            total_amount_of_analytes = 33
            # actually are 34 analytes, I think - will need to check this. Pretty sure we are currently cutting off
            # pH 02June21.
            current_analyte_index = 0
            index_of_start_of_analyte_rows = item+2
            analyte_rows = []
            triplet_pairs_dictionary = {}
            # last 3 items in the samples list are ('Maximum','Limits','Permissable'), below line removes
            sample_line = self.mb_file_split_lines[item - 1][:len(self.mb_file_split_lines[item - 1]) - 3]
            # last 3 items in the samples list are ('In','Drinking','Water'), below line removes
            header_line = self.mb_file_split_lines[item][:len(self.mb_file_split_lines[item]) - 3]
            # gets all the relevant analyte rows and adds them to analyte_rows
            while current_analyte_index <= total_amount_of_analytes:
                analyte_row = self.mb_file_split_lines[(index_of_start_of_analyte_rows + current_analyte_index)]
                # below removes the drinking water limit information from the analyte rows
                if analyte_row[-1] == 'listed':
                    analyte_row = analyte_row[:len(analyte_row)-3]
                elif analyte_row[-1] == 'AO':
                    analyte_row = analyte_row[:len(analyte_row)-4]
                elif analyte_row[-1] == 'hard':
                    analyte_row = analyte_row[:len(analyte_row)-4]
                else:
                    analyte_row = analyte_row[:len(analyte_row)-2]
                analyte_rows.append(analyte_row)
                current_analyte_index += 1
            for sample_number in sample_line:
                self.metal_triplets_dictionary[sample_number] = []
                # each sample number in the ICP table gets added as a key to metal_triplets_dictionary, and the value
                # is an empty list (similar to how samples_dictionary works). We then start adding data triplet lists
                # to this list.
            for subitem in analyte_rows:
                try:
                    int(subitem[0][0])
                    # indicates a regular metal analyte line '1) Aluminum Al'
                    # in which case, we want 'Al' to be our analyte identifier
                    analyte_identifier = subitem[2]
                    value_counter = 3
                    for sample_number in sample_line:
                        value = subitem[value_counter]
                        if value[0] == "<":
                            # switches out <(x), where x == LOD, to ND
                            value = 'ND'
                        self.metal_triplets_dictionary[sample_number].append([analyte_identifier,
                                                                              '(' + subitem[-1] + ')',
                                                                              value])
                        value_counter += 1
                except ValueError:
                    analyte_identifier = subitem[0] + ' ' + subitem[1] + ' ' + subitem[2]
                    # indicates a non-metal line with more info than just a two letter metal, like 'Hardness (as CaCO3)'
                    # in which case, we want the whole line to be our analyte identifier.
                    value_counter = 3
                    for sample_number in sample_line:
                        value = subitem[value_counter]
                        if value[0] == "<":
                            # switches out <(x), where x == LOD, to ND
                            value = 'ND'
                        self.metal_triplets_dictionary[sample_number].append([analyte_identifier,
                                                                              '(' + subitem[-1] + ')',
                                                                              value])
                        value_counter += 1

    def combine_metal_triplet_dictionary_with_samples_dictionary(self):
        """assimilates metals_triplet_dictionary with samples_dictionary.

        creates a list of samples_dictionary keys. Iterates through metal_triplets_dictionary items, and if the key
        is in one the samples_dictionary_keys, then the value from metal_triplets_dictionary is appended to the
        appropriate samples_dictionary list. This works because the keys (sample names) in samples_dictionary contain
        the sample number, and the keys for metals_triplet_dictionary are the sample numbers. """

        samples_dictionary_keys = []
        for key in self.samples_dictionary.keys():
            samples_dictionary_keys.append(key)
        for key, value in self.metal_triplets_dictionary.items():
            for item in samples_dictionary_keys:
                if key in item[:len(key)]:
                    key = item
                    for triplet in value:
                        self.samples_dictionary[key].append(triplet)

    def qc_check_for_samples_dictionary_keys_after_backups_made(self):
        """checks to see if there are any sample dictionary keys after the backups are made.

        If there aren't, it means that no sample metadata has been gathered, and the overall file conversion will
        certainly fail.
        """

        if len(self.samples_dictionary.keys()) == 0:
            self.parse_log += '\nno samples dictionary keys have been created.\n' +\
                              'script was unable to pull sample information\n' +\
                              'from either horizontal data tables, or\n' +\
                              'header information.\n\n'

    def qc_check_for_metal_triplets_dictionary_keys_after_analyte_indexes(self):
        """checks to see if there are analyte indexes available but no metal triplet dictionary keys.

        This means that at least 1 ICP table has not been parsed properly. """

        if len(self.metal_triplets_dictionary.keys()) == 0:
            if len(self.analyte_list_indexes) > 0:
                self.parse_log += '\nno ICP keys have been created.\n' +\
                                'an issue with the vertical ICP tables\n' +\
                                'has prevented the script from reading data.\n\n' +\
                                'Possible errors:\n\n' +\
                                "1) 'Maximum Limits Permissable in Drinking Water'\n" +\
                                'has been shortened or abbreviated somehow.\n\n' +\
                                "2) Sample numbers are not on the line above the\n" +\
                                "'ELEMENTS' tag.\n\n"



