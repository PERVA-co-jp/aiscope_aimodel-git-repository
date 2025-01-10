import pandas as pd
from src.data_loader import DatabaseConnection
from datetime import datetime

class DataInsertUpdate:
    def __init__(self):

        self.db_connection = DatabaseConnection(
                                ssh_host='162.43.30.233',
                                ssh_port=22,
                                ssh_user='root',
                                ssh_pkey='mikata.ppk', 
                                db_host='127.0.0.1',
                                db_port=3306,
                                db_user='aiscope',
                                db_password='Root@123',
                                db_name='ps_scope'
                            )

        self.db_connection.start_tunnel()

    def create_query_for_insert(self, insert_ids, dict_values):
        
        ymdHMS = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        query = f"""
INSERT INTO re_model_results (KatashikiId, GrossProfit, Concept, Performance, Content, SaleUnit, Spec, Period, News, Running, Returns, Price, ModelLife, created_at, updated_at)
VALUES
        """
        
        for i, key in enumerate(insert_ids):
            results = dict_values[key]

            query += (f"('{key}',"
                        f"'{int(results['GrossProfit'])}',"
                        f"'{results['Concept']}',"
                        f"'{results['Performance']}',"
                        f"'{results['Content']}',"
                        f"'{results['SaleUnit']}',"
                        f"'{results['Spec']}',"
                        f"'{results['Period']}',"
                        f"'{results['News']}',"
                        f"'{results['Running']}',"
                        f"'{results['Returns']}',"
                        f"'{results['Price']}',"
                        f"'{results['ModelLife']}',"                        
                        f"'{ymdHMS}',"
                        f"'{ymdHMS}')")
        
            if i != len(insert_ids) - 1:
                query += ', \n'
            else:
                query += ';'
        return query
    
    def create_query_for_update(self, update_ids, dict_values):
        ymdHMS = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        keys = ['GrossProfit', 'Concept', 'Performance', 'Content',
                'SaleUnit', 'Spec', 'Period', 'News', 'Running', 'Returns', 'Price', 'ModelLife', 'updated_at']
        query = 'UPDATE re_model_results \n SET \n'
        for i, key in enumerate(keys):
            query += f"{key} = CASE\n"
            for j, KatashikiId in enumerate(update_ids):
                if key != 'updated_at':
                    if key in ['GrossProfit']:
                        query += f"   WHEN KatashikiId = '{KatashikiId}' THEN '{int(dict_values[KatashikiId][key])}'"

                    else: 
                        query += f"   WHEN KatashikiId = '{KatashikiId}' THEN '{dict_values[KatashikiId][key]}'"
                else:
                    query += f"   WHEN KatashikiId = '{KatashikiId}' THEN '{ymdHMS}'"

                if j != len(update_ids) - 1:
                    query += "\n"
                else:
                    query += f"\n   ELSE {key}"

            query += "\nEND,\n" if i != len(keys) - 1 else "\nEND\n"

        tuple_ids = '('
        for j, KatashikiId in enumerate(update_ids):
            tuple_ids += f"'{KatashikiId}'"

            if j != len(update_ids) - 1:
                tuple_ids += ','
            else:
                tuple_ids += ');'
        query += "WHERE KatashikiId IN " + tuple_ids
        return query
    
    def process(self, list_ids, dict_values):

        # テーブルに存在するIDを抽出
        db_ids = self.db_connection.execute_query("SELECT KatashikiId from re_model_results")
        db_ids = db_ids['KatashikiId'].tolist()

        # 挿入用と更新用に分ける
        insert_ids = [x for x in list_ids if x not in db_ids]
        update_ids = [x for x in list_ids if x in db_ids]

        if len(insert_ids) > 0:
            self.db_connection.execute_write_query(self.create_query_for_insert(insert_ids, dict_values))
        if len(update_ids) > 0:
            self.db_connection.execute_write_query(self.create_query_for_update(update_ids, dict_values))