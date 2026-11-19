# Учебная кредитная база: PostgreSQL + Python

Групповая работа по дисциплине «Базы данных». РГАУ-МСХА имени К. А. Тимирязева, группа D18-25, 2026.

- Абельцев Герман Сергеевич — тимлид, разработчик.
- Иванов Игорь Евгеньевич — администратор БД.
- Рипчук Павел Андреевич — аналитик.

Проект опубликован 19.11.2026: [germanrod55555-code/group-credit-db](https://github.com/germanrod55555-code/group-credit-db). Репозиторий открытый: преподаватель может читать файлы и историю коммитов без приглашения. Три исходных коммита перенесены без изменения авторов, дат и идентификаторов. Игорь и Павел пока не подключены; их личные коммиты должны появиться после собственной работы. Сдача преподавателю не выполнялась.

## Что внутри

14 таблиц, 8 аналитических запросов, 5 дополнительных B-tree индексов, VIEW и MATERIALIZED VIEW, PL/pgSQL-функция риска, кредитные и аудиторские триггеры, 4 роли, Python-доступ и потоковая загрузка/выгрузка. 23 проверки прошли. Полные планы пяти запросов лежат в results/explain.

Источник: [SBA 7(a) FOIA](https://data.sba.gov/dataset/7a-504-foia), два CSV на 30.09.2026, **1 236 084 строки**. Суммы, даты, банки, отрасли и статусы — из источника. Заёмщики, прибыль, выручка, остаток, залоги и поручители — явно помеченные учебные сценарии. Расчёты не описывают реальную платёжеспособность компаний. Подробнее: docs/analysis/domain.md.

## Быстрый запуск с нуля

Нужны Python 3.12+, PostgreSQL 16 и около 4 ГБ свободного места. Готовый дамп в поставке позволяет пропустить загрузку CSV; в Git дамп не включается. Docker — один из способов запуска PostgreSQL, не обязательное условие.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# В .env задайте свой POSTGRES_PASSWORD. Не публикуйте этот файл.
docker compose up -d
# Задайте DATABASE_URL со своим паролем, например:
$env:DATABASE_URL='postgresql://postgres:YOUR_PASSWORD@127.0.0.1:55438/credit_lab'
python python/download_data.py
python python/setup_database.py
python python/benchmark.py
python tests/test_database.py
python python/demo.py
```

Если PostgreSQL уже установлен, создайте отдельную пустую базу credit_lab и настройте shared_preload_libraries='pg_stat_statements', track_io_timing=on; после изменения перезапустите только свой учебный сервер. Затем используйте его DATABASE_URL вместо Docker. Скрипты не предназначены для чужой рабочей базы.

Загрузка с нуля скачивает около 574 МБ CSV. Контрольные суммы проверяются. Повторный setup_database.py на полностью установленной базе останавливается; для проверки идемпотентности выполните python python/load_data.py. При ошибке промежуточной загрузки setup можно повторить: опубликованные строки не дублируются.

## Повседневные команды

```powershell
python python/db_access.py borrower 10000001
python python/db_access.py quality
python python/db_access.py export data/risk_export.csv
python python/demo.py
```

Команда balance ID AMOUNT изменяет остаток в транзакции; запускать её только на учебной копии. Меню demo всегда откатывает свои изменения. Для обновления витрины владелец выполняет REFRESH MATERIALIZED VIEW mart.mv_credit_risk. Инструкция восстановления: docs/backup.md.

## Результаты EXPLAIN ANALYZE

| Запрос | Индекс | До, мс | После, мс | Сканирование до / после |
|---|---|---:|---:|---|
| B1_profit: ТОП-5 прибыль + долг | idx_financial_year_profit, idx_loan_borrower | 1396.016 | 0.144 | Index Scan borrower_pkey, Seq Scan / Index Only Scan idx_financial_year_profit, Index Only Scan idx_loan_borrower, Index Scan borrower_pkey |
| B2_month: Кредиты за месяц | idx_loan_approval | 192.144 | 1.501 | Seq Scan / Index Only Scan idx_loan_approval |
| B3_lender: Кредиты банка | idx_loan_lender | 197.397 | 0.088 | Seq Scan / Index Only Scan idx_loan_lender |
| B4_borrower: Долг заёмщика | idx_loan_borrower | 152.600 | 0.026 | Seq Scan / Index Only Scan idx_loan_borrower |
| B5_region: Отрасли региона | idx_borrower_region | 152.645 | 0.633 | Seq Scan / Index Only Scan idx_borrower_region |

По одному прогреву и три измерения в каждой фазе. PK/UNIQUE присутствуют в обеих фазах, дополнительные индексы — только после. JIT off, параллелизм 0, без принуждения к Index Scan. Это тёплый тест; DISCARD ALL не очищает shared_buffers и кэш ОС. Подробности и буферы: docs/results.md, docs/implementation.md и results/environment.json.

## Навигация

- docs/analysis: предметная область, полная карта 62 полей, CSV-копия карты, матрица доступа, защита и схема потока.
- docs/diagrams/er_diagram.png: ER-диаграмма; исходник .dot рядом.
- sql: схема, запросы, триггеры, роли, индексы и статистика.
- python: загрузка, доступ, демонстрация и измерения.
- results: исходные протоколы, реальные планы, образцы результатов и проверки.
- report.pdf: пояснительная записка.
- defense: презентация PPTX/PDF и текст выступления PDF; редактируемый текст — docs/defense/speech.md.
- docs/defense/questions.md: вопросы по всем ролям.
- docs/team.md: распределение ответственности и порядок личных коммитов.
- docs/assignment.md: исходное задание.

## Что ещё требуется от команды

1. Каждому повторить свой блок и разобрать чужие: это прямое условие защиты.
2. Игорю и Павлу внести и закоммитить собственные проверенные изменения; общий архив не заменяет личную историю.
3. Передать преподавателю ссылку на открытый репозиторий. Для чтения приглашение не требуется. Игоря и Павла подключить позже по их GitHub-логинам для совместной работы.
4. При получении методичек по паттернам и чек-листа семинара 14 сверить с ними реализацию. Сейчас эти тексты отсутствуют; точное соответствие им не заявляется.
5. Уточнить точную дату в середине декабря. Полностью холодный режим EXPLAIN обсуждается отдельно: приложенная честно описанная методика использует одинаковый прогрев.
