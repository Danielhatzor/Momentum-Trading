import os
import time

from Momentum import Momentum
from SLinkedList import InvestData
from datetime import *
from LinkedList import *
from Statistics import Statistics
from stock_history import HistoryDownload


class Backtest:
    @classmethod
    def get_relative_momentum(cls, stocks, stock_count, total_return_time_lengths, std_time_length, description,
                              condition_key, skip_return_last_node, skip_std_last_node):
        arrr = []
        for stock in stocks:
            if stock.head.data.date == stock.head.data.until_date:
                raise Exception("Impossible dates")
            stat = Statistics.get_statistics_list_relative_momentum(stock.head, total_return_time_lengths,
                                                                    std_time_length, skip_return_last_node,
                                                                    skip_std_last_node)
            if stat is not None:
                arrr.append(stat.head)
        stat_mat = Statistics.get_best_scoring_stock_lists_array(arrr, stock_count, condition_key)
        rel_mom = cls.summarize_stat_nodes_into_one_investment(stat_mat, description)

        return rel_mom

    @classmethod
    def summarize_investments_into_one(cls, investment_nodes_list, data_key, description, condition_key,
                                       start_together=False):
        temp_investment_nodes_list = investment_nodes_list[:]

        latest_start_date = None
        # Getting rid of irrelevant nodes at the beginning
        for i in range(len(temp_investment_nodes_list)):
            tmp_data = data_key(temp_investment_nodes_list[i])
            while temp_investment_nodes_list[i] is not None and condition_key is not None and not \
                    condition_key(temp_investment_nodes_list[i], lambda x: x.data):
                temp_investment_nodes_list[i] = temp_investment_nodes_list[i].nextval
                if temp_investment_nodes_list[i] is not None:
                    tmp_data = data_key(temp_investment_nodes_list[i])
            if temp_investment_nodes_list[i] is not None and \
                    (latest_start_date is None or latest_start_date < data_key(temp_investment_nodes_list[i]).date):
                latest_start_date = data_key(temp_investment_nodes_list[i]).date

        if start_together:
            for i in range(len(temp_investment_nodes_list)):
                while temp_investment_nodes_list[i] is not None and \
                        data_key(temp_investment_nodes_list[i]).date < latest_start_date:
                    temp_investment_nodes_list[i] = temp_investment_nodes_list[i].nextval

        temp_investment_nodes_list = [i for i in temp_investment_nodes_list if i is not None]

        # Setting invest_date
        date_node = None
        invest_date = datetime.today()
        for temp_node in temp_investment_nodes_list:
            node_data = data_key(temp_node)
            if node_data.date < invest_date:
                date_node = data_key(temp_node).cash_ref
                invest_date = node_data.date

        summary_linked_list = LinkedList()
        prev_summary_node = None
        while len(temp_investment_nodes_list) > 0:
            count_investments = 0
            sum_return = 0
            max_data = 0
            max_data_node = None
            latest_until_date = invest_date
            for i in range(len(temp_investment_nodes_list)):
                temp_node = temp_investment_nodes_list[i]
                node_data = data_key(temp_node)

                if node_data.date < invest_date:
                    raise Exception
                elif node_data.date == invest_date:
                    if condition_key is None or condition_key(temp_node, lambda x: x.data):
                        count_investments += 1
                        if node_data.until_date > latest_until_date:
                            latest_until_date = node_data.until_date
                        if node_data.data > max_data:
                            max_data = node_data.data
                            max_data_node = node_data
                            # print(node_data.asset, "is a problem")
                            # time.sleep(60)
                        sum_return += node_data.data
                    temp_investment_nodes_list[i] = temp_node.nextval

            if count_investments == 0:
                avg_return = 1
                # print("no investments were chosen, using 1 instead")
            else:
                avg_return = sum_return / count_investments
                # print(str(max_data), str(avg_return), max_data_node.asset)
            print(str(avg_return), str(invest_date))

            summary_node = LNode()
            summary_node.data = InvestData()
            summary_node.data.data = avg_return
            summary_node.data.date = invest_date
            summary_node.data.count_investments = count_investments
            summary_node.data.until_date = latest_until_date
            summary_node.data.description = description
            summary_node.prevval = prev_summary_node
            if prev_summary_node is None:
                summary_linked_list.head = summary_node
            else:
                prev_summary_node.nextval = summary_node
            summary_node.parent = summary_linked_list

            prev_summary_node = summary_node
            date_node = date_node.nextval
            if date_node is not None:
                invest_date = data_key(date_node).date
            temp_investment_nodes_list = [i for i in temp_investment_nodes_list if i is not None]

        return summary_linked_list

    @classmethod
    def summarize_stat_nodes_into_one_investment(cls, stat_nodes_lists_arr, description):
        temp_stat_nodes_lists_arr = stat_nodes_lists_arr[:]
        while len(temp_stat_nodes_lists_arr[0]) == 0:
            temp_stat_nodes_lists_arr.pop(0)
        cash_date_node = temp_stat_nodes_lists_arr[0][0].end_node.data.cash_ref
        invest_date = cash_date_node.data.until_date

        summary_linked_list = LinkedList()
        prev_summary_node = None

        for stat_node_arr in temp_stat_nodes_lists_arr:
            count_investments = 0
            sum_return = 0
            # latest_until_date = invest_date
            if cash_date_node.nextval is not None:
                latest_until_date = cash_date_node.nextval.data.until_date
            else:
                latest_until_date = None
            for stat_node in stat_node_arr:
                node = stat_node.end_node.nextval
                # if lnode is not None:
                count_investments += 1
                sum_return += node.data.data
                if node.data.date != invest_date:
                    raise Exception("date:", node.data.date, "is not", invest_date)
                # if node.data.until_date > latest_until_date:
                #     latest_until_date = node.data.until_date
                #     print("woooowwww")
                # if latest_until_date == invest_date:
                #         raise Exception("lololo")

            if count_investments == 0:
                avg_return = 1
                # print("no investments were chosen for stats, using 1 instead")
            else:
                avg_return = sum_return / count_investments

            # if count_investments > 25:
            #     raise Exception("weee:" + str(count_investments))

            cash_ref = cash_date_node.nextval

            # if invest_date == latest_until_date:
            #     raise Exception("Impossible dates " + str(invest_date) + " and " + str(latest_until_date))

            summary_node = LNode()
            summary_node.data = InvestData()
            summary_node.data.data = avg_return
            summary_node.data.date = invest_date
            summary_node.data.count_investments = count_investments
            summary_node.data.until_date = latest_until_date
            summary_node.data.description = description
            summary_node.data.cash_ref = cash_ref
            summary_node.prevval = prev_summary_node
            if prev_summary_node is None:
                summary_linked_list.head = summary_node
            else:
                prev_summary_node.nextval = summary_node
            summary_node.parent = summary_linked_list

            prev_summary_node = summary_node
            cash_date_node = cash_date_node.nextval
            if cash_date_node is not None:
                invest_date = cash_date_node.data.until_date

        return summary_linked_list

    @classmethod
    def get_best_stocks_by_abs_momentum_stats(cls, stocks_list, momentum_lookback_periods, statistics_time_length,
                                              stocks_count):
        stats_list = []
        for stock in stocks_list:
            # print("stock start:", stock.head.date)
            cash = HistoryDownload.load_cash_data_by_date(stock.head.date)
            mom = Momentum.complete_momentum(stock.head, cash.head, momentum_lookback_periods)
            stats = Statistics.get_statistics_list_efficient(mom, statistics_time_length)
            if stats is not None:
                stats_list.append(stats.head)
            # else:
            # print("stats none")
        best_stocks_lists_arr = Statistics.get_best_scoring_stock_lists_array(stats_list, stocks_count)
        return best_stocks_lists_arr
