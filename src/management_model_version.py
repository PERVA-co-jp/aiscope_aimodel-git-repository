import json
from datetime import datetime
import pandas as pd
import os

class management_model_version:
    def __init__(self, version_file, version_history_file, update_key):
        self.version_file = version_file
        self.version_history_file = version_history_file
        self.update_key = update_key

        with open(version_file, "r") as file:
            self.version_index = json.load(file)
        
        current_datetime = datetime.now()
        self.formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
        self.registered_at = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")

        self.hyperparameter, self.training = self.get_new_version()
        self.model_suffix, self.param_suffix = self.get_model_version_name(self.hyperparameter,
                                                                        self.training)
        
        # tempフォルダに使用中バージョンと前のバージョンを保存
        if not os.path.exists('temp'):
            os.makedirs('temp')
        self.df_history = pd.read_csv(version_history_file)
        
        if len(self.df_history) == 0:
            prev_model_version = 'No_model'
        else:
            prev_model_version = self.df_history['model_version'].iloc[-1]
        
        with open("temp/prev_and_new_versions.txt", "w") as file:
            file.write(f"{prev_model_version},{self.model_suffix}")

    def get_new_version(self):
        hyperparameter = self.version_index['hyperparameter']
        training = self.version_index['training']

        if self.update_key == 'tuning':
            hyperparameter += 1
            training = 1 # １から始まる
        if self.update_key == 'training':
            training += 1
        return hyperparameter, training
    
    def get_model_version_name(self, hyperparameter, training):

        model_suffix = str(hyperparameter) + '_' + str(training) + '_' + self.formatted_datetime
        param_suffix = str(hyperparameter) + '_' + self.formatted_datetime

        return model_suffix, param_suffix
    
    def get_current_paths(self):
        return self.version_index
    
    def get_path_names(self):

        model_eval_pkl = f'output_train/{self.model_suffix}/models_evaluation_{self.model_suffix}.pickle'
        model_profit_pkl = f'output_train/{self.model_suffix}/models_profit_{self.model_suffix}.pickle'

        model_eval_hyperparameter = f'output_train/best_parameters_lightgbm_{self.param_suffix}.json'
        model_profit_hyperparameter = f'output_train/best_parameters_profit_lightgbm_{self.param_suffix}.json'

        evaluation_path = f'output_train/{self.model_suffix}/evaluation'

        #train_test_data = f'output_train/{self.model_suffix}/train_test_dataset_{self.model_suffix}.csv'
        train_data = f'output_train/{self.model_suffix}/train_dataset_{self.model_suffix}.csv'
        test_data = f'output_train/{self.model_suffix}/test_dataset_{self.model_suffix}.csv'

        return {'model_eval_pkl': model_eval_pkl,
                'model_profit_pkl' : model_profit_pkl, 
                'model_eval_hyperparameter' : model_eval_hyperparameter,
                'model_profit_hyperparameter' : model_profit_hyperparameter,
                'evaluation_path' : evaluation_path,
                'train_data' : train_data,
                'test_data' : test_data}

    def get_updated_status_file(self):

        self.version_index['hyperparameter'] = self.hyperparameter
        self.version_index['training'] = self.training

        dict_path = self.get_path_names()

        self.version_index["model_eval_in_use"] = dict_path['model_eval_pkl']
        self.version_index["model_profit_in_use"] = dict_path['model_profit_pkl']
        self.version_index["evaluation_folder_in_use"] = dict_path['evaluation_path']
        self.version_index["train_data"] = dict_path['train_data']
        self.version_index["test_data"] = dict_path['test_data']

        if self.update_key == 'tuning':
            self.version_index["hyperparameters_eval_in_use"] = dict_path['model_eval_hyperparameter']
            self.version_index["hyperparameters_profit_in_use"] = dict_path['model_profit_hyperparameter']

        return self.version_index

    def update_status_file(self):
        updated_file_status = self.get_updated_status_file()
        with open(self.version_file, "w") as file:
            json.dump(updated_file_status, file, indent=4) 

    def update_history_file(self):
        data = {'registered_at' : [self.registered_at], 'model_version' : [self.model_suffix]}
        df = pd.DataFrame(data)
        df = pd.concat([self.df_history, df])

        print()

        df.to_csv(self.version_history_file, index=False)