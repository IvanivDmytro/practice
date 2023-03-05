#!/usr/bin/env python3

import json
from urllib.request import urlopen


ENDPOINT_URL = 'https://api.open-meteo.com/v1/forecast?{params}'
GEO_URL = 'https://geocoding-api.open-meteo.com/v1/search?name={city}'


class WeatherAPIError(Exception):
    pass


class City:
    def __init__(self, name):
        self.name = name
        self.latitude, self.longitude = self._get_coords()

    def _get_coords(self):
        url = GEO_URL.format(city=self.name)
        data = self._make_request(url)

        data = data['results']
        if not data:
            raise WeatherAPIError(f"No results for city '{self.name}'")

        # set to new, could differ as city is the first match
        # of search results
        city = data[0]['name']

        lat = data[0]['latitude']
        lon = data[0]['longitude']

        return lat, lon

    def _make_request(self, url):
        response = urlopen(url)
        data = response.read()

        data = data.decode('utf-8')
        res = json.loads(data)

        if 'error' in res:
            raise WeatherAPIError(res['error'])

        return res


class Weather:
    def __init__(self, city):
        self.city = city
        self.current_temp = self._request_curtemp()

    def _request_curtemp(self):
        url = self._req_url(latitude=self.city.latitude,
                            longitude=self.city.longitude,
                            current_weather='true')

        resp = self.city._make_request(url)
        current = resp['current_weather']
        current_temp = float(current['temperature'])

        return current_temp

    def _req_url(self, **kwargs):
        """Make resuling url for GET req to the ENDPOINT."""
        params = '&'.join([f'{k}={v}' for k, v in kwargs.items()])
        return ENDPOINT_URL.format(params=params)


def main(args):
    prog, *args = args

    if len(args) != 1:
        exit(f"USAGE: {prog} CITY\nGet current temperature.")

    city = City(args[0])
    weather = Weather(city)

    _deg = '\u00b0'
    print(f'Currently in {city.name} is {weather.current_temp} {_deg}C')


if __name__ == '__main__':
    import sys
    main(sys.argv)
