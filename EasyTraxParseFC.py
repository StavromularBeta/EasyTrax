import itertools

class EasyTraxParseFC:

    def __init__(self, job_number, fc_file):
        self.job_number = job_number
        self.fc_file = fc_file
        self.fc_file_split_lines = []
        self.sample_list_indexes = []
        self.analyte_list_indexes = []
        self.job_dictionary = {}
        self.samples_dictionary = {}
        self.metal_triplets_dictionary = {}

    def easy_trax_parse_controller(self):
        self.split_lines_by_spacing()
        self.get_client_name_and_jobnumber()
        self.look_for_sample_indexes_in_split_lines()
        self.look_for_analyte_indexes_in_split_lines()
        self.use_sample_indexes_to_get_sample_data()
        self.use_analyte_indexes_to_get_sample_data()
        self.combine_metal_triplet_dictionary_with_samples_dictionary()
        return self.samples_dictionary, self.job_dictionary

    def split_lines_by_spacing(self):
        for item in self.fc_file:
            self.fc_file_split_lines.append(item.split())

    def get_client_name_and_jobnumber(self):
        # if you leave a blank line before the start of the header, will need to access self.fc_file_split_lines[1][0:2]
        # otherwise, you want to access the first line.
        self.job_dictionary['client identifier'] = " ".join(self.fc_file_split_lines[0][0:2])
        self.job_dictionary['job number'] = self.get_job_number_from_first_line(self.fc_file_split_lines[0])

    def get_job_number_from_first_line(self, list_to_check):
        # checks to see if there is a 'pg X' after the job number. Checks by seeing if the length of the last element is
        # 7. If it is, it's assumed to be the job number. If it isn't, it's assumed to be the 'pg X' designator, and it
        # is also assumed that the list element before it is the job number.
        if len(list_to_check[-1]) == 7:
            return list_to_check[-1]
        else:
            return list_to_check[-2]

    def look_for_sample_indexes_in_split_lines(self):
        for item in self.fc_file_split_lines:
            if len(item) > 0:
                if item[0] == 'SAMPLE':
                    self.sample_list_indexes.append(self.fc_file_split_lines.index(item))

    def look_for_analyte_indexes_in_split_lines(self):
        for item in self.fc_file_split_lines:
            if len(item) > 0:
                if item[0] == 'ELEMENTS':
                    self.analyte_list_indexes.append(self.fc_file_split_lines.index(item))

    def use_sample_indexes_to_get_sample_data(self):
        for item in self.sample_list_indexes:
            analyte_information = self.get_analyte_information(item)
            units = self.get_units_information(item)
            samples = self.get_samples_data(item)
            samples_binary_list = self.split_samples_into_name_and_information(samples,
                                                                               analyte_information)
            self.generate_samples_dictionary_entries(samples_binary_list)
            self.generate_data_triplets(analyte_information, units, samples_binary_list)

    def get_analyte_information(self, sample_index):
        analyte_information = self.fc_file_split_lines[sample_index - 1]
        if analyte_information[0] == '0':
            analyte_information = analyte_information[1:]
        return analyte_information

    def get_units_information(self, sample_index):
        units = self.fc_file_split_lines[sample_index]
        units = units[3:]
        return units

    def get_samples_data(self, sample_index):
        samples = []
        item_index = sample_index + 2
        blank_counter = 0
        while blank_counter == 0:
            sample = self.fc_file_split_lines[item_index]
            if len(sample) > 0:
                samples.append(sample)
                item_index += 1
            else:
                blank_counter += 1
        return samples

    def split_samples_into_name_and_information(self, samples, analyte_information):
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
                sample_time = sample_name_date_time_list.pop()
                sample_date = sample_name_date_time_list.pop()
                # checks for sampling information. All i can do is look for 5 character sequences with at least 1 number
                # and assume that's the sampling location.
                check_for_digits = False
                if len(sample_name_date_time_list[-1]) == 5:
                    for sub_item in sample_name_date_time_list[-1]:
                        if sub_item.isdigit():
                            check_for_digits = True
                if check_for_digits is True:
                    sampling_information = sample_name_date_time_list.pop()
                else:
                    sampling_information = 'no location'
                sample_name = " ".join(sample_name_date_time_list)
                sample_name_date_time.append([sample_name, sampling_information, sample_date, sample_time])
                sample_information.append(item[index_samples_start_at:])
        return [sample_name_date_time, sample_information]

    def generate_samples_dictionary_entries(self, samples_binary_list):
        for item in samples_binary_list[0]:
            if len(item) == 1:
                if item[0] in self.samples_dictionary:
                    pass
                else:
                    self.samples_dictionary[item[0]] = ["no location", "no date", "no time"]
            else:
                if item[0] in self.samples_dictionary:
                    pass
                else:
                    self.samples_dictionary[item[0]] = [item[1], item[2], item[3]]

    def generate_data_triplets(self, analyte_information, units, samples_binary_list):
        sample_number_index = 0
        for item in samples_binary_list[0]:
            unit_index = 0
            item_index = 0
            sample_name_and_dict_key = item[0]
            for subitem in analyte_information:
                analyte_name = subitem
                if analyte_name == 'pH':
                    analyte_unit = 'pH'
                else:
                    analyte_unit = units[unit_index]
                    unit_index += 1
                value = samples_binary_list[1][sample_number_index][item_index]
                self.samples_dictionary[sample_name_and_dict_key].append([analyte_name, analyte_unit, value])
                item_index += 1
            sample_number_index += 1

    def use_analyte_indexes_to_get_sample_data(self):
        for item in self.analyte_list_indexes:
            total_amount_of_analytes = 33
            current_analyte_index = 0
            index_of_start_of_analyte_rows = item+2
            analyte_rows = []
            triplet_pairs_dictionary = {}
            # last 3 items in the samples list are ('Maximum','Limits','Permissable'), below line removes
            sample_line = self.fc_file_split_lines[item-1][:len(self.fc_file_split_lines[item-1]) - 3]
            # last 3 items in the samples list are ('In','Drinking','Water'), below line removes
            header_line = self.fc_file_split_lines[item][:len(self.fc_file_split_lines[item]) - 3]
            # gets all the relevant analyte rows and adds them to analyte_rows
            while current_analyte_index <= total_amount_of_analytes:
                analyte_row = self.fc_file_split_lines[(index_of_start_of_analyte_rows + current_analyte_index)]
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
            for subitem in analyte_rows:
                try:
                    int(subitem[0][0])
                    analyte_identifier = subitem[2]
                    value_counter = 3
                    for sample_number in sample_line:
                        value = subitem[value_counter]
                        if value[0] == "<":
                            value = 'ND'
                        self.metal_triplets_dictionary[sample_number].append([analyte_identifier,
                                                                              '(' + subitem[-1] + ')',
                                                                              value])
                        value_counter += 1
                except ValueError:
                    analyte_identifier = subitem[0] + ' ' + subitem[1] + ' ' + subitem[2]
                    value_counter = 3
                    for sample_number in sample_line:
                        value = subitem[value_counter]
                        if value[0] == "<":
                            value = 'ND'
                        self.metal_triplets_dictionary[sample_number].append([analyte_identifier,
                                                                              '(' + subitem[-1] + ')',
                                                                              value])
                        value_counter += 1

    def combine_metal_triplet_dictionary_with_samples_dictionary(self):
        samples_dictionary_keys = []
        for key in self.samples_dictionary.keys():
            samples_dictionary_keys.append(key)
        for key, value in self.metal_triplets_dictionary.items():
            for item in samples_dictionary_keys:
                if key in item:
                    key = item
                    for triplet in value:
                        self.samples_dictionary[key].append(triplet)
