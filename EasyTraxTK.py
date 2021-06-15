import tkinter as Tk
import EasyTraxParse as Parse
import EasyTraxConvert as Convert


class MainApplication(Tk.Frame):
    """Runs the TK window that allows the user to interact with EasyTrax.

    currently a very simple frame, consisting of one Tk.Entry box (where the user inputs the job number)
    and one button that runs easy_trax_controller.

    The controller function gets the jobnumber, gets the corresponding file from /Files_To_Report/,
    and reads it line by line into mb_file_contents.

    It passes mb_file_contents and job_number to EasyTraxParse. It receives back an intermediate sample dictionary
    and job dictionary.

    It passes these dictionaries to EasyTraxConvert, which handles the conversion and file writing processes.

    Last Updated: 10 June 2021, P.L.

    Attributes
    ----------
    job_number : str
        the job number belonging to the report to be created.

    file_path_and_name : str
        the full filename (name and path) of the file to be read.

    mb_file : str
        the full file, as one continuous string.

    mb_file_contents : list(str)
        the lines in the file, line by line, in list format.

    file_dump_directory_location : str
        the location of the files we are going to be looking for.

    job_number_entry : Tk.Entry
        where the user inputs the job number of the report they want to make.

    EasyTraxMakerLog : Tk.Entry
        where the user can see the error log for the file they want to parse.

    Methods
    -------
    * `easy_trax_controller()` -
        executes the various methods/functions in the script in the right order. Essentially controls the whole
        program.

    * `clear_text()` -
        clears the text from job_number_entry, so another job can be entered.

    * `get_file_from_job_number()` -
        tries to open the requested file. If it can find the file, reads it line by line into mb_file_contents (list).

    * `write_log_to_text_box()` -
        clears any text in EasyTraxMakerLog, and then writes the passed text to the Text box.
    """

    def __init__(self, parent, **kwargs):
        """
        Parameters
        ----------
        parent : Tk.Frame
            a TkInter frame.
        kwargs
            no additional parameters are passed.
        """

        Tk.Frame.__init__(self, parent, **kwargs)
        # Variables
        self.job_number = ""
        self.file_path_and_name = ""
        self.mb_file = ""
        self.mb_file_contents = ""
        self.file_dump_directory_location = 'T:\\ANALYST WORK FILES\\Peter\\EasyTrax\\Files_To_Report\\W'
        # TKinter stuff
        self.job_number_entry = Tk.Entry(self)
        self.EasyTraxMakerLog = Tk.Text(self, height=25, width=60)
        self.EasyTraxMakerLog.config(state=Tk.DISABLED)
        self.job_number_entry.grid(row=0, column=0, sticky=Tk.W, padx=5, pady=5)
        Tk.Button(self,
                  text="Create WTX File",
                  command=self.easy_trax_controller).grid(row=1, column=0, sticky=Tk.W, padx=5)
        self.EasyTraxMakerLog.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def easy_trax_controller(self):
        """executes the various methods/functions in the script in the right order.

        gets the job number, clears the text from the entry box. Gets the file, and reads the file line by
        line into a list, stored in mb_file_contents. if mb_file_contents isn't empty, then we have our file.
        It's first passed to the parsing script. The intermediate file format is collected, and passed
        to the converting script. The converting script handles the writing of the file. If no file is found,
        an error message is printed to the console.
        """

        self.job_number = self.job_number_entry.get()
        self.clear_text()
        self.get_file_from_job_number()
        if self.mb_file_contents:
            self.write_log_to_text_box("MB Labs file found, attempting to create WTX file.\n", True)
            parsing_script = Parse.EasyTraxParse(self.job_number, self.mb_file_contents)
            samples_dictionary, job_dictionary, parse_log = parsing_script.easy_trax_parse_controller()
            self.write_log_to_text_box(parse_log)
            converting_script = Convert.EasyTraxConvert(samples_dictionary, job_dictionary)
            convert_log = converting_script.easy_trax_convert_controller()
            self.write_log_to_text_box(convert_log)
        else:
            self.write_log_to_text_box("No MB Labs file found with that job number.\n" +
                                       "You either incorrectly typed it in, or it \n" +
                                       "doesn't exist in Files_To_Report. Remember,\n" +
                                       "don't type the 'W' before the job number.\n", True)

    def clear_text(self):
        """clears the text from job_number_entry, so another job can be entered.
        """

        self.job_number_entry.delete(0, 'end')

    def get_file_from_job_number(self):
        """tries to open the requested file. Reads it line by line into mb_file_contents (list).

        If the file isn't found, sets mb_file_contents to False so it can be detected in the controller.
        """

        self.file_path_and_name = self.file_dump_directory_location + self.job_number + ".txt"
        try:
            self.mb_file = open(self.file_path_and_name, 'r')
            self.mb_file_contents = self.mb_file.readlines()
        except FileNotFoundError:
            self.mb_file_contents = False

    def write_log_to_text_box(self, passed_text, with_delete=False):
        """clears any text in EasyTraxMakerLog, and then writes the passed text to the Text box."""

        self.EasyTraxMakerLog.config(state=Tk.NORMAL)
        if with_delete:
            self.EasyTraxMakerLog.delete('1.0', Tk.END)
        if len(self.EasyTraxMakerLog.get("1.0", Tk.END)) == 1:
            self.EasyTraxMakerLog.insert(Tk.END, passed_text)
        else:
            self.EasyTraxMakerLog.insert(Tk.END, passed_text)
        self.EasyTraxMakerLog.config(state=Tk.DISABLED)


root = Tk.Tk()
root.geometry('495x470')
MainApplication(root, height=470, width=495).grid()
root.mainloop()
