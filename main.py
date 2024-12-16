import os

import keyboards
import functions

import asyncio
import logging
import pandas as pd
import warnings

from aiogram import Router, F
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

bot = Bot(token=os.getenv('BOT_TOKEN'))

dp = Dispatcher()
start_router = Router()
dp.include_router(start_router)

user_choices = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Привіт, шукачу! \n'
                         'Можеш звати мене містером Яма Хав. Я той самий помічник з блекджеком та фічами!\n\n'
                         'Отже, коротко і по ділу. Щось я уже вмію, а чогось можу ще навчитись. Якщо хочеш моєї допомоги - користуйся меню, яке я спеціально створив для тебе (воно нижче). '
                         'Хочеш мене чогось навчити - пиши сюди: @foff_pls.\n\n'
                         'p.s. Я просто робот, тому не несу відповідальність за результат. Будь пильним, кожаний!', reply_markup=keyboards.main_kb())

@dp.message(F.text == "\U0001F4C2Файл xlsx в csv")
async def convert_to_csv(message: types.Message):
    user_choices[message.from_user.id] = 'convert_to_csv'
    with open("clear.txt", "r", encoding="utf-8") as clear_file:
        clear_lines = clear_file.readlines()
    line_count = len(clear_lines)
    await message.reply("Надсилайте свій файл .xlsx\n\n"
                        "- видалення дублікатів\n"
                        f"- очистка від попередніх розсилок ({line_count}шт)\n"
                        "- видалення всіх стовбців крім phone\n"
                        "- перевірка на наявність стовбця phone\n"
                        "- запис нового пулу номерів у список очищення\n"
                        "- конвертування в csv", reply_markup=keyboards.main_kb())

@dp.message(F.text == "\U0001F9F9Очистити CL від дублікатів")
async def convert_to_csv(message: types.Message):
    result = functions.remove_duplicates_from_clear()
    if result == 0:
        await message.reply("Shit happened!")
    else:
        await message.reply(f"Файл має {result} унікальних номерів!", reply_markup=keyboards.main_kb())

@dp.message(F.text == "\U0001F5D1Очистити CL")
async def convert_to_csv(message: types.Message):
    result = functions.clear_except_specific_numbers()
    if result == 0:
        await message.reply("Shit happened!")
    else:
        await message.reply(f"Оистка виконана успішно! {result} унікальних номерів!", reply_markup=keyboards.main_kb())


@dp.message(F.text == "\U0001F4E5Завантажити CL")
async def send_clear_as_xlsx(message: types.Message):
    try:
        with open("clear.txt", "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]

        df = pd.DataFrame(lines, columns=['phone'])
        output_file = "clear.xlsx"
        df.to_excel(output_file, index=False)

        await message.reply_document(FSInputFile(output_file), reply_markup=keyboards.main_kb())

        if os.path.exists(output_file):
            os.remove(output_file)
    except Exception as e:
        logging.error(f"Помилка при створенні файлу clear.xlsx: {e}")
        await message.reply("Сталася помилка під час створення файлу.", reply_markup=keyboards.main_kb())

@dp.message(F.text == "\U0001F4C4Файл csv в xlsx")
async def convert_to_csv(message: types.Message):
    user_choices[message.from_user.id] = 'convert_to_xlsx'
    await message.reply("Надсилайте свій файл .csv", reply_markup=keyboards.main_kb())

@dp.message(F.text == "\U00002194Замінити CL на власний")
async def replace_clear_txt(message: types.Message):
    user_choices[message.from_user.id] = 'replace_clear_txt'
    await message.reply("Надсилайте свій файл .xlsx", reply_markup=keyboards.main_kb())

@dp.message(F.text)
async def replace_clear_txt(message: types.Message):
    await message.reply("Давай без зайвих розмов, кожаний!\n"
                        "МЕНЮ нижче! Користуйся!", reply_markup=keyboards.main_kb())

@dp.message(F.document)
async def handle_file(message: types.Message):
    user_choice = user_choices.get(message.from_user.id)
    warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl')

    try:
        if user_choice == 'convert_to_csv':
            document = message.document

            if not document.file_name.endswith('.xlsx'):
                await message.reply("Будь ласка, надішліть файл у форматі .xlsx", reply_markup=keyboards.main_kb())
                return

            file_info = await bot.get_file(document.file_id)
            file_path = file_info.file_path
            file = await bot.download_file(file_path)
            df = pd.read_excel(file)

            if 'phone' not in df.columns:
                await message.reply("У файлі немає стовпця 'phone'.", reply_markup=keyboards.main_kb())
                return

            df = df[['phone']].drop_duplicates()

            with open("clear.txt", "r", encoding="utf-8") as clear_file:
                clear_lines = set(line.strip() for line in clear_file)

            df['phone'] = df['phone'].astype(str).str.strip()
            df['phone'] = df['phone'].apply(lambda x: f"+{x}" if not x.startswith('+') else x)

            rows_to_remove = df[df['phone'].isin(clear_lines)]
            df = df[~df['phone'].isin(clear_lines)]
            deleted_count = len(rows_to_remove)

            output_file = f"{document.file_name.rsplit('.', 1)[0]}.csv"
            df.to_csv(output_file, index=False)

            new_numbers = df['phone'].tolist()
            with open("clear.txt", "a", encoding="utf-8") as clear_file:
                clear_file.write("\n".join(new_numbers) + "\n")

            total_numbers = len(clear_lines) + len(new_numbers)

            await message.reply(f"Було видалено {deleted_count} номерів з файлу.\n"
                                f"Додано до списку очищення {len(new_numbers)} номерів.\n"
                                f"Загальна кількість номерів у списку очищення {total_numbers}шт.", reply_markup=keyboards.main_kb())
            await message.reply_document(FSInputFile(output_file))

            if os.path.exists(output_file):
                os.remove(output_file)
        elif user_choice == 'convert_to_xlsx':
            document = message.document

            if not document.file_name.endswith('.csv'):
                await message.reply("Будь ласка, надішліть файл у форматі .csv", reply_markup=keyboards.main_kb())
                return

            file_info = await bot.get_file(document.file_id)
            file_path = file_info.file_path
            csv_file = await bot.download_file(file_path)

            xlsx_file_path = f"{document.file_name.rsplit('.', 1)[0]}.xlsx"

            try:
                result_file = functions.csv_to_xlsx_fix_phone(csv_file, xlsx_file_path)
                await message.reply_document(FSInputFile(result_file))
            except Exception as e:
                logging.error(f"Помилка конвертації: {e}")
                await message.reply("Сталася помилка під час конвертації файлу.", reply_markup=keyboards.main_kb())
        elif user_choice == 'replace_clear_txt':
            document = message.document

            if not document.file_name.endswith('.xlsx'):
                await message.reply("Будь ласка, надішліть файл у форматі .xlsx", reply_markup=keyboards.main_kb())
                return

            file_info = await bot.get_file(document.file_id)
            file_path = file_info.file_path
            file = await bot.download_file(file_path)
            df = pd.read_excel(file)

            if 'phone' not in df.columns:
                await message.reply("У файлі немає стовпця 'phone'.", reply_markup=keyboards.main_kb())
                return

            df = df[['phone']].drop_duplicates()

            # Очищення та заміна старого clear.txt на новий
            new_clear_file = "clear.txt"
            df['phone'] = df['phone'].astype(str).str.strip()
            df['phone'] = df['phone'].apply(lambda x: f"+{x}" if not x.startswith('+') else x)

            # Запис нових номерів у clear.txt
            with open(new_clear_file, "w", encoding="utf-8") as clear_file:
                for phone in df['phone']:
                    clear_file.write(phone + "\n")

            await message.reply(f"Файл clear.txt успішно оновлено! Загальна кількість номерів: {len(df)}",
                                reply_markup=keyboards.main_kb())
    except Exception as e:
        logging.error(f"Помилка при обробці файлу: {e}")
        await message.reply("Сталася помилка під час обробки файлу. Перевірте його вміст.", reply_markup=keyboards.main_kb())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
