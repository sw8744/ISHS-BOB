import datetime
import json
import os
import random
import re
import time

import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from instagrapi import Client
from instagrapi.story import Path


def slack_noti(payload):
  slack_key = os.environ.get('SLACK_KEY')
  url = "https://hooks.slack.com/services/" + slack_key
  r = requests.post(
    url,
    headers={
      "Content-Type": "application/json"
    },
    json=payload
  )


def load_bob(date: datetime.datetime):
  date_time = date.strftime("%Y%m%d")

  try:
    if date.weekday() == 5 or date.weekday() == 6:
      return
    load_dotenv()
    NEIS_KEY = os.environ.get("NEIS_KEY")
    res = requests.get(
      f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={NEIS_KEY}&type=json&&ATPT_OFCDC_SC_CODE=E10&SD_SCHUL_CODE=7310058&MLSV_YMD=" + date_time)
    res = json.loads(res.text)["mealServiceDietInfo"][1]["row"]
    changeName = {
      "조식": "아침",
      "중식": "점심",
      "석식": "저녁"
    }
    meal = []
    for i in res:
      meal.append([changeName[i["MMEAL_SC_NM"]]] + i["DDISH_NM"].split("<br/>"))
    # 이미지 크기 설정
    width, height = 1080, 1920

    # 배경색과 텍스트 색상 설정
    background_color = (10, 10, 10)
    text_color = (250, 250, 250)

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
    y = 100
    draw.text((x, y), title, font=title_font, fill=text_color)

    for i in range(len(meal)):
      for j in range(len(meal[i])):
        text = meal[i][j]
        y = 250 + 500 * i + 60 * j
        if j == 0:
          _, _, text_width, text_height = draw.textbbox((0, 0), text, font=time_font)
          draw.text(((width - text_width) / 2, y), text, font=time_font, fill=text_color)

        else:
          cut_text = re.sub(r"\((\d*.)*\d*\)", "", text)
          cut_text = cut_text.strip()
          if cut_text.endswith('.'):
            cut_text = cut_text[:-1]

          _, _, text_width, text_height = draw.textbbox((0, 0), cut_text, font=content_font)
          draw.text(((width - text_width) / 2, y), cut_text, font=content_font, fill=text_color)
    image.save('imgs/' + date_time + '.png')
  except Exception as e:
    print(e)


def upload(date: datetime.datetime):
  load_dotenv()
  date_time = date.strftime("%Y%m%d")
  try:
    if date.weekday() == 5 or date.weekday() == 6:
      return

    cl = Client()
    totp = os.environ.get("TOTP_CODE")

    if os.path.isfile("session.json"):
      cl.load_settings("session.json")

    vcode = cl.totp_generate_code(totp)
    cl.login(os.environ.get("INSTAGRAM_ID"), os.environ.get("INSTAGRAM_PW"), verification_code=vcode)

    time.sleep(random.random() * 10)
    file_path = './imgs/' + date_time + '.png'
    path = Path(file_path)
    cl.photo_upload_to_story(path)

    slack_noti({
      "blocks": [
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "🍣 급식 업로드 완료 ✅"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": f"*{date_time}의 급식을 업로드했습니다.*"
          }
        }
      ]
    })
  except Exception as e:
    slack_noti({
      "blocks": [
        {
          "type": "header",
          "text": {
            "type": "plain_text",
            "text": "⚠️ 급식 자동 업로드 실패 ⚠️"
          }
        },
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": f"*{date_time}의 급식을 업로드하지 못했습니다.*"
          }
        },
        {
          "type": "context",
          "elements": [
            {
              "type": "mrkdwn",
              "text": f"Exception:\n{e}"
            }
          ]
        }
      ]
    })


def make_bob(timedelta=1):
  datetime_f = datetime.datetime.now() + datetime.timedelta(days=timedelta)
  load_bob(datetime_f)
  upload(datetime_f)


if __name__ == "__main__":
  make_bob()
