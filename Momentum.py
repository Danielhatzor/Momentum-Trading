import datetime
from math import *

import stock_history
from SLinkedList import *


class Momentum:
    @classmethod
    def get_descriptions_for_investments_lnode(cls, investments_list):
        description = "["
        investment_descriptions = []
        for investment in investments_list:
            if investment.data.description not in investment_descriptions:
                investment_descriptions.append(investment.data.description)
                description += investment.data.description + ", "
        description = description[:-2] + "]"

        return description

    # Processes momentum for a list of lnode assets (+ risk free asset?) with a single lookback period
    # Returns a single linked list
    @classmethod
    def momentum_lnode(cls, asset_yields_arr, risk_free_node, stock_node, momentum_lookback, description=None,
                       risk_adjusted=False):
        month_count = 0
        momentum_one_year_list = LinkedList()
        temp_asset_yields_arr = asset_yields_arr[:]

        # Setting month_start to the beginning of the latest asset's history
        month_start = datetime.datetime(1950, 1, 1)
        for i in range(len(temp_asset_yields_arr)):
            temp_month_date = temp_asset_yields_arr[i].data.date
            if temp_month_date > month_start:
                month_start = temp_month_date

        # Aligning all assets to start at month_start
        for i in range(len(temp_asset_yields_arr)):
            while temp_asset_yields_arr[i].data.date < month_start:
                temp_asset_yields_arr[i] = temp_asset_yields_arr[i].nextval
            if temp_asset_yields_arr[i].data.date != month_start:
                raise Exception('Momentum: bad dates')
        while risk_free_node.data.date < month_start:
            risk_free_node = risk_free_node.nextval
        risk_free_node_prevval = risk_free_node.prevval
        while stock_node.data.date < month_start:
            stock_node = stock_node.nextval
        if not stock_node.data.date == risk_free_node.data.date == month_start:
            raise Exception('Momentum: bad dates')

        while all(v is not None for v in temp_asset_yields_arr):
            # Just checking
            if temp_asset_yields_arr[0].nextval is not None and temp_asset_yields_arr[0].data.data is None:
                raise Exception("problem")

            winner_node = None
            winner_ratio = -999

            # Calculating avg yield for cash
            if month_count >= momentum_lookback:
                sum_yield_risk_free = 0
                temp_node = risk_free_node_prevval
                for j in range(momentum_lookback):
                    #print(str(temp_node.data))
                    sum_yield_risk_free += log(temp_node.data.data)
                    temp_node = temp_node.prevval
                    # sum_yield_risk_free *= temp_node.data
                avg_risk_free_yield = sum_yield_risk_free / momentum_lookback

            for i in range(len(temp_asset_yields_arr)):
                asset_node = temp_asset_yields_arr[i]

                if month_count >= momentum_lookback:

                    # Calculating avg yield
                    sum_yield = 0
                    temp_node = asset_node
                    for j in range(momentum_lookback):
                        temp_node = temp_node.prevval
                        sum_yield += log(temp_node.data.data)
                        # sum_yield *= temp_node.data

                    avg_yield = sum_yield / momentum_lookback

                    # Calculating avg standard deviation
                    sum_sd = 0
                    temp_node = asset_node
                    for j in range(momentum_lookback):
                        temp_node = temp_node.prevval
                        sum_sd += abs(temp_node.data.data - avg_yield)  # abs(log(temp_node.data) - avg_yield)
                    if momentum_lookback == 1:
                        avg_sd = 1
                    else:
                        avg_sd = sum_sd / momentum_lookback

                    # --------------------IMPORTANT-----------------------------------------
                    if avg_risk_free_yield != 0:
                        raise Exception("Risk free yield not zero")
                    if risk_adjusted:
                        if avg_sd == 0:
                            if avg_yield == 0:
                                ratio = 0
                            else:
                                raise Exception("zero sd for non-zero return")
                        else:
                            if avg_yield > avg_risk_free_yield:
                                ratio = (avg_yield - avg_risk_free_yield) / avg_sd
                            else:
                                ratio = (avg_yield - avg_risk_free_yield) * avg_sd
                    else:
                        ratio = avg_yield - avg_risk_free_yield

                    if ratio > winner_ratio:
                        winner_node = asset_node
                        winner_ratio = ratio

                temp_asset_yields_arr[i] = asset_node.nextval

            if month_count >= momentum_lookback:
                # Just a check
                if winner_node is None:
                    raise Exception("problem")

                if stock_node is None:
                    print("stock is:", "None")

                if description is None:
                    prev_description = cls.get_descriptions_for_investments_lnode(asset_yields_arr)
                    description = "mom" + str(momentum_lookback) + prev_description
                if momentum_one_year_list.head is None:
                    momentum_node = LNode()
                    momentum_one_year_list.head = momentum_node
                else:
                    momentum_node.nextval = LNode()
                    momentum_node.nextval.prevval = momentum_node
                    momentum_node = momentum_node.nextval
                momentum_node.parent = momentum_one_year_list

                data = InvestData()
                data.asset = winner_node.data.asset
                data.stock_ref = stock_node
                data.cash_ref = risk_free_node
                data.date = winner_node.data.date
                data.until_date = winner_node.data.until_date
                data.description = description
                data.ref = winner_node
                data.data = winner_node.data.data
                data.count_investments = winner_node.data.count_investments

                momentum_node.data = data

            risk_free_node_prevval = risk_free_node
            if risk_free_node is not None:
                risk_free_node = risk_free_node.nextval
            stock_node = stock_node.nextval
            month_count += 1

        #  return momentum_one_year_list
        return momentum_one_year_list.head

    # Function to process momentum for several lookback periods
    # Returns a list of linked-lists, each is momentum for different lookback period
    @classmethod
    def multi_momentum(cls, asset_yields_arr, risk_free_node, stock_node, momentum_lookback_list, description=None):
        if description is None:
            description = "mom["
            for momentum_lookback in momentum_lookback_list:
                description += str(momentum_lookback) + ", "
            description = description[:-2] + "]"
            description += cls.get_descriptions_for_investments(asset_yields_arr)
        momentum_result_list = []
        for momentum_lookback in momentum_lookback_list:
            # noinspection PyArgumentList
            momentum_result_list.append(cls.momentum_lnode(asset_yields_arr, risk_free_node, stock_node,
                                                     momentum_lookback, description=description))
        return momentum_result_list

    @classmethod
    def complete_momentum(cls, stock_node, risk_free_node, lookback_lists_list, description=None):
        if len(lookback_lists_list[-1]) > 1:
            print("bad lookback list input")
            return None
        temp_asset_yields_arr = [stock_node]
        temp_risk_free_node = risk_free_node
        temp_stock_node = stock_node

        for lookback_list in lookback_lists_list:
            temp_asset_yields_arr.insert(0, temp_risk_free_node)

            if len(lookback_list) > 1:
                temp_asset_yields_arr = cls.multi_momentum(temp_asset_yields_arr, temp_risk_free_node, temp_stock_node,
                                                           lookback_list, description=description)
            elif len(lookback_list) == 1:
                temp_asset_yields_arr = [cls.momentum_lnode(temp_asset_yields_arr, temp_risk_free_node, temp_stock_node,
                                                            lookback_list[0], description=description)]
            else:
                raise Exception

            if not all(v is not None for v in temp_asset_yields_arr):
                return None
            temp_risk_free_node = temp_asset_yields_arr[0].data.cash_ref
            temp_stock_node = temp_asset_yields_arr[0].data.stock_ref

        if len(temp_asset_yields_arr) > 1:
            print("list too big")
            return None
        return temp_asset_yields_arr[0]
