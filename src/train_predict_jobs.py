import pandas as pd
from datetime import datetime
import configparser
import pandas as pd
import pickle
import os
import shutil

from src.data_extraction_operator import DataExtractionOperator
from src.data_dev_extraction_operator import DevDataExtractionOperator
from src.data_brand_operator import BrandDataProcessing
from src.data_processing_operator import DataProcessingOperator
from src.hyperparameters_tuning import model_tuning
from data_columns.dictionary_of_columns import cols
from data_columns.features_and_targets import features, targets_eval, targets_profit
from src.modeling import modeling
from src.evaluation import evaluation
from src.management_model_version import management_model_version
from src.management_model_detail_log import management_model_detail_log

config = configparser.ConfigParser()
config.read('config.ini')

def train_test_split_time_series(df, split_datetime='2024-01-01'):
    df = df.sort_values(by='Regist_Date')

    df_train = df[df['Regist_Date'] < pd.to_datetime(split_datetime)]
    df_test = df[df['Regist_Date'] >= pd.to_datetime(split_datetime)]
    return df_train, df_test

def train(current_date, split_datetime='2024-01-01', update_model_history=False, hyperparameter_tuning=False, dev_database=False):

    if not os.path.exists('output_train'):
        os.makedirs('output_train')

    # データの抽出
    if dev_database == False:
        df, df_katashiki_frame_relation, df_frame = DataExtractionOperator(end_date=current_date, start_date='2015-01-01', training=True).extract_and_process()
    else:
        df, df_katashiki_frame_relation, df_frame = DevDataExtractionOperator(end_date=current_date, start_date='2015-01-01', training=True).extract_and_process()

    # ブランドマスターの更新
    ke = BrandDataProcessing(api_key=config['openai']['api_key'])
    df_brand_list = ke.create_if_nan(df, 'data_processing_files/brand_list.csv')
    df_brand_list.to_csv('data_processing_files/brand_list.csv', index=False) 

    # モデル構築用のデータ作成
    df_train_test = DataProcessingOperator(current_date, training=True).process(
                                                                                df.copy(),
                                                                                df_katashiki_frame_relation,
                                                                                df_frame,
                                                                                df_brand_list)

    # ---- モデル構築 ----
    df_train, df_test = train_test_split_time_series(df_train_test, split_datetime)

    print('train data length: ', len(df_train))
    print('test data length :', len(df_test))

    # 保存に使うファイル名を取得
    update_key = 'tuning' if hyperparameter_tuning else 'training'
    mmv = management_model_version('newest_version_and_current_paths.json', 'model_version_history.csv', update_key)

    # 更新されたパス
    path_dict = mmv.get_updated_status_file()

    if hyperparameter_tuning:
        # ハイパーパラメータのチューニング
        # スコア予測モデル
        model_tuning(
            file_path= path_dict['hyperparameters_eval_in_use']
            ).search_parameters(features,
                                targets_eval,
                                df_train,
                                model_kind='lightgbm_regressor',
                                n_trials=2, loss='rmse', n_searches=5,
                                random_states=[42, 34, 10, 2, 234]) 
        # 貢献週・粗利予測モデル
        model_tuning(
            file_path= path_dict['hyperparameters_profit_in_use']
            ).search_parameters(features,
                        targets_profit,
                        df_train,
                        model_kind='lightgbm_regressor_poisson',
                        n_trials=2, loss='rmse', n_searches=5,
                        random_states=[42, 34, 10, 2, 234]) 

    # --- モデルの評価（パラメータを読み込んでテストデータに予測）---
    m = modeling(features, targets=targets_eval)
    models_gbm = m.load_and_train_all(df_train,
                                param_path= path_dict['hyperparameters_eval_in_use'],
                                model_kind='lightgbm_regressor')
    df_output_gbm = m.predict_all(models_gbm, df_test)
    df_output_gbm_train = m.predict_all(models_gbm, df_train)

    m_profit = modeling(features, targets=targets_profit)
    models_profit_gbm = m_profit.load_and_train_all(df_train,
                                param_path= path_dict['hyperparameters_profit_in_use'],
                                model_kind='lightgbm_regressor')
    df_output_profit_gbm = m_profit.predict_all(models_profit_gbm, df_test)
    df_output_profit_gbm_train = m_profit.predict_all(models_profit_gbm, df_train)

    # ここで評価
    path_evaluation = path_dict['evaluation_folder_in_use']
    if not os.path.exists(path_evaluation):
        os.makedirs(path_evaluation)
    evaluation(path_evaluation).generate(df_output_gbm, models_gbm, features, setting='スコア予測モデル', suffix='テスト')
    evaluation(path_evaluation).generate(df_output_gbm_train, models_gbm, features, setting='スコア予測モデル', suffix='学習')

    evaluation(path_evaluation).generate(df_output_profit_gbm, models_profit_gbm, features, setting='貢献週・粗利予測', suffix='テスト')
    evaluation(path_evaluation).generate(df_output_profit_gbm_train, models_profit_gbm, features, setting='貢献週・粗利予測', suffix='学習')

    # 全てのデータに学習して保存
    models_gbm = m.load_and_train_all(df_train_test,
                                param_path= path_dict['hyperparameters_eval_in_use'],
                                model_kind='lightgbm_regressor')
    models_profit_gbm = m_profit.load_and_train_all(df_train_test,
                                param_path= path_dict['hyperparameters_profit_in_use'],
                                model_kind='lightgbm_regressor')
    
    with open(path_dict['model_eval_in_use'], 'wb') as handle:
        pickle.dump(models_gbm, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(path_dict['model_profit_in_use'], 'wb') as handle:
        pickle.dump(models_profit_gbm, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # 学習・テストデータの保存
    df_train.to_csv(path_dict['train_data'], index=False)
    df_test.to_csv(path_dict['test_data'], index=False)
    
    # ブランドデータとカテゴリデータの保存
    shutil.copy("data_processing_files/brand_list.csv", f"output_train/{mmv.model_suffix}")
    shutil.copy("data_processing_files/enc_model.pickle", f"output_train/{mmv.model_suffix}")

    # モデルの履歴を更新
    if update_model_history:
        mmv.update_status_file()
        mmv.update_history_file()
        
    # パスファイルの保存
    import json
    with open('output_train/' + mmv.model_suffix +'/paths.json', "w") as file:
        json.dump(mmv.get_updated_status_file(), file, indent=4) 
    
    return df_train_test

def predict(current_date, dev_database=False):
    # 一度はtrainを起動したと想定
    
    if not os.path.exists('output_predict'):
        os.makedirs('output_predict')

    # データの抽出
    if dev_database == False:
        df, df_katashiki_frame_relation, df_frame = DataExtractionOperator(end_date=current_date, start_date='2010-01-01', training=False).extract_and_process()
    else:
        df, df_katashiki_frame_relation, df_frame = DevDataExtractionOperator(end_date=current_date, start_date='2010-01-01', training=False).extract_and_process()

    # ブランドマスターの更新
    ke = BrandDataProcessing(api_key=config['openai']['api_key'])
    df_brand_list = ke.create_if_nan(df, 'data_processing_files/brand_list.csv')
    df_brand_list.to_csv('data_processing_files/brand_list.csv', index=False) 

    # 推論用データ作成
    df = DataProcessingOperator(current_date, training=False).process(
                                                                    df,
                                                                    df_katashiki_frame_relation,
                                                                    df_frame,
                                                                    df_brand_list)
    
    df.to_csv('output_predict/prediction_features.csv', index=False)

    import json
    with open('newest_version_and_current_paths.json', "r") as file:
        paths = json.load(file)

    # --- モデルを読み込んで推論---
    with open(paths['model_eval_in_use'], 'rb') as handle:
        models_gbm = pickle.load(handle)
    with open(paths['model_profit_in_use'], 'rb') as handle:
        models_profit_gbm = pickle.load(handle)

    m = modeling(features, targets=targets_eval)
    df_output = m.predict_all(models_gbm, df, contain_target=False)

    m_profit = modeling(features, targets=targets_profit)
    df_output_profit = m_profit.predict_all(models_profit_gbm, df, contain_target=False)

    df_output.to_csv('output_predict/prediction_scores.csv', index=False)
    df_output_profit.to_csv('output_predict/prediction_profit.csv', index=False)

    return df_output, df_output_profit, df

if __name__ == "__main__":
    from datetime import datetime, timedelta
    today_date = datetime.today().strftime('%Y-%m-%d')
    split_datetime = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')

    import sys
    # ハイパーパラメータチューニングを行うかどうか
    arg1 = sys.argv[1]
    # モデルの履歴を更新するか
    arg2 = sys.argv[2]

    if arg1 == 'True':
        arg1 = True
    else:
        arg1 = False
    
    if arg2 == 'True':
        arg2 = True
    else:
        arg2 = False

    train(today_date, split_datetime=split_datetime, update_model_history=arg2, hyperparameter_tuning=arg1, dev_database=False)
