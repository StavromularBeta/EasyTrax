**EasyTrax**

EasyTrax is a python module that converts human-readable analytical reports
into a delimited ASCII flat file. This file format (.WTX) is used to upload
analytical data to the website WaterTrax. Several clients of the lab require
their reports to be handled by WaterTrax. WaterTrax data can be entered by
hand via a web client. This can be extremely tedious - for example, 12 sampling
locations with 50 analytes each is 700 individual pieces of data that need to
be hand-entered. EasyTrax files take seconds to create, and a minute to upload.

**How to Use**

- a 'client good copy' of the report is added to /Files_To_Report. This can be
opened using notepad.
  
- the 'client good copy' is trimmed of any data that is **not yet handled** by
  EasyTrax (for infomation on what type of data is handled currently by
  EasyTrax, see the **Data Formats** section)

- run **EasyTraxTK.py**

- type the file name (jobnumber) into the box provided, and hit the button labeled
  "Create WTX File". The .WTX file format will be created
  and saved in WTX_reports. 
  
- log in to lab.watertrax.com and sign in using the lab credentials

- under "Service Functions", select "Lab Reports". Then select "Upload Report".
  browse to the file you just created, and hit "Upload".
  
- File will be submitted at this point. Open up the file to review, if desired.

**Data Formats**

as of June 2nd, 2021

Currently supported data formats:

- horizontally formatted chemistry data
- vertically formatted icp data

Not supported yet (May not be a complete list):

- microbiology data
- microcystins data

It is possible to trim out the unsupported data, upload the supported data
via .WTX file, and then upload the rest of the data manually with some 
designation (for example, if you uploaded the first part using W161000, 
you can upload the second part manually and save it as file W161000B). 

As this program is developed, more data formats will be supported.

**Documentation**

as of June 2nd, 2021:

fully documented files:

- EasyTraxParse.py

partially documented files:

undocumented files:

- EasyTraxConvert.py

- EasyTraxTK.py

documentation can be found written into the python files themselves.
Files have help() accessible docstrings as well as comments throughout.

**Contact Information**

This readme and program was written by Peter Levett (MB Laboratories ltd.). This readme
was last updated June 2nd, 2021. Any questions or concerns about this program
can be sent to peterlevett@gmail.com.

