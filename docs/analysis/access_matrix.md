# Матрица доступа

Соответствует sql/roles.sql. Права владельца/суперпользователя в эту матрицу не входят.

| Сущность | Категория | Роль | Разрешено | Запрещено | Основание |
|---|---|---|---|---|---|
| audit.audit_log | Внутренние учебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| audit.audit_log | Внутренние учебные | credit_operator | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| audit.audit_log | Внутренние учебные | loan_committee | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| audit.audit_log | Внутренние учебные | credit_admin | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.borrower | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.borrower | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.borrower | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.borrower | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.industry | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.industry | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.industry | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.industry | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.lender | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.lender | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.lender | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.lender | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.load_run | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.load_run | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.load_run | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.load_run | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_contract | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_contract | Открытые/служебные | credit_operator | SELECT, INSERT, UPDATE | DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_contract | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_contract | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_status | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_status | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_status | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.loan_status | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.region | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.region | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.region | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.region | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.source_file | Открытые/служебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.source_file | Открытые/служебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.source_file | Открытые/служебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| credit.source_file | Открытые/служебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.collateral | Внутренние учебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.collateral | Внутренние учебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.collateral | Внутренние учебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.collateral | Внутренние учебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.financial_report | Внутренние учебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.financial_report | Внутренние учебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.financial_report | Внутренние учебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.financial_report | Внутренние учебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantee | Внутренние учебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantee | Внутренние учебные | credit_operator | SELECT, INSERT, UPDATE | DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantee | Внутренние учебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantee | Внутренние учебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantor | Учебные ПДн | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantor | Учебные ПДн | credit_operator | SELECT, INSERT, UPDATE | DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantor | Учебные ПДн | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.guarantor | Учебные ПДн | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.loan_collateral | Внутренние учебные | credit_analyst | Нет | SELECT, INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.loan_collateral | Внутренние учебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.loan_collateral | Внутренние учебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| private.loan_collateral | Внутренние учебные | credit_admin | SELECT, INSERT, UPDATE, DELETE | Нет | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.v_borrower_summary | Внутренние учебные | credit_analyst | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.v_borrower_summary | Внутренние учебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.v_borrower_summary | Внутренние учебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.v_borrower_summary | Внутренние учебные | credit_admin | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.mv_credit_risk | Внутренние учебные | credit_analyst | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.mv_credit_risk | Внутренние учебные | credit_operator | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.mv_credit_risk | Внутренние учебные | loan_committee | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
| mart.mv_credit_risk | Внутренние учебные | credit_admin | SELECT | INSERT, UPDATE, DELETE | Минимальные привилегии; 152-ФЗ для модели ПДн; 98-ФЗ при введении режима |
