"""Small terminal demo for the oral defense. Mutating examples are always rolled back."""
import os,json
import psycopg
from psycopg.rows import dict_row
def show(con,q,args=None):
    rows=con.execute(q,args).fetchall()
    for row in rows:print(json.dumps(row,ensure_ascii=False,default=str))
def main():
    with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row,connect_timeout=10) as con:
        while True:
            print('\n1 Объём и источник  2 ТОП-5 по прибыли  3 Риск по ID  4 Запрет аналитику\n5 Лимит кредита  6 Аудит изменения  7 Состояние витрины  0 Выход')
            choice=input('Номер: ').strip()
            if choice=='0':break
            try:
                if choice=='1':show(con,'SELECT filename,row_count,sha256 FROM credit.source_file ORDER BY source_id')
                elif choice=='2':show(con,'SELECT case_code,net_profit,debt,risk_level FROM mart.mv_credit_risk ORDER BY net_profit DESC,borrower_id LIMIT 5')
                elif choice=='3':
                    key=int(input('ID (например, 10000001): '));show(con,'SELECT borrower_id,case_code,risk_level,revenue,debt FROM mart.mv_credit_risk WHERE borrower_id=%s',(key,))
                elif choice=='4':
                    with con.transaction():
                        con.execute('SET LOCAL ROLE credit_analyst')
                        show(con,'SELECT * FROM private.guarantor LIMIT 1')
                elif choice=='5':
                    with con.transaction():con.execute('UPDATE credit.loan_contract SET amount=amount*10 WHERE loan_id=10000001')
                elif choice=='6':
                    con.execute('SET LOCAL ROLE credit_operator')
                    con.execute('UPDATE credit.loan_contract SET outstanding=1 WHERE loan_id=10000001')
                    con.execute('RESET ROLE')
                    show(con,'SELECT event_at,effective_role,table_name,operation,old_data->>\'outstanding\' old_balance,new_data->>\'outstanding\' new_balance FROM audit.audit_log ORDER BY audit_id DESC LIMIT 1')
                elif choice=='7':show(con,'SELECT risk_level,count(*) cases FROM mart.mv_credit_risk GROUP BY risk_level ORDER BY risk_level')
                else:print('Выберите номер из меню.')
            except (psycopg.Error,ValueError) as exc:print('Ожидаемая проверка / ошибка:',str(exc).splitlines()[0])
            finally:con.rollback()
if __name__=='__main__':main()
