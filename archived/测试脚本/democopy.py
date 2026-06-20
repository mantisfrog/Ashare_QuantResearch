import csv
from datetime import datetime

from tqcenter import tq

tq.initialize(__file__)
fdc = tq.get_stock_info(stock_code='688318.SH', field_list=['Name','rs_hyname','blockzscode'])
print(fdc)
