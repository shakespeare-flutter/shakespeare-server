# shakespeare-server
 
## 1. 패키지
 music.zip의 mp3 파일들을 music 폴더에 압축 해제 

    python -m pip install --upgrade pip
    pip install -r requirements.txt

참고: https://wikidocs.net/81041

---
## 2. 실행방법
    http://127.0.0.1:5000/
    flask run --debug                 // 에뮬레이터
    flask run --host=0.0.0.0 --debug  // 외부 접속 허용

---
## 3. 통신예시
### 3-1. 책 검색

    ## 요청 예시    
    GET http://localhost:5000/book?id=identifier-example-0
### 3-1-1. 응답 예시
    HTTP/1.1 200 OK
    Content-Type: application/json
    
    {
        data:
        [
            {
                "start" : "0",
                "end" : "10",
                "emotion":{ "joy":0.2, "excitement":0.5, "gratitude":0.7 },
                "color" : "red",
                "weather" : "rain"
            },
            {
                "start" : "10",
                "end" : "20",
                "emotion":{ "joy":0.2, "excitement":0.5, "gratitude":0.7 },
                "color" : "white",
                "weather" : "cloudy"
            }
        ]        
    }
### 3-1-2. 결과
    200: 성공
    400: 잘못된 요청
    404: 정보 없음 → POST
---
### 3-2. 책 추가
    POST http://localhost:5000/book?id=identifier-example-0
    Content-Type: application/json

    {
        "content" : "content-example:0"
    }
### 3-2-1. 결과
    201: 성공 → GET
    400: 잘못된 요청
---
### 3-3. 음악 검색
    POST http://localhost:5000/music
    Content-Type: application/json

    {
        "start":"0",
        "end":"10",
        "emotion":{ "joy":0.2, "excitement":0.5, "gratitude":0.7 },
        "color":"red",
        "weather":"rain"
    }

### 3-3-1. 응답 예시
    HTTP/1.1 302 FOUND
    Location: /music?id=10
### 3-3-2. 결과
    302: 음악 재생으로 redirect
    400: 잘못된 요청

---
### 3-4. 음악 재생

    GET http://localhost:5000/music?id=1

### 3-4-1. 결과
    → 음악 스트림
    400: 잘못된 요청
    404: 파일 없음
---
### 3-5. 음악 정보

    GET http://localhost:5000/music_info?id=1
### 3-5-1. 응답예시
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
        "ENG": "The Swan(Le Cygne)",
        "KOR": "백조",
        "GENRE": "fast swing",
        "TEMPO": "빠르게",
        "MOOD": "ENERGETIC",
        "INSTRUMENT": "콘트라베이스(CONTRABASS)+피아노(PIANO)+드럼(DRUM)"
    }
### 3-5-2. 결과
    200: 성공
    400: 잘못된 요청
    404: 파일 없음