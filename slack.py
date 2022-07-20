# coding: UTF-8

import requests
import json


class SlackService(object):
    @classmethod
    def post(
        cls,
        text="",
        username="Yahoo!ニュースInsightsレポート",
        icon_emoji=":information_source:",
        link_names=1,
        attachments={},
    ):
        """
        Slack Post
        :param text: post text
        :param color: post color
        :param webhook: webhook url
        :param username: slack user
        :param icon_emoji: slack icon
        :param link_names: mention(true or false)
        :param attachments: attachments options
        :return:
        """
        requests.post(
            attachments["url"],
            data=json.dumps(
                {
                    "text": text,
                    "username": username,
                    "icon_emoji": icon_emoji,
                    "link_names": link_names,
                    "attachments": [attachments],
                }
            ),
        )


class Message(object):
    @classmethod
    def danger(cls, **kwargs):
        """
        Error(danger)
        :return: (dict)attachments
        """
        return {
            "url": kwargs.get("url"),
            "title": kwargs.get("name"),
            "text": kwargs.get("text"),
            "color": "danger",
        }

    @classmethod
    def warning(cls, **kwargs):
        """
        Warning
        :return: (dict)attachments
        """
        return {
            "url": kwargs.get("url"),
            "title": kwargs.get("name"),
            "text": kwargs.get("text"),
            "color": "warning",
        }

    @classmethod
    def info(cls, **kwargs):
        """
        info
        :return: (dict)attachments
        """
        return {
            "url": kwargs.get("url"),
            "title": kwargs.get("name"),
            "text": kwargs.get("text"),
            "color": "good",
        }
