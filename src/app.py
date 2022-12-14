import datetime
import pytz
import sqlite3

import dash
from dash import dcc, html, Input, Output, callback, no_update, ctx
import dash_daq as daq
import numpy as np
import pandas as pd

DBFILENAME = "file:/ctdata/heatpumpctdata.sqlite?mode=ro"
COSTPERKWH = 0.18 + 0.01  # Extra is "Energy efficiency charge"

app = dash.Dash(__name__)
conn = sqlite3.connect(DBFILENAME, uri=True, check_same_thread=False)

app.layout = html.Div(
    children=[
        html.H1(
            children="Heat Pump Analytics",
        ),
        daq.NumericInput(
            id="days-to-show",
            label="Number of Days",
            labelPosition="bottom",
            value=1,
            min=1,
            max=100,
        ),
        html.P(
            id="total-kwh",
        ),
        html.P(
            id="last_updated",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="ct3-chart",
                        config={"displayModeBar": True},
                    ),
                    className="card",
                ),
                dcc.Interval(
                    id="countdown_component",
                    interval=60000,  # in milliseconds
                    n_intervals=0,
                ),
            ],
            className="wrapper",
        ),
    ]
)


@callback(
    Output("ct3-chart", "figure"),
    Output("total-kwh", "children"),
    Output("last_updated", "children"),
    Input("countdown_component", "n_intervals"),
    Input("days-to-show", "value"),
)
def update_charts(n, daystoshow):
    """Updates chart data on events.

    Args:
        n: n_intervals from the `dcc.Interval` instance. Only used
          for firing a callback.
        daystoshow: Number of days to show on the chart, counting
          back from now.

    Returns:
        See `Output()`s in callback decorator.
    """
    # Filter data when showing many days' worth to speed up
    # plotting. Also applies to calculations (which don't seem
    # to suffer much in accuracy).
    # Equation from the two (day, nth) points (1, 1) and (5, 3).
    X, Y = [1, 5], [2, 5]
    linecoeffs = np.polyfit(X, Y, 1)
    nth = min(8, int(round(np.dot([daystoshow, 1], linecoeffs))))

    startdate = datetime.datetime.now() - datetime.timedelta(daystoshow)
    qry = f'SELECT * from housectdata where DateTime >= "{startdate.isoformat()}"'
    data = pd.read_sql_query(qry, conn)

    data = data.iloc[::nth, :]  # Don't need to see everything
    data["DateTime"] = pd.to_datetime(data["DateTime"], utc=True)
    data["DateTime"] = data["DateTime"].dt.tz_convert("US/Eastern")

    noisemask = data["ct3"] < 150  # Noise when nothing is happening
    data.loc[noisemask, "ct3"] = 0.0

    incrseconds = (
        (data["DateTime"] - data["DateTime"].shift())
        .fillna(pd.Timedelta(0))
        .dt.total_seconds()
    )
    totkwh = (incrseconds * data["ct3"] / 1000 / 3600).sum()
    totcost = totkwh * COSTPERKWH

    datastr = f"Total kWh: {totkwh:.2f}  Total Cost: ${totcost:.2f}"

    ct3_chart_figure = {
        "data": [
            {
                "x": data["DateTime"],
                "y": data["ct3"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {
                "text": "CT3 readings",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": False},
            "yaxis": {"fixedrange": False},
            "colorway": ["#17B897"],
        },
    }

    if ctx.triggered_id == "days-to-show":
        lastupdate = no_update
    else:
        ltz = pytz.timezone("America/New_York")
        utcnow = datetime.datetime.utcnow()
        lastupdate = utcnow.astimezone(ltz).isoformat(" ", "seconds")[:-6]
        lastupdate = f"Last updated: {lastupdate}"

    return ct3_chart_figure, datastr, lastupdate


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")
