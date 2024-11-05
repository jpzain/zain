from flask import Flask, jsonify
import requests
import json
from bs4 import BeautifulSoup

def create_app():
    app = Flask(__name__)
    
    @app.route('/api/data-home', methods=['GET'])
    def get_leagues_home():
        with open('leagues-home.json') as json_file:
            data_leagues = json.load(json_file)
        with open('cups-home.json') as json_file:
            data_cups = json.load(json_file)
        return jsonify({
            'status_code': 1,
            'message': 'Success',
            'payload': {
                'leagues': data_leagues,
                'cups': data_cups
            }
        })
        
    @app.route('/api/leagues-all', methods=['GET'])
    def get_leagues_all():
        with open('leagues-all.json') as json_file:
            data = json.load(json_file)
        return jsonify({
            'status_code': 1,
            'message': 'Success',
            'payload': {
                'leagues': data
            }
        })
        
    @app.route('/api/cups-all', methods=['GET'])
    def get_cups_all():
        with open('cups-all.json') as json_file:
            data = json.load(json_file)
        return jsonify({
            'status_code': 1,
            'message': 'Success',
            'payload': {
                'cups': data
            }
        })

    @app.route('/api/fixtures/<string:league>', methods=['GET'])
    def get_fixtures(league):
        fixtures = scrape_fixtures(league)
        return jsonify({
            'status_code': 1,
            'message': 'Success',
            'payload': {
                'fixtures': fixtures
            }
        })

    @app.route('/api/results/<string:league>', methods=['GET'])
    def get_results(league):
        results = scrape_results(league)
        return jsonify({
            'status_code': 1,
            'message': 'Success',
            'payload': {
                'results': results
            }
        })

    @app.route('/api/table/<string:league>', methods=['GET'])
    def get_table(league):
        table = scrape_table(league)
        return jsonify({
            'status_code': 1,
            'message': 'Success',
            'payload': {
                'table': table
            }
        })

    @app.route('/api/match-details/<path:match_path>/<int:match_id>', methods=['GET'])
    def get_match_details(match_path, match_id):
        match_stats = scrape_match_stats(match_path, match_id)
        match_result = scrape_match_result(match_path, match_id)
        match_players = scrape_match_players(match_path, match_id)

        if match_stats and match_result and match_players:
            return jsonify({
                'status_code': 1,
                'message': 'Success',
                'payload': {
                    'stats': match_stats,
                    'result': match_result,
                    'players': match_players
                }
            })

        return jsonify({
            'status_code': 0,
            'message': 'Match details not found'
        })

    return app

def scrape_fixtures(league):
    url = f"https://www.skysports.com/{league}-fixtures"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    fixtures = []
    current_header1 = None
    current_header2 = None
    
    for element in soup.find_all(['h3', 'h4', 'div'], class_=['fixres__header1', 'fixres__header2', 'fixres__item']):
        if element.name == 'h3' and 'fixres__header1' in element.get('class', []):
            current_header1 = element.text.strip()
        elif element.name == 'h4' and 'fixres__header2' in element.get('class', []):
            current_header2 = element.text.strip()
        elif element.name == 'div' and 'fixres__item' in element.get('class', []):
            match_link = element.find('a', class_='matches__link')
            data_status = match_link.get('data-status', 'N/A') if match_link else 'N/A'
            
            a_tag = element.find('a', class_='matches__item matches__link')
            full_match_url = a_tag['href'].strip() if a_tag else "N/A"
            match_title = full_match_url.split('/football/')[1].rsplit('/', 1)[0] if '/football/' in full_match_url else "N/A"
            item_id = full_match_url.rsplit('/', 1)[-1]

            team1_element = element.find('span', class_='matches__participant--side1').find('span', class_='swap-text--bp30')
            team1 = team1_element['title'].strip() if team1_element else "N/A"
            
            team2_element = element.find('span', class_='matches__participant--side2').find('span', class_='swap-text--bp30')
            team2 = team2_element['title'].strip() if team2_element else "N/A"
            
            time = element.find('span', class_='matches__date').text.strip()
            scores = element.find_all('span', class_='matches__teamscores-side')
            score1 = scores[0].text.strip() if scores else "N/A"
            score2 = scores[1].text.strip() if scores else "N/A"

            match_info_element = element.find('span', class_='matches__item-col matches__info')
            match_info = match_info_element.text.strip() if match_info_element else "N/A"

            fixtures.append({
                'header1': current_header1,
                'header2': current_header2,
                'team1': team1,
                'team2': team2,
                'time': time,
                'score1': score1,
                'score2': score2,
                'info': match_info,
                'status': data_status,
                'title': match_title,
                'item_id': item_id
            })
    
    return fixtures

def scrape_results(league):
    url = f"https://www.skysports.com/{league}-results"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = []
    current_header1 = None
    current_header2 = None

    for element in soup.find_all(['h3', 'h4', 'div'], class_=['fixres__header1', 'fixres__header2', 'fixres__item']):
        if element.name == 'h3' and 'fixres__header1' in element.get('class', []):
            current_header1 = element.text.strip()
        elif element.name == 'h4' and 'fixres__header2' in element.get('class', []):
            current_header2 = element.text.strip()
        elif element.name == 'div' and 'fixres__item' in element.get('class', []):
            match_link = element.find('a', class_='matches__link')
            data_status = match_link.get('data-status', 'N/A') if match_link else 'N/A'
            
            a_tag = element.find('a', class_='matches__item matches__link')
            full_match_url = a_tag['href'].strip() if a_tag else "N/A"
            match_title = full_match_url.split('/football/')[1].rsplit('/', 1)[0] if '/football/' in full_match_url else "N/A"
            item_id = full_match_url.rsplit('/', 1)[-1]

            team1_element = element.find('span', class_='matches__participant--side1').find('span', class_='swap-text--bp30')
            team1 = team1_element['title'].strip() if team1_element else "N/A"
            
            team2_element = element.find('span', class_='matches__participant--side2').find('span', class_='swap-text--bp30')
            team2 = team2_element['title'].strip() if team2_element else "N/A"
            
            time = element.find('span', class_='matches__date').text.strip()
            scores = element.find_all('span', class_='matches__teamscores-side')
            score1 = scores[0].text.strip() if scores else "N/A"
            score2 = scores[1].text.strip() if scores else "N/A"

            match_info_element = element.find('span', class_='matches__item-col matches__info')
            match_info = match_info_element.text.strip() if match_info_element else "N/A"

            results.append({
                'header1': current_header1,
                'header2': current_header2,
                'team1': team1,
                'team2': team2,
                'time': time,
                'score1': score1,
                'score2': score2,
                'info': match_info,
                'status': data_status,
                'title': match_title,
                'item_id': item_id
            })
    
    return results
    
def scrape_table(league):
    url = f"https://www.skysports.com/{league}-table"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = []
    table.append({
        'team': '',
        'Pl': '',
        'W': '',
        'D': '',
        'L': '',
        'GD': '',
        'Pts': ''
    })
    
    for row in soup.select('tbody tr.sdc-site-table__row'):
        team = row.find('span', class_='sdc-site-table__name-target').text.strip()
        rank = row.find('td', headers="th--0").text.strip()
        played = row.find('td', headers="th--2").text.strip()
        wins = row.find('td', headers="th--3").text.strip()
        draws = row.find('td', headers="th--4").text.strip()
        losses = row.find('td', headers="th--5").text.strip()
        gd = row.find('td', headers="th--8").text.strip()
        points = row.find('td', headers="th--9").text.strip()

        table.append({
            'team': team,
            'rank': rank,
            'Pl': played,
            'W': wins,
            'D': draws,
            'L': losses,
            'GD': gd,
            'Pts': points
        })
    
    return table
    
def scrape_match_stats(match_path, match_id):
    url = f"https://www.skysports.com/football/{match_path}/stats/{match_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    stats = []
    keys = [
        'possession', 'total_shots', 'on_target', 'off_target', 'blocked',
        'passing', 'clear_cut_chances', 'corners', 'offsides', 'tackles',
        'aerial_duels', 'saves', 'fouls_committed', 'fouls_won', 
        'yellow_cards', 'red_cards'
    ]
    titles = [
        "Possession %", "Total Shots", "On Target", "Off Target", "Blocked",
        "Passing %", "Clear-Cut Chances", "Corners", "Offsides", "Tackles %",
        "Aerial Duels %", "Saves", "Fouls Committed", "Fouls Won", 
        "Yellow Cards", "Red Cards"
    ]

    for key, title in zip(keys, titles):
        stat_div = soup.find('h5', text=title)
        if stat_div:
            home_value = stat_div.find_next('div', class_='sdc-site-match-stats__stats-home').find('span', class_='sdc-site-match-stats__val').text.strip()
            away_value = stat_div.find_next('div', class_='sdc-site-match-stats__stats-away').find('span', class_='sdc-site-match-stats__val').text.strip()
            stats.append({
                'title': title,
                'home': home_value,
                'away': away_value
            })

    return stats

def scrape_match_result(match_path, match_id):
    url = f"https://www.skysports.com/football/{match_path}/{match_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    result = {}
    result['home_team'] = soup.find('span', class_='sdc-site-match-header__team-name--home').text.strip()
    result['away_team'] = soup.find('span', class_='sdc-site-match-header__team-name--away').text.strip()
    result['home_score'] = soup.find('span', {'data-update': 'score-home'}).text.strip()
    result['away_score'] = soup.find('span', {'data-update': 'score-away'}).text.strip()

    status_element = soup.find('div', class_='sdc-site-match-header__status')
    if status_element:
        match_status = status_element.find('span', class_='sdc-site-match-header__match-status--ft')
        result['status'] = match_status.text.strip() if match_status else "LIVE"

    match_time = soup.find('time', class_='sdc-site-match-header__detail-time')
    if match_time:
        result['match_time'] = match_time.text.strip()

    venue = soup.find('span', class_='sdc-site-match-header__detail-venue')
    if venue:
        result['venue'] = venue.text.strip()

    result['home_goals'] = []
    result['away_goals'] = []

    home_scorers = soup.find('ul', {'data-update': 'synopsis-home'})
    if home_scorers:
        for scorer in home_scorers.find_all('li'):
            result['home_goals'].append(scorer.text.strip())

    away_scorers = soup.find('ul', {'data-update': 'synopsis-away'})
    if away_scorers:
        for scorer in away_scorers.find_all('li'):
            result['away_goals'].append(scorer.text.strip())

    return result
    
def scrape_match_players(match_path, match_id):
    url = f"https://www.skysports.com/football/{match_path}/teams/{match_id}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve data'}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    home_players = []
    away_players = []

    team_columns = soup.find_all('div', class_='sdc-site-team-lineup__col')

    for column in team_columns:
        players = column.find_all('dl', class_='sdc-site-team-lineup__players')
        player_numbers = players[0].find_all('dt', class_='sdc-site-team-lineup__player-number')
        player_names = players[0].find_all('span', class_='sdc-site-team-lineup__player-surname')

        for number, name in zip(player_numbers, player_names):
            player_info = {
                'number': number.text.strip(),
                'name': name.text.strip()
            }
            if column == team_columns[0]:
                home_players.append(player_info)
            else:
                away_players.append(player_info)

    match_players = [{'number': -1, 'name': ''}] + home_players + [{'number': -2, 'name': ''}] + away_players

    return match_players
