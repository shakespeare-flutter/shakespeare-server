import pandas as pd
import numpy as np
import json
import enum
import time
#from multiprocessing.pool import ThreadPool

class HEADER(enum.IntEnum):
    FILE = 0
    ENG = 1
    KOR = 2
    GENRE = 3
    TEMPO = 4
    MOOD = 5
    INSTRUMENT = 6

MUSIC = pd.read_csv('music.csv', header=0, index_col=0)
COUNT = len(MUSIC.index)
RELAVANCE = pd.read_csv('relavance.csv', header=0, index_col=0)

TAGS = pd.read_csv('tags.csv', header=0)
GENRE = [str(i) for i in TAGS[HEADER.GENRE.name] if i is not np.nan]
TEMPO = [str(i) for i in TAGS[HEADER.TEMPO.name] if i is not np.nan]
MOOD = [str(i) for i in TAGS[HEADER.MOOD.name] if i is not np.nan]
INST = [str(i) for i in TAGS[HEADER.INSTRUMENT.name] if i is not np.nan]

WEIGHT = json.load(open('weight.json', encoding="UTF-8"))

def get_music(emotion:dict, color, weather, test = False)->str:
    df = RELAVANCE[list(emotion.keys())].multiply(emotion.values()).sum(axis=1)
    gnr = df[GENRE] * WEIGHT[HEADER.GENRE.name]
    tmp = df[TEMPO] * WEIGHT[HEADER.TEMPO.name]
    mud = df[MOOD] * WEIGHT[HEADER.MOOD.name]
    inst = df[INST] * WEIGHT[HEADER.INSTRUMENT.name]

    def get_value(series:pd.Series)->float:
        return gnr[series[HEADER.GENRE.value]] + tmp[series[HEADER.TEMPO.value]] + mud[series[HEADER.MOOD.value]] + np.average([inst[tag] for tag in series[HEADER.INSTRUMENT.value].split('+')])
    
    if test:
        temp = MUSIC.copy()
        temp.insert(3, 'score', [get_value(series) for series in MUSIC.values])
        temp = temp.sort_values('score', ascending=False)
        return temp

    result = None
    max = 0
    for idx, series in MUSIC.iterrows():
        value = get_value(series)
        if value > max:
            max = value
            result = idx

    #print(' / '.join(MUSIC.iloc[result][HEADER.KOR.value:]))
    return str(result)

def get_musics(emotions:list, colors:list, weather:list):
    start_time = time.time()
    print('Music Recommend...')

    # pool = ThreadPool(4)
    # musics = pool.starmap(get_music, zip(emotions, colors, weather))
    # pool.close()
    # pool.join()
    musics = [get_music(e, None, None) for e in emotions]

    print('Done!...', (time.time() - start_time), 'sec')
    return musics

def get_path(index:int):
    index = int(index)
    if index >= COUNT:
        return None
    return MUSIC.iloc[index][HEADER.FILE.value]

def get_info(index:int):
    index = int(index)
    if index >= COUNT:
        return None
    srz = MUSIC.iloc[index]
    return {
        HEADER.ENG.name:srz[HEADER.ENG.value],
        HEADER.KOR.name:srz[HEADER.KOR.value],
        HEADER.GENRE.name:srz[HEADER.GENRE.value],
        HEADER.TEMPO.name:srz[HEADER.TEMPO.value],
        HEADER.MOOD.name:srz[HEADER.MOOD.value],
        HEADER.INSTRUMENT.name:srz[HEADER.INSTRUMENT.value],
        }