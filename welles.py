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
from spotipy.oauth2 import SpotifyOAuth
import re
from fuzzywuzzy import fuzz
from credentials import CLIENT_SECRET, CLIENT_ID

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

            # Retourner les deux premières phrases
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
        # Get the current user's currently playing track
        current_track = sp.current_playback()
        
        if current_track is not None and 'item' in current_track and 'name' in current_track['item']:
            track_name = clean_track_name(current_track['item']['name'])
            artist_name = current_track['item']['artists'][0]['name'] if 'artists' in current_track['item'] and current_track['item']['artists'] else 'Unknown Artist'
            album_name = current_track['item']['album']['name'] if 'album' in current_track['item'] else 'Unknown Album'
            
            # Get featurings (if available)
            featuring_artists = ', '.join([artist['name'] for artist in current_track['item']['artists'][1:]]) if len(current_track['item']['artists']) > 1 else None

            # Build the output string
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

def next_track(sp):
    sp.next_track()
    print("Piste suivante")

def previous_track(sp):
    sp.previous_track()
    print("Piste précédente")

def blind_test(playlist_name,goal):
    # Search for the playlist by name
    goal = int(goal)
    playlists = sp.search(q=playlist_name, type='playlist')

    if len(playlists['playlists']['items']) == 0:
        print(f"No playlist found with the name '{playlist_name}'. Exiting.")
        return

    playlist_id = playlists['playlists']['items'][0]['id']

    # Get the track list from the specified playlist
    playlist_tracks = sp.playlist_tracks(playlist_id)
    
    # Shuffle the playlist
    sp.shuffle(True)

    # Start playback
    try:
        sp.start_playback(context_uri=f'spotify:playlist:{playlist_id}')
    except spotipy.SpotifyException as e:
        print(f"Error starting playback: {e}")
        return

    # Initialize variables
    wrong_count = 0
    right_count = 0
    
    while right_count < goal:
        wrong_count = 0
        sp.next_track()
        time.sleep(3)
        current_track = sp.current_playback()

        while wrong_count < 3:
            if current_track is not None and 'item' in current_track and 'name' in current_track['item']:
                # Clean the song name
                clean_current_track_name = clean_track_name(current_track['item']['name'])

                guessed_song = input("Réponse: ")

                # Clean the guessed song name
                clean_guessed_song = clean_track_name(guessed_song.lower())

                # Use fuzzy string matching to check similarity
                similarity_ratio = fuzz.ratio(clean_guessed_song, clean_current_track_name.lower())

                if similarity_ratio >= 80:  # Adjust the threshold as needed
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
                    # Skip to the next track
                    break

    print("Fini !")

def clean_track_name(song_name):
    # Remove anything after " (" in the song name
    return song_name.split(" (")[0]

#DATE AND TIME

def get_date():
    now = datetime.datetime.now()
    return now.strftime("%d/%m/%Y")

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

#WEATHER

def get_weather(city="Paris"):
    api_key = "372a91e6dc52dda810f63d3392deefc7"  # Remplacez cela par votre clé API Weatherstack
    base_url = f"http://api.weatherstack.com/current?access_key={api_key}&query={city}"
    
    response = requests.get(base_url)
    data = response.json()

    if "error" in data:
        return "Ville non trouvée"
    else:
        temperature = data["current"]["temperature"]
        description = data["current"]["weather_descriptions"][0]

        translator = Translator()
        translated_description = translator.translate(description, src="en", dest="fr").text
        print(translated_description)

        return f"La température à {city} est actuellement {temperature}°C. Conditions météorologiques : {translated_description}"
    

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
                x = datetime.datetime.now().weekday()
                if x==0:
                    x="Lundi"
                elif x==1:
                    x="Mardi"
                elif x==2:
                    x="Mercredi"
                elif x==3:
                    x="Jeudi"
                elif x==4:
                    x="Vendredi"
                elif x==5:
                    x="Samedi"
                elif x==6:
                    x="Dimanche"
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
            elif any(word in command for word in ["list", "liste"]):
                print("Voici votre To Do list")
                view_todo_list()
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
                query = command.capitalize()  # Utiliser le mot clé pour commencer la requête
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
