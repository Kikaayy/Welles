import speech_recognition as sr
import datetime
import requests
from googletrans import Translator
import spotipy
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import os
import time
import random
import json
from spotipy.oauth2 import SpotifyOAuth
from fuzzywuzzy import fuzz
import webbrowser
from credentials import CLIENT_SECRET, CLIENT_ID, WEATHER_API, FOOTBALL, LOL
from riotwatcher import LolWatcher, ApiError


#TODO LIST
TODO_FILE = "todolist.txt"

def add_task_to_todo_list(task):
    with open(TODO_FILE, "a") as file:
        file.write(f"- {task}\n")
    print(f"Tâche ajoutée à la liste : {task}")

def view_todo_list():
    with open(TODO_FILE, "r") as file:
        todolist_content = file.read()
        print(todolist_content)

def delete_task_from_todo_list(task):
    with open(TODO_FILE, "r") as file:
        lines = file.readlines()

    with open(TODO_FILE, "w") as file:
        for line in lines:
            if line.strip() != f"- {task}":
                file.write(line)
    
    print(f"Tâche supprimée de la liste : {task}")


#GOOGLE SEARCH

def google_search(query):
    try:
        print("Recherche Google en cours...")
        for j in search(query, num=1, stop=1, pause=2, safe="off", user_agent="Mozilla/5.0"):
            page_url = j
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')

            if len(paragraphs) >= 3:
                result = paragraphs[0].text + ' ' + paragraphs[1].text
            else:
                result = ' '.join([p.text for p in paragraphs])

            return result
    except Exception as e:
        print(f"Erreur lors de la recherche Google : {e}")
        return "Erreur lors de la recherche Google."
    
#RANDOM

def pileouface():
    result = random.choice(["Pile", "Face"])
    return result

def choose_random(input_list):
    return random.choice(input_list)

#SPOTIPY

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                        client_secret=CLIENT_SECRET,
                                                        redirect_uri="https://google.com",
                                                        scope='user-modify-playback-state user-read-currently-playing'))

def play_track(sp, track_name):
    results = sp.search(q=track_name, type="track", limit=1)
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        print(f"Lecture de la piste : {track_name}")
    else:
        print(f"Piste non trouvée : {track_name}")

def titremusique():
        current_track = sp.current_playback()
        
        if current_track is not None and 'item' in current_track and 'name' in current_track['item']:
            track_name = clean_track_name(current_track['item']['name'])
            artist_name = current_track['item']['artists'][0]['name'] if 'artists' in current_track['item'] and current_track['item']['artists'] else 'Unknown Artist'
            album_name = current_track['item']['album']['name'] if 'album' in current_track['item'] else 'Unknown Album'
            
            featuring_artists = ', '.join([artist['name'] for artist in current_track['item']['artists'][1:]]) if len(current_track['item']['artists']) > 1 else None

            output_string = f"La chanson actuelle est {track_name} par {artist_name} sur l'album {album_name}"

            if featuring_artists:
                output_string += f" avec {featuring_artists}"

            return output_string
        else:
            return "No track currently playing."

def pause_playback(sp):
    sp.pause_playback()
    print("Lecture en pause")

def resume_playback(sp):
    sp.start_playback()
    print("Reprise de la lecture")

def get_volume(sp):
    volume = sp.current_playback()
    return volume['device']['volume_percent']

def next_track(sp):
    sp.next_track()
    print("Piste suivante")

def previous_track(sp):
    sp.previous_track()
    print("Piste précédente")

def blind_test(playlist_name,goal):
    goal = int(goal)
    playlists = sp.search(q=playlist_name, type='playlist')

    if len(playlists['playlists']['items']) == 0:
        print(f"No playlist found with the name '{playlist_name}'. Exiting.")
        return

    playlist_id = playlists['playlists']['items'][0]['id']
    
    sp.shuffle(True)

    try:
        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
    except spotipy.SpotifyException as e:
        print(f"Error starting playback: {e}")
        return

    wrong_count = 0
    right_count = 0
    
    while right_count < goal:
        wrong_count = 0
        sp.next_track()
        time.sleep(3)
        current_track = sp.current_playback()

        while wrong_count < 3:
            if current_track is not None and 'item' in current_track and 'name' in current_track['item']:
                clean_current_track_name = clean_track_name(current_track['item']['name'])

                guessed_song = input("Réponse: ")

                clean_guessed_song = clean_track_name(guessed_song.lower())

                similarity_ratio = fuzz.ratio(clean_guessed_song, clean_current_track_name.lower())

                if similarity_ratio >= 80:  
                    print("Correct!\n")
                    right_count += 1
                    break
                else:
                    print(f"Faux !")
                    wrong_count += 1

                if wrong_count == 3:
                    print("Perdu ! La bonne réponse était:", clean_current_track_name,
                          "par", current_track['item']['artists'][0]['name'])
                    wrong_count = 0
                    break

    print("Fini !")

def clean_track_name(song_name):
    return song_name.split(" (")[0]

def radioassocie():
    current_playback = sp.current_playback()
    GOOOOO = "Radio "+ current_playback['item']['name'] + " " + current_playback['item']['artists'][0]['name']
    print(GOOOOO)
    playlis_play(GOOOOO)


def playlis_play(playlist_name):
    playlists = sp.search(q=playlist_name, type='playlist')

    if len(playlists['playlists']['items']) == 0:
        print(f"No playlist found with the name '{playlist_name}'. Exiting.")
        return

    playlist_id = playlists['playlists']['items'][0]['id']
    
    sp.shuffle(True)
    try:
        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
    except spotipy.SpotifyException as e:
        print(f"Error starting playback: {e}")
        return

#DATE AND TIME

def get_date():
    now = datetime.datetime.now()
    return now.strftime("%d/%m/%Y")

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

#FOOTBALL

def classement(comp):
    url = f"https://api.football-data.org/v4/competitions/{comp}/standings"
    headers = {'X-Auth-Token': FOOTBALL}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        retour = parse_standings(response.json())  
        i = 0
        while i < len(retour):
            print(retour[i],"\t",retour[i+1],"\t","\t","\t",retour[i+2])
            i = i + 3
    else:
        print(f"Erreur lors de la requête : {response.status_code}")
        print(response.text)
        return None

def parse_standings(json_data):
    teams_info = []

    for team_data in json_data['standings'][0]['table']:
        position = team_data['position']
        team_name = team_data['team']['name']
        points = team_data['points']

        teams_info.append(position)
        teams_info.append(team_name)
        teams_info.append(points)

    return teams_info
    
def football(team_name):
    api_key = FOOTBALL
    base_url = 'https://api.football-data.org/v4/'
    teams_url = f'{base_url}teams'
    teams_response = requests.get(teams_url, headers={'X-Auth-Token': api_key})
    teams_data = teams_response.json()

    team_id = None
    for team in teams_data['teams']:
        if team['name'] == team_name:
            team_id = team['id']
            break

    if team_id is None:
        print(f"L'équipe {team_name} n'a pas été trouvée.")
    else:
        standings_url = f'{base_url}competitions/FL1/standings'
        standings_response = requests.get(standings_url, headers={'X-Auth-Token': api_key})
        standings_data = standings_response.json()

        for standing in standings_data['standings'][0]['table']:
            if standing['team']['id'] == team_id:
                position = standing['position']
                print(f"Classement de {team_name}: {position}")

        fixtures_url = f'{base_url}teams/{team_id}/matches'
        fixtures_response = requests.get(fixtures_url, headers={'X-Auth-Token': api_key})
        fixtures_data = fixtures_response.json()

        for fixture in fixtures_data['matches']:
            if fixture['status'] == 'SCHEDULED':
                date = fixture['utcDate']
                opponent = fixture['homeTeam']['name'] if fixture['awayTeam']['id'] == team_id else fixture['awayTeam']['name']
                print(f"Prochain match de {team_name} le {date} contre {opponent}")
                break

#League of Legends

lol_watcher = LolWatcher(LOL)

def get_summoner_id(summoner_name):
    me = lol_watcher.summoner.by_name("euw1", summoner_name)

    my_ranked_stats = lol_watcher.league.by_summoner("euw1", me['id'])
    tier = my_ranked_stats[0]['tier']
    rank = my_ranked_stats[0]['rank']
    return f'Rank : {tier} {rank}'


def get_current_game(summoner_name):
    summoner = lol_watcher.summoner.by_name("euw1", summoner_name)
    summoner_id = summoner['id']
    try:
        headers = {'X-Riot-Token': LOL}
        response = requests.get(f"https://euw1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if response.status_code == 400 and "Exception decrypting" in response.text:
            print("Erreur de déchiffrement. Quitter le programme.")
            quit()
        else:
            print(f"Le joueur n'est pas dans une partie")
            return
    current_game = lol_watcher.spectator.by_summoner("euw1", summoner_id)
    print(summoner_name," est actuellement dans",current_game["gameType"],"depuis",(current_game["gameLength"]//60)+4, "minutes")
    team_id = 0
    for nom in current_game["participants"]:
        if nom["summonerName"] == summoner_name:
            team_id = nom["teamId"]
    target_team_id = []
    for nom in current_game["participants"]:
        if nom["teamId"] == team_id and nom["summonerName"]!=summoner_name:
            target_team_id.append(nom["summonerName"])
    print(f"{summoner_name} joue avec {target_team_id}")

#WEATHER

def get_weather(city):
    api_key = WEATHER_API 
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=fr"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        temperature_celsius = data['current']['temp_c']
        condition = data['current']['condition']['text']

        return f'Température : {temperature_celsius}°C, Condition météorologique : {condition}'
    else:
        print(f"Erreur de requête HTTP. Statut : {response.status_code}")
        return None

def previsions(city):
    api_key = WEATHER_API 
    url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city}&lang=fr&days=3"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        temperature_celsius = data["forecast"]["forecastday"][0]["day"]['avgtemp_c']
        max_temperature = data["forecast"]["forecastday"][0]["day"]['maxtemp_c']
        pluiepourcent = data["forecast"]["forecastday"][0]["day"]['daily_chance_of_rain']
        condition = data["forecast"]["forecastday"][0]["day"]["condition"]["text"]

        return f'Température moyenne : {temperature_celsius}°C, avec un pic à {max_temperature}°C Condition météorologique : {condition} avec {pluiepourcent}% de chance de pluie'
    else:
        print(f"Erreur de requête HTTP. Statut : {response.status_code}")
        return None
    

#MAIN

def assistant_vocal():
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                print("Dites quelque chose...")
                audio = recognizer.listen(source, timeout=5)
                print("Enregistrement terminé. Analyse en cours...")

            command = recognizer.recognize_google(audio, language="fr-FR")
            print("Vous avez dit: {}".format(command))

            if any(word in command for word in ["stop", "quitter", "au revoir"]):
                print("Au revoir!")
                break
            elif "bonjour" in command:
                print("Bonjour! Comment puis-je vous aider?")
            elif any(word in command for word in ["date", "jour"]):
                translator=Translator()
                x = translator.translate(datetime.datetime.now().strftime('%A'), dest='fr').text
                print("Nous sommes le", x, "{}".format(datetime.datetime.now().strftime('%d-%m-%y')))
            elif "pile ou face" in command:
                print(pileouface())
            elif "choisis un nombre" in command:
                number = int(input("Choisissez le max : "))
                if number <= 1:
                    print("Le nombre doit être supérieur à 1.")
                    continue
                print(random.randint(1, int(number)))
            elif "choisis entre" in command:
                input_list = []
                while True:
                    user_input = input("Entrez les choix (or appuyer sur Entrée pour finir): ")
                    if user_input == "":
                        break
                    input_list.append(user_input)
                print(choose_random(input_list))
            elif "heure" in command:
                print("Il est actuellement {}".format(get_time()))
            elif "supprime la tâche" in command:
                task = input("Quelle tâche voulez-vous supprimer de la liste? : ")
                delete_task_from_todo_list(task)
            elif "supprime tout" in command:
                with open(TODO_FILE, "w") as file:
                    file.write("")
                print("Toutes les tâches ont été supprimées de la liste.")
            elif "tâche" in command:
                task = input("Quelle tâche voulez-vous ajouter à la liste? : ")
                add_task_to_todo_list(task)
            elif any(word in command for word in [" list", " liste"]):
                print("Voici votre To Do list")
                view_todo_list()
            elif "football" in command:
                print("Veuillez préciser l'équipe.")
                team_name = input("Équipe : ")
                football(team_name)
            elif "classement" in command:
                print("Veuillez préciser la compétition.")
                comp = input("Compétition : ")
                print(classement(comp))
            elif any(word in command for word in ["legend","légende","Legends"]):
                print("Veuillez préciser le nom")
                name = input("nom : ")
                if name == "moi":
                    name = "MarkíngYourAss"
                get_current_game(name)    
            elif any(word in command for word in ["LP","rank","rang"]):
                print("Veuillez préciser le nom")
                name = input("nom : ")
                if name == "moi":
                    name = "MarkíngYourAss"
                print(get_summoner_id(name))        
            elif any(word in command for word in ["prévision","prévisions"]):
                print("Veuillez préciser la ville.")
                ville = input("Ville : ")
                print(previsions(ville))
            elif "météo" in command:
                print("Veuillez préciser la ville.")
                ville = input("Ville : ")
                print(get_weather(ville))
            elif "ton nom" in command:
                print("Je m'appelle Welles tout comme Orson Welles le célèbre écrivain où le personnage de Cyberpunk 2077 Jackie Welles.")
                play_track(sp, track_name)
            elif "blind test" in command:
                print("Lancement du blind test...")
                playlist_name = input("Blind Test sur quoi ? ")
                goal = input("En combien de points ?")
                blind_test(playlist_name, goal)
            elif "playlist" in command:
                print("Lancement de la playlist...")
                playlist_name = input("Quelle playlist voulez-vous lancer ? ")
                playlis_play(playlist_name)
            elif any(word in command for word in ["radio", "similaire"]):
                print("Lancement de titre associés")
                radioassocie()
            elif "volume" in command:
                volume = int(input("Combien ? (en pourcentages) : "))
                sp.volume(volume)
            elif "plus fort" in command:
                volume = get_volume(sp)
                sp.volume(volume + 20)
            elif "moins fort" in command:
                volume = get_volume(sp)
                sp.volume(volume - 20)
            elif "pause" in command:
                pause_playback(sp)
            elif "remet" in command:
                resume_playback(sp)
            elif "reprise" in command:
                resume_playback(sp)
            elif "suivante" in command:
                next_track(sp)
            elif "précédente" in command:
                previous_track(sp)
            elif "chanson" in command:
                print(titremusique())
            elif any(word in command for word in ["lance", "mets"]):
                track_name = input("Quelle chanson voulez-vous écouter? : ")
            elif any(word in command for word in ["quoi", "qui", "où", "quel", "quelle", "comment", "que"]):
                query = command.capitalize() 
                result = google_search(query)
                print(f"Résultat de la recherche Google : {result}")



            else:
                print("Désolé, je ne comprends pas cette commande.")

        except sr.UnknownValueError:
            print("Impossible de comprendre la parole. Veuillez réessayer.")
        except sr.RequestError as e:
            print("Erreur lors de la demande de reconnaissance vocale; {0}".format(e))

if __name__ == "__main__":
    assistant_vocal()
