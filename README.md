# YCTest

# Визначення неактивних користувачів

Цей скрипт визначає неактивних користувачів у BigQuery та надсилає email-повідомлення зі списком цих користувачів.

## Функціональність

* Підключається до BigQuery та виконує SQL-запит для визначення користувачів, які не взаємодіяли з продуктом протягом певного періоду.
* Надсилає email-повідомлення з результатами запиту.
* Використовує Google API для BigQuery та Gmail.
* Записує логи виконання скрипта у файл.

## Вимоги

* Python 3.10+
* Бібліотеки Python:
    * google-api-core
    * google-api-python-client
    * google-auth
    * google-auth-httplib2
    * google-auth-oauthlib
    * google-cloud-bigquery
    * google-cloud-core
    * google-crc32c
    * google-resumable-media
    * googleapis-common-protos
* Обліковий запис Google з доступом до BigQuery та Gmail.
* Файли з ключами API для BigQuery та Gmail.

## Налаштування

1. Встановіть необхідні бібліотеки Python:
   ```bash
   pip install -r requirements.txt

## Зауваження
* В ході виконання завдання помітив не коректність задачі, а саме умова про 30 днів від поточної дати у 2023 році. Тест виконую на початку Січня, і 30 днів поточного року ще не пройшло.
* В скрипт буда додана можливість оберати з якої дати фільтрувати та кількість днів не активності
