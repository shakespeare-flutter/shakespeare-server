import os
import openai

openai.api_key = os.environ.get('SECRET_KEY')

### test text
text="People were screaming in the darkness, some crying and some praying. The snowflake shined under sunlight.\n\n###\n\n"

def getEmotionFromGPT(text):
    response = openai.Completion.create(
        model="ada:ft-personal-2023-05-20-19-22-18",
        prompt=text + "\n\n###\n\n",
        temperature=0,
        max_tokens=1,
        top_p=1.0,
        frequency_penalty=0.0,
        logprobs=5,
        presence_penalty=0.0
    )
    result=response["choices"][0]["text"].strip()
    
    return result

def getLogProbEmotionFromGPT(text):
    response = openai.Completion.create(
        model="ada:ft-personal-2023-05-20-19-22-18",
        prompt=text + "\n\n###\n\n",
        temperature=0,
        max_tokens=1,
        top_p=1.0,
        frequency_penalty=0.0,
        logprobs=5,
        presence_penalty=0.0
    )
    result=response["choices"][0]["logprobs"]["top_logprobs"]
    
    return result


def getWeatherFromGPT(text):
    response = openai.Completion.create(
        model="ada:ft-personal-2023-05-04-14-32-30",
        prompt= text + "\n\n###\n\n",
        temperature=0,
        max_tokens=1,
        top_p=1.0,
        frequency_penalty=0.0,
        logprobs=3,
        presence_penalty=0.0
    )
    result=response["choices"][0]["text"].strip()
    
    return result


def getColorFromGPT(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Please answer only the main color code that you can feel in the text. the answer should be in color code like #ddddff.\n\nSentence: "+text+"\n\n###\n\n",
        temperature=0.7,
        max_tokens=20,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    result=response["choices"][0]["text"].strip()
    return result