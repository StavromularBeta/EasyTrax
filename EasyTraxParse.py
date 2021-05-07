class EasyTraxParse:

    def __init__(self, job_number, chm_file):
        self.job_number = job_number
        self.chm_file = chm_file
        self.chm_file_split_lines = []
        self.sample_list_indexes = []
        self.job_dictionary = {}
        self.samples_dictionary = {}

    def easy_trax_parse_controller(self):
        self.split_lines_by_spacing()
        self.look_for_sample_indexes_in_split_lines()
        self.use_sample_indexes_to_get_sample_data()
        self.print_sample_dictionary_to_console()

    def split_lines_by_spacing(self):
        for item in self.chm_file:
            self.chm_file_split_lines.append(item.split())

    def look_for_sample_indexes_in_split_lines(self):
        for item in self.chm_file_split_lines:
            if len(item) > 0:
                if item[0] == 'SAMPLE':
                    self.sample_list_indexes.append(self.chm_file_split_lines.index(item))

    def use_sample_indexes_to_get_sample_data(self):
        for item in self.sample_list_indexes:
            analyte_information = self.get_analyte_information(item)
            units = self.get_units_information(item)
            samples = self.get_samples_data(item)
            index_samples_start_at = len(samples[0]) - len(analyte_information)
            samples_binary_list = self.split_samples_into_name_and_information(index_samples_start_at, samples)
            self.generate_samples_dictionary_entries(samples_binary_list)
            self.generate_data_triplets(analyte_information, units, samples_binary_list)

    def get_analyte_information(self, sample_index):
        analyte_information = self.chm_file_split_lines[sample_index - 1]
        if analyte_information[0] == '0':
            analyte_information = analyte_information[1:]
        return analyte_information

    def get_units_information(self, sample_index):
        units = self.chm_file_split_lines[sample_index]
        units = units[3:]
        return units

    def get_samples_data(self, sample_index):
        samples = []
        item_index = sample_index + 2
        blank_counter = 0
        while blank_counter == 0:
            sample = self.chm_file_split_lines[item_index]
            if len(sample) > 0:
                samples.append(sample)
                item_index += 1
            else:
                blank_counter += 1
        return samples

    def split_samples_into_name_and_information(self, index_samples_start_at, samples):
        sample_name_date_time = []
        sample_information = []
        for item in samples:
            if item[0] + " " + item[1] == 'Lab Blank':
                sample_name = item[0] + " " + item[1]
                sample_name_date_time.append([sample_name])
                sample_information.append(item[2:])
            else:
                sample_name_date_time_list = item[:index_samples_start_at]
                sample_time = sample_name_date_time_list.pop()
                sample_date = sample_name_date_time_list.pop()
                sample_name = " ".join(sample_name_date_time_list)
                sample_name_date_time.append([sample_name, sample_date, sample_time])
                sample_information.append(item[index_samples_start_at:])
        return [sample_name_date_time, sample_information]

    def generate_samples_dictionary_entries(self, samples_binary_list):
        for item in samples_binary_list[0]:
            if len(item) == 1:
                if item[0] in self.samples_dictionary:
                    pass
                else:
                    self.samples_dictionary[item[0]] = ["no date", "no time"]
            else:
                if item[0] in self.samples_dictionary:
                    pass
                else:
                    self.samples_dictionary[item[0]] = [item[1], item[2]]

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

    def print_sample_dictionary_to_console(self):
        for key, value in self.samples_dictionary.items():
            print(key)
            print(value)



