import pandas as pd
from src.data_loader import DatabaseConnection

class DevDataExtractionOperator:
    def __init__(self, end_date, start_date='2020-01-01', training=True):

        self.start_date = start_date
        self.end_date = end_date

        self.db_connection = DatabaseConnection(
                                ssh_host='www.redesign777.tokyo',
                                ssh_port=22,
                                ssh_user='rddev',
                                ssh_password='rdDev@20240521',
                                db_host='localhost',
                                db_port=3306,
                                db_user='rddev',
                                db_password='rdSql@20240521',
                                db_name='redesign')

        self.db_connection.start_tunnel()

        self.training = training

    def generate_katashiki_query(self):
        query = f"""
        SELECT
            KatashikiId,
            Regist_Date, 
            MakerId, 
            Kind,
            Name,
            SaleUnitOther, 
            Price, 
            NairanFlag,
            TenjiFlag,
            InspectFlag
        FROM re_m_katashiki
        WHERE Regist_Date >= '{self.start_date} 00:00:00'
        AND Regist_Date <= '{self.end_date} 23:59:59'
        AND (
                (Kind = 0 AND (Name LIKE 'P%%' OR Name LIKE 'e%%'))
                OR Kind = 1
            );
        """
        return query

    def generate_pachinko_query(self):
        query = f"""
        SELECT 
            re_m_katashiki.KatashikiId,
            re_m_katashikidetailpachinko.TypeId1,
            re_m_katashikidetailpachinko.TypeDetailId1,
            re_m_katashikidetailpachinko.BigRate,
            re_m_katashikidetailpachinko.SmallRate,
            re_m_katashikidetailpachinko.KakuhenRate1_1,
            re_m_katashikidetailpachinko.KakuhenRate1_2,
            re_m_katashikidetailpachinko.KakuhenRate1_3,
            re_m_katashikidetailpachinko.EquivalentBranch, 
            re_m_katashikidetailpachinko.ContinueCountAve, 
            re_m_katashikidetailpachinko.PayCountAve, 
            re_m_katashikidetailpachinko.TamaUnitPrice,
            re_m_katashikidetailpachinko.MovieUlr1 AS MovieUrl1_p, 
            re_m_katashikidetailpachinko.MovieUlr2 AS MovieUrl2_p, 
            re_m_katashikidetailpachinko.SiteUlr AS SiteUrl_p,
            re_m_katashikidetailpachinko.ModelLife AS ModelLife_p_detail,
            re_m_katashikidetailpachinko.GrossProfit AS GrossProfit_p_detail
        FROM re_m_katashiki
        LEFT JOIN re_m_katashikidetailpachinko
        ON re_m_katashiki.KatashikiId = re_m_katashikidetailpachinko.KatashikiId
        WHERE re_m_katashiki.Regist_Date >= '{self.start_date} 00:00:00'
        AND re_m_katashiki.Regist_Date <= '{self.end_date} 23:59:59'
        AND (
                (re_m_katashiki.Kind = 0 AND (re_m_katashiki.Name LIKE 'P%%' OR re_m_katashiki.Name LIKE 'e%%'))
                OR re_m_katashiki.Kind = 1
            );
        """
        return query

    def generate_slot_query(self):
        query = f"""
        SELECT 
            re_m_katashiki.KatashikiId,
            re_m_katashikidetailslot.SpecId,
            re_m_katashikidetailslot.CoinUnit,
            re_m_katashikidetailslot.GameUnit,
            re_m_katashikidetailslot.ModelLife AS ModelLife_s_detail,
            re_m_katashikidetailslot.GrossProfit AS GrossProfit_s_detail,
            re_m_katashikidetailslot.BonusFlag1_1,
            re_m_katashikidetailslot.BonusFlag1_2, 
            re_m_katashikidetailslot.BonusFlag1_3,
            re_m_katashikidetailslot.BonusFlag1_4, 
            re_m_katashikidetailslot.BonusFlag1_5,
            re_m_katashikidetailslot.BonusFlag2_1, 
            re_m_katashikidetailslot.BonusFlag2_2,
            re_m_katashikidetailslot.BonusFlag2_3, 
            re_m_katashikidetailslot.BonusFlag2_4,
            re_m_katashikidetailslot.BonusFlag2_5,  
            re_m_katashikidetailslot.BonusFlag3_1,
            re_m_katashikidetailslot.BonusFlag3_2, 
            re_m_katashikidetailslot.BonusFlag3_3,
            re_m_katashikidetailslot.BonusFlag3_4,
            re_m_katashikidetailslot.BonusFlag3_5,
            re_m_katashikidetailslot.BonusFlag4_1,
            re_m_katashikidetailslot.BonusFlag4_2,
            re_m_katashikidetailslot.BonusFlag4_3,  
            re_m_katashikidetailslot.BonusFlag4_4,
            re_m_katashikidetailslot.BonusFlag4_5, 
            re_m_katashikidetailslot.BonusFlag5_1,
            re_m_katashikidetailslot.BonusFlag5_2,
            re_m_katashikidetailslot.BonusFlag5_3,
            re_m_katashikidetailslot.BonusFlag5_4, 
            re_m_katashikidetailslot.BonusFlag5_5,
            re_m_katashikidetailslot.BonusFlag6_1, 
            re_m_katashikidetailslot.BonusFlag6_2,
            re_m_katashikidetailslot.BonusFlag6_3,  
            re_m_katashikidetailslot.BonusFlag6_4,
            re_m_katashikidetailslot.BonusFlag6_5,
            re_m_katashikidetailslot.BonusValue1_1,
            re_m_katashikidetailslot.BonusValue1_2,
            re_m_katashikidetailslot.BonusValue1_3,
            re_m_katashikidetailslot.BonusValue1_4,
            re_m_katashikidetailslot.BonusValue1_5,
            re_m_katashikidetailslot.BonusValue2_1,
            re_m_katashikidetailslot.BonusValue2_2,
            re_m_katashikidetailslot.BonusValue2_3,
            re_m_katashikidetailslot.BonusValue2_4,
            re_m_katashikidetailslot.BonusValue2_5,
            re_m_katashikidetailslot.BonusValue3_1,
            re_m_katashikidetailslot.BonusValue3_2,
            re_m_katashikidetailslot.BonusValue3_3,
            re_m_katashikidetailslot.BonusValue3_4,
            re_m_katashikidetailslot.BonusValue3_5,
            re_m_katashikidetailslot.BonusValue4_1,
            re_m_katashikidetailslot.BonusValue4_2,
            re_m_katashikidetailslot.BonusValue4_3,
            re_m_katashikidetailslot.BonusValue4_4,
            re_m_katashikidetailslot.BonusValue4_5,
            re_m_katashikidetailslot.BonusValue5_1,
            re_m_katashikidetailslot.BonusValue5_2,
            re_m_katashikidetailslot.BonusValue5_3,
            re_m_katashikidetailslot.BonusValue5_4,
            re_m_katashikidetailslot.BonusValue5_5,
            re_m_katashikidetailslot.BonusValue6_1,
            re_m_katashikidetailslot.BonusValue6_2,
            re_m_katashikidetailslot.BonusValue6_3,
            re_m_katashikidetailslot.BonusValue6_4,
            re_m_katashikidetailslot.BonusValue6_5,
            re_m_katashikidetailslot.MovieUlr1 AS MovieUrl1_s,
            re_m_katashikidetailslot.MovieUlr2 AS MovieUrl2_s,
            re_m_katashikidetailslot.SiteUlr AS SiteUrl_s
        FROM re_m_katashiki
        LEFT JOIN re_m_katashikidetailslot
        ON re_m_katashiki.KatashikiId = re_m_katashikidetailslot.KatashikiId
        WHERE re_m_katashiki.Regist_Date >= '{self.start_date} 00:00:00'
        AND re_m_katashiki.Regist_Date <= '{self.end_date} 23:59:59'
        AND (
                (re_m_katashiki.Kind = 0 AND (re_m_katashiki.Name LIKE 'P%%' OR re_m_katashiki.Name LIKE 'e%%'))
                OR re_m_katashiki.Kind = 1
            );
    """
        return query

    def generate_katashiki_frame_relation_query(self):
        query = f"""
        SELECT 
            re_m_katashiki.KatashikiId,
            re_m_katashikiframerelation.FrameId
        FROM re_m_katashiki
        INNER JOIN re_m_katashikiframerelation
        ON re_m_katashiki.KatashikiId = re_m_katashikiframerelation.KatashikiId
        WHERE re_m_katashiki.Regist_Date >= '{self.start_date} 00:00:00'
        AND re_m_katashiki.Regist_Date <= '{self.end_date} 23:59:59'
        AND (
                (re_m_katashiki.Kind = 0 AND (re_m_katashiki.Name LIKE 'P%%' OR re_m_katashiki.Name LIKE 'e%%'))
                OR re_m_katashiki.Kind = 1
            );
    """
        return query

    def generate_evaluation_query(self):
        query = f"""
        SELECT 
            re_m_katashiki.KatashikiId, 
            re_m_modelevaluation.Performance,
            re_m_modelevaluation.Spec,
            re_m_modelevaluation.Content,
            re_m_modelevaluation.News,
            re_m_modelevaluation.Concept,
            re_m_modelevaluation.Period,
            re_m_modelevaluation.SaleUnit AS SaleUnit_eval,
            re_m_modelevaluation.Running,
            re_m_modelevaluation.Returns,
            re_m_modelevaluation.Price AS Price_eval
        FROM re_m_katashiki
        INNER JOIN re_m_modelevaluation
        ON re_m_katashiki.KatashikiId = re_m_modelevaluation.KatashikiId
        WHERE re_m_katashiki.Regist_Date >= '{self.start_date} 00:00:00'
        AND re_m_katashiki.Regist_Date <= '{self.end_date} 23:59:59'
        AND (
                (re_m_katashiki.Kind = 0 AND (re_m_katashiki.Name LIKE 'P%%' OR re_m_katashiki.Name LIKE 'e%%'))
                OR re_m_katashiki.Kind = 1
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
        df_katashiki = self.db_connection.execute_query(self.generate_katashiki_query())
        df_pachinko = self.db_connection.execute_query(self.generate_pachinko_query())
        df_slot = self.db_connection.execute_query(self.generate_slot_query())
        df_pachinko_type = self.db_connection.execute_query("SELECT TypeId, TypeName FROM re_m_pachinkotype")
        df_pachinko_type_detail = self.db_connection.execute_query("SELECT TypeDetailId, TypeName AS TypeName_detail FROM re_m_pachinkotypedetail")

        df_katashiki_frame_relation = self.db_connection.execute_query(self.generate_katashiki_frame_relation_query())
        df_frame = self.db_connection.execute_query("SELECT FrameId, Color FROM re_m_frame")

        df_evaluation = self.db_connection.execute_query(self.generate_evaluation_query())
        self.db_connection.close_tunnel()

        # 結合を行いメインテーブル「df」を作成する
        df = pd.merge(df_katashiki, df_pachinko, on='KatashikiId', how='left')
        df = pd.merge(df, df_slot, on='KatashikiId', how='left')

        df_pachinko_type['TypeId'] = df_pachinko_type['TypeId'].astype(int)
        df = pd.merge(df, df_pachinko_type, left_on='TypeId1', right_on='TypeId', how='left')

        df_pachinko_type_detail['TypeDetailId'] = df_pachinko_type_detail['TypeDetailId'].astype(int)
        df = pd.merge(df, df_pachinko_type_detail, left_on='TypeDetailId1', right_on='TypeDetailId', how='left')

        df = df.drop(columns=['TypeId1', 'TypeDetailId1'])

        # モデル構築用のデータは正解データを付与する
        if self.training:
            # 評価値があるレコードのみ残す
            df = pd.merge(df, df_evaluation, on='KatashikiId', how='inner')
        else:
            # 全ての型式IDを残すようにする
            df = pd.merge(df, df_evaluation, on='KatashikiId', how='left')

        df['MovieUrl1'] = df['MovieUrl1_p'].fillna(df['MovieUrl1_s'])
        df['MovieUrl2'] = df['MovieUrl2_p'].fillna(df['MovieUrl2_s'])
        df['SiteUrl'] = df['SiteUrl_p'].fillna(df['SiteUrl_s'])

        df['ModelLife'] = df['ModelLife_p_detail'].fillna(df['ModelLife_s_detail'])
        df['GrossProfit'] = df['GrossProfit_p_detail'].fillna(df['GrossProfit_s_detail'])

        for x in ['MovieUrl1', 'MovieUrl2', 'SiteUrl']:
            df = df.drop(columns=[x + '_s', x + '_p'])

        for x in ['ModelLife', 'GrossProfit']:
            df = df.drop(columns=[x + '_s_detail', x + '_p_detail'])

        return df, df_katashiki_frame_relation, df_frame