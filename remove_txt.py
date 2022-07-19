# coding: UTF-8
import os
from slack import SlackService, Message


class RemoveTxt():
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
            url='https://hooks.slack.com/services/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',
            name="",
            text="--------------- 削除バッチ処理完了 ---------------"))


if __name__ == '__main__':
    removeTxt = RemoveTxt()
    removeTxt.main()
