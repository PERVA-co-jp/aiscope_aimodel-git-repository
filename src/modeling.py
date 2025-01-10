import numpy as np
import json
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import lightgbm as lgb
from data_columns.features_and_targets import targets_eval

class modeling:
    def __init__(self, features, targets):
        self.features = features
        self.targets = targets

    def train(self, df_train, target, params=None, model_kind='random_forest_regressor'):

        if params == None:
            params = {"random_state": 42}

        if model_kind == 'random_forest_regressor':
            model = RandomForestRegressor(**params)        
        elif model_kind == 'random_forest_classifier':
            model = RandomForestClassifier(**params)
        elif model_kind == 'lightgbm_regressor':
            model = lgb.LGBMRegressor(**params)
        elif model_kind == 'lightgbm_classifier':
            model = lgb.LGBMClassifier(**params)

        model.fit(df_train[self.features], df_train[target])

        return model
    
    def train_all(self, df_train, all_params=None, model_kind='random_forest_regressor'):
        models = {}
        for target in self.targets:
            model = self.train(df_train,
                               target,
                               params=all_params[target]['best_params'] if all_params is not None else None,
                               model_kind=model_kind)
            models[target] = model
        return models
    
    def load_and_train_all(self, df_train, param_path, model_kind='random_forest_regressor'):

        f = open(param_path)
        all_params = json.load(f)

        models = self.train_all(df_train, all_params, model_kind=model_kind)
        return models
    
    def predict_all(self, models, df_test, contain_target=True):

        if contain_target:
            df_output = df_test[['KatashikiId', 'Kind']+self.targets].copy()
        else:
            df_output = df_test[['KatashikiId', 'Kind']].copy()

        for target in self.targets:

            y_pred = models[target].predict(df_test[self.features])

            df_output[target + '_pred'] = y_pred

            if target in targets_eval:
                # 出力を0.05刻みにする
                df_output[target+'_pred'] = df_output[target+'_pred'].apply(lambda x : self.round_x(x))
            
        return df_output
    
    def round_x(self, x):
        """
        0.05刻みにする。
        """
        frac_x = np.round(x % 1, 3)
        
        for d in np.arange(0.05, 1.05, 0.05):
            if d >= frac_x:
                y = d if (d - frac_x <= 0.025) else d - 0.05
                break
        
        x = int(x) + y
        return x

