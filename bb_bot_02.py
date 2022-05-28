import inspect
from pybit import HTTP
import config
import threading
import time
import datetime
import requests
import random
import sqlalchemy
import pandas as pd
import telebot

session = HTTP("https://api-testnet.bybit.com", api_key=config.bb_test_api_key, api_secret=config.bb_test_api_secret,
               recv_window=10000)
coins = []
positions = {}
exclude = ['BTCDOMUSDT']
engine = sqlalchemy.create_engine('sqlite:///data.db')
sql_table_DEPO = 'DEPO'
open_positions = {}
quarantine = {}
stop_loss_list = []
order_list = pd.DataFrame({'Open time': {'THR 01 ': 'none', 'THR 02 ': 'none', 'THR 03 ': 'none', 'THR 04 ': 'none'},
                           'Side': {'THR 01 ': 'none', 'THR 02 ': 'none', 'THR 03 ': 'none', 'THR 04 ': 'none'},
                           'Coin': {'THR 01 ': 'none', 'THR 02 ': 'none', 'THR 03 ': 'none', 'THR 04 ': 'none'}})
zero_point = datetime.datetime.now().replace(microsecond=0)
thr_list = order_list.index.tolist()


def live_time():
    duration = datetime.datetime.now().replace(microsecond=0) - zero_point
    return duration


def sleep(n):
    time.sleep(random.randint(4 // n, 12 // n))


def msg_new_position(thr_name, side, coin, entry_price, trailing_stop, quantity):
    try:
        pos = [coin, entry_price, trailing_stop, quantity, str(round(((quantity * entry_price) / 10), 2)) + '$',
               datetime.datetime.now()]  # position list
        msg = ('\n!!! ' + thr_name + side + ' position !!!' +
               '\nCoin: ' + str(pos[0]) +
               '\nEntry price: ' + (str(pos[1])) +
               '\nTrailing stop: ' + str(pos[2]) +
               '\nQuantity: ' + str(pos[3]) +
               '\nInvest: ' + str(pos[4]) +
               '\nOpen time: ' + str(pos[5].replace(microsecond=0)) + '\n'
               )
        telegram_bot(thr_name, msg)
        print(msg)
        order_list.loc[thr_name] = [str(pos[5].strftime("%H:%M:%S")), str(side), str(pos[0])]
        return pos
    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        sleep(1)


def msg_breakeven(thr_name, coin, entry_price, breakeven, last_price):
    try:
        msg = ('<<< ' + thr_name + ' breakeven >>>' +
               '\nCoin: ' + str(coin) +
               '\nEntry price: ' + str(entry_price) +
               '\nBreakeven: ' + str(breakeven) +
               '\nLast price: ' + str(last_price) + '\n'
               )
        telegram_bot(thr_name, msg)
        print(msg)
        return
    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        sleep(1)


def write_profit(thr_name, coin, pnl, side, duration):
    equity = round((get_equity(thr_name)), 4)
    live = str(live_time())
    df = pd.DataFrame(
        {'time': [datetime.datetime.now()], 'equity': [equity], 'pnl': [pnl], 'side': [side], 'coin': [coin],
         'duration': [duration], 'live': [live]})
    df.to_sql(sql_table_DEPO, engine, if_exists='append', index=False)
    return equity


def quarantine_in(coin, duration):
    quar_time = time.time() + duration
    quarantine[coin] = quar_time


def quarantine_out():
    while True:
        sleep(1)
        # print('Quarantine: ' + str(quarantine))
        if not quarantine:
            sleep(1)
        else:
            try:
                for coin in quarantine:
                    if time.time() > quarantine[coin]:
                        quarantine.pop(coin)
                        break
            except Exception as err:
                print('\n quarantine ' + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
                sleep(1)


def telegram_bot(thr_name, msg):
    try:
        bot = telebot.TeleBot(config.bot_token)
        bot.send_message(509963083, msg)
    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        sleep(1)


def order_list_msg():
    thr_name = threading.current_thread().name
    order_list_prev = pd.DataFrame()
    i = 0
    while True:
        if not order_list_prev.equals(order_list) or i == 20:
            i = 0
            upnl_list = []
            order_list_prev = order_list.copy()
            order_list_pnl = order_list.copy()
            for index, row in order_list.iterrows():
                if row['Coin'] != 'none':
                    upnl = get_unrealised_pnl(thr_name, row['Coin'], row['Side'])
                    if upnl is not None:
                        upnl_list.append(str(f'{upnl:.4f}'))
                    else:
                        upnl_list.append('ERR')
                else:
                    upnl_list.append('none')
            order_list_pnl.insert(0, 'PNL', upnl_list, allow_duplicates=True)
            equity = get_equity(thr_name)
            uptime = live_time()
            msg = ('\n### Order list. Equity: ' + str(equity) + ' ###\nUpdate time: '
                   + str(datetime.datetime.now().replace(microsecond=0))
                   + '\nLive time: ' + str(uptime)
                   + '\n' + str(order_list_pnl.to_string(header=False, justify='center')) + '\n')
            telegram_bot('Order list', msg)
            print(msg)
        i += 1
        time.sleep(30)


def get_open_position():
    try:
        print('\nSearching open position...')
        with open('coins.txt', 'r') as f:
            for line in f:
                coin = line[:-1]
                active_pos_buy = session.my_position(symbol=coin)['result'][0]['size']
                active_pos_sell = session.my_position(symbol=coin)['result'][1]['size']
                if active_pos_buy != 0 or active_pos_sell != 0:
                    if active_pos_buy != 0:
                        side = 'Buy'
                    else:
                        side = 'Sell'
                    print('\nPosition found! Coin: ' + str(coin) + ' Side: ' + str(side))
                    open_positions[coin] = side
                    if len(open_positions) == 4:
                        print('\nАll positions found\n')
                        break
                time.sleep(0.1)
            if len(open_positions) == 0:
                print('\nNo open positions\n')
            else:
                print('\nАll positions found\n')
    except Exception as err:
        print('\n' + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        time.sleep(1)


def get_data(thr_name, payload):
    time.sleep(1)
    while True:
        try:
            response = requests.post(config.URL, headers=config.HEADERS, json=payload, timeout=15)
            return response.json()
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            time.sleep(1)


def get_coins_list(thr_name, data, coins):
    try:
        ind = 0
        for _ in data['data']:
            while ind < len(data['data']):
                coin = data['data'][ind]['d'][2]
                coins.append(coin)
                ind += 1
    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        time.sleep(1)


def get_buy_list(thr_name, side):
    try:
        coins_01 = []
        coins_05 = []
        coins_15 = []

        match side:
            case 'Buy':
                data_01 = get_data(thr_name, config.payload_buy_01)
                data_05 = get_data(thr_name, config.payload_buy_05)
                data_15 = get_data(thr_name, config.payload_buy_15)
            case 'Sell':
                data_01 = get_data(thr_name, config.payload_sell_01)
                data_05 = get_data(thr_name, config.payload_sell_05)
                data_15 = get_data(thr_name, config.payload_sell_15)

        get_coins_list(thr_name, data_01, coins_01)
        get_coins_list(thr_name, data_05, coins_05)
        get_coins_list(thr_name, data_15, coins_15)
        coins_list = list(set(coins_01) & set(coins_05) & set(coins_15))
        return coins_list

    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        time.sleep(1)


def get_coin(thr_name, side):
    try:
        with open('coins.txt', 'r') as f:
            cont = f.read()
        coins_list = get_buy_list(thr_name, side)
        out_coin = ''
        if coins_list:
            for coin in coins_list:
                if (coin in cont and coin not in exclude
                        and coin not in quarantine and coin is not None):
                    out_coin = coin
                    exclude.append(out_coin)
                    print(thr_name, out_coin, exclude)
                    return out_coin
        else:
            print(thr_name + ' list of coins is empty')
            return out_coin
    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        time.sleep(1)


def get_equity(thr_name):
    while True:
        sleep(4)
        try:
            equity = round(float(session.get_wallet_balance()['result']['USDT']['equity']), 2)
            return equity
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            sleep(1)


def get_available_balance(thr_name):
    while True:
        sleep(4)
        try:
            equity = round(session.get_wallet_balance()['result']['USDT']['available_balance'], 4)
            return equity
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            sleep(1)


def get_last_price(thr_name, coin):
    while True:
        sleep(4)
        try:
            last_price = float(session.latest_information_for_symbol(symbol=coin)['result'][0]['last_price'])
            if last_price is not None:
                return last_price
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            if 'Too many visits' in str(err):
                print(thr_name + ' sleep 30 sec\n')
                time.sleep(30)
            sleep(1)


def get_close_price(thr_name, coin):
    while True:
        sleep(4)
        try:
            close_price = round(float(session.closed_profit_and_loss(symbol=coin)
                                      ['result']['data'][0]['avg_exit_price']), 4)
            if close_price is not None:
                return close_price
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            sleep(1)


def get_pnl(thr_name, coin):
    while True:
        sleep(4)
        try:
            order_id = session.user_trade_records(symbol=coin)['result']['data'][0]['order_id']
            order_id_pnl = session.closed_profit_and_loss(symbol=coin)['result']['data'][0]['order_id']
            if order_id_pnl == order_id:
                pnl = round(float(session.closed_profit_and_loss(symbol=coin)['result']['data'][0]['closed_pnl']), 4)
                return pnl
            sleep(4)
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            sleep(1)


def get_unrealised_pnl(thr_name, coin, side):
    match side:
        case 'Buy':
            side_ind = 0
        case 'Sell':
            side_ind = 1
    while True:
        sleep(4)
        try:
            unrealised_pnl = session.my_position(symbol=coin)['result'][side_ind]['unrealised_pnl']
            return unrealised_pnl
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            if 'Too many visits' in str(err):
                print(thr_name + ' Sleep 30 sec\n')
                time.sleep(30)
            sleep(1)


def place_active_order(thr_name, coin, side, quantity):
    while True:
        sleep(4)
        try:
            session.place_active_order(symbol=coin, side=side, order_type=config.order_type, qty=quantity,
                                       time_in_force=config.time_in_force, reduce_only=False, close_on_trigger=False)
            sleep(2)
            active_pos = get_active_position(thr_name, coin, side)
            if active_pos is not None:
                return active_pos
            else:
                return 0
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            sleep(1)


def get_trailing_stop(thr_name, coin, side, trailing_stop):
    precision = 4
    match side:
        case 'Buy':
            side_ind = 0
        case 'Sell':
            side_ind = 1
    while True:
        sleep(4)
        try:
            active_pos = session.my_position(symbol=coin)['result'][side_ind]['size']
            if active_pos != 0 and active_pos is not None:
                session.set_trading_stop(symbol=coin, side=side, trailing_stop=trailing_stop)
                return True
            else:
                return False
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            if 'Stoploss err' in str(err):
                precision -= 1
                trailing_stop = round(trailing_stop, precision)
                sleep(4)
            if 'Too many visits' in str(err):
                print(thr_name + ' Sleep 30 sec\n')
                time.sleep(30)
            if 'Not modified' in str(err):
                order_id = session.get_conditional_order(symbol=coin)['result']['data'][0]['stop_order_id']
                order_status = session.get_conditional_order(symbol=coin)['result']['data'][0]['order_status']
                if order_status == 'Untriggered':
                    session.cancel_conditional_order(symbol=coin, stop_order_id=order_id)
            time.sleep(1)


def get_entry_price(thr_name, coin, side):
    match side:
        case 'Buy':
            side_ind = 0
        case 'Sell':
            side_ind = 1
    while True:
        sleep(4)
        try:
            entry_price = float(session.my_position(symbol=coin)['result'][side_ind]['entry_price'])
            sleep(4)
            if entry_price is not None:
                return entry_price
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            if 'Too many visits' in str(err):
                print(thr_name + ' Sleep 30 sec\n')
                time.sleep(30)
            sleep(1)


def get_active_position(thr_name, coin, side):
    match side:
        case 'Buy':
            side_ind = 0
        case 'Sell':
            side_ind = 1
    while True:
        sleep(4)
        try:
            active_pos = session.my_position(symbol=coin)['result'][side_ind]['size']
            return active_pos
        except Exception as err:
            print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
            if 'Too many visits' in str(err):
                print(thr_name + ' Sleep 30 sec\n')
                time.sleep(30)
            sleep(1)


def get_quantity(thr_name, coin):
    try:
        last_price = get_last_price(thr_name, coin)
        equity = round((get_equity(thr_name) / 5), 4) * config.leverage
        info = session.query_symbol()['result']
        min_size = [i for i in info if i['name'] == coin][0]['lot_size_filter']['min_trading_qty']
        if float(min_size) < 1:
            quantity = float(round(round(equity / last_price, 4) - float(min_size), 4))
        else:
            quantity = int(equity // last_price)
        if quantity < min_size:
            return 0
        else:
            return quantity
    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        time.sleep(1)


def trading(thr_name, position, side):
    msg_stop_loss = ('--- ' + thr_name + ' STOP LOSS ---\n' +
                     'Coin: ' + str(position[0]) + '\nStop loss: ')
    msg_take_profit = ('+++ ' + thr_name + ' TAKE PROFIT +++\n' +
                       'Coin: ' + str(position[0]) + '\nTake profit: ')
    breakeven_buy = float(position[1] + position[2])
    breakeven_sell = float(position[1] - position[2])
    breakeven = False
    while True:
        active_pos = get_active_position(thr_name, position[0], side)
        if active_pos is not None:
            if active_pos == 0:
                pnl = get_pnl(thr_name, position[0])
                if pnl < 0:
                    msg = msg_stop_loss
                    if position[0] in stop_loss_list:
                        quarantine_in(position[0], 120)
                    else:
                        stop_loss_list.append(position[0])
                    break
                else:
                    msg = msg_take_profit
                    if position[0] in stop_loss_list:
                        stop_loss_list.remove(position[0])
                    quarantine_in(position[0], 30)
                    break
            else:
                if not breakeven:
                    last_price = get_last_price(thr_name, position[0])
                    if breakeven_buy < last_price or last_price < breakeven_sell:
                        breakeven = True
                        trailing_stop = round(float(position[2] / 2), 4)
                        check = get_trailing_stop(thr_name, position[0], side, trailing_stop)
                        if check:
                            match side:
                                case 'Buy':
                                    breakeven = breakeven_buy
                                case 'Sell':
                                    breakeven = breakeven_sell
                            msg_breakeven(thr_name, position[0], position[1], breakeven, last_price)
                sleep(4)
        else:
            print('\n???', thr_name, inspect.currentframe().f_code.co_name, str(active_pos), '???\n')

    close_time = datetime.datetime.now().replace(microsecond=0)
    duration = str(close_time.replace(microsecond=0) - position[5].replace(microsecond=0))
    equity = write_profit(thr_name, position[0], pnl, side, duration)
    close_price = get_close_price(thr_name, position[0])
    msg = msg + (str(pnl) + '\nEquity: ' + str(equity) + '\nClose price: ' + str(close_price) +
                 '\nClose time: ' + str(close_time) + '\nDuration: ' + str(duration) + '\n')
    exclude.remove(position[0])
    telegram_bot(thr_name, msg)
    print(msg)


def position(side):
    thr_name = threading.current_thread().name
    equity = get_equity(thr_name)
    while equity > 0:
        coin = get_coin(thr_name, side)
        print('\n%%%', thr_name, side, coin, 'check 01 %%%\n')
        if coin != '' and coin is not None:
            quantity = get_quantity(thr_name, coin)
            if quantity is not None and quantity > 0:
                active_pos = place_active_order(thr_name, coin, side, quantity)
                if active_pos != 0:
                    match side:
                        case 'Buy':
                            stop_loss = (config.stop_loss_buy / 100)
                        case 'Sell':
                            stop_loss = (config.stop_loss_sell / 100)
                    entry_price = get_entry_price(thr_name, coin, side)
                    trailing_stop = round((entry_price * stop_loss), 4)
                    get_trailing_stop(thr_name, coin, side, trailing_stop)
                    pos = msg_new_position(thr_name, side, coin, entry_price, trailing_stop, quantity)
                    print('\n%%%', thr_name, 'start trading %%%\n')
                    trading(thr_name, pos, side)
                    order_list.loc[thr_name] = ['none', 'none', 'none']
                    print('\n%%%', thr_name, 'end trading %%%\n')
            else:
                if coin in exclude:
                    exclude.remove(coin)
        else:
            order_list.loc[thr_name] = ['none', 'none', 'none']
            match side:
                case 'Buy':
                    side = 'Sell'
                case 'Sell':
                    side = 'Buy'
        print('\n%%%', thr_name, side, 'check 02 %%%\n')
        sleep(1)
        equity = get_equity(thr_name)


def check_open_position(thr_name, coin, side):
    try:
        match side:
            case 'Buy':
                side_ind = 0
                stop_loss = (config.stop_loss_buy / 100)
            case 'Sell':
                side_ind = 1
                stop_loss = (config.stop_loss_sell / 100)
        quantity = get_active_position(thr_name, coin, side)
        entry_price = float(session.my_position(symbol=coin)['result'][side_ind]['entry_price'])
        trailing_stop = float(session.my_position(symbol=coin)['result'][side_ind]['trailing_stop'])
        while trailing_stop == 0 and quantity != 0:
            trailing_stop = round((entry_price * stop_loss), 4)
            get_trailing_stop(thr_name, coin, side, trailing_stop)
            quantity = get_active_position(thr_name, coin, side)
            trailing_stop = float(session.my_position(symbol=coin)['result'][side_ind]['trailing_stop'])
        return quantity, entry_price, trailing_stop

    except Exception as err:
        print('\n' + str(thr_name) + inspect.currentframe().f_code.co_name + f'\n<<=={err}==>>\n')
        if 'Too many visits' in str(err):
            print(thr_name + ' Sleep 30 sec\n')
            time.sleep(30)
        sleep(1)


def old_position(coin, side):
    thr_name = threading.current_thread().name
    quantity, entry_price, trailing_stop = check_open_position(thr_name, coin, side)
    active_pos = get_active_position(thr_name, coin, side)
    if active_pos is not None:
        if active_pos != 0:
            pos = msg_new_position(thr_name, side, coin, entry_price, trailing_stop, quantity)
            print('%%%', thr_name, 'OLD POS start trading %%%')
            trading(thr_name, pos, side)
            print('%%%', thr_name, 'OLD POS end trading %%%')
            order_list.loc[thr_name] = ['none', 'none', 'none']
    else:
        print('\n???', thr_name, inspect.currentframe().f_code.co_name, str(active_pos),'???\n')


def start():
    # ----- Check old open position -----
    get_open_position()
    print('Open positions:', str(open_positions))
    if open_positions:
        i = 1
        for coin in open_positions:
            exclude.append(coin)
            side = open_positions[coin]
            threading.Thread(target=old_position, name=f"THR 0{i} ", args=(coin, side,)).start()
            i += 1

    # ----- Check threads every 30 sec-----
    while True:
        thread = []
        for t in threading.enumerate():
            thread.append(t.name)
        for thr in thr_list:
            if thr not in thread:
                print('\n~~~ Start a new thread', thr, '~~~\n')
                threading.Thread(target=position, name=thr, args=('Buy',)).start()
        if 'order list ' not in thread:
            threading.Thread(target=order_list_msg, name="order list ").start()
        if 'quarantine ' not in thread:
            threading.Thread(target=quarantine_out, name="quarantine ").start()
        time.sleep(30)


if __name__ == "__main__":
    start()
