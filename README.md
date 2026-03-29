# bankrupt_parcer
Тестовое задание для компании ПКО Воксис - парсер данных о банкротстве физических лиц из открытых источников.

## Запуск
- Задайте из примера переменные окружения в файле `.env`
```bash
cp .env-example .env
```
- Отредактируйте данные в файле ./data/inn_data.xlsx, добавив ИНН физических лиц, данные которых вы хотите спарсить. В первой колонке должны быть ИНН  
- Или оставьте файл без изменений, тогда сервис будет обрабатывать ИНН из примера.
- Так же можно добавить свой файл с ИНН, указав его имя в переменной окружения `INPUT_FILE_PATH` в файле `.env`

### Запуск chrome ubuntu (обязательно до Docker)
Без реального запуска браузера парсер не работает, так как натыкается на капчу.
```bash
google-chrome \
--remote-debugging-port=9222 \
--remote-debugging-address=127.0.0.1 \
--user-data-dir="$HOME/fedresurs-parser-profile" \
--profile-directory=Default \
--disable-blink-features=AutomationControlled \
--no-first-run \
--no-default-browser-check
```

### Запуск сервиса
```bash
docker compose up --build
```