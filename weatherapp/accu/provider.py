""" Weather provider.
"""

import re
import requests
import html
from bs4 import BeautifulSoup

from weatherapp.accu import config
from weatherapp.core.abstract import WeatherProvider


class AccuProvider(WeatherProvider):
    """ Weather provider for AccuWeather site.
    """

    name = config.ACCU_PROVIDER_NAME
    title = config.ACCU_PRVIDER_TITLE

    def get_default_location(self):
        """ Default location name.
        """

        return config.DEFAULT_ACCU_LOCATION_NAME

    def get_default_url(self):
        """ Default location url.
        """
        return config.DEFAULT_ACCU_LOCATION_URL

    def get_name(self):
        """ Get name provider
        """
        return self.name

    def get_locations(self, locations_url):
        """ Choosing a place for which you need to get weather information.
        """

        soup = \
            BeautifulSoup(self.get_page_source(locations_url), 'html.parser')
        locations = []

        for location in soup.find_all('li', attrs={'class': 'drilldown cl'}):
            url = location.find('a').get('href')
            location = location.find('em').get_text()
            locations.append((location, url))
        return locations

    def configurate(self):
        """ The user chooses the city for which he wants to get the weather.
        """

        locations = self.get_locations(config.ACCU_BROWSE_LOCATIONS)
        while locations:
            for index, location in enumerate(locations):
                print("{}. {}".format((index + 1), (location[0])))
            while True:
                try:
                    selected_index = int(input('Please select location'
                                               '(in format integer number): '))
                    if selected_index > 0:
                        location = locations[selected_index - 1]
                        break
                except ValueError:
                    print("That was no valid number. Try again...")
                except IndexError:
                    print("This number out of range. Try again...")

            locations = self.get_locations(location[1])

            self.save_configuration(*location)

    def get_weather_info(self, page):
        """ The function returns a list with the values the state the weather.
        """
        # create a blank dictionary to enter the weather data
        weather_info = {}

        # find the <div> container with the information we need
        soup = BeautifulSoup(page, 'html.parser')
        if self.app.options.tomorrow == 'tomorrow':
            tag_container = \
                soup.find(class_="day hv cl")
            if tag_container:
                current_day_url = tag_container.find('a').attrs['href']
                if current_day_url:
                    current_day = self.get_page_source(current_day_url)
                    current_day_page = BeautifulSoup(current_day,
                                                     'html.parser')
                    if current_day_page:
                        weather_details = \
                            current_day_page.find(id="detail-day-night")
                        temp_info = weather_details.find('span',
                                                         class_="large-temp")
                        if temp_info:
                            weather_info['temp'] = temp_info.get_text()
                        realfeel = weather_details.find('span',
                                                        class_="realfeel")
                        if realfeel:
                            weather_info['feels_like'] = realfeel.get_text()
                        cond_info = weather_details.find(class_="cond")
                        if cond_info:
                            weather_info['cond'] = cond_info.get_text().strip()
                        wind_direction_tag = \
                            weather_details.find(class_="wind-stats")
                        wind_speed_tag = weather_details.find("strong")
                        if wind_direction_tag:
                            weather_info['wind'] = wind_speed_tag.get_text()

        elif self.app.options.regexp:
            tag_container = \
                re.compile(r"(?is)<li class=\"(day|night) current first cl\"[^>]*>(.+?)</li")
            tag = tag_container.findall(page)
            url = str(tag[0])
            forecast = re.compile(r"(?is)<h3><a href=\" *(.+?)[?\">]")
            f_info = forecast.findall(url)
            current_day_url = f_info[0]
            if current_day_url:
                current_day = self.get_page_source(current_day_url)

                temp_info = re.compile(r"(?is)<span class=\"large-temp\"[^>]*>(.+?)</span>")
                temp = temp_info.findall(current_day)
                weather_info['temp'] = html.unescape(temp[0].strip())

                realfeel_info = re.compile(r"(?is)<span class=\"real-feel\"[^>]*>(.+?)</span>")
                realfeel = realfeel_info.findall(current_day)
                weather_info['feels_like'] = html.unescape(realfeel[0].strip())

                cond_info = re.compile(r"(?is)<span class=\"cond\"[^>]*>(.+?)</span>")
                cond = cond_info.findall(current_day)
                weather_info['cond'] = cond[-1]

                wind_info = re.compile(r"(?is)<li class=\"wind\"[^>]*>(.+?)</li>")
                wind_i = wind_info.findall(current_day)
                wind_details = re.compile(r"(?is)<li class=\"wind\"><strong>(.+?)</strong></li>")
                wind_d = wind_details.findall(current_day)
                weather_info['wind'] = wind_i[0].strip() + ' ' + wind_d[0]

        else:
            tag_container = \
                soup.find(class_=re.compile("(day|night) current first cl"))
            if tag_container:
                current_day_url = tag_container.find('a').attrs['href']
                if current_day_url:
                    current_day = self.get_page_source(current_day_url)
                    current_day_page = BeautifulSoup(current_day,
                                                     'html.parser')
                    if current_day_page:
                        weather_details = \
                            current_day_page.find(id="detail-now")
                        temp_info = weather_details.find('span',
                                                         class_="large-temp")
                        if temp_info:
                            weather_info['temp'] = temp_info.get_text()
                        realfeel = weather_details.find(class_="small-temp")
                        if realfeel:
                            weather_info['feels_like'] = realfeel.get_text()
                        cond_info = weather_details.find('span', class_="cond")
                        if cond_info:
                            weather_info['cond'] = cond_info.get_text()
                        wind_direction_tag = \
                            weather_details.find(class_="wind")
                        wind_speed_tag = weather_details.find("strong")
                        if wind_direction_tag or wind_speed_tag:
                            wind_direction = ' '.join(map(lambda t: t.strip(),
                                                          wind_direction_tag))
                            wind_speed = wind_speed_tag.get_text()
                            weather_info['wind'] = wind_direction + ' ' +\
                                wind_speed

        return weather_info
