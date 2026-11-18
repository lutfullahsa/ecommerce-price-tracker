import logging
import os


def logger_olustur(isim="FiyatTakipBotu", log_dosyasi="cikti/bot.log"):
    logger = logging.getLogger(isim)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        klasor = os.path.dirname(log_dosyasi)
        if klasor:
            os.makedirs(klasor, exist_ok=True)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_dosyasi, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
