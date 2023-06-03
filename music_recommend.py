import pandas as pd
import numpy as np
import json
import enum
import time
from multiprocessing.pool import ThreadPool
from numpy.linalg import norm

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
WEIGHT = json.load(open('weight.json', encoding="UTF-8"))

MINIMUM_PLAY_SECONDS = 10
AVAERAGE_CHARACTER_PER_SECONDS = 18
MINIMUM_LENGTH = MINIMUM_PLAY_SECONDS * AVAERAGE_CHARACTER_PER_SECONDS

TAGS = pd.read_csv('tags.csv', header=0)
# GENRE = [str(i) for i in TAGS[HEADER.GENRE.name] if i is not np.nan]
# TEMPO = [str(i) for i in TAGS[HEADER.TEMPO.name] if i is not np.nan]
# MOOD = [str(i) for i in TAGS[HEADER.MOOD.name] if i is not np.nan]
# INST = [str(i) for i in TAGS[HEADER.INSTRUMENT.name] if i is not np.nan]

def get_normalized_dataframe(keys:list):
    df = RELAVANCE.loc[keys]
    return df# / norm(df, axis=1, keepdims=True)

GENRE = get_normalized_dataframe([str(i) for i in TAGS[HEADER.GENRE.name] if i is not np.nan]) # * WEIGHT[HEADER.GENRE.name]
TEMPO = get_normalized_dataframe([str(i) for i in TAGS[HEADER.TEMPO.name] if i is not np.nan]) #* WEIGHT[HEADER.TEMPO.name]
MOOD = get_normalized_dataframe([str(i) for i in TAGS[HEADER.MOOD.name] if i is not np.nan]) #* WEIGHT[HEADER.MOOD.name]
INST = get_normalized_dataframe([str(i) for i in TAGS[HEADER.INSTRUMENT.name] if i is not np.nan]) #* WEIGHT[HEADER.INSTRUMENT.name]

def get_music(emotion:dict, color, weather, test = False)->str:
    #df = RELAVANCE[list(emotion.keys())].multiply().sum(axis=1)
    keys = list(emotion.keys())
    values = list(emotion.values())
    #values = values / norm(values)

    gnr = (GENRE[keys] * values).sum(axis=1)
    tmp = (TEMPO[keys] * values).sum(axis=1)
    mud = (MOOD[keys] * values).sum(axis=1)
    inst = (INST[keys] * values).sum(axis=1)

    def get_value(series:np.array)->float:
        return gnr[series[HEADER.GENRE.value]] + tmp[series[HEADER.TEMPO.value]] + mud[series[HEADER.MOOD.value]] + np.average([inst[tag] for tag in series[HEADER.INSTRUMENT.value].split('+')])
    
    if test:
        temp = MUSIC.copy()
        temp.insert(3, 'score', [get_value(series) for series in MUSIC.values])
        temp = temp.sort_values('score', ascending=True)
        return temp

    result = None
    max = 0
    for idx, series in MUSIC.iterrows():
        value = get_value(series)
        if value > max:
            max = value
            result = idx

    #print(' / '.join(MUSIC.iloc[result][HEADER.KOR.value:]))
    return str(result) if not result is None else ''

def get_musics(emotion, length):
    print('Music Recommending...')
    start_time = time.time()
    result = [get_music(e, None, None) for e in emotion]
    result = [l if l == r else m for m, l, r in zip(result, np.roll(result, -1), np.roll(result, 1))]
    last_index = 0
    current_music = result[0]
    current_length = length[0]
    for i, (m, l) in enumerate(zip(result[1:], length[1:]), 1):
        if current_music == m:
            current_length += l
        else:
            if current_length < MINIMUM_LENGTH:
                result[last_index:i] = [''] * (i - last_index)
            #print(last_index, '~', i-1, ':', current_music, current_length)
            current_music = m
            current_length = l
            last_index = i
    if current_length < MINIMUM_LENGTH:
        result[last_index:] = [''] * (len(result) - last_index)
    #print(last_index, '~', len(result) - 1, ':', current_music, current_length)
    print('SECONDS........', (time.time() - start_time))
    return result

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