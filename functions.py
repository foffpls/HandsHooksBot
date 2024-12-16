import logging
import pandas as pd

def csv_to_xlsx_fix_phone(csv_file_path, xlsx_file_path):
    try:
        # Читання CSV-файлу
        df = pd.read_csv(csv_file_path)

        # Перевірка на наявність стовпця 'phone'
        if 'phone' not in df.columns:
            raise ValueError("У файлі немає стовпця 'phone'.")

        # Конвертація номерів у правильний формат
        def fix_number(phone):
            phone = str(phone)
            phone = phone.replace(",", "").replace(".", "")
            if phone.startswith("380"):
                return f"+{phone}"
            return phone

        df['phone'] = df['phone'].apply(fix_number)

        # Збереження у форматі XLSX
        df.to_excel(xlsx_file_path, index=False, engine='openpyxl')
        return xlsx_file_path
    except Exception as e:
        raise Exception(f"Помилка обробки файлу: {e}")

def remove_duplicates_from_clear():
    try:
        with open("clear.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()

        unique_lines = sorted(set(line.strip() for line in lines))

        with open("clear.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(unique_lines) + "\n")

        return len(unique_lines)
    except Exception as e:
        logging.error(f"Помилка при очищенні файлу clear.txt: {e}")
        return 0

def clear_except_specific_numbers():
    try:
        keep_numbers = {
            "+380506624427",
            "+380669172453",
            "+380974288769",
            "+380986293810"
        }

        with open("clear.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()

        filtered_lines = [line.strip() for line in lines if line.strip() in keep_numbers]

        with open("clear.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(filtered_lines) + "\n")

        return len(filtered_lines)
    except Exception as e:
        logging.error(f"Помилка при очищенні файлу clear.txt: {e}")
        return 0