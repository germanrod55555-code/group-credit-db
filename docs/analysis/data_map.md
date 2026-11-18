# Карта данных

Сформирована по фактической схеме PostgreSQL. Составная уникальность описана в последней колонке; «Нет» означает отсутствие индивидуального UNIQUE на одном поле.

| Источник | Сущность | Атрибут | Тип | Пример | Обязательный | Уникальный | Категория | Ограничения |
|---|---|---|---|---|---|---|---|---|
| СУБД / загрузчик | audit.audit_log | audit_id | bigint | - | Да | Да | Журнал защищаемых полей | PRIMARY KEY (audit_id) |
| СУБД / загрузчик | audit.audit_log | event_at | timestamp with time zone | - | Да | Нет | Журнал защищаемых полей |  |
| СУБД / загрузчик | audit.audit_log | session_actor | text | - | Да | Нет | Журнал защищаемых полей |  |
| СУБД / загрузчик | audit.audit_log | effective_role | text | - | Да | Нет | Журнал защищаемых полей |  |
| СУБД / загрузчик | audit.audit_log | table_name | text | - | Да | Нет | Журнал защищаемых полей |  |
| СУБД / загрузчик | audit.audit_log | operation | text | - | Да | Нет | Журнал защищаемых полей | CHECK ((operation = ANY (ARRAY['INSERT'::text, 'UPDATE'::text, 'DELETE'::text]))) |
| СУБД / загрузчик | audit.audit_log | old_data | jsonb | - | Нет | Нет | Журнал защищаемых полей |  |
| СУБД / загрузчик | audit.audit_log | new_data | jsonb | - | Нет | Нет | Журнал защищаемых полей |  |
| СУБД / загрузчик | audit.audit_log | txid | bigint | - | Да | Нет | Журнал защищаемых полей |  |
| Учебный CASE-ID / SBA | credit.borrower | borrower_id | bigint | 10000001 | Да | Да | Учебные идентификаторы | PRIMARY KEY (borrower_id) |
| Учебный CASE-ID / SBA | credit.borrower | case_code | text | CASE-10000001 | Да | Да | Учебные идентификаторы | UNIQUE (case_code) |
| Учебный CASE-ID / SBA | credit.borrower | region_code | text | IA | Да | Нет | Учебные идентификаторы | FOREIGN KEY (region_code) REFERENCES credit.region(code) |
| Учебный CASE-ID / SBA | credit.borrower | industry_code | text | UNKNOWN | Да | Нет | Учебные идентификаторы | FOREIGN KEY (industry_code) REFERENCES credit.industry(code) |
| Учебный CASE-ID / SBA | credit.borrower | synthetic | boolean | True | Да | Нет | Учебные идентификаторы | CHECK (synthetic) |
| SBA / преобразование | credit.industry | code | text | 211120 | Да | Да | Открытые / служебные | PRIMARY KEY (code) |
| SBA / преобразование | credit.industry | description | text | Crude Petroleum Extraction | Да | Нет | Открытые / служебные |  |
| SBA / преобразование | credit.lender | lender_id | bigint | 1 | Да | Да | Открытые / служебные | PRIMARY KEY (lender_id) |
| SBA / преобразование | credit.lender | name | text | Interstate Bank | Да | Да | Открытые / служебные | UNIQUE (name) |
| СУБД / загрузчик | credit.load_run | run_id | bigint | 3 | Да | Да | Открытые / служебные | PRIMARY KEY (run_id) |
| СУБД / загрузчик | credit.load_run | started_at | timestamp with time zone | 2026-11-18 13:43:47.117242+03:00 | Да | Нет | Открытые / служебные |  |
| СУБД / загрузчик | credit.load_run | finished_at | timestamp with time zone | 2026-11-18 13:47:24.391512+03:00 | Нет | Нет | Открытые / служебные |  |
| СУБД / загрузчик | credit.load_run | status | text | complete | Да | Нет | Открытые / служебные | CHECK ((status = ANY (ARRAY['loading'::text, 'complete'::text]))) |
| СУБД / загрузчик | credit.load_run | row_count | bigint | 1236084 | Да | Нет | Открытые / служебные | CHECK ((row_count >= 0)) |
| SBA / преобразование | credit.loan_contract | loan_id | bigint | 10000003 | Да | Да | Открытые / служебные | PRIMARY KEY (loan_id) |
| SBA / преобразование | credit.loan_contract | borrower_id | bigint | 10000003 | Да | Нет | Открытые / служебные | FOREIGN KEY (borrower_id) REFERENCES credit.borrower(borrower_id) |
| SBA / преобразование | credit.loan_contract | lender_id | bigint | 1189 | Да | Нет | Открытые / служебные | FOREIGN KEY (lender_id) REFERENCES credit.lender(lender_id) |
| SBA / преобразование | credit.loan_contract | source_id | smallint | 1 | Да | Нет | Открытые / служебные | UNIQUE (source_id, source_row); FOREIGN KEY (source_id) REFERENCES credit.source_file(source_id) |
| SBA / преобразование | credit.loan_contract | source_row | bigint | 3 | Да | Нет | Открытые / служебные | CHECK ((source_row > 0)); UNIQUE (source_id, source_row) |
| SBA / преобразование | credit.loan_contract | approval_date | date | 1999-10-01 | Да | Нет | Открытые / служебные |  |
| SBA / преобразование | credit.loan_contract | amount | numeric | 460400.00 | Да | Нет | Открытые / служебные | CHECK (((outstanding >= (0)::numeric) AND (outstanding <= amount))); CHECK ((amount >= (0)::numeric)) |
| Учебный генератор | credit.loan_contract | outstanding | numeric | 184160.00 | Да | Нет | Открытые / служебные | CHECK (((outstanding >= (0)::numeric) AND (outstanding <= amount))) |
| SBA / преобразование | credit.loan_contract | term_months | integer | 217 | Нет | Нет | Открытые / служебные | CHECK ((term_months >= 0)) |
| SBA / преобразование | credit.loan_contract | status_code | text | CHGOFF | Да | Нет | Открытые / служебные | FOREIGN KEY (status_code) REFERENCES credit.loan_status(status_code) |
| Учебный генератор | credit.loan_contract | scenario_fields | boolean | True | Да | Нет | Открытые / служебные | CHECK (scenario_fields) |
| SBA / преобразование | credit.loan_status | status_code | text | P I F | Да | Да | Открытые / служебные | PRIMARY KEY (status_code) |
| SBA / преобразование | credit.region | code | text | NV | Да | Да | Открытые / служебные | CHECK (((length(code) >= 1) AND (length(code) <= 10))); PRIMARY KEY (code) |
| SBA / преобразование | credit.source_file | source_id | smallint | 1 | Да | Да | Открытые / служебные | PRIMARY KEY (source_id) |
| SBA / преобразование | credit.source_file | filename | text | FOIA_7a_FY2000_FY2009_asof_260930.csv | Да | Да | Открытые / служебные | UNIQUE (filename) |
| SBA / преобразование | credit.source_file | url | text | https://data.sba.gov/sites/default/files/uploaded_resources/FOIA_ | Да | Да | Открытые / служебные | UNIQUE (url) |
| SBA / преобразование | credit.source_file | sha256 | character | e0122bce7e468fc1c4bb6f0a24100bfa0ead8c6065332a2b28cb01671ba5273e | Да | Нет | Открытые / служебные | CHECK ((sha256 ~ '^[0-9a-f]{64}$'::text)) |
| SBA / преобразование | credit.source_file | row_count | bigint | 690333 | Да | Нет | Открытые / служебные | CHECK ((row_count > 0)) |
| SBA / преобразование | credit.source_file | loaded_at | timestamp with time zone | 2026-11-18 13:43:47.117242+03:00 | Да | Нет | Открытые / служебные |  |
| Учебный генератор | private.collateral | collateral_id | bigint | 10000010 | Да | Да | Внутренние учебные | PRIMARY KEY (collateral_id) |
| Учебный генератор | private.collateral | kind | text | inventory | Да | Нет | Внутренние учебные | CHECK ((kind = ANY (ARRAY['equipment'::text, 'property'::text, 'inventory'::text]))) |
| Учебный генератор | private.collateral | appraised_value | numeric | 34300.00 | Да | Нет | Внутренние учебные | CHECK ((appraised_value >= (0)::numeric)) |
| Учебный генератор | private.collateral | synthetic | boolean | True | Да | Нет | Внутренние учебные | CHECK (synthetic) |
| Учебный генератор | private.financial_report | report_id | bigint | 1 | Да | Да | Внутренние учебные | PRIMARY KEY (report_id) |
| Учебный генератор | private.financial_report | borrower_id | bigint | 10000001 | Да | Нет | Внутренние учебные | UNIQUE (borrower_id, fiscal_year); FOREIGN KEY (borrower_id) REFERENCES credit.borrower(borrower_id) |
| Учебный генератор | private.financial_report | fiscal_year | smallint | 1998 | Да | Нет | Внутренние учебные | CHECK (((fiscal_year >= 1980) AND (fiscal_year <= 2100))); UNIQUE (borrower_id, fiscal_year) |
| Учебный генератор | private.financial_report | revenue | numeric | 105000.00 | Да | Нет | Внутренние учебные | CHECK ((revenue > (0)::numeric)) |
| Учебный генератор | private.financial_report | net_profit | numeric | 10500.00 | Да | Нет | Внутренние учебные |  |
| Учебный генератор | private.financial_report | synthetic | boolean | True | Да | Нет | Внутренние учебные | CHECK (synthetic) |
| Учебный генератор | private.guarantee | loan_id | bigint | 10000001 | Да | Нет | Внутренние учебные | PRIMARY KEY (loan_id, guarantor_id); FOREIGN KEY (loan_id) REFERENCES credit.loan_contract(loan_id) |
| Учебный генератор | private.guarantee | guarantor_id | bigint | 10000001 | Да | Нет | Внутренние учебные | FOREIGN KEY (guarantor_id) REFERENCES private.guarantor(guarantor_id); PRIMARY KEY (loan_id, guarantor_id) |
| Учебный генератор | private.guarantee | amount | numeric | 17500.00 | Да | Нет | Внутренние учебные | CHECK ((amount > (0)::numeric)) |
| Учебный генератор | private.guarantor | guarantor_id | bigint | 10000001 | Да | Да | Учебные ПДн | PRIMARY KEY (guarantor_id) |
| Учебный генератор | private.guarantor | display_name | text | Учебный поручитель 10000001 | Да | Нет | Учебные ПДн |  |
| Учебный генератор | private.guarantor | contact_email | text | demo-10000001@example.invalid | Да | Да | Учебные ПДн | CHECK ((contact_email ~~ '%@example.invalid'::text)); UNIQUE (contact_email) |
| Учебный генератор | private.guarantor | synthetic | boolean | True | Да | Нет | Учебные ПДн | CHECK (synthetic) |
| Учебный генератор | private.loan_collateral | loan_id | bigint | 10000010 | Да | Нет | Внутренние учебные | PRIMARY KEY (loan_id, collateral_id); FOREIGN KEY (loan_id) REFERENCES credit.loan_contract(loan_id) |
| Учебный генератор | private.loan_collateral | collateral_id | bigint | 10000010 | Да | Да | Внутренние учебные | PRIMARY KEY (loan_id, collateral_id); UNIQUE (collateral_id); FOREIGN KEY (collateral_id) REFERENCES private.collateral(collateral_id) |
| Учебный генератор | private.loan_collateral | allocated_value | numeric | 34300.00 | Да | Нет | Внутренние учебные | CHECK ((allocated_value >= (0)::numeric)) |
