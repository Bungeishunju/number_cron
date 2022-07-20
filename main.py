# coding: UTF-8
import os
from dotenv import load_dotenv
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common import service  # noqa
import csv
from slack import SlackService, Message
import pandas as pd
import chromedriver_binary  # noqa


class CrawlYahoo:
    load_dotenv()
    TEST = os.environ["TEST"]

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--lang=ja-JP")

    if not TEST:
        options.binary_location = "/usr/bin/google-chrome"
    driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(10)
    driver.set_window_size("1200", "1000")

    f_name = "result"
    d_name = "output"
    OUTPUT_FILE = "{}/{}.csv".format(d_name, f_name)

    START_URL = os.environ["START_URL"]
    URL = os.environ["URL"]
    BUSINESS_REALTIME_URL = os.environ["BUSINESS_REALTIME_URL"]
    SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
    SLACK_WEBHOOK_URL_ERROR = os.environ["SLACK_WEBHOOK_URL_ERROR"]
    SLACK_WEBHOOK_URL_ADMIN = os.environ["SLACK_WEBHOOK_URL_ADMIN"]
    THRESHOLD_PV = int(os.environ["THRESHOLD_PV"])
    THRESHOLD_PV2 = int(os.environ["THRESHOLD_PV2"])
    ID = os.environ["ID"]
    PW = os.environ["PW"]
    SLEEP_TIME_SHORT = 3
    SLEEP_TIME_LONG = 10
    SERVICE_NAME = "number"

    # 1回目通知リスト
    SAVE_TEXT = "./save_id_list.txt"
    SAVE_ID_LIST = []
    # 通知しないリスト
    SAVE_TEXT2 = "./save_id_list2.txt"
    SAVE_ID_LIST2 = []
    # 1度通知したが2回目通知対象リスト
    SAVE_TEXT3 = "./save_id_list3.txt"
    SAVE_ID_LIST3 = []

    def __init__(self):
        if not os.path.exists(self.d_name):
            os.makedirs(self.d_name)

        if not os.path.exists(self.SAVE_TEXT):
            open(self.OUTPUT_FILE.format(self.f_name), "a+")

        if os.path.exists(self.SAVE_TEXT):
            with open(self.SAVE_TEXT) as f:
                self.SAVE_ID_LIST = [s.strip() for s in f.readlines()]

        if os.path.exists(self.SAVE_TEXT2):
            with open(self.SAVE_TEXT2) as f:
                self.SAVE_ID_LIST2 = [s.strip() for s in f.readlines()]

        if os.path.exists(self.SAVE_TEXT3):
            with open(self.SAVE_TEXT3) as f:
                self.SAVE_ID_LIST3 = [s.strip() for s in f.readlines()]

    def _login(self, driver):
        print("----- _login ------")
        print(driver.current_url)

        inputFromId = driver.find_element(By.ID, "username")
        inputFromId.send_keys(self.ID)
        sleep(self.SLEEP_TIME_SHORT)

        nextBtn = driver.find_element(By.ID, "btnNext")
        nextBtn.click()
        sleep(self.SLEEP_TIME_SHORT)

        inputFromPw = driver.find_element(By.ID, "passwd")
        inputFromPw.send_keys(self.PW)
        sleep(self.SLEEP_TIME_SHORT)

        loginBtn = driver.find_element(By.ID, "btnSubmit")
        loginBtn.click()
        sleep(self.SLEEP_TIME_SHORT)

        print(driver.current_url)

    def _realtime(self, driver):
        print("----- _realtime ------")
        print(driver.current_url)
        driver.get(self.BUSINESS_REALTIME_URL)
        sleep(self.SLEEP_TIME_LONG)
        print(driver.current_url)

    def _crawl(self, driver):
        print("----- _crawl ------")
        print(driver.current_url)

        html = driver.page_source.encode("utf-8")
        bs = BeautifulSoup(html, "html.parser")
        table = bs.findAll("table", {"class": "realtime"})[0]
        rows = table.findAll("tr")

        with open(self.OUTPUT_FILE, "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            for row in rows:
                csvRow = []
                for cell in row.findAll(["td", "th"]):
                    if len(cell.select(".ng-binding")) > 0:
                        id = cell.select(".ng-binding")[1].string
                        csvRow.append(id)
                        title = "{} (<https://headlines.yahoo.co.jp/article?a={}|{}>)".format(
                            cell.select(".ng-binding")[0].string, id, id
                        )
                        csvRow.append(title)
                    else:
                        pv = cell.get_text()
                        csvRow.append(pv)
                writer.writerow(csvRow)

        print(driver.current_url)

    def _read_csv(self):
        df = pd.read_csv(
            self.OUTPUT_FILE, header=0, names=["no", "id", "title", "pv"], thousands=","
        )
        df = df[["id", "title", "pv"]]

        SlackService.post(
            attachments=Message.info(
                url=self.SLACK_WEBHOOK_URL_ADMIN,
                name="[done] バッチ処理完了(all) \n",
                text="df:{}".format(df),
            )
        )

        df = df[df["pv"] >= self.THRESHOLD_PV].sort_values(
            "pv", ascending=False)
        df = df.reset_index(drop=True)
        cnt = df.title.count()
        saveCnt = 0

        for _, d in df.iterrows():
            if d.id in self.SAVE_ID_LIST:
                continue
            else:
                saveCnt += 1

        SlackService.post(
            attachments=Message.info(
                url=self.SLACK_WEBHOOK_URL_ADMIN,
                name="[done] バッチ処理完了 \n",
                text="""
            1回目通知リスト:\n{}\ncnt:\n{}\nsaveCnt:\n{}\ndf:{}
            """.format(
                    self.SAVE_ID_LIST, cnt, saveCnt, df
                ),
            )
        )

        if cnt > 0 and saveCnt > 0:
            SlackService.post(
                attachments=Message.info(
                    url=self.SLACK_WEBHOOK_URL,
                    name="<!here>",
                    text="""
                :baseball: :basketball: :soccer: 以下の記事がリアルタイムで{}PVを超えました（{}件）:baseball: :basketball: :soccer:
                """.format(
                        self.THRESHOLD_PV, saveCnt
                    ),
                )
            )

            for _, d in df.iterrows():
                if d.id in self.SAVE_ID_LIST:
                    continue

                text = """
                ```記事タイトル: {}\n\nPV数: {}```
                """.format(
                    d["title"], d["pv"]
                )
                SlackService.post(
                    attachments=Message.info(
                        url=self.SLACK_WEBHOOK_URL, name="記事", text=text
                    )
                )

                with open(self.SAVE_TEXT, mode="a+", encoding="utf-8") as fp:
                    fp.write("{}\n".format(d.id))

                if d.pv < self.THRESHOLD_PV2:
                    with open(self.SAVE_TEXT3, mode="a+", encoding="utf-8") as fp:
                        fp.write("{}\n".format(d.id))

    def _read_csv2(self):
        df = pd.read_csv(
            self.OUTPUT_FILE, header=0, names=["no", "id", "title", "pv"], thousands=","
        )
        df = df[["id", "title", "pv"]]

        SlackService.post(
            attachments=Message.info(
                url=self.SLACK_WEBHOOK_URL_ADMIN,
                name="[done] 1000バッチ処理完了(all) \n",
                text="df:{}".format(df),
            )
        )

        df = df[df["pv"] >= self.THRESHOLD_PV2].sort_values(
            "pv", ascending=False)
        df = df.reset_index(drop=True)
        cnt = df.title.count()
        saveCnt = 0

        for _, d in df.iterrows():
            if d.id in self.SAVE_ID_LIST2:
                continue
            elif d.id not in self.SAVE_ID_LIST3:
                continue
            else:
                saveCnt += 1

        SlackService.post(
            attachments=Message.info(
                url=self.SLACK_WEBHOOK_URL_ADMIN,
                name="[done] 1000バッチ処理完了 \n",
                text="""
            通知しないリスト:\n{}\ncnt:\n{}\nsaveCnt:\n{}\ndf:{}
            """.format(
                    self.SAVE_ID_LIST2, cnt, saveCnt, df
                ),
            )
        )

        SlackService.post(
            attachments=Message.info(
                url=self.SLACK_WEBHOOK_URL_ADMIN,
                name="[done] 1000バッチ処理完了 \n",
                text="""
            1度通知したが2回目通知対象リスト:\n{}\n
            """.format(
                    self.SAVE_ID_LIST3
                ),
            )
        )

        if cnt > 0 and saveCnt > 0:
            SlackService.post(
                attachments=Message.info(
                    url=self.SLACK_WEBHOOK_URL,
                    name="<!here>",
                    text="""
                :bomb: :boom: :boom: 以下の記事がリアルタイムで{}PVを超えました（{}件）:boom: :boom: :bomb:
                """.format(
                        self.THRESHOLD_PV2, saveCnt
                    ),
                )
            )

            for _, d in df.iterrows():
                if d.id in self.SAVE_ID_LIST2:
                    continue
                elif d.id not in self.SAVE_ID_LIST3:
                    continue
                text = """
                ```記事タイトル: {}\n\nPV数: {}```
                """.format(
                    d["title"], d["pv"]
                )
                SlackService.post(
                    attachments=Message.info(
                        url=self.SLACK_WEBHOOK_URL, name="記事", text=text
                    )
                )

                with open(self.SAVE_TEXT2, mode="a+", encoding="utf-8") as fp:
                    fp.write("{}\n".format(d.id))

    def main(self):
        print("----- START ------")
        # crawl
        try:
            driver = self.driver
            driver.get(self.START_URL)
            sleep(5)
            driver.get(self.URL)

            self._login(driver)
            self._realtime(driver)
            self._crawl(driver)

        except Exception as e:
            driver.save_screenshot("test.png")
            SlackService.post(
                attachments=Message.danger(
                    url=self.SLACK_WEBHOOK_URL_ERROR,
                    name="[%s] エラーが発生しました。" % self.SERVICE_NAME,
                    text="""
                <!here> error: {}\ntraceback: {}
                """.format(
                        e, traceback.format_exc()
                    ),
                )
            )
        finally:
            driver.close()
            driver.quit()

        try:
            self._read_csv()
            self._read_csv2()
        except Exception as e:
            print(e)
            SlackService.post(
                attachments=Message.danger(
                    url=self.SLACK_WEBHOOK_URL_ERROR,
                    name="[%s] エラーが発生しました。" % self.SERVICE_NAME,
                    text="""
                <!here> error: {}\ntraceback: {}
                """.format(
                        e, traceback.format_exc()
                    ),
                )
            )

        print("----- END ------")


if __name__ == "__main__":
    crawl = CrawlYahoo()
    crawl.main()
