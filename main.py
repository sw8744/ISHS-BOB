import os
import requests
from instagrapi import Client
from instagrapi.story import Path
from dotenv import load_dotenv
import json
import datetime
from PIL import Image, ImageDraw, ImageFont
import random
import time

def load_bob(date: datetime.datetime):
    date_time = date.strftime("%Y%m%d")
    print(date_time)
    try:
        if date.weekday() == 5 or date.weekday() == 6:
            return
        load_dotenv()
        res = requests.get(
            "https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=7c8f58d4e4174b94b96b1aea5fb6fd0d&type=json&&ATPT_OFCDC_SC_CODE=E10&SD_SCHUL_CODE=7310058&MLSV_YMD=" + date_time)
        res = json.loads(res.text)["mealServiceDietInfo"][1]["row"]
        changeName = {
            "조식": "아침",
            "중식": "점심",
            "석식": "저녁"
        }
        meal = []
        for i in res:
            meal.append([changeName[i["MMEAL_SC_NM"]]] + i["DDISH_NM"].split("<br/>"))
        print(meal)
        # 이미지 크기 설정
        width, height = 1080, 1920

        # 배경색과 텍스트 색상 설정
        background_color = (0, 0, 0)
        text_color = (255, 255, 255)

        # 이미지 생성
        image = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(image)

        # 폰트 설정
        font_size = 40
        title_font = ImageFont.truetype('SpoqaHanSansNeo-Bold.ttf', 70)
        time_font = ImageFont.truetype('SpoqaHanSansNeo-Medium.ttf', font_size)
        content_font = ImageFont.truetype('SpoqaHanSansNeo-Regular.ttf', font_size)

        # 텍스트 위치 설정
        title = "[ 오늘의 급식 ]"
        _, _, text_width, text_height = title_font.getbbox(title)
        x = (width - text_width) // 2
        y = 50
        draw.text((x, y), title, font=title_font, fill=text_color)

        for i in range(len(meal)):
            for j in range(len(meal[i])):
                text = meal[i][j]
                x = 75
                y = 200 + 450 * i + 50 * j
                if j == 0:
                    _, _, text_width, text_height = time_font.getbbox(text)
                    draw.text((x, y), text, font=time_font, fill=text_color)
                else:
                    _, _, text_width, text_height = content_font.getbbox(text)
                    draw.text((x, y), text, font=content_font, fill=text_color)
        image.save('img/' + date_time + '.png')
        print("Image saved")
    except Exception as e:
        print(e)

def upload(date: datetime.datetime):
    load_dotenv()
    date_time = date.strftime("%Y%m%d")
    try:
        if date.weekday() == 5 or date.weekday() == 6:
            return
        cl = Client()
        cl.login(os.environ.get("INSTAGRAM_ID"), os.environ.get("INSTAGRAM_PW"))
        print("Login success")
        time.sleep(random.random() * 10)
        file_path = './img/' + date_time + '.png'
        path = Path(file_path)
        cl.photo_upload_to_story(path)
        print("Upload success")
        cl.logout()
    except Exception as e:
        print(e)

def make_bob(timedelta=1):
    print("Schedule start")
    datetime_f = datetime.datetime.now() + datetime.timedelta(days=timedelta)
    load_bob(datetime_f)
    upload(datetime_f)
    print("Schedule end")
    time.sleep(60)

if __name__ == "__main__":
    while True:
        if datetime.datetime.now().hour == 23 and datetime.datetime.now().minute == 30:
            make_bob()
        else:
            continue
        time.sleep(1)