import optuna
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
import json
import lightgbm as lgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

optuna.logging.set_verbosity(optuna.logging.WARNING)

class model_tuning:
    def __init__(self, file_path):
        self.file_path = file_path
        self.model = None

    def objective(self, trial, features, target,
                  df, model_kind='random_forest_regressor', loss='rmse'):
        
        if model_kind == 'random_forest_regressor' or model_kind == 'random_forest_classifier':
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 90, 300), 
                'max_depth': trial.suggest_int('max_depth', 3, 20), 
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 15),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10), 
                'max_features': trial.suggest_uniform('max_features', 0.3, 1.0), 
                'bootstrap': trial.suggest_categorical('bootstrap', [True]),  
                #'criterion': trial.suggest_categorical('criterion', ['mse', 'mae']),  
                'min_weight_fraction_leaf': trial.suggest_uniform('min_weight_fraction_leaf', 0.0, 0.2),  
                'max_leaf_nodes': trial.suggest_int('max_leaf_nodes', 50, 600), 
                'min_impurity_decrease': trial.suggest_uniform('min_impurity_decrease', 0.0, 0.2),  
                'random_state': 42  # Fixed random state for reproducibility
            }

        elif model_kind in['lightgbm_regressor', 'lightgbm_classifier', 'lightgbm_regressor_poisson']:
            # 今は範囲を狭くとっている
            params = {
                "boosting_type": trial.suggest_categorical("boosting_type", ["gbdt"]), #"gbdt", "dart", "goss"
                "num_leaves": trial.suggest_int("num_leaves", 20, 50),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "learning_rate": trial.suggest_float("learning_rate", 1e-2, 0.3, log=True), 
                #"num_boost_round": trial.suggest_int("num_boost_round", 100, 1000),
                "n_estimators": trial.suggest_int("n_estimators", 100, 1000), 
                "min_child_samples": trial.suggest_int("min_child_samples", 10, 50),
                "min_child_weight": trial.suggest_float("min_child_weight", 0.0005, 0.05),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 2.0),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 2.0),
                "max_bin": trial.suggest_int("max_bin", 100, 255),
                "lambda_l1": trial.suggest_float("lambda_l1", 0, 2.0),
                "lambda_l2": trial.suggest_float("lambda_l2", 0, 2.0),
                "random_state" : 42,
                "verbose" : -1,
            }

            if model_kind == 'lightgbm_regressor_poisson':
                params.update({'objective' : 'poisson',
                               'metric' : 'poisson'})
        
        df = df.sort_values(by='Regist_Date')
        
        X = df[features]
        y = df[target]

        # データ数が少ないため、交差検証を一旦避ける
        #tscv = TimeSeriesSplit(n_splits=3)

        #rmse_list = []
        #for train_index, test_index in tscv.split(X):
        split_N = int(0.8 * len(X))
        train_x, test_x = X.iloc[:split_N], X.iloc[split_N:]
        train_y, test_y = y.iloc[:split_N], y.iloc[split_N:]
        
        if model_kind == 'random_forest_regressor':
            self.model = RandomForestRegressor(**params)
        elif model_kind == 'random_forest_classifier':
            self.model = RandomForestClassifier(**params)
        elif model_kind in ['lightgbm_regressor', 'lightgbm_regressor_poisson']:
            self.model = lgb.LGBMRegressor(**params)
        elif model_kind == 'lightgbm_classifier':
            self.model = lgb.LGBMClassifier(**params)

        self.model.fit(train_x, train_y)
        preds = self.model.predict(test_x)

        if loss == 'rmse':
            loss_value = mean_squared_error(test_y, preds, squared=False)
        elif loss == 'f1_macro':
            loss_value = f1_score(test_y, preds, average='macro')
        elif loss == 'f1_weighted':
            loss_value = f1_score(test_y, preds, average='weighted')
        elif loss == 'poisson':
            
            def poisson_loss(y_true, y_pred):
                # Add a small constant to y_pred to prevent log(0)
                epsilon = 1e-10
                y_pred = np.clip(y_pred, epsilon, None)
                
                loss = np.mean(y_pred - y_true * np.log(y_pred))
                return loss
            
            loss_value = poisson_loss(test_y.to_numpy(), preds)

        #loss_value_list.append(loss_value)
        #mean_loss = np.mean(loss_value_list)
        trial.set_user_attr(loss, loss_value)
        
        return loss_value

    def tune_models(self, features, targets, df, model_kind='random_forest_regressor', n_trials=200, loss='rmse', random_state=42):
        dict_output = {}

        if loss in ['rmse', 'poisson']:
            direction = 'minimize'
        else:
            direction = 'maximize'

        print('最適化:', direction, '', loss)
        for target in targets:
            print('---', target, '---')
            study = optuna.create_study(direction='minimize',
                                        sampler=optuna.samplers.TPESampler(seed=random_state))
            
            study.optimize(lambda x: self.objective(x, features, target, df, model_kind=model_kind, loss=loss),
                        n_trials=n_trials)

            best_trial = study.best_trial

            dict_output[target] = {}
            dict_output[target]['best_trial_num'] = best_trial.number
            dict_output[target]['best_loss'] = best_trial.value
            dict_output[target]['direction'] = direction
            dict_output[target]['best_params'] = self.model.set_params(**best_trial.params).get_params()

            print('trial:', best_trial.number)
            print('evaluation', ':', best_trial.value)
            print('ベストパラメータ:', best_trial.params)

        return dict_output

    def search_parameters(self, features, targets, df, model_kind='random_forest_regressor', n_trials=200, loss='rmse', n_searches=5, random_states=None):

        if random_states is None:
            random_states = [None] * n_searches

        if model_kind in ['random_forest_regressor', 'random_forest_classifier']:
            target_params = {
                'n_estimators': 'int', 
                'max_depth': 'int', 
                'min_samples_split': 'int',
                'min_samples_leaf': 'int', 
                'max_features': 'float', 
                'min_weight_fraction_leaf': 'float',  
                'max_leaf_nodes': 'int', 
                'min_impurity_decrease': 'float',  
            }
        elif model_kind in ['lightgbm_regressor', 'lightgbm_classifier', 'lightgbm_regressor_poisson']:
            target_params = {
                "num_leaves": 'int',
                "max_depth": 'int',
                "learning_rate": 'float', 
                "n_estimators": 'int', 
                "min_child_samples": 'int',
                "min_child_weight": 'float',
                "subsample": 'float',
                "colsample_bytree": 'float',
                "reg_alpha": 'float',
                "reg_lambda": 'float',
                "max_bin": 'int',
                "lambda_l1": 'float',
                "lambda_l2": 'float'}

        history = {}
        for n in range(n_searches):
            print('--------------')
            print("検索", n+1, "回目")

            dict_output = self.tune_models(features, targets, df, model_kind=model_kind, n_trials=n_trials, loss=loss, random_state=random_states[n])
            history[n] = dict_output
        
        # 平均値の計算
        """
        output = {}
        for target in targets:
            averaged_values = {}
            for param in list(target_params.keys()):
                list_params = []
                for n in range(n_searches):
                    list_params.append(history[n][target]['best_params'][param])
                
                #avg = np.mean(list_params)
                median = np.median(list_params)
         
                #if target_params[param] == 'int':
                #    median = int(median)
                
                averaged_values[param] = median
            
            output[target] = {'best_params': averaged_values}
        
            # その他パラメータ
            output[target]['best_params'].update({'random_state' : 42})
            if model_kind in ['lightgbm_regressor', 'lightgbm_classifier', 'lightgbm_regressor_poisson']:
                output[target]['best_params'].update({
                    "boosting_type" : 'gbdt',
                    "verbose" : -1
                })
        """
        
        output = {}
        for target in targets:
            list_loss = []
            for n in range(n_searches):
                list_loss.append(history[n][target]['best_loss'])
            
            if history[0][target]['direction'] == 'minimize':
                n_best = np.argmin(list_loss)
            elif history[0][target]['direction'] == 'maximize':
                n_best = np.argmax(list_loss)

            output[target] = history[n_best][target]
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        
        return history, output
