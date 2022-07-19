# number_cron

### .envを作成
```
START_URL='https://business.yahoo.co.jp/'

#Yahoo!ログイン
URL='https://console-news.yahoo.co.jp/insights'
ID='xxx'
PW='xxx'

#crawlするYahoo!ニュースInsightsリアルタイムURL
BUSINESS_REALTIME_URL='https://console-news.yahoo.co.jp/insights/news/bunshun/realtime'

# slack
SLACK_WEBHOOK_URL='xxx'
SLACK_WEBHOOK_URL_ERROR='xxx'

#通知する（設定したpv以上が通知）NUMBER_DEV-727
THRESHOLD_PV=500
THRESHOLD_PV2=1000

#実行環境
TEST=True
```
以下の値は担当者に確認
```
ID: Yahoo!ログインID
PW: Yahoo!ログインPW
SLACK_WEBHOOK_URL: 通常通知するSlack Webhook URL
SLACK_WEBHOOK_URL_ERROR: エラー通知するSlack Webhook URL
THRESHOLD_PV: 通常通知するPVの閾値
THRESHOLD_PV2: 通常通知するPVの閾値とは別に再度通知するPVの閾値

※各項目を仮で設定していますが上書きしてください。
```
### 通知のルール
30分に1回通知処理が実行されます。

- Yahoo!ニュースInsightsのリアルタイムにて記事のPV数が設定されたPVの閾値（THRESHOLD_PV）を超えた場合にslack通知

- 一度通知されたら当日中は通知されないが、設定された別のPVの閾値（THRESHOLD_PV2）を超えた場合は一度だけ通知

