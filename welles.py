import speech_recognition as sr
import datetime
import requests
from googletrans import Translator
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def authenticate_spotify():
    scope = "user-library-read user-modify-playback-state user-read-playback-state"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    return sp

def play_track(sp, track_name):
    results = sp.search(q=track_name, type="track", limit=1)
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        print(f"Lecture de la piste : {track_name}")
    else:
        print(f"Piste non trouvée : {track_name}")

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

def assistant_vocal():
    sp = authenticate_spotify()
    recognizer = sr.Recognizer()

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

            if "bonjour" in command:
                print("Bonjour! Comment puis-je vous aider?")
            elif "date" in command:
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
            elif "météo" in command:
                print("Veuillez préciser la ville.")
                ville = input("Ville : ")
                print(get_weather(ville))
            elif "ton nom" in command:
                print("Je m'appelle Welles tout comme le personnage de Cyberpunk 2077 Jackie Welles.")
            elif "lance" in command:
                track_name = input("Quelle chanson voulez-vous écouter? : ")
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
            elif "quitter" in command:
                print("Au revoir!")
                break
            else:
                print("Désolé, je ne comprends pas cette commande.")

        except sr.UnknownValueError:
            print("Impossible de comprendre la parole. Veuillez réessayer.")
        except sr.RequestError as e:
            print("Erreur lors de la demande de reconnaissance vocale; {0}".format(e))

if __name__ == "__main__":
    assistant_vocal()
