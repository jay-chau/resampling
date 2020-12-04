import pandas as pd

##GLOBALS##
#File column names
start = 'Startdate'
end = 'Enddate'
identify = 'Meter id'
consumption = 'Consumption'
usagetype = 'Usage Type'

#Handlers
subtract_end = True #Subtract one from the end date (to handle inclusive date ranges)

#Created columns
daynum = 'daysnumber'
dayuse = 'daysconsumption'
blank = 'blank_column'
monthend = 'monthend'

##FUNCTIONS##
def importdata(f):
    return pd.read_csv(f,engine='c', dtype={
        identify: 'str', consumption: 'float', usagetype: 'str'
    }, parse_dates=[start, end], infer_datetime_format = True)

def shorten_date_range(d):
    if subtract_end == True:
        d[end] = d[end] - pd.Timedelta(days=1)
    return d

def grabyearmonth(row):
    return (row[end].year, row[end].month)

def processdata(d):
    d = shorten_date_range(d)
    d = createvariables(d)
    startday, endday, totaldays, totalmonth = createglobals(d)
    return d, startday, endday, totaldays, totalmonth

def createvariables(d):
    d[daynum] = (d[end] - d[start])
    d[dayuse] = d[consumption] / ((d[daynum]/pd.Timedelta(days=1))+1)
    d[monthend] = d.apply(lambda row: grabyearmonth(row), axis=1)
    return d

def createglobals(d):
    startday = d[start].min()
    endday = d[end].max()
    totaldays = int((endday - startday) / pd.Timedelta(days=1))
    totalmonth = (endday.year - startday.year)*12 + (endday.month - startday.month) + 1
    return startday, endday, totaldays,totalmonth

def shift_columns(d):
    date_tuple = (startday.year,startday.month)
    month_columns = list(d.loc[:,date_tuple:].columns)
    main_columns = list(d.loc[:,:date_tuple].columns)
    month_columns.insert(0, blank)
    columns_to_use = main_columns[:-1] + month_columns[:-1]
    d.columns = columns_to_use
    return d

def incrementvariables(year, i, y):
    i += 1
    if i >= 12:
        i=0
        y+=1
        print('Year Done : {}'.format(year+y))
    return i, y

def createmonths(d, startday, totalmonth):
    i = y = cumulative_correction = end_days = end_filter = 0
    for v in range(totalmonth):

        currentmonth = pd.datetime(startday.year+y,startday.month+i,1)
        month_tuple = (currentmonth.year, currentmonth.month)

        day_count = (currentmonth-d[start])/pd.Timedelta(days=1)
        day_end = (d[end] - currentmonth)/pd.Timedelta(days=1)

        start_pos = day_count >= 0
        end_pos = day_end >=0

        filter_mask = ((start_pos)&(end_pos))
        total_days_count = filter_mask*day_count

        d[month_tuple] = ((total_days_count - cumulative_correction*filter_mask) + ((1+end_days)*end_filter))*d[dayuse]


        cumulative_correction = total_days_count  
        end_days = day_end
        end_filter = (d[monthend] == month_tuple)

        i, y = incrementvariables(startday.year, i,y)
    d = shift_columns(d)
    return d

def rescalebill(f):
    d = importdata(f)
    d, startday, endday, totaldays,totalmonth = processdata(d)
    d = createmonths(d, startday,totalmonth)
    return d