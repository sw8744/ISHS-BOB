import os
import requests
from instagrapi import Client
from dotenv import load_dotenv
import json
import datetime
from PIL import Image, ImageDraw, ImageFont
import schedule
import random
import time

def load_bob(date: datetime.datetime):
    date_time = datetime.datetime.strptime(date, "%Y%m%d")
    if date_time.weekday() == 5 or date_time.weekday() == 6:
        return
    load_dotenv()
    res = requests.get("https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=" + os.environ.get("NEIS_KEY") + "&type=json&&ATPT_OFCDC_SC_CODE=E10&SD_SCHUL_CODE=7310058&MLSV_YMD=" + date)
    res = json.loads(res.text)["mealServiceDietInfo"][1]["row"]
    meal = []
    for i in res:
        meal.append(i["DDISH_NM"].split("<br/>"))
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
    meal_time = ["< 아침 >", "< 점심 >", "< 저녁 >"]
    date_time = datetime.datetime.strptime(date, "%Y%m%d")
    if date_time.weekday() == 0:
        meal_time = ["< 점심 >", "< 저녁 >"]
    for i in range(len(meal)):
        meal[i] = [meal_time[i]] + meal[i]

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
    image.save('img/' + date + '.png')
    print("Image saved")

def upload(date):
    load_dotenv()
    date_time = datetime.datetime.strptime(date, "%Y%m%d")
    if date_time.weekday() == 5 or date_time.weekday() == 6:
        return
    cl = Client()
    cl.login(os.environ.get("INSTAGRAM_ID"), os.environ.get("INSTAGRAM_PW"))
    print("Login success")
    time.sleep(random.random() * 10)
    cl.photo_upload_to_story('./img/' + date + '.png')
    print("Upload success")
    cl.logout()

def schedule_load_bob():
    load_bob(datetime.datetime.now().strftime("%Y%m%d"))

def schedule_upload():
    upload(datetime.datetime.now().strftime("%Y%m%d"))

if __name__ == "__main__":
    schedule.every().day.at("00:00").do(schedule_load_bob)
    schedule.every().day.at("00:01").do(schedule_upload)
    while True:
        schedule.run_pending()
        time.sleep(1)
