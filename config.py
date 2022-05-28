#----- API KEY -----
bb_test_api_key = ''
bb_test_api_secret = ''

#----- Stop loss percent -----
stop_loss_buy = 1
stop_loss_sell = 1

#----- Leverage -----
leverage = 10

#----- Telegram bot token -----
bot_token = ''

#----- Order parameter -----
order_type = 'Market'
time_in_force = 'GoodTillCancel'

#----- Trading view -----
URL = "https://scanner.tradingview.com/crypto/scan"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'}

#------ Coin selection conditions -----

#long position
payload_buy = {"filter":[{"left":"Recommend.All|5","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"change|1","operation":"greater","right":0},{"left":"Recommend.All|5","operation":"nequal","right":0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.All|5","operation":"in_range","right":[0.1,0.5]}},{"expression":{"left":"Recommend.All|5","operation":"in_range","right":[0.5,1]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.All|5","change|1","description","type","subtype","update_mode|5"],"sort":{"sortBy":"Recommend.All|5","sortOrder":"desc"},"range":[0,150]}

#short position
payload_sell = {"filter":[{"left":"Recommend.All|5","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"change|1","operation":"less","right":0},{"left":"Recommend.All|5","operation":"nequal","right":-0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.All|5","operation":"in_range","right":[-0.5,-0.1]}},{"expression":{"left":"Recommend.All|5","operation":"in_range","right":[-1,-0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.All|5","change|1","description","type","subtype","update_mode|5"],"sort":{"sortBy":"Recommend.All|5","sortOrder":"asc"},"range":[0,150]}


#------ Coin select condition from 3 lists -----

#buy
payload_buy_01 = {"filter":[{"left":"Recommend.MA|1","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"Recommend.MA|1","operation":"nequal","right":0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"active_symbols_only":"true","lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.MA|1","operation":"in_range","right":[0.5,1]}},{"expression":{"left":"Recommend.MA|1","operation":"in_range","right":[0.1,0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.MA|1","close|1","SMA20|1","SMA50|1","SMA200|1","BB.upper|1","BB.lower|1","description","type","subtype","update_mode|1","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"Recommend.MA|1","sortOrder":"desc"},"range":[0,150]}
payload_buy_05 = {"filter":[{"left":"Recommend.MA|5","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"Recommend.MA|5","operation":"nequal","right":0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"active_symbols_only":"true","lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.MA|5","operation":"in_range","right":[0.5,1]}},{"expression":{"left":"Recommend.MA|5","operation":"in_range","right":[0.1,0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.MA|5","close|5","SMA20|5","SMA50|5","SMA200|5","BB.upper|5","BB.lower|5","description","type","subtype","update_mode|5","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"Recommend.MA|5","sortOrder":"desc"},"range":[0,150]}
payload_buy_15 = {"filter":[{"left":"Recommend.MA|15","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"Recommend.MA|15","operation":"nequal","right":0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"active_symbols_only":"true","lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.MA|15","operation":"in_range","right":[0.5,1]}},{"expression":{"left":"Recommend.MA|15","operation":"in_range","right":[0.1,0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.MA|15","close|15","SMA20|15","SMA50|15","SMA200|15","BB.upper|15","BB.lower|15","description","type","subtype","update_mode|15","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"Recommend.MA|15","sortOrder":"desc"},"range":[0,150]}

#short
payload_sell_01 = {"filter":[{"left":"Recommend.MA|1","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"Recommend.MA|1","operation":"nequal","right":-0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"active_symbols_only":"true","lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.MA|1","operation":"in_range","right":[-0.5,-0.1]}},{"expression":{"left":"Recommend.MA|1","operation":"in_range","right":[-1,-0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.MA|1","close|1","SMA20|1","SMA50|1","SMA200|1","BB.upper|1","BB.lower|1","description","type","subtype","update_mode|1","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"Recommend.MA|1","sortOrder":"asc"},"range":[0,150]}
payload_sell_05 = {"filter":[{"left":"Recommend.MA|5","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"Recommend.MA|5","operation":"nequal","right":-0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"active_symbols_only":"true","lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.MA|5","operation":"in_range","right":[-0.5,-0.1]}},{"expression":{"left":"Recommend.MA|5","operation":"in_range","right":[-1,-0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.MA|5","close|5","SMA20|5","SMA50|5","SMA200|5","BB.upper|5","BB.lower|5","description","type","subtype","update_mode|5","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"Recommend.MA|5","sortOrder":"asc"},"range":[0,150]}
payload_sell_15 = {"filter":[{"left":"Recommend.MA|15","operation":"nempty"},{"left":"exchange","operation":"equal","right":"BYBIT"},{"left":"Recommend.MA|15","operation":"nequal","right":-0.1},{"left":"name,description","operation":"match","right":"USDT"}],"options":{"active_symbols_only":"true","lang":"en"},"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"expression":{"left":"Recommend.MA|15","operation":"in_range","right":[-0.5,-0.1]}},{"expression":{"left":"Recommend.MA|15","operation":"in_range","right":[-1,-0.5]}}]}}]},"markets":["crypto"],"symbols":{"query":{"types":[]},"tickers":[]},"columns":["base_currency_logoid","currency_logoid","name","Recommend.MA|15","close|15","SMA20|15","SMA50|15","SMA200|15","BB.upper|15","BB.lower|15","description","type","subtype","update_mode|15","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"Recommend.MA|15","sortOrder":"asc"},"range":[0,150]}
