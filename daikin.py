import requests
import urllib
import re
from enum import Enum
from netdisco.daikin import Daikin

def discover():
    disco = Daikin()
    disco.update()
    units = map(lambda x: Unit(x['ip'], x['name'].lower()), disco.entries)
    return UnitCollection(units)


class Mode(Enum):
    auto = 1
    dry = 2
    cooling = 3
    heating = 4
    fan = 6

class UnitCollection:
    def __init__(self, units):
        self.units = units

    def apply(self, alias, expression):
        filtered = filter(lambda u: alias is None or u.alias == alias.lower(), self.units)
        result = {u.alias: expression(u) for u in filtered}
        return result

class Temperature:
    def __init__(self, inside, outside):
        self.inside = inside
        self.outside = outside

class Mode:
    def __init__(self, power, temperature): 
        self.power = power
        self.temperature = temperature

class Unit:
    def __init__(self, ip, alias):
        self.ip = ip
        self.alias = alias

    def temperature(self):
        data = self.__request('aircon/get_sensor_info')
        return Temperature(
            re.sub(r".0$", "", data['htemp']),
            re.sub(r".0$", "", data['otemp'])
        )

    def name(self):
        data = self.__request('common/basic_info')
        return urllib.unquote(data['name']).decode('utf8')

    def mode(self):
        m = self.__raw_mode()
        return Mode(m['pow'] == '1', re.sub(r".0$", "", m['stemp']))

    def off(self):
        m = self.__raw_mode()
        m['pow'] = 0
        data = self.__request(
                 'aircon/set_control_info', 'post',
                 urllib.urlencode(m)
               )
        return data['ret'] == 'OK'

    def on(self):
        m = self.__raw_mode()
        m['pow'] = 1
        data = self.__request(
                 'aircon/set_control_info', 'post',
                 urllib.urlencode(m)
               )
        return data['ret'] == 'OK'

    def __raw_mode(self):
        data = self.__request('aircon/get_control_info')
        return {
            'pow': data['pow'],
            'mode': data['mode'],
            'stemp': data['stemp'],
            'shum': data['shum'],
            'f_rate': data['f_rate'],
            'f_dir': data['f_dir'],
        }

    def __request(self, path, method = 'get', payload ='' ):
        url = 'http://{}/{}'.format(self.ip, path)
        if method == 'get':
        	response = requests.get(url)
        else:
                response = requests.post(url, data = bytearray(payload))
        data = dict(map(lambda x: x.split('='), response.text.split(',')))
        return data
