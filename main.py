import os
import requests
from instagrapi import Client
from dotenv import load_dotenv
import json

def load_bob():
    load_dotenv()
    res = requests.get("https://open.neis.go.kr/hub/mealServiceDietInfo?KEY=" + os.environ.get("NEIS_KEY") + "&type=json&&ATPT_OFCDC_SC_CODE=E10&SD_SCHUL_CODE=7310058&MLSV_YMD=20240627")
    res = json.loads(res.text)["mealServiceDietInfo"][1]["row"]
    meal = []
    for i in res:
        meal.append(i["DDISH_NM"].split("<br/>"))
    # print(meal)




if __name__ == "__main__":
    load_dotenv()
    load_bob()
    cl = Client()
    cl.login(os.environ.get("INSTAGRAM_ID"), os.environ.get("INSTAGRAM_PW"))
    print("Login success")

