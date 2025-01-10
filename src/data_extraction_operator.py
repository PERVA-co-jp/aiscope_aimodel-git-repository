import pandas as pd
from src.data_loader import DatabaseConnection

class DataExtractionOperator:
    def __init__(self, end_date, start_date='2020-01-01', training=True):

        self.start_date = start_date
        self.end_date = end_date

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

        self.training = training

    def generate_remachines_query(self):
        query = f"""
        SELECT
            KatashikiId,
            created_at AS Regist_Date,
            ReleaseDate,
            makerId AS MakerId,
            MachineCategory AS Kind,
            Name,
            SaleUnitOther,
            Price,
            pachinkoTypeId AS TypeId,
            pachinkoTypeDetailId AS TypeDetailId,
            BigRate,
            SmallRate,
            KakuhenRate1_1,
            KakuhenRate1_2,
            KakuhenRate1_3,
            NairanFlag,
            TenjiFlag,
            InspectFlag,
            ContinueCountAve,
            PayCountAve,
            EquivalentBranch,
            TamaUnitPrice,
            MovieUrl1,
            MovieUrl2,
            GrossProfit,
            ModelLife,
            slotSpecId AS SpecId,
            CoinUnit,
            GameUnit,
            BonusFlag1_1,
            BonusFlag1_2, 
            BonusFlag1_3,
            BonusFlag1_4, 
            BonusFlag1_5,
            BonusFlag2_1, 
            BonusFlag2_2,
            BonusFlag2_3, 
            BonusFlag2_4,
            BonusFlag2_5,  
            BonusFlag3_1,
            BonusFlag3_2, 
            BonusFlag3_3,
            BonusFlag3_4,
            BonusFlag3_5,
            BonusFlag4_1,
            BonusFlag4_2,
            BonusFlag4_3,  
            BonusFlag4_4,
            BonusFlag4_5, 
            BonusFlag5_1,
            BonusFlag5_2,
            BonusFlag5_3,
            BonusFlag5_4, 
            BonusFlag5_5,
            BonusFlag6_1, 
            BonusFlag6_2,
            BonusFlag6_3,  
            BonusFlag6_4,
            BonusFlag6_5,
            BonusValue1_1,
            BonusValue1_2,
            BonusValue1_3,
            BonusValue1_4,
            BonusValue1_5,
            BonusValue2_1,
            BonusValue2_2,
            BonusValue2_3,
            BonusValue2_4,
            BonusValue2_5,
            BonusValue3_1,
            BonusValue3_2,
            BonusValue3_3,
            BonusValue3_4,
            BonusValue3_5,
            BonusValue4_1,
            BonusValue4_2,
            BonusValue4_3,
            BonusValue4_4,
            BonusValue4_5,
            BonusValue5_1,
            BonusValue5_2,
            BonusValue5_3,
            BonusValue5_4,
            BonusValue5_5,
            BonusValue6_1,
            BonusValue6_2,
            BonusValue6_3,
            BonusValue6_4,
            BonusValue6_5
        FROM re_machines
        WHERE created_at >= '{self.start_date} 00:00:00'
        AND created_at <= '{self.end_date} 23:59:59'
        AND (
                (MachineCategory = 0 AND (Name LIKE 'P%%' OR Name LIKE 'e%%'))
                OR MachineCategory = 1
            );
        """
        return query

    def generate_re_frame_relation_query(self):
        query = f"""
        SELECT 
            re_machines.KatashikiId,
            re_frame_relation.frameId AS FrameId
        FROM re_machines
        INNER JOIN re_frame_relation
        ON re_machines.KatashikiId = re_frame_relation.KatashikiId
        WHERE re_machines.created_at >= '{self.start_date} 00:00:00'
        AND re_machines.created_at <= '{self.end_date} 23:59:59'
        AND (
                (re_machines.MachineCategory = 0 AND (re_machines.KatashikiId LIKE 'P%%' OR re_machines.KatashikiId LIKE 'e%%'))
                OR re_machines.MachineCategory = 1
            );
    """
        return query

    def generate_evaluation_query(self):
        query = f"""
        SELECT 
            re_machines.KatashikiId, 
            modelevaluation.Performance,
            modelevaluation.Spec,
            modelevaluation.Content,
            modelevaluation.News,
            modelevaluation.Concept,
            modelevaluation.Period,
            modelevaluation.SaleUnit AS SaleUnit_eval,
            modelevaluation.Running,
            modelevaluation.Returns,
            modelevaluation.Price AS Price_eval
        FROM re_machines
        INNER JOIN modelevaluation
        ON re_machines.KatashikiId = modelevaluation.KatashikiId
        WHERE re_machines.created_at >= '{self.start_date} 00:00:00'
        AND re_machines.created_at <= '{self.end_date} 23:59:59'
        AND (
                (re_machines.MachineCategory = 0 AND (re_machines.KatashikiId LIKE 'P%%' OR re_machines.KatashikiId LIKE 'e%%'))
                OR re_machines.MachineCategory = 1
            );
    """
        return query
    
    def extract_and_process(self):
        """
        データを抽出して結合を行う

        以下のテーブルに関しては後続で処理を行う
        df_katashiki_frame_relation
        df_frame
        """
        df = self.db_connection.execute_query(self.generate_remachines_query())
        df_pachinko_type = self.db_connection.execute_query("SELECT id AS TypeId, TypeName from re_pachinko_type")
        df_pachinko_type_detail = self.db_connection.execute_query("SELECT id AS TypeDetailId, TypeName AS TypeName_detail from re_pachinko_type_detail")

        df_katashiki_frame_relation = self.db_connection.execute_query(self.generate_re_frame_relation_query())
        df_frame = self.db_connection.execute_query("SELECT id AS FrameId, Color from re_frames")

        df_evaluation = self.db_connection.execute_query(self.generate_evaluation_query())
        self.db_connection.close_tunnel()

        # 結合を行いメインテーブル「df」を作成する
        df_pachinko_type['TypeId'] = df_pachinko_type['TypeId'].astype(int)
        df = pd.merge(df, df_pachinko_type, on='TypeId', how='left')

        df_pachinko_type_detail['TypeDetailId'] = df_pachinko_type_detail['TypeDetailId'].astype(int)
        df = pd.merge(df, df_pachinko_type_detail, on='TypeDetailId', how='left')

        # モデル構築用のデータは正解データを付与する
        if self.training:
            # 評価値があるレコードのみ残す
            df = pd.merge(df, df_evaluation, on='KatashikiId', how='inner')
        else:
            # 全ての型式IDを残すようにする
            df = pd.merge(df, df_evaluation, on='KatashikiId', how='left')

        return df, df_katashiki_frame_relation, df_frame