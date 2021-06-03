import tkinter as Tk
import EasyTraxParse as Parse
import EasyTraxConvert as Convert


class MainApplication(Tk.Frame):
    def __init__(self, parent, **kwargs):
        Tk.Frame.__init__(self, parent, **kwargs)
        # Variables
        self.job_number = ""
        self.file_path_and_name = ""
        self.mb_file = ""
        self.mb_file_contents = ""
        self.file_dump_directory_location = 'T:\\ANALYST WORK FILES\\Peter\\EasyTrax\\Files_To_Report\\W'
        # TKinter stuff
        self.job_number_entry = Tk.Entry(self)
        self.job_number_entry.grid(row=1, column=0)
        Tk.Label(self, text="EasyTrax").grid(row=0)
        Tk.Button(self,
                  text="Create WTX File",
                  command=self.easy_trax_controller).grid(row=2, column=0)

    def easy_trax_controller(self):
        self.job_number = self.job_number_entry.get()
        self.clear_text()
        self.get_file_from_job_number()
        if self.mb_file_contents:
            print('file found')
            parsing_script = Parse.EasyTraxParse(self.job_number, self.mb_file_contents)
            samples_dictionary, job_dictionary = parsing_script.easy_trax_parse_controller()
            converting_script = Convert.EasyTraxConvert(samples_dictionary, job_dictionary)
            converting_script.easy_trax_convert_controller()
        else:
            print('no FirstChoice file found.')

    def clear_text(self):
        self.job_number_entry.delete(0, 'end')

    def get_file_from_job_number(self):
        self.file_path_and_name = self.file_dump_directory_location + self.job_number + ".txt"
        try:
            self.mb_file = open(self.file_path_and_name, 'r')
            self.mb_file_contents = self.mb_file.readlines()
        except FileNotFoundError:
            self.mb_file_contents = False


root = Tk.Tk()
root.geometry('475x100')
MainApplication(root, height=100, width=475).grid()
root.mainloop()
