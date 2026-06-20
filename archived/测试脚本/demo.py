import csv
from datetime import datetime

from tqcenter import tq

tq.initialize(__file__)
# df = tq.get_market_data(
# field_list = ['Close'],
# stock_list = ["600696.SH"],
# start_time = '20260428',
# end_time = '20260608',
# dividend_type='front',
# period='1d',
# )

trade_dates = tq.get_trading_dates(
    market='SZ',
    start_time='',
    end_time='',
)
trade_dates = sorted(map(int, trade_dates), reverse=True)

with open('dim_trade_date.csv', 'w', newline='', encoding='utf-8-sig') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['trade_day_id', 'trade_date'])
    writer.writerows(
        (
            trade_day_id,
            datetime.strptime(str(trade_day_id), '%Y%m%d').date(),
        )
        for trade_day_id in trade_dates
    )
