# coding: UTF-8
import os
from slack import SlackService, Message
from dotenv import load_dotenv


class RemoveTxt():
    load_dotenv()
    SLACK_WEBHOOK_URL_ADMIN = os.environ["SLACK_WEBHOOK_URL_ADMIN"]

    SAVE_TEXT = "./save_id_list.txt"
    SAVE_TEXT2 = "./save_id_list2.txt"
    SAVE_TEXT3 = "./save_id_list3.txt"

    def main(self):
        if os.path.exists(self.SAVE_TEXT):
            os.remove(self.SAVE_TEXT)

        if os.path.exists(self.SAVE_TEXT2):
            os.remove(self.SAVE_TEXT2)

        if os.path.exists(self.SAVE_TEXT3):
            os.remove(self.SAVE_TEXT3)

        SlackService.post(attachments=Message.info(
            url=self.SLACK_WEBHOOK_URL_ADMIN,
            name="",
            text="--------------- 削除バッチ処理完了 ---------------"))


if __name__ == '__main__':
    removeTxt = RemoveTxt()
    removeTxt.main()
