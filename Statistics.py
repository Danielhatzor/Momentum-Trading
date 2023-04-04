import bisect
from datetime import datetime
import math

import stock_history
from Constants import Constants
from LinkedList import LNode, LinkedList


class Statistics:
    def __init__(self):

        # self.asset = asset
        # self.date = date
        # self.ref = None

        self.count = None
        self.avg_return_log = None
        self.return_sum_log = None
        self.return_squared_sum_log = None
        self.standard_deviation = None
        self.avg_abs_deviation = None
        self.variance = None
        # self.sum_negative_sd = None
        # self.sum_positive_sd = None
        self.times_invested = None
        self.sum_of_losses_log = None
        self.sum_of_potential_loss_log = None
        self.score = None
        self.start_node = None
        self.end_node = None

    @classmethod
    def get_statistics(cls, start_node, end_node, stock_start_node):
        tmp_node = start_node
        stock_node = stock_start_node
        count_nodes = 0
        return_sum_log = 0
        return_squared_sum_log = 0
        times_invested = 0
        sum_of_losses_log = 0
        sum_of_potential_loss_log = 0

        while tmp_node is not end_node.nextval:
            count_nodes += 1

            # TODO: !!!!!!!!!!!! SHOULD BE < CASH !!!!!!!!!!!!!!!!!
            if stock_node.data < 1:
                sum_of_potential_loss_log += math.log(stock_node.data)

            if tmp_node.asset is not stock_history.HistoryDownload.cash_name:
                times_invested += 1
                return_sum_log += math.log(tmp_node.data)
                return_squared_sum_log += math.log(tmp_node.data) ** 2

                # TODO: !!!!!!!!!!!! SHOULD BE < CASH !!!!!!!!!!!!!!!!!
                if tmp_node.data < 1:
                    sum_of_losses_log += math.log(tmp_node.data)

            tmp_node = tmp_node.nextval
            stock_node = stock_node.nextval

        # Creating returned object
        sdata = Statistics()
        sdata.times_invested = times_invested
        sdata.sum_of_losses_log = sum_of_losses_log
        sdata.sum_of_potential_loss_log = sum_of_potential_loss_log
        sdata.return_sum_log = return_sum_log
        sdata.return_squared_sum_log = return_squared_sum_log
        sdata.start_node = start_node
        sdata.end_node = end_node
        sdata.count = count_nodes

        # Quitting if data is inefficient
        if times_invested <= 1 or sum_of_potential_loss_log == 0:
            sdata.score = 0
            return sdata

        # Calculating avg standard deviation
        tmp_node = start_node
        sum_sd_log = 0
        sum_squared_deviations = 0
        avg_yield_log = return_sum_log / times_invested

        while tmp_node is not end_node.nextval:
            if tmp_node.asset is not stock_history.HistoryDownload.cash_name:
                sum_sd_log += abs(math.log(tmp_node.data) - avg_yield_log)
                sum_squared_deviations += (math.log(tmp_node.data) - avg_yield_log) ** 2
            tmp_node = tmp_node.nextval

        variance = sum_squared_deviations / times_invested
        standard_deviation = math.sqrt(variance)
        # avg_abs_deviation = sum_sd_log / times_invested

        # sdata.avg_abs_deviation = avg_abs_deviation
        sdata.avg_return_log = avg_yield_log
        sdata.standard_deviation = standard_deviation
        sdata.variance = variance
        sdata.calc_score()

        return sdata

    @classmethod
    def calc_return(cls, start_node, end_node):
        return_sum_log = 0
        nodes_count = 0
        tmp_node = start_node
        while tmp_node is not end_node.nextval:
            return_sum_log += math.log(tmp_node.data.data)
            nodes_count += 1
            tmp_node = tmp_node.nextval

        return return_sum_log, nodes_count

    @classmethod
    def calc_variance(cls, start_node, end_node, avg_return_log):
        tmp_node = start_node
        sum_squared_deviations = 0
        nodes_count = 0
        while tmp_node is not end_node.nextval:
            nodes_count += 1
            sum_squared_deviations += (math.log(tmp_node.data.data) - avg_return_log) ** 2
            tmp_node = tmp_node.nextval

        variance = sum_squared_deviations / nodes_count
        return variance

    @classmethod
    def get_statistics_relative_momentum(cls, start_nodes, end_node, std_start_node, skip_return_last_node,
                                         skip_std_last_node):
        if skip_std_last_node:
            std_end_node = end_node.prevval
        else:
            std_end_node = end_node
        if skip_return_last_node:
            return_end_node = end_node.prevval
        else:
            return_end_node = end_node

        # Calculating return for std_start_node to end_node, using custom interval ref (week?)
        std_return_sum_log, std_nodes_count = cls.calc_return(std_start_node.data.week_ref, std_end_node.data.week_ref)
        avg_std_return_log = std_return_sum_log / std_nodes_count

        # Calculating avg standard deviation
        variance = cls.calc_variance(std_start_node.data.week_ref, std_end_node.data.week_ref, avg_std_return_log)
        standard_deviation = math.sqrt(variance)

        all_return_sum_log = 0
        for start_node in start_nodes:
            # Calculating total return
            return_sum_log, count_nodes = cls.calc_return(start_node, return_end_node)
            all_return_sum_log += return_sum_log
            # avg_yield_log = return_sum_log / count_nodes

        # Creating returned object
        sdata = Statistics()
        sdata.return_sum_log = all_return_sum_log
        sdata.start_node = start_nodes[0]
        sdata.end_node = end_node
        sdata.skip_return_last_node = skip_return_last_node
        sdata.skip_std_last_node = skip_std_last_node
        # sdata.count = count_nodes
        # sdata.avg_return_log = avg_yield_log
        sdata.standard_deviation = standard_deviation
        sdata.variance = variance
        sdata.std_return_sum_log = std_return_sum_log
        sdata.std_nodes_count = std_nodes_count
        sdata.avg_std_return_log = avg_std_return_log
        sdata.calc_score_relative_momentum()

        return sdata

    @classmethod
    def get_next_statistics(cls, statistics):
        # Loading previous info
        times_invested = statistics.times_invested
        return_sum_log = statistics.return_sum_log
        return_squared_sum_log = statistics.return_squared_sum_log
        sum_of_losses_log = statistics.sum_of_losses_log
        sum_of_potential_loss_log = statistics.sum_of_potential_loss_log

        removed_node = statistics.start_node
        added_node = statistics.end_node.nextval
        if added_node is None:
            return None

        # Updating sum of potential loss
        if added_node.stock_ref.data < 1:
            sum_of_potential_loss_log += math.log(added_node.stock_ref.data)
        if removed_node.stock_ref.data < 1:
            sum_of_potential_loss_log -= math.log(removed_node.stock_ref.data)

        # Updating times invested, return sum and sum of losses
        removed = False
        added = False
        if added_node.asset is not stock_history.HistoryDownload.cash_name:
            added = True
            times_invested += 1
            return_sum_log += math.log(added_node.data)
            return_squared_sum_log += math.log(added_node.data) ** 2
            if added_node.data < 1:
                sum_of_losses_log += math.log(added_node.data)
        if removed_node.asset is not stock_history.HistoryDownload.cash_name:
            removed = True
            times_invested -= 1
            return_sum_log -= math.log(removed_node.data)
            return_squared_sum_log -= math.log(removed_node.data) ** 2
            if removed_node.data < 1:
                sum_of_losses_log -= math.log(removed_node.data)

        # Creating returned object
        sdata = Statistics()
        sdata.times_invested = times_invested
        sdata.sum_of_losses_log = sum_of_losses_log
        sdata.sum_of_potential_loss_log = sum_of_potential_loss_log
        sdata.return_sum_log = return_sum_log
        sdata.return_squared_sum_log = return_squared_sum_log
        sdata.start_node = statistics.start_node.nextval
        sdata.end_node = statistics.end_node.nextval
        sdata.count = statistics.count

        # Quitting if data is inefficient
        if times_invested <= 1 or sum_of_potential_loss_log == 0:
            sdata.score = 0
            return sdata

        # Updating new average, variance and std
        avg_return_log = return_sum_log / times_invested
        variance = return_squared_sum_log / times_invested - (return_sum_log ** 2) / (times_invested ** 2)
        # Fixing miscalculations
        if -0.000000001 < variance < 0:
            variance = 0
        standard_deviation = math.sqrt(variance)

        # Returning new data
        sdata.avg_return_log = avg_return_log
        sdata.standard_deviation = standard_deviation
        sdata.variance = variance
        # sdata.sum_negative_sd = sum_negative_sd
        # sdata.sum_positive_sd = sum_positive_sd

        # Quitting if data is inefficient
        if standard_deviation == 0:
            sdata.score = 0
            return sdata

        sdata.calc_score()

        return sdata

    @classmethod
    def get_statistics_list_relative_momentum(cls, head_node, total_return_time_lengths, std_time_length,
                                              skip_return_last_node, skip_std_last_node):
        max_return_time_length = max(return_time_len for return_time_len in total_return_time_lengths)
        max_time_length = max(max_return_time_length, std_time_length)
        end_node = head_node
        for i in range(max_time_length - 1):
            end_node = end_node.nextval
            if end_node is None:
                return None

        return_start_nodes = []
        for return_time_len in total_return_time_lengths:
            tmp_node = end_node
            for i in range(return_time_len - 1):
                tmp_node = tmp_node.prevval
            return_start_nodes.append(tmp_node)
        tmp_node = end_node
        for i in range(std_time_length - 1):
            tmp_node = tmp_node.prevval
        std_start_node = tmp_node

        stat_list = LinkedList()
        stat_node = None

        while end_node is not None:
            if stat_node is not None:
                stat_node.nextval = LNode()
                stat_node.nextval.prevval = stat_node
                stat_node = stat_node.nextval
            else:
                stat_node = LNode()
                stat_list.head = stat_node
            stat_node.parent = stat_list
            stat_node.data = cls.get_statistics_relative_momentum(return_start_nodes, end_node, std_start_node,
                                                                  skip_return_last_node, skip_std_last_node)
            for i in range(len(return_start_nodes)):
                return_start_nodes[i] = return_start_nodes[i].nextval
            std_start_node = std_start_node.nextval
            end_node = end_node.nextval
        return stat_list

    @classmethod
    def get_statistics_list(cls, head_node, stock_node, statistics_time_length):
        end_node = head_node
        for i in range(statistics_time_length - 1):
            end_node = end_node.nextval
            if end_node is None:
                return None

        stat_list = LinkedList()
        stat_node = None

        while end_node is not None:
            if stat_node is not None:
                stat_node.nextval = LNode()
                stat_node.nextval.prevval = stat_node
                stat_node = stat_node.nextval
            else:
                stat_node = LNode()
                stat_list.head = stat_node
            stat_node.parent = stat_list
            stat_node.data = cls.get_statistics(head_node, end_node, stock_node)
            head_node = head_node.nextval
            stock_node = stock_node.nextval
            end_node = end_node.nextval
        return stat_list

    @classmethod
    def get_statistics_list_efficient(cls, head_node, statistics_time_length):
        if head_node is None:
            return None
        end_node = head_node
        for i in range(statistics_time_length - 1):
            end_node = end_node.nextval
            if end_node is None:
                return None

        list_node = LNode()
        list_node.data = cls.get_statistics(head_node, end_node, head_node.stock_ref)
        stat_list = LinkedList()
        stat_list.head = list_node
        list_node.parent = stat_list

        while end_node.nextval is not None:
            head_node = head_node.nextval
            end_node = end_node.nextval

            list_node.nextval = LNode()
            list_node.nextval.prevval = list_node
            list_node = list_node.nextval
            list_node.parent = stat_list
            list_node.data = cls.get_next_statistics(list_node.prevval.data)
        return stat_list

    def calc_score(self):
        self.score = (self.avg_return_log / self.standard_deviation) * \
                     ((self.sum_of_potential_loss_log - self.sum_of_losses_log) / self.sum_of_potential_loss_log)
        return self.score

    def calc_score_relative_momentum(self):
        if self.standard_deviation == 0:  # Happens when stock has 0 volume for long time
            self.score = -999
            # raise Exception("std deviation was zero for:", self.end_node.asset, str(self.end_node.date))
        else:
            self.score = self.return_sum_log / self.standard_deviation
        return self.score

    @classmethod
    def get_best_scoring_stock_lists_array(cls, statistics_lists_array, stocks_count, condition_key):
        statistics_lists_array = statistics_lists_array[:]
        date_node = None
        date_before_invest = datetime.today()
        for stat_node in statistics_lists_array:
            if stat_node.data.end_node.data.date < date_before_invest:
                date_node = stat_node.data.end_node.data.cash_ref
                date_before_invest = date_node.data.date

        best_stocks_stats_matrix = []
        j = 0
        while len(statistics_lists_array) > 0 and date_node is not None:
            date_before_invest = date_node.data.date
            best_stats_sorted_arr = []
            min_score = 0
            #  min_score_node = None
            i = 0
            relevant_stocks_count = 0
            while i < len(statistics_lists_array):
                stat_node = statistics_lists_array[i]

                if stat_node.data.end_node.data.date == date_before_invest:
                    relevant_stocks_count += 1
                    if stat_node.data.score > 0 and \
                            (stat_node.data.score > min_score or len(best_stats_sorted_arr) < stocks_count) and \
                            stat_node.data.end_node.nextval is not None and \
                            stat_node.data.end_node.nextval.data.asset is not stock_history.HistoryDownload.cash_name and \
                            stat_node.data.end_node.data.stock_ref.data.min_volume > Constants.minimum_daily_stock_volume and \
                            condition_key(stat_node.data.end_node.data.stock_ref, lambda x: x.data):
                        # noinspection PyArgumentList
                        bisect.insort(best_stats_sorted_arr, stat_node.data, key=lambda t: t.score)

                        if len(best_stats_sorted_arr) > stocks_count:
                            best_stats_sorted_arr.pop(0)
                            #  min_score_node = best_stats_sorted_arr[0]
                            min_score = best_stats_sorted_arr[0].score

                    if stat_node.nextval is None:
                        statistics_lists_array.pop(i)
                        continue  # We don't want i to increase
                    else:
                        statistics_lists_array[i] = stat_node.nextval
                i += 1

            best_stocks_stats_matrix.append(best_stats_sorted_arr)

            date_node = date_node.nextval
            print(date_before_invest, ": relevant stocks for stats:", relevant_stocks_count)
            j += 1

        return best_stocks_stats_matrix
