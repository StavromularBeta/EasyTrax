import tkinter as Tk
import EasyTraxParse as Parse


class MainApplication(Tk.Frame):
    def __init__(self, parent, **kwargs):
        Tk.Frame.__init__(self, parent, **kwargs)
        # Variables
        self.job_number = ""
        self.file_path_and_name = ""
        self.chm_file = ""
        self.chm_file_contents = ""
        self.univ_directory_location = 'U:\\UNIV\\W'
        # TKinter stuff
        self.job_number_entry = Tk.Entry(self)
        self.job_number_entry.grid(row=1, column=0)
        Tk.Label(self, text="EasyTrax").grid(row=0)
        Tk.Button(self, text="Go!", command=self.easy_trax_controller).grid(row=1, column=1)

    def easy_trax_controller(self):
        self.job_number = self.job_number_entry.get()
        self.clear_text()
        self.get_chm_file_from_job_number()
        parsing_script = Parse.EasyTraxParse(self.job_number, self.chm_file_contents)
        parsing_script.easy_trax_parse_controller()

    def clear_text(self):
        self.job_number_entry.delete(0, 'end')

    def get_chm_file_from_job_number(self):
        self.file_path_and_name = self.univ_directory_location + self.job_number + ".CHM"
        self.chm_file = open(self.file_path_and_name, 'r')
        self.chm_file_contents = self.chm_file.readlines()


root = Tk.Tk()
root.geometry('475x600')
MainApplication(root, height=600, width=475).grid()
root.mainloop()
