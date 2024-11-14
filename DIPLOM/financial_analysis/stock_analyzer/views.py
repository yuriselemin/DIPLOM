import urllib

from django.shortcuts import render
from .models import Stock
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from urllib.parse import quote

def home(request):
    context = {}
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        period = request.POST.get('period')

        data = yf.download(tickers=ticker, period=period, progress=False)
        data.reset_index(inplace=True)
        data.rename(columns={'index': 'date'}, inplace=True)
        data['date'] = pd.to_datetime(data['date']).dt.date

        for _, row in data.iterrows():
            Stock.objects.create(
                ticker=ticker,
                date=row['date'],
                open_price=row['Open'],
                high_price=row['High'],
                low_price=row['Low'],
                close_price=row['Close'],
                volume=row['Volume']
            )

        stocks = Stock.objects.filter(ticker=ticker)
        plot = create_plot(stocks)
        context['plot'] = plot

    return render(request, 'stock_analyzer/home.html', context)


def create_plot(stocks):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = [s.date for s in stocks]
    y = [s.close_price for s in stocks]
    ax.plot(x, y)
    ax.set_xlabel('Дата')
    ax.set_ylabel('Цена закрытия')
    ax.set_title(f'График цены закрытия {stocks.first().ticker}')

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)

    return uri