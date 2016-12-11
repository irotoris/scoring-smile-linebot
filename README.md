# scoring_smile_bot
LINE BOT to score your smile on AWS Lambda with Emotion API

## Requirements
* Python 2.7
* Your AWS Account
  * API Gateway
  * Lambda
* Your LINE BOT Account
* Microsoft Emotion API Subscription
  * Subscription key
  * https://azure.microsoft.com/ja-jp/services/cognitive-services/emotion/

## Attribute
You need to set Environment variables on AWS Lambda (or change attributes in `main.py`).
* `LINE_CHANNEL_ACCESS_TOKEN`
* `EMOTION_API_SUBSCRIPTION_KEY`

## Deploy
1. Create your LINE BOT Account and Access token
1. Deploy codes to Lambda and Configure API Gateway
  * `git clone https://github.com/irotoris/scoring_smile_bot.git`
  * `cd scoring_smile_bot && pip install -r requirements.txt -t ./`
  * `zip -r upload.zip ./*`
  * Upload `upload.zip` to AWS Lambda
  * Configure Environment variables on AWS Lambda
    * Handler is `main.lambda_handler`
  * Configure Lambda Trigger (->API Gateway)
  * (Optional) Configure API Gateway for Signature Validation
1. Configure LINE BOT Webhook URL (->API Gateway URL)

## License
MIT License
