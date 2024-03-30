import logging
import asyncio
import csv
from catboost import CatBoostClassifier
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.types import URLInputFile
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Creating bot")
BOT_TOKEN = "7002908305:AAEz0EBvBR2zCCNvFiIC8J_lX4-Snp6oURo"


if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

logger.info("Loading model")

model_file = "../anomaly_detection/anomaly_classifier"

# Загрузка модели
model = CatBoostClassifier()
model.load_model(model_file)


# Прогнозирование
def predict(input_data):
    # input_data - это данные для прогнозирования, представленные в нужном формате
    print("we are here!") # для дебага
    print(input_data)
    print(type(input_data))
    prediction = model.predict(input_data)
    return prediction

@dp.message(Command(commands=["start"]))
async def start(message: types.Message):
    photo_z = FSInputFile("Z_sasha.png")

    photo_start = URLInputFile(
        "https://kirovets-ptz.com/upload/iblock/e59/90mngsuutxn0i6ysesxqus33z1v5d5q6/k7m-2021-new.png",
        filename="K7m-logo.png"
    )

    logging.info("Received /start command")
    await message.reply(
        """
        Привет! Это бот созданный в рамках хакатона EESTech Challenge.
        Его основной задачей является анализ и предсказание поведения тракторов Кировец.
        Данный бот использует ML для анализа всех датчиков и систем машины, с целью выявления аномальный значений.
        Бот создан командой "ЪЕЪ" - @sastsy , @echo100 ,  @alice3e.
        """
    )
    await message.answer_photo(photo_z)


@dp.message(Command(commands=["base"]))
async def start(message: types.Message):
    logging.info("Received /base command")

    await message.reply(
        """Базы данных не подключена"""
    )

@dp.message(Command(commands=["help"]))
async def start(message: types.Message):
    logging.info("Received /help command")

    await message.reply(
        """Для анализа отправьте файл .csv
            Для получения обработанных файлов используйте /base"""
    )


@dp.message()
async def message(message: types.Message):
    logging.info("Received message: " + str(message))

    if message.document:
        # Проверяем, что документ является CSV файлом
        if message.document.mime_type == 'text/csv':
            try:
                file_id = message.document.file_id
                file = await bot.get_file(file_id)
                file_path = file.file_path
                await bot.download_file(file_path, "data_downloaded.csv")
            except Exception as e:
                await message.reply("Error reading CSV file: " + str(e))
                return
        else:
            await message.reply("Please send a CSV file.")
            return
    else:
        await message.reply("Please send a document.")
        return

    try:
        print("HELLO")
        with open("data_downloaded.csv", 'r') as csv_file:
            for line in csv_file.readlines():
                line_sep = (list(line.split(";")))
                print(line_sep) # проверка на правильность данных
                churn_probability = predict(line_sep)
                print(churn_probability)
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Bot started!")
    asyncio.run(main())

#%