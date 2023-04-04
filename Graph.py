import datetime

import plotly.express as px
import plotly.graph_objects as go
from Momentum import Momentum
from stock_history import HistoryDownload
import pandas as pd
import numpy as np


class Graph:
    # @classmethod
    # def draw_graphs(cls, lnode_arr):
    #     dataframes = [lnode.to_dataframe((lambda y: y.data)) for lnode in lnode_arr]
    #     combined_df = pd.concat(dataframes)
    #
    #     fig = px.line(combined_df, x="Date", y="Return", color="Investment", title='Life expectancy in Canada',
    #                   log_y=True, range_x=[datetime.datetime.strptime("31/12/1984", "%d/%m/%Y"),
    #                                        datetime.datetime.strptime("01/01/2005", "%d/%m/%Y")])
    #     fig.show()

    @classmethod
    def draw_graphss(cls, lnode_arr):
        dataframes = [lnode.to_dataframe((lambda y: y.data)) for lnode in lnode_arr]
        combined_df = pd.concat(dataframes)

        # customdata = np.stack((combined_df['Investments Count']), axis=-1)
        customdata = combined_df['Investments Count']

        fig = px.line(combined_df, x="Date", y="Return", color="Investment", title='Life expectancy in Canada',
                      log_y=True) #  , range_x=[datetime.datetime.strptime("31/12/1984", "%d/%m/%Y"),
                                           #  datetime.datetime.strptime("01/01/2005", "%d/%m/%Y")])

        hovertemplate = ('Investments Count: %{customdata}<br>' +
                         'Date: %{x} <br>' +
                         'Return: %{y}' +
                         '<extra></extra>')

        fig.update_traces(customdata=customdata, hovertemplate=hovertemplate)
        fig.show()

    @classmethod
    def draww(cls, lnode_arr, stop_date=None):
        fig = go.Figure()

        for lnode in lnode_arr:
            df = lnode.to_dataframe((lambda y: y.data), stop_date=stop_date)

            fig.add_trace(
                go.Line(
                    x=df['Date'],
                    y=df['Return'],
                    #customdata=[df['Investments Count'], df['Investment']],
                    customdata=np.stack((df['Investment'], df['Investments Count']), axis=-1),
                    name=lnode.data.description,
                    hovertemplate='%{customdata[0]}<br>' +
                                  'Investments Count: %{customdata[1]}<br>' +
                                  'Date: %{x} <br>' +
                                  'Return: %{y}' +
                                  '<extra></extra>',
                )
            )

            fig.update_layout(
                xaxis={'title': 'Date', 'type': 'date', 'range': [datetime.datetime.strptime("31/12/1984", "%d/%m/%Y"),
                                                                  datetime.datetime.strptime("01/01/2005",
                                                                                             "%d/%m/%Y")]},
                yaxis={'title': 'Return', 'type': 'log'},
            )

            #fig.write_html('fig.html', auto_open=True)
        fig.show()

    @classmethod
    def grade(cls):
        pool = HistoryDownload.load_stock_data("AAPL")
        cash = HistoryDownload.load_cash_data_by_date(pool.head.date)

        mom1 = Momentum.momentum([pool.head, cash.head], cash.head, pool.head, 1).head.to_lnode()
        pool_lnode = pool.head.to_lnode()
        df1 = pool_lnode.to_dataframe(lambda y: y.data)
        df2 = mom1.to_dataframe(lambda y: y.data)
        dff = pd.concat([df1, df2])

        fig = px.line(dff, x="Date", y="Return", color="Investment", title='Life expectancy in Canada')
        fig.show()
