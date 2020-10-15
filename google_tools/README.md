# Google Tools

Utilities for the Google Sheets API. Lets you easily read and write to Google spreadsheets, you just need to make sure you have the proper outh file/permissions for pygsheets (instructions here: https://pygsheets.readthedocs.io/en/stable/authorization.html). For any questions/comments, please email alia.jo.victor@gmail.com.

## GSheets class

### read function

Returns a pandas dataframe of a given range in a Google spreadsheet. The user must pass the following parameters:
- <b>sheet_name:</b> The name of the target spreadsheet.
- <b>tab_name:</b> The name of the tab within the target spreadsheet which contains the range you want to pull.
- <b>start_row:</b> The first cell of the range you want to pull (i.e. 'A2').
There are then additional optional parameters a user can pass:
- <b>end_col:</b> The last column of the range you're trying to pull (i.e. 'Z' or 'Z200,' if you only wanted up to row 200).
- <b>header (boolean):</b> Whether or not the first row of the target range contains headers (default=True).
- <b>reformat (boolean):</b> Whether or not to change all headers to lowercase and replace spaces with underscores (default=True, when False exact headers are returned)

### write function

Takes a pandas dataframe and inserts it into a specific range in a Google Spreadsheet. The user must pass the following parameters:
- <b>df:</b> The dataframe to insert.
- <b>sheet_name:</b> The name of the target spreadsheet.
- <b>tab_name:</b> The name of the tab within the target spreadsheet which contains the range you want to insert the df.
- <b>start_row:</b> The first cell of the range where you want to insert the df.
- <b>copy_header (boolean):</b> Whether or not to include the df's column names.
- <b>clear_first (boolean):</b> Whether or not to clear the target range before inserting the df.
- <b>start_last_row (boolean):</b> Whether or not to insert the df starting at the first available row of the range.
	- <b>Note:</b> When this is set to True, only the column letter of the start_row parameter is used, the exact start_row will be determined by the function

## Prerequisites<br>
- googleapiclient
- numpy
- pandas
- pygsheets
- httplib2
