import json
import math
import re

import pandas
import pandas as pd
import requests
import os
from Constants import Constants
from datetime import datetime
from SLinkedList import *


# class A:
#
#     def __init__(self):
#         pass


def get_next_month_index(date_list: list[datetime], start_index, interval):
    if start_index >= len(date_list) - 1:
        return None
    if interval == "day":
        if len(date_list) > start_index + 1:
            return start_index + 1
        else:
            return None

    month = date_list[start_index].month
    week = date_list[start_index].isocalendar().week
    i = start_index
    while i < len(date_list):
        if interval == "month":
            if month is not date_list[i].month:
                return i
        elif interval == "week":
            if week is not date_list[i].isocalendar().week:
                return i
        i += 1
    return len(date_list) - 1


class HistoryDownload:
    cash_name = "my cash"
    _cash_list_dict = {}  # Is initialized at load_cash_data
    __stocks_table = None  # Is initialized at load_stock_table
    url: str = "https://www.portfolio123.com/app/stock/issueData/"
    main_page_url: str = "https://www.portfolio123.com/app/stock/issues/"
    stocks_table_url: str = "https://www.portfolio123.com/stocklookup.jsp"
    my_headers: dict[str, str] = {"Connection": "keep-alive",
                                  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                                "like Gecko) "
                                                "Chrome/91.0.4472.124 Safari/537.36",
                                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                                            "image/webp, image/apng, */*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                                  "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.9,he;q=0.8",
                                  "Cookie":
                                      "JSESSIONID=2FA1DE12BB47371FE08FA8DEDEF575B7; "
                                      "customerly_jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
                                      ".eyJpc3MiOiJodHRwczovL2N1c3RvbWVybHkuaW8iLCJqdGkiOiJiMjZmZjdkYy04MjBiLTExZWQtYT"
                                      "c5OS0wMjQyYWMxMjAwMDQiLCJpYXQiOjE2NzE3MjIyMjYuODI4NzUyLCJuYmYiOjE2NzE3MjIyMjYuOD"
                                      "I4NzU2LCJleHAiOjI2NTAwMjk0MjYuODI4NzU4LCJ0eXBlIjo0LCJhcHAiOiI0ZTgwNzQ4NiIsImlkIj"
                                      "oyODUzMTQzM30.KUhpASOCSaS7YNJnKk_1wLV7Pymr6V_luxv03VqZNMY;"
                                      "XSRF-TOKEN=z3VyimZMXRmm9HclRKZD;"
                                      "P123AUTH=9dee840d-ee29-420a-ba45-5e0d7e6cbaa51a792eac-85fd-4d3f-8395-04540d95435"
                                      "f "
                                  }

    @classmethod
    def __remove_garbage_from_ticker(cls, ticker_str, country):
        str_parts = ticker_str.split(":" + country)
        ticker = str_parts[0] + ":" + country
        return ticker

    @classmethod
    def download_stock_table(cls):
        my_data = {'symbol': '', 'name': '', 'activeOnly': '0', 'country': 'any', 'sumAll': '', 'sumExact': '',
                   'sumOne': '', 'orderBy': '3', 'rowspp': '0', 'offset': '0', 'resulttot': '0', 'hiddenGo': 'true',
                   'mkttype': '1'}

        r = requests.post(cls.stocks_table_url, headers=cls.my_headers, data=my_data)
        print(r.text)
        table = pd.read_html(r.text, skiprows=[0], header=[0])[0]
        print(1)
        table = table.iloc[:, 1:]
        table['Ticker'] = table.apply(lambda x: cls.__remove_garbage_from_ticker(x["Ticker"], x["Country"]), axis=1)
        print(1)
        table.to_csv(Constants.stocks_table_file_path)
        print(1)
        # print(table)

    @classmethod
    def get_dates_from_mega_file(cls):
        file_path = Constants.stocks_price_history_directory + "all_usa_stocks.csv"
        out_path = Constants.stocks_price_history_directory + "all_usa_dates.csv"

        with open(file_path) as f:
            lines = f.readlines()
        new_line_list = []
        for line in lines:
            # try:
            match = re.search(r'(\d+/\d+/\d+)', line)
            if match is not None:
                tmp_line = match.group(1)
                new_line_list.append(tmp_line)
            # except:
        uniq_list = set(new_line_list)

        text = ""
        for uniq_line in uniq_list:
            text += uniq_line + "\r\n"
        with open(out_path, "w") as f:
            f.write(text)

    @classmethod
    def load_stock_history_table(cls, stock_name):
        encoded_stock_name = stock_name
        for key in Constants.filename_encoding_dict:
            encoded_stock_name = encoded_stock_name.replace(key, Constants.filename_encoding_dict[key])

        if stock_name == cls.cash_name:
            file_path = Constants.cash_price_history_file_path
        else:
            file_path = "{0}{1}.csv".format(Constants.stocks_price_history_directory, encoded_stock_name)
        try:
            with open(file_path, mode='r') as f:
                stock_history_table = pd.read_csv(f)
        except:
            #  print("Error loading ", file_path, ", skipping")
            return None
        return stock_history_table

    @classmethod
    def load_stock_table(cls, filter_expression: str = None):
        if cls.__stocks_table is None:
            with open(Constants.stocks_table_file_path, mode='r') as f:
                cls.__stocks_table = pd.read_csv(f)

        table = cls.__stocks_table
        if filter_expression:
            table = table.query(filter_expression)
        return table

    @classmethod
    def load_stock_metadata(cls, stock_name):
        table = cls.load_stock_table()
        return table.loc[table['Ticker'] == stock_name]

    # @classmethod
    # def get_min_price_and_min_volume(cls, table, index, count):
    #     min_price = None
    #     min_volume = None
    #
    #     for i in range(index, index + count):
    #         if min_price is None or min_price > table["Value"][i]:
    #             min_price = table["Value"][i]
    #

    @classmethod
    def load_stock_ticker_list(cls, query: bool):
        if query:
            table = cls.load_stock_table(filter_expression=Constants.stock_table_filter_query)
        else:
            table = cls.load_stock_table()
        stock_ticker_list = table["Ticker"].tolist()
        return stock_ticker_list

    @classmethod
    def download_stocks_history(cls, query: bool):
        session = requests.session()
        session.headers = cls.my_headers
        session.verify = False

        # with open(Constants.symbol_list_file_path, mode="r") as symbol_list_file:
        #     symbol_list: list[str] = json.load(symbol_list_file)

        symbol_list = cls.load_stock_ticker_list(query)
        for symbol in symbol_list:
            # print(symbol)

            encoded_symbol: str = symbol
            for key in Constants.filename_encoding_dict:
                encoded_symbol = encoded_symbol.replace(key, Constants.filename_encoding_dict[key])
            symbol_file_path: str = "{0}{1}.csv".format(Constants.stocks_price_history_directory, encoded_symbol)

            if not os.path.isfile(symbol_file_path):
                print("Downloading", symbol)
                symbol_page_url = cls.main_page_url + symbol

                retry: bool = True
                while retry:
                    try:

                        # Loading main page for symbol
                        r = session.get(symbol_page_url)

                        if r.status_code != 200:
                            raise Exception
                        data = r.json()["issues"][0]
                        start_date_str = data["startDt"]
                        end_date_str = data["endDt"]
                        end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
                        start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
                        # start_date = end_date.replace(year=end_date.year - 2)
                        end_date_str = end_date.strftime("%m/%d/%Y")
                        start_date_str = start_date.strftime("%m/%d/%Y")

                        # Getting the actual history table
                        # 0 - price, 1 - divs + splits, 2 - splits only
                        r = session.post(cls.url + symbol, json={"mktUid": data["mktUid"],
                                                                 "period": "MAX",
                                                                 "startDt": start_date_str, "endDt": end_date_str,
                                                                 "adjustment": 2})
                        # Saving table to CSV
                        prices_data = r.json()
                        table = pd.json_normalize(prices_data["prices"])
                        table.to_csv(symbol_file_path)

                        retry = False
                        print("Downloaded", symbol)
                    except requests.exceptions.ConnectionError:
                        print("Connection error, retrying {0}".format(symbol))
                        session = requests.session()
                        session.headers = cls.my_headers
                        session.verify = False

                        retry = True
                    except BaseException as e:
                        print("error: symbol {0} skipped".format(symbol))

                        retry = False

    @classmethod
    def download_stocks_volume(cls):
        session = requests.session()
        session.headers = cls.my_headers

        symbol_list = cls.load_stock_ticker_list(False)
        for symbol in symbol_list:
            print(symbol)

            encoded_symbol: str = symbol
            for key in Constants.filename_encoding_dict:
                encoded_symbol = encoded_symbol.replace(key, Constants.filename_encoding_dict[key])
            symbol_file_path: str = "{0}{1}.csv".format(Constants.stocks_price_history_directory, encoded_symbol)

            if not os.path.isfile(symbol_file_path):
                symbol_page_url = cls.main_page_url + symbol

                retry: bool = True
                while retry:
                    try:

                        # Loading main page for symbol
                        r = session.get(symbol_page_url)
                        if r.status_code != 200 or '<div id="prices-data"></div>' not in r.text:
                            print(r.status_code, '<div id="prices-data"></div>' in r.text)
                            raise Exception

                        # Getting the actual history table
                        # 0 - price, 1 - divs + splits, 2 - splits only
                        r = session.post(cls.url, data={"adjustment": 2})

                        # Saving table to CSV
                        table = pd.read_html(r.text)[0]
                        table = table[:len(table) - 1]
                        table.to_csv(symbol_file_path)

                        retry = False
                    except requests.exceptions.ConnectionError:
                        print("Connection error, retrying {0}".format(symbol))
                        session = requests.session()
                        session.headers = cls.my_headers

                        retry = True
                    except BaseException:
                        print("error: symbol {0} skipped".format(symbol))

                        retry = False

    @classmethod
    def download_stock_volume(cls, query: bool):
        session = requests.session()
        session.headers = cls.my_headers
        session.verify = False

        # with open(Constants.symbol_list_file_path, mode="r") as symbol_list_file:
        #     symbol_list: list[str] = json.load(symbol_list_file)

        symbol_list = cls.load_stock_ticker_list(query)
        for symbol in symbol_list:
            # print(symbol)

            encoded_symbol: str = symbol
            for key in Constants.filename_encoding_dict:
                encoded_symbol = encoded_symbol.replace(key, Constants.filename_encoding_dict[key])
            symbol_file_path: str = "{0}{1}.csv".format(Constants.stocks_price_history_directory, encoded_symbol)

            if os.path.isfile(symbol_file_path):
                print("checking volume", symbol)

                retry: bool = True
                while retry:
                    try:
                        url1 = format("https://www.portfolio123.com/app/stock/fundChartCtx?t={}", symbol)
                        # Loading main page for symbol
                        r1 = session.get(url1)

                        if r1.status_code != 200:
                            raise Exception

                        # data_to_post = {'graphType': 'line', 'name': 'Volume, averages, and liquidity Daily (10 Days)',
                        #                 'formula': 'VolD%ShsOut', 'excludeEqualValues': False}
                        # url2 = "https://www.portfolio123.com/app/stock/fundChartMetric"
                        #
                        # r2 = session.post(url2, json=data_to_post)
                        #
                        # data_recieved = r2.json()
                        # metric_id = int(data_recieved["metric"]["id"])

                        url3 = "https://www.portfolio123.com/app/stock/fundChartSeries?endDt=2022-12-11" \
                               "&metricId=2&startDt=2010-01-01"
                        r3 = session.get(url3)


                        start_date_str = data["startDt"]
                        end_date_str = data["endDt"]
                        end_date = datetime.strptime(end_date_str, "%Y/%m/%d")
                        start_date = datetime.strptime(start_date_str, "%Y/%m/%d")
                        # start_date = end_date.replace(year=end_date.year - 2)
                        end_date_str = end_date.strftime("%m/%d/%Y")
                        start_date_str = start_date.strftime("%m/%d/%Y")

                        # Getting the actual history table
                        # 0 - price, 1 - divs + splits, 2 - splits only
                        r = session.post(cls.url + symbol, json={"mktUid": data["mktUid"],
                                                                 "period": "MAX",
                                                                 "startDt": start_date_str, "endDt": end_date_str,
                                                                 "adjustment": 2})
                        # Saving table to CSV
                        prices_data = r.json()
                        table = pd.json_normalize(prices_data["prices"])
                        table.to_csv(symbol_file_path)

                        retry = False
                        print("Downloaded", symbol)
                    except requests.exceptions.ConnectionError:
                        print("Connection error, retrying {0}".format(symbol))
                        session = requests.session()
                        session.headers = cls.my_headers
                        session.verify = False

                        retry = True
                    # except BaseException as e:
                    #     print("error: symbol {0} skipped".format(symbol))
                    #
                    #     retry = False

    @classmethod
    def save_linked_list_to_csv(cls, linked_list, filename=None):
        node = linked_list.head
        if filename is None:
            if node.data.ref is None:
                filename = node.data.asset
            else:
                filename = datetime.now().timestamp()
        file_path: str = "{0}{1}.csv".format(Constants.saved_lists_directory, filename)
        row = 0
        dict = {"Date": [], "Return": []}
        while node is not None:
            dict["Date"].append(node.data.date)
            dict["Return"].append(node.data.data)
            row += 1
            node = node.nextval

        dataframe = pandas.DataFrame(dict)
        dataframe.to_csv(file_path)

    @classmethod
    def __to_float(cls, x):
        if type(x) == str:
            x = float(x.replace(',', ''))
        return x

    @classmethod
    def load_stock_file_to_arrs(cls, stock_name, max_end_date=None):
        stock_history_table = cls.load_stock_history_table(stock_name)
        if stock_history_table is None:
            print("Error loading ", stock_name, ", skipping")
            return None

        dates_str_arr = list(reversed(stock_history_table["dt"]))  # Date
        dates_arr = []
        for date_str in dates_str_arr:
            try:
                date = datetime.strptime(date_str, "%Y/%m/%d")
            except:  # For files edited by Excel:
                date = datetime.strptime(date_str, "%d/%m/%Y")
            if max_end_date is None or date < max_end_date:
                dates_arr.append(date)
            else:
                break
        values_arr = list(reversed(stock_history_table["open"]))
        volume_arr = list(reversed(stock_history_table["vol"]))
        for i in range(len(values_arr)):
            values_arr[i] = cls.__to_float(values_arr[i])
            volume_arr[i] = cls.__to_float(volume_arr[i])

        return dates_arr, values_arr, volume_arr

    @classmethod
    def get_avg(cls, arr, index, count):
        if index + count > len(arr):
            raise Exception()

        sum = 0
        for i in range(index, index + count):
            sum += arr[i]
        avg = sum / count
        return avg

    @classmethod
    def get_max_avg(cls, arr, count):
        avg = cls.get_avg(arr, 0, count)
        tmp_sum = avg * count
        max_sum = tmp_sum

        for i in range(len(arr) - count):
            tmp_sum = tmp_sum - arr[i] + arr[i + count]
            if tmp_sum > max_sum:
                max_sum = tmp_sum
        return max_sum / count

    @classmethod
    def update_dates_to_stock_table(cls):
        with open(Constants.stocks_table_file_path, mode='r') as f:
            table = pd.read_csv(f)

        if "start_date" not in table:
            table = table.assign(start_date=float("nan"), end_date=float("nan"))
        if "max_avg_volume" not in table:
            table = table.assign(max_avg_volume=float("nan"), max_avg_price=float("nan"))

        update_count = 0
        for i in range(len(table.index)):
            val = table["max_avg_volume"][i]
            if isinstance(val, float) and math.isnan(val):
                stock_name = table["Ticker"][i]

                try:
                    dates_arr, values_arr, volume_arr = cls.load_stock_file_to_arrs(stock_name)
                    dates_arr, values_arr, volume_arr = cls.fill_missing_stock_data(stock_name, dates_arr, values_arr,
                                                                                    volume_arr)
                except Exception as e:
                    continue

                volume_usd_arr = []
                for j in range(len(volume_arr)):
                    volume_usd_arr.append(volume_arr[j] * values_arr[j])

                table.at[i, "max_avg_volume"] = cls.get_max_avg(volume_usd_arr, Constants.days_count_for_volume)
                table.at[i, "max_avg_price"] = cls.get_max_avg(values_arr, Constants.days_count_for_price)
                table.at[i, "start_date"] = dates_arr[0]
                table.at[i, "end_date"] = dates_arr[-1]
                update_count += 1

                if update_count % 1000 == 0:
                    table.to_csv(Constants.stocks_table_file_path)
                    print(str(update_count), "/", len(table.index))

        if update_count > 0:
            table.to_csv(Constants.stocks_table_file_path)

    @classmethod
    def fill_missing_stock_data(cls, stock_name, dates_arr, values_arr, volume_arr):
        dates_arr = dates_arr[:]
        values_arr = values_arr[:]
        volume_arr = volume_arr[:]
        cash_dates_arr, cash_values_arr, cash_volume_arr = cls.get_cash_arrs()
        first_date_index = cash_dates_arr.index(dates_arr[0])
        cash_dates_arr = cash_dates_arr[first_date_index:]

        # for i in range(len(dates_arr) - 1):
        i = 0
        while i < len(dates_arr):  # - 1:
            if dates_arr[i] != cash_dates_arr[i]:
                # if dates_arr[i] == cash_dates_arr[i + 1]:
                #     print("filling data for", stock_name)
                #     date = cash_dates_arr[i]
                #     value = (values_arr[i] + values_arr[i-1]) / 2
                #     volume = (volume_arr[i] + volume_arr[i-1]) / 2
                #
                #     dates_arr.insert(i, date)
                #     values_arr.insert(i, value)
                #     volume_arr.insert(i, volume)
                if dates_arr[i] > cash_dates_arr[i]:
                    delta_days = 1
                    while dates_arr[i] != cash_dates_arr[i + delta_days]:
                        delta_days += 1
                    if delta_days > Constants.maximum_missing_days_in_a_row:
                        #  print(stock_name, "bad dates, missing days in a row: ", str(dates_arr[i] - cash_dates_arr[i]),
                        #      str(cash_dates_arr[i]), "-", str(dates_arr[i]))
                        # if i < len(dates_arr) - 1:
                        print("deleted from", str(dates_arr[0]), "to", str(dates_arr[i]), "for", stock_name)
                        dates_arr = dates_arr[i:]
                        values_arr = values_arr[i:]
                        volume_arr = volume_arr[i:]
                        cash_dates_arr = cash_dates_arr[i + delta_days:]
                        i = 0
                        # else:
                        #     raise Exception("bad stock data")
                    else:
                        #  print("filling", str(delta_days), "days of data for", stock_name)

                        delta_value = (values_arr[i] - values_arr[i - 1]) / delta_days
                        delta_volume = (volume_arr[i] - volume_arr[i - 1]) / delta_days
                        for days_counter in range(delta_days):
                            date = cash_dates_arr[i + days_counter]
                            value = (values_arr[i - 1] + delta_value * days_counter)
                            volume = (volume_arr[i - 1] + delta_volume * days_counter)

                            dates_arr.insert(i + days_counter, date)
                            values_arr.insert(i + days_counter, value)
                            volume_arr.insert(i + days_counter, volume)
                elif dates_arr[i] < cash_dates_arr[i]:
                    print("you need to add " + str(dates_arr[i]) + "to cash dates for", stock_name)
                    raise Exception("cash bad dates")
                else:
                    #  print(stock_name, " bad dates, missing days in a row: ", str(dates_arr[i] - cash_dates_arr[i]),
                    #  str(cash_dates_arr[i]), "-", str(dates_arr[i]))
                    raise Exception(stock_name + " bad dates")
            elif values_arr[i] == 0:  # or values_arr[i] * volume_arr[i] < Constants.minimum_daily_stock_volume:
                values_arr[i] = 0.0001
                # if i < len(dates_arr) - 1:
                #     dates_arr = dates_arr[i + 1:]
                #     values_arr = values_arr[i + 1:]
                #     volume_arr = volume_arr[i + 1:]
                #     cash_dates_arr = cash_dates_arr[i + 1:]
                #     i = 0
                # else:
                #     raise Exception("bad stock data")
            i += 1

        if len(dates_arr) < Constants.minimum_values_count_for_file:
            raise Exception("Not enough days for", stock_name, "skipping")

        return dates_arr, values_arr, volume_arr

    @classmethod
    def load_stock_data_new_new(cls, stock_name, interval, dates_arr, values_arr, volume_arr, min_start_date=None):
        if len(values_arr) < Constants.minimum_values_count_for_file or \
                (min_start_date is not None and dates_arr[0] > min_start_date):

            return None
        else:
            pass
            # print(str(dates_arr[0]), "<", str(min_start_date))
            # print("added", stock_name)

        linked_list = LinkedList()
        linked_list.data = InvestMetadata()
        linked_list.data.metadata_df = cls.load_stock_metadata(stock_name)
        previous_node = None
        months_count = 0
        last_month_value_index = 0

        current_month_index = get_next_month_index(dates_arr, 0, interval)
        next_month_index = get_next_month_index(dates_arr, current_month_index, interval)

        # Making sure there is a minimum count of days for volume calculation
        days_to_wait = Constants.days_count_for_volume
        if interval == "month":
            days_to_wait += 7  # In order to handle a situation which monthly stock head is earlier than weekly
        while current_month_index is not None and current_month_index <= days_to_wait:
            current_month_index = next_month_index
            next_month_index = get_next_month_index(dates_arr, current_month_index, interval)
        if next_month_index is None:
            return None

        first_iteration = True
        while next_month_index is not None:
            my_date = dates_arr[current_month_index]
            my_node = LNode()
            my_node.parent = linked_list
            my_node.data = InvestData()
            my_node.data.asset = stock_name
            my_node.data.date = my_date
            my_node.data.description = stock_name

            num1 = cls.__to_float(values_arr[next_month_index])
            num2 = cls.__to_float(values_arr[current_month_index])

            if num1 == 0 or num2 == 0:
                raise Exception("stock has a value of 0:", stock_name)

            # Getting min and avg volume
            min_vol = None
            sum_vol = 0
            for i in range(next_month_index - Constants.days_count_for_volume, next_month_index):
                temp_volume = cls.__to_float(volume_arr[i])
                temp_value = cls.__to_float(values_arr[i])
                temp_vol_usd = temp_volume * temp_value

                if min_vol is None or temp_vol_usd < min_vol:
                    min_vol = temp_vol_usd
                sum_vol += temp_vol_usd
            avg_vol = sum_vol / Constants.days_count_for_volume

            # Getting min and avg price
            min_price = None
            sum_price = 0
            for i in range(next_month_index - Constants.days_count_for_price, next_month_index):
                temp_price = cls.__to_float(values_arr[i])

                if min_price is None or temp_price < min_price:
                    min_price = temp_price
                sum_price += temp_price
            avg_price = sum_price / Constants.days_count_for_price

            my_node.data.min_volume = min_vol
            my_node.data.avg_volume = avg_vol
            my_node.data.min_price = min_price
            my_node.data.avg_price = avg_price
            my_node.data.data = num1 / num2
            my_node.data.start_price = num2
            my_node.data.end_price = num1
            my_node.data.until_date = dates_arr[next_month_index]
            if my_node.data.date == my_node.data.until_date:
                raise Exception("Bad dates")
            my_node.prevval = previous_node
            if first_iteration:
                first_iteration = False
                linked_list.head = my_node
                if stock_name != cls.cash_name:
                    cash_list = cls.load_cash_data_by_date(my_node.data.date, interval)
                    if cash_list is None:
                        raise Exception("bad date for cash:", my_node.data.date)
                        #  return None
                    my_node.data.cash_ref = cash_list.head
                    my_node.data.stock_ref = my_node

            else:
                if stock_name != cls.cash_name:
                    my_node.data.cash_ref = previous_node.data.cash_ref.nextval
                    my_node.data.stock_ref = my_node
                    if my_node.data.date != my_node.data.cash_ref.data.date:
                        raise Exception("bad dates for:", stock_name, "stock has:", my_node.data.date, "cash:",
                                        my_node.data.cash_ref.data.date)
                        #  print("bad dates for:", stock_name, "stock has:", my_node.date, "cash:", my_node.cash_ref.date)
                        #  return None
                previous_node.nextval = my_node
            previous_node = my_node

            current_month_index = next_month_index
            next_month_index = get_next_month_index(dates_arr, current_month_index, interval)
        return linked_list

        # for i in range(current_month_index, len(dates_arr)):
        #     my_date = datetime.strptime(dates_arr[i], "%Y/%m/%d")
        #     previous_date = datetime.strptime(dates_arr[i - 1], "%Y/%m/%d")
        #
        #     # Check if new month
        #     if my_date.month != previous_date.month:
        #         my_node = Node(stock_name, date=my_date)
        #         if months_count > 0:
        #             my_node.data = values_arr[i] / values_arr[last_month_value_index]
        #             my_node.prevval = previous_node
        #             previous_node.nextval = my_node
        #         else:
        #             linked_list.head = my_node
        #         previous_node = my_node
        #         months_count += 1
        #         last_month_value_index = i
        #
        # return linked_list

    @classmethod
    def get_stocklists_subset_by_metadata_param(cls, stocklists_arr, param_name, param_val):
        stocks_subset = [stock for stock in stocklists_arr if stock.data.metadata_df[param_name].values[0] == param_val]
        return stocks_subset

    @classmethod
    def get_sectors_list(cls, filter_expression=None):
        table = cls.load_stock_table(filter_expression=filter_expression)
        sectors = list(set(table["Sector"].values))
        return sectors

    @classmethod
    def get_stocklists_subsets_list_by_sector(cls, stocklists_arr):
        sectors = cls.get_sectors_list()
        stocklists_subsets_list = []
        for sector in sectors:
            stocklists_subset = cls.get_stocklists_subset_by_metadata_param(stocklists_arr, "Sector", sector)
            if len(stocklists_subset) > 0:
                stocklists_subsets_list.append(stocklists_subset)
        return stocklists_subsets_list

    @classmethod
    def link_times_by_key(cls, stock_data_1, stock_data_2, key_str):
        if stock_data_1 is not None and stock_data_2 is not None:
            tmp_node = stock_data_1.head
            while tmp_node is not None:
                tmp_node_2 = stock_data_2.head
                executed = False

                last_date = 0
                last_date_2 = 0

                while tmp_node_2 is not None:
                    if tmp_node.data.date >= tmp_node_2.data.date and (
                            tmp_node_2.nextval is None or tmp_node_2.nextval.data.date > tmp_node.data.date):
                        exec("tmp_node.data.{}_ref = tmp_node_2".format(key_str))
                        executed = True
                        last_date = tmp_node.data.date
                        last_date_2 = tmp_node_2.data.date
                    tmp_node_2 = tmp_node_2.nextval
                if not executed:
                    raise Exception("could not link times for", stock_data_1.head.data.asset, str(last_date),
                                    str(last_date_2))
                tmp_node = tmp_node.nextval

    @classmethod
    def link_times(cls, stock_data_day, stock_data_week, stock_data_month):
        cls.link_times_by_key(stock_data_month, stock_data_week, "week")
        cls.link_times_by_key(stock_data_month, stock_data_day, "day")
        cls.link_times_by_key(stock_data_week, stock_data_day, "day")

    @classmethod
    def load_stock_data_multiple_interval(cls, stock_name, is_day, is_week, is_month, min_start_date=None,
                                          max_end_date=None):
        try:
            dates_arr, values_arr, volume_arr = cls.load_stock_file_to_arrs(stock_name, max_end_date)
            dates_arr, values_arr, volume_arr = cls.fill_missing_stock_data(stock_name, dates_arr, values_arr,
                                                                            volume_arr)
        except Exception as e:
            return None

        day_data = None
        week_data = None
        month_data = None

        if is_day:
            day_data = cls.load_stock_data_new_new(stock_name, "day", dates_arr, values_arr, volume_arr, min_start_date)
        if is_week:
            week_data = cls.load_stock_data_new_new(stock_name, "week", dates_arr, values_arr, volume_arr,
                                                    min_start_date)
        if is_month:
            month_data = cls.load_stock_data_new_new(stock_name, "month", dates_arr, values_arr, volume_arr,
                                                     min_start_date)

        if (month_data is not None and week_data is None) or (month_data is None and week_data is not None):
            raise Exception("woot", stock_name)
        cls.link_times(day_data, week_data, month_data)

        return day_data, week_data, month_data

    @classmethod
    def load_all_stocks_data(cls, query: bool, is_day=False, is_week=True, is_month=True, max_count=0,
                             min_start_date=None, max_end_date=None):
        stock_lists_arr = []
        # filenames_list = os.listdir(Constants.stocks_price_history_directory)
        ticker_list = cls.load_stock_ticker_list(query)
        i = 0

        for ticker in ticker_list:
            try:

                stock_day, stock_week, stock_month = cls.load_stock_data_multiple_interval(ticker, is_day, is_week,
                                                                                           is_month,
                                                                                           min_start_date=min_start_date,
                                                                                           max_end_date=max_end_date)
            except TypeError as e:
                continue
            if is_month:
                stock_list = stock_month
            elif is_week:
                stock_list = stock_week
            else:
                stock_list = stock_day

            if stock_list is not None:
                stock_lists_arr.append(stock_list)
                print(ticker, i)
                i += 1
                if i >= max_count > 0:
                    return stock_lists_arr

        # for filename in filenames_list:
        #     if filename.endswith(".csv"):
        #         encoded_stock_name = filename[:-4]
        #         stock_name = encoded_stock_name
        #         for key in Constants.filename_encoding_dict:
        #             stock_name = stock_name.replace(Constants.filename_encoding_dict[key], key)
        #         stock_list = cls.load_stock_data(stock_name)
        #         if stock_list is not None:
        #             stock_lists_arr.append(stock_list)
        #             print(stock_name, stock_list)
        #             i += 1
        #             if i >= max_count > 0:
        #                 return stock_lists_arr

        return stock_lists_arr

    @classmethod
    def get_cash_arrs(cls):
        if "dates_arr" not in cls._cash_list_dict.keys():
            dates_arr, values_arr, volume_arr = cls.load_stock_file_to_arrs(cls.cash_name)
            cls._cash_list_dict["dates_arr"] = dates_arr
            cls._cash_list_dict["values_arr"] = values_arr
            cls._cash_list_dict["volume_arr"] = volume_arr
        return cls._cash_list_dict["dates_arr"], cls._cash_list_dict["values_arr"], cls._cash_list_dict["volume_arr"]

    @classmethod
    def load_cash_data(cls, interval):
        if "dates_arr" not in cls._cash_list_dict.keys():
            (dates_arr, values_arr, volume_arr) = cls.load_stock_file_to_arrs(cls.cash_name)
            cls._cash_list_dict["dates_arr"] = dates_arr
            cls._cash_list_dict["values_arr"] = values_arr
            cls._cash_list_dict["volume_arr"] = volume_arr

        if interval not in cls._cash_list_dict.keys():
            cls._cash_list_dict[interval] = cls.load_stock_data_new_new(cls.cash_name, interval,
                                                                        cls._cash_list_dict["dates_arr"],
                                                                        cls._cash_list_dict["values_arr"],
                                                                        cls._cash_list_dict["volume_arr"])
        return cls._cash_list_dict[interval]

    @classmethod
    def load_cash_data_by_date(cls, date, interval):
        cash_list = cls.load_cash_data(interval)

        node = cash_list.head
        while node is not None:
            if node.data.date == date:
                linked_list = LinkedList()
                linked_list.head = node
                return linked_list
            node = node.nextval
        return None
