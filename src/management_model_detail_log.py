
import pandas as pd
from datetime import datetime

class management_model_detail_log:
    def __init__(self, model_version, git_commit_hash):

        self.model_version = model_version
        self.git_commit_hash = git_commit_hash

        date_part = model_version.split('_')[-1]
        dt = datetime.strptime(date_part, "%Y%m%d%H%M%S")
        self.formatted_datetime = dt.strftime("%Y-%m-%d-%H-%M-%S")

        self.df = pd.read_csv('model_log.csv')

    def get_evaluation_info(self):

        evaluation_path = f'output_train/{self.model_version}/evaluation'
        evaluation_score_path = evaluation_path + '/' + '精度評価_全体__スコア予測モデル_テスト.csv'
        evaluation_profit_path = evaluation_path + '/' + '精度評価_全体_貢献週・粗利予測_テスト.csv'

        df_score = pd.read_csv(evaluation_score_path)
        df_profit = pd.read_csv(evaluation_profit_path)

        df_score = df_score.set_index('targets').T
        df_profit = df_profit.set_index('targets').T

        df_score = df_score.loc[['RMSE']]
        df_profit = df_profit.loc[['RMSE']]

        df_eval = df_score.join(df_profit)
        columns = [col + '_rmse' for col in df_eval.columns]
        df_eval.columns = columns
        df_eval = df_eval.reset_index(drop=True)
        return df_eval
    
    def get_basic_info(self):
        path_train = f'output_train/{self.model_version}/train_dataset_{self.model_version}.csv'
        path_test = f'output_train/{self.model_version}/test_dataset_{self.model_version}.csv'

        df_train = pd.read_csv(path_train)
        df_test = pd.read_csv(path_test)

        data = {
        'created_at' : [self.formatted_datetime],
        'model_version' : [self.model_version],
        'git_commit_hashID' : [self.git_commit_hash],
        'train_start_date' : [df_train['Regist_Date'].min()],
        'train_end_date': [df_train['Regist_Date'].max()],
        'test_start_date' : [df_test['Regist_Date'].min()],
        'test_end_date' : [df_test['Regist_Date'].max()],
        'train_records' : [len(df_train)],
        'test_records' : [len(df_test)]}

        return pd.DataFrame(data)
    
    def update(self):
        df_new_record = self.get_basic_info().join(self.get_evaluation_info())
        self.df = pd.concat([self.df, df_new_record])
        self.df.to_csv('model_log.csv', index=False, encoding='utf-8_sig')

if __name__ == "__main__":
    import sys
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]

    management_model_detail_log(arg1, arg2).update()
    