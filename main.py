import math
import time

import numpy
import requests

import Graph
import stock_history
from LinkedList import LinkedList, LNode
from SLinkedList import *
from Statistics import Statistics
from stock_history import HistoryDownload
from Constants import Constants
from Momentum import Momentum
import pandas as pd
from datetime import datetime
import bisect
from Graph import *
from Backtest import *
import logging

if __name__ == '__main__':
    requests.urllib3.disable_warnings()
    numpy.seterr(all='raise')

    HistoryDownload.download_stock_volume(True)
    #HistoryDownload.update_dates_to_stock_table()

    # # HistoryDownload.download_stocks_history(True)
    # rrr = HistoryDownload.load_stock_data_new("AAPL-USA", "week")
    # hhh = Momentum.complete_momentum(rrr.head, rrr.head.cash_ref, [[50]])
    #
    # print("holl")

    #  stock = HistoryDownload.load_stock_data_new("YELL-USA", "day", max_end_date=datetime.strptime("01/01/2005", "%d/%m/%Y"))
    # stock = HistoryDownload.load_stock_data_new("JPM-USA", "day",
    #                                             max_end_date=datetime.strptime("01/01/2005", "%d/%m/%Y"))
    # s1, s2, stock = HistoryDownload.load_stock_data_multiple_interval("JPM-USA", True, True, True,
    #                                                                   max_end_date=datetime.strptime("01/01/2005",
    #                                                                                                  "%d/%m/%Y"))
    BRK = HistoryDownload.load_stock_data_multiple_interval('BRK.A-USA', False, True, True)
    amzn = HistoryDownload.load_stock_data_multiple_interval('AMZN-USA', False, True, True)
    aapl = HistoryDownload.load_stock_data_multiple_interval('AAPL-USA', False, True, True)

    def condition_key(x, data_key, sector=None):
        return (sector is None or sector == x.parent.data.sector) and x.prevval is not None and \
               data_key(x.prevval).avg_volume > Constants.minimum_avg_stock_volume and \
               data_key(x).avg_price > Constants.minimum_avg_price_for_stock


    stocks = HistoryDownload.load_all_stocks_data(True)#, max_count=100,
                                                  #min_start_date=datetime.strptime("01/01/1995", "%d/%m/%Y"))
    stocks += [BRK[2]]


    # stocks_by_sectors = HistoryDownload.get_stocklists_subsets_list_by_sector(stocks)
    # sectors_portfolios = []
    #
    # for stocklists_arr in stocks_by_sectors:
    #     stocknodes_arr = [x.head for x in stocklists_arr]
    #     sector_portfolio = Backtest.summarize_investments_into_one(stocknodes_arr, lambda x: x.data,
    #                                                                stocklists_arr[0].data.metadata_df["Sector"].values[
    #                                                                    0],
    #                                                                start_together=False,
    #                                                                condition_key=condition_key)
    #     sectors_portfolios.append(sector_portfolio)

    for stock in stocks:
        if stock.head is None:
            print("")
    stock_nodes = [i.head for i in stocks]
    portfolio = Backtest.summarize_investments_into_one(stock_nodes, lambda x: x.data, "All Stocks",
                                                        start_together=False,
                                                        condition_key=condition_key)

    # arrr = []
    # for stock in stocks:
    #     stat = Statistics.get_statistics_list_relative_momentum(stock.head, 12, 36)
    #     if stat is not None:
    #         arrr.append(stat.head)
    # stat_mat = Statistics.get_best_scoring_stock_lists_array(arrr, 20, condition_key)
    # rel_mom = Backtest.summarize_stat_nodes_into_one_investment(stat_mat, "relative momentum")

    # rel_mom_12_36 = Backtest.get_relative_momentum(stocks, 20, [12], 36, "rel_12/36", condition_key)

    rel_mom_12_12 = Backtest.get_relative_momentum(stocks, 20, [12], 12, "rel_12/12", condition_key, True, True)
    # rel_mom_12_6_36 = Backtest.get_relative_momentum(stocks, 20, [12, 6], 36, "rel_12+6/36", condition_key)
    rel_mom_12_6_12 = Backtest.get_relative_momentum(stocks, 20, [12, 6], 12, "rel_12+6/12", condition_key, True, True)
    # rel_mom_6_3_1_18 = Backtest.get_relative_momentum(stocks, 20, [6, 3, 1], 18, "rel_6+3+1/18", condition_key)
    rel_mom_6_3_6 = Backtest.get_relative_momentum(stocks, 20, [6, 3], 6, "rel_6+3/6", condition_key, True, True)
    rel_mom_6_6 = Backtest.get_relative_momentum(stocks, 20, [6], 6, "rel_6/6", condition_key, True, True)
    rel_mom_3_3 = Backtest.get_relative_momentum(stocks, 20, [3], 3, "rel_3/3", condition_key, True, True)
    rel_mom_12_6_3_12 = Backtest.get_relative_momentum(stocks, 20, [12, 6, 3], 12, "rel_12+6+3/12", condition_key, True,
                                                       True)
    # rel_mom_1_3 = Backtest.get_relative_momentum(stocks, 20, [1], 3, "rel_1/3", condition_key)

    stock_node = rel_mom_12_12.head
    cash_ref = rel_mom_12_12.head.data.cash_ref
    mom_options = [rel_mom_12_12.head, rel_mom_12_6_12.head, rel_mom_6_3_6.head]

    jjj = Momentum.momentum_lnode(mom_options, cash_ref, stock_node, 12, risk_adjusted=True)

    tmpp = jjj
    while tmpp.nextval is not None:
        tmpp = tmpp.nextval

    #to_draw_list = [sector_portfolio.head for sector_portfolio in sectors_portfolios]
    to_draw_list = [portfolio.head, jjj, rel_mom_12_12.head, rel_mom_12_6_12.head, rel_mom_6_3_6.head,
                      rel_mom_6_6.head, rel_mom_3_3.head, rel_mom_12_6_3_12.head]

    Graph.draww(to_draw_list)#, stop_date=datetime.strptime("10/01/2005", "%d/%m/%Y"))  # , stocks[0].head.to_lnode()])
    # statssss = Statistics.get_statistics_list_relative_momentum(stock.head, 12, 36)

    #  stock.listprint()
    #
    # mom = Momentum.complete_momentum(stock.head, stock.head.cash_ref, Constants.loopback_periods_daily)
    # mom1 = Momentum.momentum([stock.head.cash_ref, stock.head], stock.head.cash_ref, stock.head, 1).to_lnode()
    # mom3 = Momentum.momentum([stock.head.cash_ref, stock.head], stock.head.cash_ref, stock.head, 3).to_lnode()
    # mom6 = Momentum.momentum([stock.head.cash_ref, stock.head], stock.head.cash_ref, stock.head, 5).to_lnode()
    # mom12 = Momentum.momentum([stock.head.cash_ref, stock.head], stock.head.cash_ref, stock.head, 25).to_lnode()
    #
    # stockk = stock.head.to_lnode()
    # mom = mom.to_lnode()
    # Graph.draw_graphs([stockk, mom, mom1, mom3, mom6, mom12])


def lolipop():
    stocks = HistoryDownload.load_all_stocks_data(True, 1000,
                                                  min_start_date=datetime.strptime("01/01/1999", "%d/%m/%Y"))
    stock_nodes = [i.head for i in stocks]
    portfolio = Backtest.summarize_investments_into_one(stock_nodes, lambda x: x, "All stocks", condition_key=
    lambda x: x.prevval is not None and
              x.prevval.min_volume > Constants.minimum_daily_stock_volume)

    momentum_stocks = [Momentum.complete_momentum(stock, stock.cash_ref, Constants.loopback_periods) for stock in
                       stock_nodes]
    momentum_stocks = [i for i in momentum_stocks if i is not None]
    momentum_portfolio = Backtest.summarize_investments_into_one(momentum_stocks, lambda x: x, "Momentum",
                                                                 condition_key=lambda x:
                                                                 x.asset is not HistoryDownload.cash_name and
                                                                 x.prevval is not None and
                                                                 x.prevval.stock_ref.min_volume > Constants.minimum_daily_stock_volume)
    best_stocks = Backtest.get_best_stocks_by_abs_momentum_stats(stocks, Constants.loopback_periods,
                                                                 Constants.stats_period, 20)
    stats_porfolio = Backtest.summarize_stat_nodes_into_one_investment(best_stocks, "Good stats")
    print("hi")
    Graph.draw_graphs([portfolio.head, momentum_portfolio.head, stats_porfolio.head])
    # HistoryDownload.download_stocks_history()
    # Momentum.test()


def do_something():
    cash = HistoryDownload.load_cash_data()
    kj = HistoryDownload.load_stock_data("IBM")

    mom1 = Momentum.momentum([kj.head, cash.head], cash.head, kj.head, 1)
    mom6 = Momentum.momentum([kj.head, cash.head], cash.head, kj.head, 6)
    mom112 = Momentum.momentum([kj.head, cash.head], cash.head, kj.head, 1)
    mom112 = Momentum.momentum([mom112.head, mom112.head.cash_ref], mom112.head.cash_ref, mom112.head.stock_ref, 12)
    mom612 = Momentum.momentum([kj.head, cash.head], cash.head, kj.head, 6)
    mom612 = Momentum.momentum([mom612.head, mom612.head.cash_ref], mom612.head.cash_ref, mom612.head.stock_ref, 12)

    BRK_A = HistoryDownload.load_stock_data("BRK_A")

    BRK_A6 = Momentum.momentum([BRK_A.head, cash.head], cash.head, BRK_A.head, 6)
    BRK_A612 = Momentum.momentum([BRK_A.head, cash.head], cash.head, BRK_A.head, 6)
    BRK_A612 = Momentum.momentum([BRK_A612.head, BRK_A612.head.cash_ref], BRK_A612.head.cash_ref,
                                 BRK_A612.head.stock_ref, 12)

    KMB = HistoryDownload.load_stock_data("KMB")

    KMB6 = Momentum.momentum([KMB.head, cash.head], cash.head, KMB.head, 6)
    KMB612 = Momentum.momentum([KMB.head, cash.head], cash.head, KMB.head, 6)
    KMB612 = Momentum.momentum([KMB612.head, KMB612.head.cash_ref], KMB612.head.cash_ref, KMB612.head.stock_ref, 12)

    COKE = HistoryDownload.load_stock_data("COKE")

    COKE6 = Momentum.momentum([COKE.head, cash.head], cash.head, COKE.head, 6)
    COKE612 = Momentum.momentum([COKE.head, cash.head], cash.head, COKE.head, 6)
    COKE612 = Momentum.momentum([COKE612.head, COKE612.head.cash_ref], COKE612.head.cash_ref, COKE612.head.stock_ref,
                                12)

    for asset in [mom1, mom6, mom112, kj]:
        while asset.head.date != mom612.head.date:
            asset.head = asset.head.nextval

    HistoryDownload.save_linked_list_to_csv(kj)
    HistoryDownload.save_linked_list_to_csv(mom1, "mom1")
    HistoryDownload.save_linked_list_to_csv(mom6, "mom6")
    HistoryDownload.save_linked_list_to_csv(mom112, "mom112")
    HistoryDownload.save_linked_list_to_csv(mom612, "mom612")
    mom612.listprint()

    begin = mom1.head
    tmp_node = mom1.head
    count = 0
    while count < 10:
        if tmp_node is None:
            # return None
            raise Exception()
        count += 1
        tmp_node = tmp_node.nextval

    end = tmp_node

    # ssss = get_statistics(begin, end, begin.stock_ref)
    ffff = Statistics.get_statistics_list(begin, begin.stock_ref, 101)

    s1 = Statistics.get_statistics_list(mom6.head, mom6.head.stock_ref, 10)  # 101)
    s1_efficient = Statistics.get_statistics_list_efficient(mom6.head, 10)  # 101)

    tmpp = s1.head
    tmpp2 = s1_efficient.head
    while tmpp is not None:
        print(tmpp.data.score, tmpp2.data.score, tmpp.data.start_node.date, "-->", tmpp.data.end_node.date)
        if abs(tmpp.data.score - tmpp2.data.score) > 0.00000000000001:
            print("problem")
        tmpp = tmpp.nextval
        tmpp2 = tmpp2.nextval
    # s6 = Statistics.get_statistics_list(mom6.head, mom6.head.stock_ref, 101)
    # s112 = Statistics.get_statistics_list(mom112.head, mom112.head.stock_ref, 101)
    # s612 = Statistics.get_statistics_list(mom612.head, mom612.head.stock_ref, 101)

    print(s1.head.data)

    s1 = Statistics.get_statistics_list_efficient(mom612.head, 10)
    s2 = Statistics.get_statistics_list_efficient(BRK_A612.head, 10)
    s3 = Statistics.get_statistics_list_efficient(KMB612.head, 10)
    s4 = Statistics.get_statistics_list_efficient(COKE612.head, 10)

    matrix = Statistics.get_best_scoring_stock_lists_array([s1.head, s2.head, s3.head, s4.head], 2)

    print("ki")

    # print(ssss.score)
