import vectorbt as vbt
import numpy as np
import datetime as dt


def get_data(tickers, startDate, endDate):
    dados = vbt.YFData.download(tickers, start = startDate, end = endDate,
                                missing_index='drop',interval='1h').get('Close')
    close = dados[:]
    return close


def custom_indicator(close, rsi_window = 14, slow_ma=200, fast_ma=50, entry=30, exit=70):
    rsi = vbt.RSI.run(close, window = rsi_window).rsi
    media_rap = vbt.MA.run(close, window = slow_ma).ma.to_numpy()
    media_lenta = vbt.MA.run(close, window = fast_ma).ma.to_numpy()

    trend = np.where( (rsi > exit) & (media_lenta < media_rap), -1, 0)  ## This array creates entries and exits
    trend = np.where( (rsi < entry) & (media_rap > media_lenta), 1, trend) 
    
    # rsi.plot(title='RSI IBOV')  ## Plot the asset RSI, in this case "IBOV"
    return trend


### INDICATOR FACTORY ### Excelent for parameter optimization
ind = vbt.IndicatorFactory(    
        class_name = "Combination",
        short_name = "comb",
        input_names = ["close"],
        param_names = ["rsi_window", "slow_ma", "fast_ma", "entry", "exit"],
        output_names = ["value"]    
        ).from_apply_func(
                custom_indicator,  
                rsi_window = 14,
                slow_ma = 200,
                fast_ma = 50,
                entry = 30,
                exit = 70
                )


def create_signals(result):
    entries = result.value == 1.0
    exits = result.value == -1.0
    return entries, exits


def build_portfolio(close, entries, exits):
    pf = vbt.Portfolio.from_signals(close, entries=entries, exits=exits,
                                    direction='all', sl_stop=0.05)
    print(pf.stats(silence_warnings=True))
    return pf


def main():
    endDate = dt.datetime.now()
    startDate = endDate - dt.timedelta(days=730)
    tickers = ['^BVSP']
    rsi_windows = 14
    slow_ma = 200
    fast_ma = 50
    entry = 30
    exit = 65


    close = get_data(tickers, startDate, endDate)
    trend = custom_indicator(close, rsi_window=rsi_windows, slow_ma=slow_ma, fast_ma=fast_ma, entry=entry, exit=exit)    
    result = ind.run(close, rsi_window=rsi_windows, slow_ma=slow_ma, fast_ma=fast_ma, entry=entry, exit=exit)
    entries, exits = create_signals(result)


    pf = build_portfolio(close, entries, exits)
    fig = pf.plot()
    fig.show()
  

if __name__ == '__main__':
    main()





