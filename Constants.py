class Constants:
    stocks_table_file_path: str = "stocks_table.csv"
    stocks_price_history_directory: str = "stocks_price_history/"
    saved_lists_directory: str = "saved_lists/"
    cash_price_history_file_path: str = "CASH_all_usa_dates.csv"
    symbol_list_file_path: str = "new_stocks_list.json"
    filename_encoding_dict = {":": "-", ".": "_"}
    minimum_values_count_for_file = 150
    days_count_for_volume = 100
    days_count_for_price = days_count_for_volume
    extra_days_for_volume_count = 7
    maximum_missing_days_in_a_row = 5

    # "Exchange == 'NASDAQ'" or "Exchange == 'NYSE'"  #
    # stock_table_filter_query = ("Exchange == 'NASDAQ'"
    #                             or "Exchange == 'NYSE'") and "start_date < '1995-01-01'"
    stock_table_filter_query = "(Country == 'USA')  \
                               and max_avg_volume > @Constants.minimum_avg_stock_volume \
                               and max_avg_price > @Constants.minimum_avg_price_for_stock"
    minimum_daily_stock_volume = 1000000  # Dollars
    minimum_price_for_stock = 3
    minimum_avg_stock_volume = 1000000
    minimum_avg_price_for_stock = 3
    loopback_periods_monthly = [[1, 3, 6, 12], [12, 24, 36], [60]]
    loopback_periods_weekly = [[1, 3, 6, 12], [12, 24, 36], [60]]
    loopback_periods_daily = [[1, 3, 5], [10, 20, 60], [60]]
    stats_period = 60
