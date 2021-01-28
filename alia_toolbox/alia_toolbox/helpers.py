from alia_toolbox.colors import *
from contextlib import redirect_stdout, contextmanager
from datetime import datetime, timedelta, date
from dateutil.parser import parse
import difflib
import traceback
import pickle
import re
import json
import pandas as pd
import os

# MISC FUNCTIONS

@contextmanager
def suppress():
    """Silences printed outputs when used in with statement (with suppress(): etc)"""
    with open(os.devnull,'w') as null:
        with redirect_stdout(null):
            yield

def show_error(ix=(2,0),as_list=True,err_name=False):
    """
    ix: Index(es) of traceback to return. Can be a single int or a tuple of 2 ints.
    as_list: When True (default) output is returned as a list, otherwise as a strong joined by \n.
    err_name: Set to True to only return the name of the error.
    """
    show_error.err = [i.strip() for i in traceback.format_exc().split('\n') if i != '']
    if err_name:
        rgx = re.compile("^[A-Za-z]+: .*")
        raw = [i for i in show_error.err if rgx.match(i)]
        if len(raw) == 0:
            raw = [i for i in show_error.err if 'Error:' in i]
        if len(raw) > 0:
            return raw[0].split(':')[0].strip()
    if ix:
        if type(ix) == tuple:
            try:
                ix1 = ix[0]
            except IndexError:
                ix1 = None
            try:
                ix2 = ix[1]
            except IndexError:
                ix2 = None
            if ix1 and ix2:
                out = show_error.err[ix1:ix2]
            elif ix1:
                out = show_error.err[ix1:]
            elif ix2:
                out = show_error.err[:ix2]
    else:
        out = show_error.err.copy()
    if as_list:
        return out
    else:
        return '\n'.join(out)

def regex(string,pattern):
    """Returns a regex extration of a string. A compiled object can be passed as the pattern."""
    try:
        if type(pattern) == str:
            return re.search(pattern,string).group(1)
        else:
            return pattern.search(string).group(1)
    except:
        pass

def rgxmatch(string,pattern):
    """Returns re.match(pattern,string)"""
    try:
        if type(pattern) == str:
            out = bool(re.match(pattern,string))
        else:
            out = bool(pattern.match(string))
        if out is None:
            return False
        else:
            return out
    except:
        return None

def find_common(t1,t2,keep_order=True):
    """Returns common items between two lists. When keep_order=True, the order of t1 is kept."""
    if type(t1) == pd.core.indexes.base.Index:
        t1 = list(t1)
    elif type(t1) == pd.DataFrame:
        t1 = list(t1.columns)
    if type(t2) == pd.core.indexes.base.Index:
        t2 = list(t2)
    elif type(t2) == pd.DataFrame:
        t2 = list(t2.columns)
    items = set(t1)&set(t2)
    if keep_order:
        return sorted(items,key=lambda x:t1.index(x))
    else:
        return list(items)

def find_uncommon(t1,t2,keep_order=True):
    """Returns items found in t1 that do NOT exist in t2. When keep_order=True, the order of t1 is kept."""
    if type(t1) == pd.core.indexes.base.Index:
        t1 = list(t1)
    elif type(t1) == pd.DataFrame:
        t1 = list(t1.columns)
    if type(t2) == pd.core.indexes.base.Index:
        t2 = list(t2)
    elif type(t2) == pd.DataFrame:
        t2 = list(t2.columns)
    items = set(t1)-set(t2)
    if keep_order:
        return sorted(items,key=lambda x:t1.index(x))
    else:
        return list(items)

def contains(items,to_check,exact=True,_all=True):
    """
    Iterates through passed items and checks if they exist in to_check (list). When exact=False to_check list
    will be lowercased to find matches regardless of captilization/trailing spaces. When _all=False only the
    first matching item is returned (as a list object).
    """
    if type(to_check) in [pd.Series,pd.core.indexes.base.Index]:
        to_check = list(to_check)
    if not exact:
        to_check = [str(i).lower().strip() for i in to_check]
    if type(items) == str:
        if ',' in items and items.strip() != ',':
            items = [i.strip() for i in items.split(',')]
        else:
            items = [items]
    if exact:
        dd = [i for i in items if i in to_check]
    else:
        dd = [i for i in items if str(i).lower().strip() in to_check]
    if len(dd) == 0:
        pink("None of the passed items were found in the given list",ts=False)
    else:
        if _all or len(dd) == 1:
            out = dd
        else:
            out = [dd[0]]
        return out

def keys(d,_all=True):
    """Returns the keys of a dictionary as a list. If _all=False only the first key is returned."""
    key_list = list(d.keys())
    if _all:
        out = key_list
    else:
        out = key_list[:1]
    if type(out) != list:
        out = [out]
    return out

def numdict(input_list,rtype=dict):
    """
    Makes dict out of input_list where the keys are the order of the item in the list. When rtype=list a
    list of dicts is returned, otherwise a single dict is returned. If input_list is a series, it will
    automatically be converted to a list.
    """
    if type(input_list) != list:
        if type(input_list) == pd.Series:
            dd = uinput("<200><b>Should Series be deduped before converted to a list?</b></200>")
            if dd:
                input_list = unique(input_list)
            else:
                input_list = list(input_list)
    input_list = list(filter(None,input_list))
    try:
        out = dict(zip(range(1,len(input_list)+1),input_list))
        if rtype in [dict,'dict']:
            return out
        elif rtype in [list,'list']:
            return [{k:v} for k,v in out.items()]
    except:
        numdict.error = show_error()
        red('Encountered error, see numdict.error for details',ts=False)

def dupedic(dic):
    """Returns a list of values that appear in multiple keys in a dictionary."""
    dd = {}
    for key, value in dic.items():
        dd.setdefault(value,set()).add(key)
    return [k for k,v in dd.items() if len(v) > 1]

def uniquedic(dic):
    """Returns a list of values that appear in only one key in a dictionary."""
    dd = {}
    for key, value in dic.items():
        dd.setdefault(value,set()).add(key)
    return [k for k,v in dd.items() if len(v) == 1]

def invert(dic):
    """Inverts a dictionary (returns {v:k for k,v in dic.items()})"""
    dupes = dupedic(dic)
    not_dupes = uniquedic(dic)
    if not empty(dupes):
        nd = {}
        for d in dupes:
            td = {k:v for k,v in dic.items() if v == d}
            nd.update({d:list(td)})
        if not empty(not_dupes):
            for n in not_dupes:
                nd.update({k:v for k,v in dic.items() if v == n})
        return nd
    else:
        try:
            return {v:k for k,v in dic.items()}
        except TypeError:
            red('<b>TypeError</b>',ts=False)
            return None

def uinput(msg,**kwargs):
    """
    User input function that gives you more customization options in terms of text color/format. kwargs can
    be dict of mapping what answer = what (e.g. {'Y':True,'N':False} which is the default). When no kwargs are
    passed, just the raw input is returned. If formatting (e.g. {0}) is in msg it'll automatically make {0} and
    {1} list(kwargs)[0] and list(kwargs)[1]. msg param is passed through pprint() function, so feel free to use
    that function's formatting syntax.
    """
    if kwargs or (not kwargs and rgxmatch(msg.replace('\n',''),'.*Y\/N.*')):
        if not kwargs:
            kwargs = {'Y':True,'N':False}
        kkeys = keys(kwargs)
        if rgxmatch(msg.replace('\n',''),'.*(\{\d\}).*'):
            msg = msg.format(kkeys[0],kkeys[1])
        elif not rgxmatch(msg.replace('\n',''),'.*Y\/N.*'):
            msg = msg.strip()
            if '?' in msg:
                msg = msg.replace('?','')
            if msg[-1] == '>':
                tmsg = msg
                while tmsg[-1] == '>':
                    ix = tmsg.rfind('</')
                    tmsg = tmsg[:tmsg.rfind('</')]
                syntax = msg[ix:]
                msg = msg[:msg.rfind(syntax)]+' ({0}/{1})? '.format(kkeys[0],kkeys[1])+syntax
            else:
                msg = msg+' ({0}/{1})? '.format(kkeys[0],kkeys[1])
        if msg[-1] != ' ':
            msg = msg+' '
        raw_input = str(input(pprint(msg,ts=False,r=True))).upper()
        if raw_input not in kkeys:
            temp = difflib.get_close_matches(raw_input,kkeys,n=1,cutoff=0.8)
            if empty(temp):
                temp = difflib.get_close_matches(raw_input,kkeys,n=1,cutoff=0.7)
                if empty(temp):
                    red("<b>'{0}' not found in kwarg keys</b>".format(raw_input),ts=False)
                    return None
                else:
                    raw_input = temp[0]
            else:
                raw_input = temp[0]
        return kwargs[raw_input]
    else:
        msg = msg.strip()+' '
        raw_input = str(input(pprint(msg,ts=False,r=True)))
        return raw_input

def strip_currency(x,vtype=float):
    """Removes all non-digit/decimal values (effectively strips all currency symbols)"""
    try:
        return vtype(re.compile(r'[^\d.,-]+').sub('',x.replace(',','')))
    except:
        return None

def match(rinput,opts,hush=True):
    """Returns difflib.get_close_matches(rinput,opts). rinput should be a string and opts should be a list."""
    if type(opts) == str:
        with suppress():
            split_str = bool(contains(',',opts) is not None and opts.strip() != ',')
        if split_str:
            opts = [i.strip() for i in opts.split(',')]
        else:
            opts = [opts]
    if type(rinput) == list:
        if not hush:
            red('<b>rinput must be a string</b>',ts=False)
        return None
    z = 1
    for i in range(4):
        z += -0.1
        temp = difflib.get_close_matches(rinput,opts,cutoff=round(z,1))
        if not empty(temp):
            break
    if empty(temp):
        if not hush:
            red(f"{rinput} can't be found in passed list",ts=False)
        return None
    if len(temp) > 1:
        temp = numdict(temp)
        popts = '\n'.join([f'{k}: {v}' for k,v in temp.items()])
        pmsg = "Do any of these match (give index)? {0}".format(popts)
        raw_inp = str(input(pink(pmsg,ts=False,r=True)))
        if raw_inp == '':
            if not hush:
                red(f"{rinput} can't be found in passed list",ts=False)
            return None
        try:
            ix = int(raw_inp.strip())
            return temp[ix]
        except (ValueError,KeyError):
            if not hush:
                red(f"Having trouble finding {rinput} in passed list",ts=False)
            return None
    else:
        return temp[0]

def unique(obj):
    """Returns a list or Pandas Series after ensuring there are unique values."""
    if type(obj) == pd.Series:
        out = list(obj.unique())
    else:
        out_temp = set()
        out_add = out_temp.add
        out = [x for x in obj.copy() if not (x in out_temp or out_add(x))]
    return out

def empty(obj):
    """Return True if obj is either null, blank or len(obj) == 0."""
    if obj is None:
        return True
    elif type(obj) in (pd.DataFrame,pd.Series):
        if len(list(obj.columns)) > 1:
            return bool(len(obj)==0 or (obj[list(obj.columns)[0]].values[0] == '' and
                                        obj[list(obj.columns)[1]].values[0] == ''))
        else:
            return bool(len(obj)==0 or obj[list(obj.columns)[0]].values[0] == '')
    elif type(obj) == list:
        return bool(obj == [])
    elif type(obj) == str:
        return bool(obj == '')
    elif type(obj) == dict:
        return bool(len(keys(obj))==0)

# FILE PARSING FUNCTIONS

def save_pkl(obj_to_save,filename,path,overwrite=False):
    """
    Saves object as a pickle file. SP (SavePkl class) is global, so you can later reference the final filename.
    This is helpful in cases where a file with the desired filename already exists and gets automatically adjusted
    (i.e. if file.pkl already exists and overwrite=False this file would end up being named file (1).pkl)

    ::PARAMETERS::
    obj_to_save: Any pickelable object you want to save
    filename: Desired filename (no need to include extension)
    path: The (full) path where you want the file saved
    overwrite: Whether or not an existing file should be overwritten if found (default False)
    """
    global SP
    class SavePkl(object):
        def __init__(self):
            pass
    SP = SavePkl()
    SP.filename = filename.replace('.pkl','').strip() # just in case extension was accidentally added already
    if not overwrite:
        num = 0
        while os.path.exists('{0}{1}.pkl'.format(path,SP.filename)):
            num += 1
            SP.filename = '{0} ({1})'.format(SP.filename.split(' ')[0].strip(),num)
    try:
        f = open(f'{path}{SP.filename}.pkl','wb')
        pickle.dump(obj_to_save,f)
        f.close()
        green(f'{SP.filename} saved',False)
    except:
        err = errname()
        red(f'<b>{err}</b>',False)
        return None

def save_json(obj_to_save,filename,path='desktop',overwrite=False):
    """
    Saves object as a JSON file. SJ (SaveJSON class) is global, so you can later reference the final filename.
    This is helpful in cases where a file with the desired filename already exists and gets automatically adjusted
    (i.e. if file.json already exists and overwrite=False this file would end up being named file (1).json)

    ::PARAMETERS::
    obj_to_save: Any JSON object you want to save
    filename: Desired filename (no need to include extension)
    path: The (full) path where you want the file saved
    overwrite: Whether or not an existing file should be overwritten if found (default False)
    """
    global SJ
    class SaveJSON(object):
        def __init__(self):
            pass
    SJ = SaveJSON()
    SJ.filename = filename.replace('.json','').strip() # just in case extension was accidentally added already
    if not overwrite:
        num = 0
        while os.path.exists('{0}{1}.json'.format(path,SJ.filename)):
            num += 1
            SJ.filename = '{0} ({1})'.format(SJ.filename.split(' ')[0].strip(),num)
    try:
        f = open(f'{path}{SJ.filename}.json','w')
        json.dump(obj_to_save,f)
        f.close()
        green(f'{SJ.filename} saved',False)
    except:
        err = errname()
        red(f'<b>{err}</b>',False)
        return None

def filelist(dirpath,prefix=None):
    """
    Returns a list of files in the given directory path. You can optionally pass a file prefix
    to only pull files that start with the given prefix.

    ::PARAMETERS::
    dirpath: Path to the folder containing the target files
    prefix: Only pulls files that start with this given prefix
    """
    try:
        files = [i for i in os.listdir(dirpath) if i[0].isalnum()]
    except FileNotFoundError:
            red("<b>Can't locate files in given directory</b>")
            return None
    if prefix:
        return [i for i in files if prefix in i]

# DATAFRAME FUNCTIONS

def reset(df):
    "Simply returns df.reset_index(drop=True)"
    return df.reset_index(drop=True)

def dtcol(dt_column,style=None):
    """
    Returns a formatted datetime column in the format passed in the style parameter.
    """
    if style:
        return pd.to_datetime(pd.to_datetime(dt_column.astype(str)).dt.strftime(style))
    else:
        return pd.to_datetime(dt_column.astype(str))

def select_dtcols(df):
    """Returns all columns with datetime64 dtype (df.select_dtypes(include=['datetime64']))."""
    return list(df.select_dtypes(include=['datetime64']).columns)

def dedupe(df,cols=None,ix=False):
    """
    Returns df.drop_duplicates() or df.drop_duplicates(subset=cols) depending on if any cols are passed.
    When ix=True original indexes are kept, otherwise they're reset.
    """
    if cols is not None:
        if type(cols) == str:
            with suppress():
                split_str = bool(contains(',',cols) is not None and cols.strip() != ',')
            if split_str:
                cols = [i.strip() for i in cols.split(',')]
            else:
                cols = [cols]
        try:
            if ix:
                return df.drop_duplicates(subset=cols)
            else:
                return reset(df.drop_duplicates(subset=cols))
        except:
            dedupe.error = show_error()
            red('Encountered error, see dedupe.error for details',ts=False)
    else:
        try:
            if ix:
                return df.drop_duplicates()
            else:
                return reset(df.drop_duplicates())
        except:
            dedupe.error = show_error()
            red('Encountered error, see dedupe.error for details',ts=False)

def dedupe_cols(df):
    """Ensures there are no duplicate columns (returns df.loc[:,~df.columns.duplicated()])."""
    return reset(df.loc[:,~df.columns.duplicated()])

def cmerge(df,cols,sep=None):
    """Returns a column merging all columns passed in the cols param."""
    if type(cols) == str:
        if ',' in cols:
            cols = [i.strip() for i in cols.split(',')]
        else:
            cols = [cols.strip()]
    for j,k in enumerate(cols):
        if j == 0:
            out = df[k].fillna('').str.strip()
        elif sep:
            out = out+sep+df[k].fillna('').str.strip()
        else:
            out = out+df[k].fillna('').str.strip()
    if sep:
        if (out.str.contains(f'.*{sep}{sep}',na=False)).any():
            m = out.str.contains(f'.*{sep}{sep}',na=False)
            out.loc[m] = out.loc[m].str.replace(f'{sep}{sep}',sep)
        if (out.str[-1]==sep).any():
            m = out.str[-1]==sep
            out.loc[m] = out.loc[m].str[:-1]
    return out

def pdnull(series):
    """Applies lambda x: pd.isnull(x) or x in ['',None,'nan','NaN','None','NaT',pd.NaT]"""
    if type(series) == pd.DataFrame:
        return (series.isnull())|(series.isin(['',None,'nan','NaN','None','NaT',pd.NaT]))
    else:
        fm = lambda x: pd.isnull(x) or x in ['',None,'nan','NaN','None','NaT',pd.NaT]
        return series.apply(fm)

def splitrows(df,col,sep=None):
    """
    Use this function when you want to extract certain values from rows of a df and insert them into their
    own individual rows. It looks for the passed sep (i.e. '\n') in the given col and splits by that sep so
    each value gets its own row and then the df is returned.
    """
    dd = []
    for ix,r in df.iterrows():
        row = r.to_dict()
        if '\n' in r[col]:
            for i in r[col].split(sep):
                nrow = row.copy()
                nrow[col] = i
                dd.append(nrow)
        elif type(r[col]) == list:
            for i in r[col]:
                nrow = row.copy()
                nrow[col] = i
                dd.append(nrow)
        else:
            dd.append(row)
    return pd.DataFrame(dd)[list(df.columns)]

def todict(df,key_col,cols=None):
    """Creates a dictionary from a df (column passed at key_col param becomes keys of the dictionary)."""
    def merge(df,key_col,cols):
        dicts = []
        for c in cols:
            exec(f"temp = df.set_index('{key_col}')['{c}'].to_dict()")
            dicts.append({k:{c:v} for k,v in locals()['temp'].items()})
        dd = {}
        for d in dicts:
            for k,v in d.items():
                if k not in keys(dd):
                    dd[k] = {}
                for y,z in v.items():
                    dd[k][y] = z
        return dd
    try:
        if cols:
            if (type(cols) == str and cols.lower() == 'all'):
                return merge(df,ix=key_col,cols=[i for i in list(df.columns) if i != key_col])
            if type(cols) != list:
                cols = [i.strip() for i in cols.split(',')]
            if len(cols) == 1:
                return df.set_index(key_col)[cols[0]].to_dict()
            else:
                return merge(df,ix=key_col,cols=cols)
        else:
            return df.set_index(key_col).to_dict()
    except AttributeError:
        pass
    except:
        todict.error = show_error()
        red('<b>Encountered error</b> (see todict.error)',ts=False)

def rowsdict(df):
    """Returns df as a list with a dict of each row (df.to_dict('records'))."""
    return df.to_dict('records')

# DATETIME FUNCTIONS

def now(style='%Y-%m-%d %H:%M:%S'):
    """Reurns datetime.now().strftime(style)"""
    return datetime.now().strftime(style)

def todate(date_obj=None,ts=False):
    """
    If date_obj is None, default is now() function.
    Only the date is returned by default, to return date AND time set ts to True.
    """
    if date_obj is None:
        date_obj = now()
    elif '_' in date_obj:
        date_obj = date_obj.replace('_','-')
    if ts:
        return parse(date_obj)
    else:
        return parse(date_obj).date()

def elapsed(start,stop=None,full=False,metric='minutes'):
    """
    Returns elapsed time between two timestamps.
    Start parameter must be a datetime object of the start time.
    When stop is None (default) the current time is used.
    Metric opts: seconds, minutes, hours.
    When full=True elapsed time is returned as H:M:S, otherwise only the chosen metric is returned."""
    opts = ['minutes','hours','seconds']
    actual = difflib.get_close_matches(metric.lower(),opts,cutoff=0.7)
    if len(actual) == 1:
        metric = actual[0]
    else:
        if len(actual) > 1:
            orange(f"Multiple metric options found ({', '.join(actual)}). Which did you mean?",ts=False)
        elif len(actual) == 0:
            red("Metric value seems to be incorrect, try again",ts=False)
        print('')
        metric = str(input('seconds, minutes or hours? '))
        actual = difflib.get_close_matches(metric.lower(),opts,cutoff=0.7)
        if len(actual) == 1:
            metric = actual[0]
        else:
            red("Having trouble recognizing metric")
            return None
    if stop is not None:
        stop = todate(str(stop),ts=True)
    else:
        stop = todate(now(),ts=True)
    diff = (stop-todate(str(start),ts=True)).total_seconds()
    if full:
        hours, leftover = divmod(diff,3600)
        minutes, seconds = divmod(leftover, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours),int(minutes),int(seconds))
    else:
        seconds = round(diff)
        minutes = round(diff/60)
        hours = round(diff/3600)
        if metric == 'seconds':
            return seconds
        elif metric == 'minutes':
            return minutes
        elif metric == 'hours':
            return hours

def daydiff(start,stop=None):
    """
    Returns number of days between two date strings. When stop=None (default) the current day is used."""
    start = todate(str(start))
    if stop is None:
        stop = todate(now())
    else:
        stop = todate(str(stop))
    return (stop-start).days

def monthnum(x):
    """e.g. if x='April' 4 is returned"""
    try:
        return todate(f'{x} 1, 2030').month
    except:
        return np.nan

def tformat(date_obj,style=None):
    """
    Takes a datetime object and returns it in the format of the style parameter.
    When no style value is passed, items are returned in the following formats:
    datetime/timestamp objects: %Y-%m-%d %H:%M:%S
    date objects: %Y-%m-%d
    """
    if type(date_obj) not in [datetime,date]:
        if ':' in date_obj:
            date_obj = todate(date_obj,ts=True)
        else:
            date_obj = todate(date_obj)
    if style is None:
        if type(date_obj) == datetime:
            style = '%Y-%m-%d %H:%M:%S'
        elif type(date_obj) == date:
            style = '%Y-%m-%d'
    try:
        return date_obj.strftime(style)
    except:
        err = show_error(err_name=True)
        red(err)
        return None