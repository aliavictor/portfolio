from alia_toolbox.colors import *
from contextlib import redirect_stdout, contextmanager
from datetime import datetime, timedelta, date
from dateutil.parser import parse
import difflib
import traceback
import pickle

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

def save_pkl(obj_to_save,filename,path,overwrite=False):
    """
    Saves object as a pickle file. SP (SavePkl class) is global, so you can later reference the final filename.
    This is helpful in cases where a file with the desired filename already exists and gets automatically adjusted (i.e. if file.pkl already exists and overwrite=False this file would end up being named file (1).pkl)

    PARAMETERS
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

def reset(df):
    "Simply returns df.reset_index(drop=True)"
    return df.reset_index(drop=True)

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