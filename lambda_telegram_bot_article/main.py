import json
import os
import pickle
import logging

from aiogram import Bot, Dispatcher, executor, types

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Creating bot")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

logger.info("Loading model")

model_file = "model_C=1.0.bin"

with open(model_file, "rb") as f_in:
    dv, model = pickle.load(f_in)


def predict(data: dict) -> float:
    X = dv.transform([data])
    y_pred = model.predict_proba(X)[0, 1]
    return y_pred


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    logging.info("Received /start command")

    await message.reply(
        """Hello friend! To get prediction from model, send me a json data, and I will send you prediction.
        
        Example: {
        "gender": "female",
        "seniorcitizen": 0,
        "partner": "yes",
        "dependents": "no",
        "phoneservice": "no",
        "multiplelines": "no_phone_service",
        "internetservice": "dsl",
        "onlinesecurity": "no",
        "onlinebackup": "yes",
        "deviceprotection": "no",
        "techsupport": "no",
        "streamingtv": "no",
        "streamingmovies": "no",
        "contract": "month-to-month",
        "paperlessbilling": "yes",
        "paymentmethod": "electronic_check",
        "tenure": 24,
        "monthlycharges": 29.85,
        "totalcharges": 719
    }"""
    )


@dp.message_handler()
async def message(message: types.Message):
    logging.info("Received message: " + str(message))

    try:
        customer = json.loads(message.text)
    except Exception as e:
        await message.reply("Invalid json data")
        return

    try:
        churn_probability = predict(customer)
    except Exception as e:
        await message.reply("Sorry. We could not make a prediction for your data")
        return

    churn = churn_probability >= 0.5

    if churn:
        await message.reply(
            f"The customer will churn. Probability: {round(churn_probability, 2)}"
        )
    else:
        await message.reply(
            f"The customer won't churn. Probability: {round(churn_probability, 2)}"
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
