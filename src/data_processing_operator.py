from sklearn.preprocessing import OrdinalEncoder
import pandas as pd
import numpy as np
import re
import pickle
import os
from data_columns.dictionary_of_columns import cols
from data_columns.features_and_targets import targets_eval, targets_profit

class DataProcessingOperator:
    def __init__(self, date_for_recency, training=True):

        self.date_for_recency = pd.to_datetime(date_for_recency)
        self.training = training
    
    def extract_floats_with_pattern(self, pattern, n_groups, input_string):
        match = re.search(pattern, input_string)
        if match:
            results = [match.group(j) for j in range(1, n_groups+1)]
            for j in range(n_groups):
                if '/' in results[j]:
                    numerator, denominator = results[j].split('/')
                    x = float(numerator) / float(denominator)
                else:
                    x = float(results[j])
                results[j] = x 
        else:
            results = [None] * n_groups
        return results if n_groups > 1 else results[0]
    
    def convert_to_float(self, df, cols):
        for col in cols:
            df[col] = df[col].astype(float)
        return df

    def extract_floats(self, df):

        df[['BigRate' + '_extracted_1', 'BigRate' + '_extracted_2']] = df['BigRate'].fillna('None').apply(
            lambda x : self.extract_floats_with_pattern(
                r'(\d+/\d+\.?\d*).+→.+(\d+/\d+\.?\d*)', 2, x)).apply(pd.Series)

        df = df.drop(columns=['BigRate'])

        df['SmallRate' + '_extracted'] = df['SmallRate'].fillna('None').apply(
            lambda x : self.extract_floats_with_pattern(
                r'(\d+/\d+\.?\d*)', 1, x))
        
        df = df.drop(columns=['SmallRate'])

        df['KakuhenRate1_3' + '_extracted'] = df['KakuhenRate1_3'].fillna('None').apply(
            lambda x : self.extract_floats_with_pattern(
                r'(\d+\.?\d*)', 1, x))

        df = df.drop(columns=['KakuhenRate1_3'])

        df['SaleUnitOther' + '_extracted'] = df['SaleUnitOther'].fillna('None').apply(
            lambda x : self.extract_floats_with_pattern(
                r'(\d+)台予定', 1, x))
        
        df = df.drop(columns=['SaleUnitOther'])

        for bonus in cols['BonusValues']:
            df[bonus] = df[bonus].fillna('None').apply(lambda x : self.extract_floats_with_pattern(r'(\d+/?\d*\.?\d*)', 1, x))

        return df
        
    def append_1_or_0_if_exists(self, x):
        if x not in [None, '', np.nan]:
            return 1
        return 0

    def extract_color(self, df, df_katashiki_frame_relation, df_frame):
        # katashikiIdとframeIdはone-to-manyの関係
        df_frame_color = pd.merge(df_katashiki_frame_relation, df_frame, on=cols['FrameId'], how='left')
        
        # Colorのカラムの中になぜかNameがそのまま入るレコードがあるため削除をする
        df_frame_color = pd.merge(df_frame_color,
                                  df[['KatashikiId', 'Name']],
                                  on='KatashikiId', how='left')
        df_frame_color = df_frame_color[df_frame_color['Name'] != df_frame_color['Color']]
        df_frame_color = df_frame_color.drop(columns='Name')

        # カラー名（string）を足し合わせる
        df_frame_color = df_frame_color.sort_values(by=['KatashikiId', 'Color'])
        df_color_string = df_frame_color.groupby('KatashikiId')['Color'].agg(lambda x:','.join(x)).reset_index()
        df_color_count = df_frame_color.groupby('KatashikiId').count()[['Color']].reset_index()

        df_color_count = df_color_count.rename(columns={'Color' : 'Color_Variations'})

        df_color = pd.merge(df_color_string, df_color_count, on='KatashikiId')
        return df_color

    def convert_to_categorical_values(self, df, training):
        
        cols_encoding = ['Color', 'TypeName', 'TypeName_detail', 'brand_name']
        new_cols_encoding = [col + '_Encoded' for col in cols_encoding]

        if training:
            enc = OrdinalEncoder(handle_unknown="use_encoded_value",
                                unknown_value=-1,
                                encoded_missing_value=-1)

            # カテゴリカル変数を整数値に変換
            df[new_cols_encoding] = enc.fit_transform(df[cols_encoding])

            if not os.path.exists('data_processing_files'):
                os.makedirs('data_processing_files')

            with open('data_processing_files/enc_model.pickle', 'wb') as handle:
                pickle.dump(enc, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:

            with open('data_processing_files/enc_model.pickle', 'rb') as handle:
                enc = pickle.load(handle)
           
            # カテゴリカル変数を整数値に変換
            df[new_cols_encoding] = enc.transform(df[cols_encoding])

        return df

    def calculate_and_append_mean_values(self, df, col_groupby, cols_calculation):

        df = df.sort_values(by=[col_groupby, 'Regist_Date'], ascending=[True, True]).reset_index(drop=True)
        
        periods = ['90days', '365days', 'all_past']
        new_columns = []
        for col in cols_calculation:
            for period in periods:
        
                col_new = col + '_' + period + '_mean_per_' + col_groupby
                new_columns.append(col_new)
                
                if period == '90days':
                    N = 90
                elif period == '365days':
                    N = 365
                else:
                    N = (df['Regist_Date'].max() - df['Regist_Date'].min()).days
        
                df[col_new] = df.groupby(col_groupby)[[col_groupby,'Regist_Date', col]].rolling(
                                window=str(N)+'D', on='Regist_Date', closed='left').mean().reset_index()[col]
        
        return df

    def process(self, df, df_katashiki_frame_relation, df_frame, df_brand_list):

        # オブジェクト型カラムをfloat型に変換
        df = self.convert_to_float(df,
            ['KakuhenRate1_1', 'KakuhenRate1_2', 'EquivalentBranch',
            'TamaUnitPrice', 'CoinUnit', 'GameUnit'])

        # オブジェクト型カラムから正規表現により数値を抽出
        df = self.extract_floats(df)

        # 商品のURLが存在するかフラグを立てる
        for url in ["MovieUrl1", "MovieUrl2"]:  #"SiteUlr"
            df[url + '_flag'] = df[url].apply(lambda x : self.append_1_or_0_if_exists(x))
            df = df.drop(columns=[url])
       
        # 年月日を特徴量にする
        df['Regist_Date'] = pd.to_datetime(df['Regist_Date'])
        df['Regist_Date_year'] = df['Regist_Date'].dt.year
        df['Regist_Date_month'] = df['Regist_Date'].dt.month
        df['Regist_Date_days'] = df['Regist_Date'].dt.day

        # Recencyの計算
        df['recency'] = (df['Regist_Date'] - self.date_for_recency).dt.days

        # 各型式のフレームカラー情報
        df = pd.merge(df, 
                      self.extract_color(df.copy(), df_katashiki_frame_relation, df_frame),
                      on='KatashikiId', how='left')

        # ブランドデータの結合
        df = pd.merge(df, df_brand_list, on='Name', how='left')

        # カテゴリを整数に変換
        df = self.convert_to_categorical_values(df, self.training)

        # 過去の平均値を計算
        cols_calculation = targets_eval + targets_profit
        if self.training:
            # 外れ値は排除
            df = df[df['Price_eval'] >= 0]  # TODO データベースのチェック中
            df = df[df['GrossProfit'] > 0]
            df = df[df['ModelLife'] > 0]  # TODO データベースのチェック中
                        
        else:
            # 外れ値はNaNとして、レコードとして残すが過去計算では無視される
            df.loc[df['Price_eval'] < 0, 'Price_eval'] = None
            df.loc[df['GrossProfit'] <= 0, 'GrossProfit'] = None
            df.loc[df['ModelLife'] <= 0, 'ModelLife'] = None
        # ここで計算
        df = self.calculate_and_append_mean_values(df, 'MakerId', cols_calculation)
        df = self.calculate_and_append_mean_values(df, 'brand_name', cols_calculation)

        return df