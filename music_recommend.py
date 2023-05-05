from models import Music
import random
import time

def get_music(emotion, color, weather)->str:
    print('... music recommendation ...\nemotion: {e}\ncolor: {c}\nweather: {w}'.format(e=emotion, c=color, w=weather))
    time.sleep(0.5)
    return str(random.randint(1, 4))