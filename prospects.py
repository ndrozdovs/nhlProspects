import urllib.request
from bs4 import BeautifulSoup
import time
import smtplib
import os
from twilio.rest import Client
from dotenv import load_dotenv
from requests import Request, Session, hooks
from twilio.http.http_client import TwilioHttpClient
from twilio.http.response import Response


class MyRequestClass(TwilioHttpClient):
    def __init__(self):
        self.response = None

    def request(self, method, url, params=None, data=None, headers=None, auth=None, timeout=None,
                allow_redirects=False):
        # Here you can change the URL, headers and other request parameters
        kwargs = {
            'method': method.upper(),
            'url': url,
            'params': params,
            'data': data,
            'headers': headers,
            'auth': auth,
        }

        session = Session()
        request = Request(**kwargs)

        prepped_request = session.prepare_request(request)
        session.proxies.update({
            'http': os.getenv('HTTP_PROXY'),
            'https': os.getenv('HTTPS_PROXY')
        })
        response = session.send(
            prepped_request,
            allow_redirects=allow_redirects,
            timeout=timeout,
        )

        return Response(int(response.status_code), response.text)


class PlayerStats:
    name = 'string'
    games_played = 0
    goals_scored = 0
    assists = 0


load_dotenv()

# Custom HTTP Class
my_request_client = MyRequestClass()
client = Client(os.getenv("ACCOUNT_SID"), os.getenv("AUTH_TOKEN"),
                http_client=my_request_client)

Pelletier = 'https://www.eliteprospects.com/player/410525/jakob-pelletier'
Nikolayev = 'https://www.eliteprospects.com/player/514152/ilya-nikolayev'
Feuk = 'https://www.eliteprospects.com/player/385539/lucas-feuk'
Nodler = 'https://www.eliteprospects.com/player/290052/josh-nodler'
Pospisil = 'https://www.eliteprospects.com/player/341691/martin-pospisil'
Koumontzis = 'https://www.eliteprospects.com/player/354063/demetrios-koumontzis'
Roman = 'https://www.eliteprospects.com/player/223844/milos-roman'
Pettersen = 'https://www.eliteprospects.com/player/274219/mathias-emilio-pettersen'
Zavgorodny = 'https://www.eliteprospects.com/player/396918/dmitri-zavgorodny'
Ruzicka = 'https://www.eliteprospects.com/player/228366/adam-ruzicka'
Sveningsson = 'https://www.eliteprospects.com/player/244859/filip-sveningsson'
Dube = 'https://www.eliteprospects.com/player/157256/dillon-dube'
Lindstrom = 'https://www.eliteprospects.com/player/242668/linus-lindstrom'
Phillips = 'https://www.eliteprospects.com/player/161060/matthew-phillips'
Tuulola = 'https://www.eliteprospects.com/player/123542/eetu-tuulola'

Players = [Pelletier, Nikolayev, Feuk, Nodler, Pospisil, Koumontzis, Roman, Pettersen, Zavgorodny, Ruzicka,
           Sveningsson, Dube, Lindstrom, Phillips, Tuulola]

number_of_players = 15

initial = 0
players_stats = [PlayerStats() for i in range(number_of_players)]
print("Executing")

while True:
    for url, player_stats in zip(Players, players_stats):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

        while True:
            try:
                request = urllib.request.Request(url, headers={'User-Agent': user_agent})
                response = urllib.request.urlopen(request)
                html = response.read()
                break
            except (urllib.error.HTTPError, urllib.error.URLError):
                continue

        soup = BeautifulSoup(html, 'html.parser')

        player_name = soup.find('h1', attrs={'class': 'plytitle'})
        player_name = player_name.text.strip()
        player_name = ' '.join(player_name.split())
        if 'Legacy verified' in player_name:
            player_name = player_name[:player_name.find('Legacy verified') - 1]
        if 'a.k.a.' in player_name:
            player_name = player_name[:player_name.find('a.k.a.') - 1]

        year = 'No'
        season_year = soup.find('td', attrs={'class': 'season sorted'})

        while year != '2019-20':
            season_year = season_year.find_next('td', attrs={'class': 'season sorted'})
            year = season_year.text.strip()

        parent = season_year.parent
        games = season_year.parent.find('td', attrs={'class': 'regular gp'})
        goals = season_year.parent.find('td', attrs={'class': 'regular g'})
        assists = season_year.parent.find('td', attrs={'class': 'regular a'})
        points = season_year.parent.find('td', attrs={'class': 'regular tp'})
        games = games.text.strip()
        goals = goals.text.strip()
        assists = assists.text.strip()
        points = points.text.strip()

        if initial == 0:
            player_stats.name = player_name
            player_stats.games_played = games
            player_stats.goals_scored = goals
            player_stats.assists = assists
        else:
            if player_stats.games_played == games:
                    goals_scored_today = int(goals) - int(player_stats.goals_scored)
                    assists_today = int(assists) - int(player_stats.assists)
                    player_stats.games_played = games
                    player_stats.goals_scored = goals
                    player_stats.assists = assists

                    body_text = "Today, {} scored {} goals and got {} assists.\n He now has {} goals and {} assists total in {} games."\
                        .format(player_name, goals_scored_today, assists_today, goals, assists, games)

                    message = client.messages.create(
                                body=body_text,
                                from_='+16043302390',
                                to='+14038038374'
                    )

    initial = 1
    time.sleep(600)
