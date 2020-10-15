import re
import httplib2
import pygsheets
import pandas as pd
import time

class GSheets(object):
    def __init__(self,outh_file,http_client=None):
        self.outh_file = outh_file
        if http_client:
            self.http_client = http_client
        else:
            self.http_client = httplib2.Http(timeout=100)
        self.gc = pygsheets.authorize(outh_file=self.outh_file,http_client=self.http_client)
    def read(self,sheet_name,tab_name,start_row,end_col=None,header=True,reformat=True):
        """When reformat=True, column names are made lowercase and spaces are replaced with underscores."""
        self.sh = self.gc.open(sheet_name)
        self.tab = self.sh.worksheet_by_title(tab_name)
        if end_col == None:
            self.df = self.tab.get_as_df(start=start_row,end=None,has_header=header,numerize=False)
        elif bool(re.search(r'\d',end_col)):
            self.df = self.tab.get_as_df(start=start_row,end=end_col,has_header=header,numerize=False)
        else:
            self.df = self.tab.get_as_df(start=start_row,end=end_col+str(self.tab.rows),has_header=header,numerize=False)
        if not header:
            reformat = False
        if header and reformat:
            self.df.columns = self.df.columns.str.replace(' ','_').str.replace("'",'').str.lower()
            for col in list(self.df.filter(regex='_id').columns):
                self.df[col] = self.df[col].astype(str)
            for col in list(self.df.filter(regex='_time|_date|date').columns):
                try:
                    self.df[col] = pd.to_datetime(pd.to_datetime(self.df[col]).dt.strftime('%Y-%m-%d'))
                except:
                    pass
        return self.df
    def write(self,df,sheet_name,tab_name,start_row,copy_header=True,clear_first=False,start_last_row=False):
        self.sh = self.gc.open(sheet_name)
        self.tab = self.sh.worksheet_by_title(tab_name)
        num_rows = self.tab.rows
        if clear_first:
            # determines the exact range to clear before writing
            start_col_num = ord(re.search('([A-Z]{1,2})\d',start_row).group(1))-64
            if df.shape[1] == 1:
                # if there's only 1 column, just grab the letter from the start_row
                end_col = re.search('([A-Z]{1,2})\d',start_row).group(1)
            else:
                # otherwise determine the letter value of the last column of the desired range
                end_col = chr((start_col_num+df.shape[1]-1)+64)
            self.tab.clear(start=start_row,end='{0}{1}'.format(end_col,num_rows))
        if start_last_row:
            # first determine if more rows need to be added to fit the df
            if num_rows < num_rows+len(df):
                # if this is the case, determine how many rows to add and add them to the tab
                self.tab.add_rows(num_rows+len(df)-num_rows)
                time.sleep(3) # ensure the tab has time to save these new rows before moving onto the next steps
            last_row = len(self.tab.get_values(start_row[0]+'1',start_row[0]+str(num_rows)))+1
            self.tab.set_dataframe(df,start=start_row[0]+str(last_row),copy_head=copy_header)
        else:
            self.tab.set_dataframe(df,start=start_row,copy_head=copy_header)
        print(f'Pasted into {tab_name} tab in {sheet_name}')