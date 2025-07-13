# KP News Crawler

📰 Веб-краулер на Scrapy + Playwright для сбора свежих новостей с сайта [kp.ru](https://www.kp.ru).

Данные сохраняются в MongoDB.

## 📦 Установка

1️⃣ Создайте виртуальное окружение:
python3 -m venv venv
source venv/bin/activate
2️⃣ Установите зависимости:
pip install -r requirements.txt

3️⃣ Установите Playwright и браузеры:
playwright install

4️⃣ Убедитесь, что MongoDB запущен локально на mongodb://localhost:27017.

## Запустите паука, указав, сколько последних новостей собрать (count=N):
scrapy crawl kp_spider -a count=10

Проверить данные в MongoDB:
mongosh
use kp_news
db.news.find().pretty()

Очистить коллекцию:
db.news.deleteMany({})
