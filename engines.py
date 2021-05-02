from urllib import request
import json
import pickle
import os.path

SUPPORTED_FIAT = ['USD', 'EUR', 'PLN']
DEFAULT_FIAT = 'USD'
SUPPORTED_CRYPTO = ['BTC', 'ETH', 'LTC', 'DOGE', 'BCH',
                    'XRP', 'DASH', 'XMR', 'EOS', 'NEO', 'OMG',
                    'LSK', 'ZEC', 'NXT', 'ARDR', 'GNT', 'ALGO']
DEFAULT_CRYPTO = 'BTC'
ALL_KEYWORD = 'raport'
TRIGGER_WORDS = SUPPORTED_FIAT + SUPPORTED_CRYPTO
TRIGGER_WORDS = [word.lower() for word in TRIGGER_WORDS] + [ALL_KEYWORD]
FILE_NAME_PRICES = 'prices.pkl'
FILE_NAME_POLLUTION = 'pollution.pkl'


class CryptoEngine():
    def __init__(self):
        # init all cryptos on start
        # TODO? wypierdolić?
        self.last_price = {}
        if os.path.isfile(FILE_NAME_PRICES):
            with open(FILE_NAME_PRICES, 'rb') as fp:
                self.last_price = pickle.load(fp)
        else:
            self.last_price = self.check_current_price_for_all_supported_cryptos()
            with open(FILE_NAME_PRICES, 'wb') as fp:
                pickle.dump(self.last_price, fp)

    @property
    def trigger_words(self):
        return TRIGGER_WORDS

    @staticmethod
    def check_current_price(crypto_symbol):
        return json.load(request.urlopen("https://min-api.cryptocompare.com/"
                                         f"data/price?fsym={crypto_symbol}"
                                         f"&tsyms={','.join(SUPPORTED_FIAT)}"
                                         ))

    @staticmethod
    def check_current_price_for_all_supported_cryptos():
        return json.load(request.urlopen("https://min-api.cryptocompare.com/"
                                         f"data/pricemulti?fsyms={','.join(SUPPORTED_CRYPTO)}"
                                         f"&tsyms={','.join(SUPPORTED_FIAT)}"
                                         ))

    def generate_crypto_status(self, crypto, used_fiat):
        fiat = used_fiat[0]
        current_price = self.check_current_price(crypto)
        change = current_price[fiat] / self.last_price[crypto][fiat] - 1
        if change > 0:
            status = f'{crypto} urus.'
        elif change < 0:
            status = f'{crypto} zmalau.'
        else:
            status = f'{crypto} stoi.'

        change *= 100
        if change != 0:
            status += f' zmiana: {change:.4f}%'
        for fiat in used_fiat:
            status += '\n1 {crypto} = {amount} {currency} '.format(
                crypto=crypto,
                amount=current_price[fiat],
                currency=fiat
            )
            self.last_price[crypto] = current_price
        return status

    def analyze_message_and_prepare_response(self, message):
        m = message.upper()
        if ALL_KEYWORD in message:
            used_crypto = SUPPORTED_CRYPTO
        else:
            used_crypto = [c for c in SUPPORTED_CRYPTO if c in m]

        used_fiat = [f for f in SUPPORTED_FIAT if f in m]

        if not used_crypto:
            used_crypto = [DEFAULT_CRYPTO]
        if not used_fiat:
            used_fiat = [DEFAULT_FIAT]

        message = ''
        for crypto in used_crypto:
            message += self.generate_crypto_status(crypto, used_fiat) + '\n\n'

        with open(FILE_NAME_PRICES, 'wb') as fp:
            pickle.dump(self.last_price, fp)
        return message


class AirPollutionEngine():
    def __init__(self):
        if os.path.isfile(FILE_NAME_POLLUTION):
            with open(FILE_NAME_POLLUTION, 'rb') as fp:
                self.last_measurement = pickle.load(fp)
        else:
            self.last_measurement = self.check_current_level()
            with open(FILE_NAME_POLLUTION, 'wb') as fp:
                pickle.dump(self.last_measurement, fp)

    @property
    def trigger_words(self):
        return ['smog']

    @staticmethod
    def check_current_level():
        return json.load(request.urlopen('https://api.waqi.info/feed/poland/slaski/katowice--ul-kossutha-6/?token=ee2c6a8c1b0244a4164e153b26df9f0a591cbb30'))['data']['iaqi']

    def analyze_message_and_prepare_response(self, message):
        last_pm10 = self.last_measurement['pm10']['v']
        last_pm25 = self.last_measurement['pm25']['v']
        current_measurement = self.check_current_level()
        current_pm10 = current_measurement['pm10']['v']
        current_pm25 = current_measurement['pm25']['v']
        if current_pm25 < last_pm25:
            status = 'smog zmalau.'
        elif current_pm25 > last_pm25:
            status = 'smog urus.'
        else:
            status = 'smog stoi.'
        status += f'\nPM2.5: {current_pm25}'
        status += f'\nPM10: {current_pm10}'
        self.last_measurement = current_measurement
        with open(FILE_NAME_POLLUTION, 'wb') as fp:
            pickle.dump(self.last_measurement, fp)
        return status
