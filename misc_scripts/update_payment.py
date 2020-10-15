from google_tools import GSheets
from alia_toolbox.helpers import *
from alia_toolbox.colors import *
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException, NoSuchWindowException)
from selenium.webdriver.common.action_chains import ActionChains

# custom helper formulas
def fb_refresh(fb,df,cols,key='adset_id'):
    """
    fb: should be an instance of the FACEBOOK class from the facebook_tools package
    df: df containing the FB objects you want to refresh (which should already contain placeholder columns, see below)
    cols: list of columns/attributes you want to refresh, note that the column name must match its corresponding API field name (i.e. budget column would have to be called daily_budget)
    key: column containing the IDs of the FB objects you want to refresh (adset_id by default)
    fbr (FBRefresh class) is global so certain variables within this function are accessible outside of it (without having to make multiple global items)
    """
    global fbr
    class FBRefresh(object):
        def __init__(self,df,cols,key):
            self.df = df.copy()
            if type(cols) == str:
                self.cols = cols.split(',')
            else:
                self.cols = cols
            self.key = key
    fbr = FBRefresh(df,cols=cols,key=key)
    # provides mapping so column names can temporarily be switched to corresponding API names (if needed)
    # at the end this mapping is used to remap altered column names back to their original names
    fbr.fields = []
    fbr.remap = {}
    for c in fbr.cols:
        if 'status' in c:
            # with the exception of accounts, the status of an FB object is called effective_status
            # so when key != account_id the value here is always effective_status, otherwise it's account_status
            if fbr.key != 'account_id':
                fbr.fields.append('effective_status')
                fbr.remap[c] = 'effective_status'
            else:
                fbr.fields.append('account_status')
                fbr.remap[c] = 'account_status'
        elif 'reason' in c:
            # personally i like to rename the ad_review_feedback field in the API to reason
            # just keeps the column names short and concise, which i prefer
            fbr.fields.append('ad_review_feedback')
        elif 'card' in c and fbr.key == 'account_id':
            # similar to the above; i tend to rename this API field to something shorter
            fbr.fields.append('funding_source_details')
            fbr.remap[c] = 'funding_source_details'
        else:
            fbr.fields.append(c)
    if fbr.key == 'account_id':
        # this ensures it doesn't matter if your input account_ids already have the act_ prefix or not
        ids = unique('act_'+fbr.df.query(f"{key} == {key}")[fbr.key].str.replace('act_',''))
        fbr.fdf = fb.bulk_read(ids,id_col=fbr.key,fields=fbr.fields)
        fbr.fdf['account_id'] = fbr.fdf['account_id'].str.replace('act_','')
    else:
        ids = unique(fbr.df.query(f"{key} == {key}")[fbr.key])
        fbr.fdf = fb.bulk_read(ids,id_col=fbr.key,fields=fbr.fields)
    if fbr.key == 'ad_id' and 'creative' in list(fbr.fdf.columns):
        # if key == ad_id then by default the id value should be extracted from the creative
        # (this only applies to ads)
        fbr.fdf['creative'] = fbr.fdf['creative'].apply(lambda x: x['id'] if not nullstr(x) and 'id' in x else None)
    # checks for columns dealing with currency
    try:
        fbr.curr_cols = not empty(fbr.fdf.filter(regex='^bid|budget'))
    except IndexError:
        fbr.curr_cols = False
    if fbr.curr_cols:
        # if any currency columns exist, iterate through them and format accordingly
        for c in list(fbr.fdf.filter(regex='^bid|budget').columns):
            fbr.fdf[c] = fbr.fdf[c].fillna(0).astype(int)/100
    if 'end_time' in fbr.fields:
        # when no adsets have a set end_time fbr.fdf won't have this column
        # if that's the case, add placeholder column
        if 'end_time' not in list(fbr.fdf):
            fbr.fdf = fbr.fdf.assign(end_time=None)
        # in cases where some adsets do have end_times, add placeholder only for rows where end_time is null
        m = pdnull(fbr.fdf['end_time'])
        fbr.fdf.loc[m,'end_time'] = pd.to_datetime('2030-01-01 23:59:59')
    if 'funding_source_details' in list(fbr.fdf):
        # extracts display_string value from funding_source_details dict
        cc = lambda x: x['display_string'] if 'display_string' in x else None
        fbr.fdf['funding_source_details'] = fbr.fdf['funding_source_details'].apply(cc)
    if 'business' in list(fbr.fdf):
        # extracts id value from business dict
        fbr.fdf['business'] = fbr.fdf['business'].apply(lambda x: x['id'] if (not nullstr(x) and 'id' in x) else x)
    fbr.fdf = todict(fbr.fdf,fbr.key,'all')
    # now remap any altered column names back to their original names to match input df
    for c in fbr.cols:
        if c in fbr.remap:
            col = fbr.remap[c]
        else:
            col = c
        fbr.df[c] = set_none(fbr.df[fbr.key].apply(lambda x: fbr.fdf[x][col] if x in fbr.fdf else None))
    if len(fbr.cols) == 1:
        # if only 1 column was updated no need for plural in print statement
        gray('<b>{0} column updated</b>'.format(fbr.cols[0]),False)
    else:
        gray('<b>{0} columns updated</b>'.format(', '.join(fbr.cols)),False)
    return fbr.df
def start_chrome(headless=False):
    "Initiates instance of Chrome's webdriver (note this Mac-specific)"
    options = webdriver.ChromeOptions()
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    options.add_argument('--window-size=2000,1500')
    options.add_argument('user-data-dir=/Application Support/Google/Chrome/Default')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36")
    options.add_experimental_option('excludeSwitches',['enable-automation'])
    if headless:
        options.add_argument('--headless')

    path = '/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(executable_path=path,chrome_options=options)
    wait = WebDriverWait(driver,5)
    driver.implicitly_wait(1)

    return driver, wait

target_card = 'Visa *1234'
# template url for accessing the payment page of an ad account
url = 'https://business.facebook.com/ads/manager/account_settings/account_billing/?act={0}&pid=p1&business_id=your_business_id&page=account_settings&tab=account_billing_settings'

# xpath/css to what needs to be clicked/waiting for
add_payment = '//*[contains(text(),"Add Payment Method")]'
payment_window = '//*[contains(text(),"Add Payment Information")]'
payment_from_bm = '//*[contains(text(),"Business Manager Payment Method")]'
cont_button = 'div[aria-label="Next"]'
card_window = '//*[contains(text(),"Add Business Manager payment method")]'
card_xpath = '//*[contains(text(),"{0}")]'.format(target_card)
cont_button2 = 'div[aria-label="Confirm"]'
success = '//*[contains(text(),"{0} is now the primary payment")]'.format(target_card)

gs = GSheets(outh_file='path-to-outh_file')
# create master df by reading Google Sheet with ad account table
dfm = gs.read('Ad Account Database','Active','A1','B')
dfm['link'] = dfm['account_id'].apply(lambda x: url.format(x))
# add placeholder columns
dfm['done'] = None
dfm['attempts'] = 0
dfm['account_status'] = None
dfm['card'] = None
# use fb_refresh to pull realtime account statuses and current cards
dfm = fb_refresh(dfm,['card','account_status'],key='account_id')
# filter out accounts that are disabled or already have the target card
mask = (dfm['account_status']==1)&(dfm['card']!=target_card.upper())
df = reset(dfm.loc[mask])

# initialize Chrome webdriver
driver, wait = start_chrome()

# time to loop through the df!
# it's a good idea to loop through a few times to catch anything that stalled/failed
y = 0
while y < 3 and (df['done']!='Y').any():
    y += 1
    # filter out items that are either done or have 3+ failed attempts (not worth trying these again)
    todo = (df['done']!='Y')&(df['attempts']<3)
    z = 0
    for row in df.loc[todo].itertuples():
        z += 1
        df.loc[row.Index,'attempts'] += 1
        try:
            # wait for account's payment page to load, then click "Add Payment Method"
            driver.get(row.link)
            WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,add_payment)))
            driver.find_element_by_xpath(add_payment).click()

            # wait for next window to load, then click "Business Manager Payment Method" and then "Continue"
            WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,payment_window)))
            WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,payment_from_bm)))
            WebDriverWait(driver,10).until(EC.visibility_of_element_located((By.XPATH,payment_from_bm)))
            driver.find_element_by_xpath(payment_from_bm).click()
            WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,cont_button)))
            driver.find_element_by_css_selector(cont_button).click()

            # wait for next window to load, then find the target card and click it
            WebDriverWait(driver,15).until(EC.visibility_of_element_located((By.XPATH,card_window)))
            wait.until(EC.element_to_be_clickable((By.XPATH,card_xpath)))
            driver.find_element_by_xpath(card_xpath).click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,cont_button2)))
            driver.find_element_by_css_selector(cont_button2).click()

            # wait for confirmation that the change was successfully applied
            WebDriverWait(driver,30).until(EC.visibility_of_element_located((By.XPATH,success)))
            df.loc[row.Index,'done'] = 'Y'
            teal(f'{z}/{to_go} <b>act_{row.account_id}</b>')
        except:
            err = show_error()
            errors.append({'account_id':row.account_id,'error':err})
            df.loc[row.Index,'done'] = 'ERROR'
            red('<b>ERROR</b>')

if (df['done']!='Y').any():
    num_failed = len(df.query("done != 'Y'"))
    red(f'{num_failed} accounts failed')
# save df + errors in a pickle file
fname = 'updated_accounts_{0}'.format(now('%m-%d-%y'))
save_pkl({'df':df,'errors':errors},fname,path='/desired-path/')
