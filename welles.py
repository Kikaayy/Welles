import speech_recognition as sr
import datetime
import requests
from googletrans import Translator
import spotipy
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import os
from spotipy.oauth2 import SpotifyOAuth
from credentials import CLIENT_SECRET, CLIENT_ID

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                        client_secret=CLIENT_SECRET,
                                                        redirect_uri="https://google.com",
                                                        scope='user-modify-playback-state user-read-currently-playing'))
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


def play_track(sp, track_name):
    results = sp.search(q=track_name, type="track", limit=1)
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        print(f"Lecture de la piste : {track_name}")
    else:
        print(f"Piste non trouvée : {track_name}")

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

def get_date():
    now = datetime.datetime.now()
    return now.strftime("%d/%m/%Y")

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

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
