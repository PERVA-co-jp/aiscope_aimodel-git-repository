import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
from data_columns.en_jp_dictionary import targets_jp, features_jp
import matplotlib.pylab as plt
import seaborn as sns
import japanize_matplotlib
import pickle
from data_columns.dictionary_of_columns import cols
from data_columns.features_and_targets import targets_eval, targets_profit

class evaluation:
    def __init__(self, folder_directory):
        self.folder_directory = folder_directory
        
    def evaluate_all(self, df, targets, eval_types=['rmse', 'r2']):
        """
        rmseと決定係数をパチンコ、スロット、全体に分けて計算。
        """
        
        df_all_kinds = pd.DataFrame()
        df_all_kinds['targets'] = [targets_jp[x] for x in targets]    
        df_slot = pd.DataFrame()
        df_slot['targets'] = [targets_jp[x] for x in targets]    
        df_pachinko = pd.DataFrame()
        df_pachinko['targets'] = [targets_jp[x] for x in targets]    

        for eval_type in eval_types:
            df_all_kinds = pd.merge(df_all_kinds, self.evaluate(df, targets, eval_type=eval_type, slot_or_pachinko=[0, 1]), on='targets')
            df_slot = pd.merge(df_slot, self.evaluate(df, targets, eval_type=eval_type, slot_or_pachinko=[1]), on='targets')
            df_pachinko = pd.merge(df_pachinko, self.evaluate(df, targets, eval_type=eval_type, slot_or_pachinko=[0]), on='targets')

        return df_all_kinds, df_slot, df_pachinko

    def evaluate(self, df, targets, eval_type, slot_or_pachinko=[0, 1]):

        if eval_type == 'rmse':
            func = lambda x, y : mean_squared_error(x, y, squared=False)
            type_name = 'RMSE'
        elif eval_type == 'r2':
            func = r2_score
            type_name = '決定係数'
        elif eval_type == 'accuracy':
            func = accuracy_score
            type_name = '正解率'

        list_eval = []
        for target in targets:
            y_actual = df[df['Kind'].isin(slot_or_pachinko)][target]
            y_pred = df[df['Kind'].isin(slot_or_pachinko)][target + '_' + 'pred']
            
            list_eval.append(func(y_actual, y_pred))

        # 評価テーブルの作成
        df_eval = pd.DataFrame()
        df_eval['targets'] = [targets_jp[x] for x in targets]
        df_eval[type_name] = list_eval
        return df_eval

    def plot_feature_importance(self, models, targets, features, N=8, fig_N_rows=2, fig_N_cols=5, figsize=(40, 12)):
        df_fea_eval = pd.DataFrame(columns=['features'], data=features)
        for target in targets:
            
            importances = models[target].feature_importances_

            df_fea_eval = pd.concat([df_fea_eval, pd.DataFrame(columns=[target], data=importances)], axis=1)

        sns.set_theme('talk', 'whitegrid', 'dark', font_scale=1.0, rc={"lines.linewidth": 2, 'grid.linestyle': '--'}) 
        japanize_matplotlib.japanize()

        fig, axs = plt.subplots(fig_N_rows, fig_N_cols, figsize=figsize)
        for ax, target in zip(axs.flatten(), targets):
            
            df_fea_eval = df_fea_eval.sort_values(by=target, ascending=True)
            ax.barh(df_fea_eval['features'].iloc[-N:], df_fea_eval[target].iloc[-N:])
            ax.set_title(targets_jp[target])
            ax.set_yticks(range(N))

            list_features = [features_jp[x] for x in df_fea_eval['features'].iloc[-N:].tolist()]
            
            ax.set_yticklabels(list_features, ha="right") 
        fig.tight_layout()
        return fig

    def create_confusion_matrix(self, df, min_value, max_value, N, target):

        bin_edges = np.linspace(min_value, max_value, N)        
        bin_labels = [f"({bin_edges[i]}, {bin_edges[i+1]}]" for i in range(len(bin_edges)-1)]
        
        df[target + '_bin'] = pd.cut(df[target], bins=bin_edges, labels=bin_labels, include_lowest=False)
        df[target + '_pred_bin'] = pd.cut(df[target+'_pred'], bins=bin_edges, labels=bin_labels, include_lowest=False)
        
        confusion_matrix = pd.crosstab(df[target+'_bin'], df[target+'_pred_bin'], rownames=['Actual'], colnames=['Predicted'])
        
        complete_index = pd.Index(bin_labels, name='Actual')
        complete_columns = pd.Index(bin_labels, name='Predicted')
        
        confusion_matrix_full = confusion_matrix.reindex(index=complete_index, columns=complete_columns, fill_value=0)
        confusion_matrix_full = confusion_matrix_full.sort_index(ascending=False)
        
        return confusion_matrix_full

    def add_headmap_to_ax(self, ax, confusion_matrix, min_value, max_value, N, title, label_decimals, tick_labels):
        sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', ax=ax)

        ax.set_title(f"{targets_jp[title]}スコア")

        labels = np.linspace(min_value, max_value, N)
        ax.plot(range(N), N - 1 - np.array(range(N)), linestyle='--', color='gray')

        if tick_labels == None:
            ax.set_xticklabels(['%.{}f'.format(label_decimals) % label for label in labels[1:]], rotation=0)
            ax.set_yticklabels(np.flip(['%.{}f'.format(label_decimals) % label for label in labels[1:]]), rotation=0)
        else: 
            ax.set_xticklabels(tick_labels, rotation=0, fontsize=10)
            ax.set_yticklabels(np.flip(tick_labels), rotation=0, fontsize=10)
        
        ax.set_xlabel('予測値')
        ax.set_ylabel('実測値')
        return ax
        
    def make_multiple_heatmaps(self, df, min_value, max_value, N, targets, fig_N_rows=2, fig_N_cols=5, figsize=(32, 10), label_decimals=1, tick_labels=None):

        if type(min_value) != list:
            list_min_value = [min_value] * len(targets)
            list_max_value = [max_value] * len(targets)
            list_N = [N] * len(targets)
        else:
            list_min_value = min_value
            list_max_value = max_value
            list_N = N

        if type(tick_labels) != list:
            list_tick_labels = [None] * len(targets)
        else:
            list_tick_labels = tick_labels
        
        dict_confusion_matrices = {}
        for target, min_x, max_x, n in zip(targets, list_min_value, list_max_value, list_N):
            dict_confusion_matrices[target] = self.create_confusion_matrix(df, min_x, max_x, n, target)

        fig, axs = plt.subplots(fig_N_rows, fig_N_cols, figsize=figsize)
        for ax, title, min_x, max_x, n, confusion_matrix, tick_label in zip(
            axs.flatten(),
            targets,
            list_min_value,
            list_max_value,
            list_N,
            list(dict_confusion_matrices.values()),
            list_tick_labels
        ):
            ax = self.add_headmap_to_ax(ax, confusion_matrix, min_x, max_x, n, title, label_decimals, tick_label)

        plt.tight_layout()
        #plt.show()

        return fig

    def categorize(self, df):
        def categorize_modellife(x):
            if x >= 0 and x <= 6:
                return 1
            elif x >= 7 and x <= 9:
                return 2
            elif x >= 10 and x <= 13:
                return 3
            elif x >= 14 and x <= 17:
                return 4
            else:
                return 5

        def categorize_grossprofit(x):
            if x <= 200000:
                return 1
            elif x > 200000 and x <= 300000:
                return 2
            elif x > 300000 and x <= 400000:
                return 3
            elif x > 400000 and x <= 600000:
                return 4
            elif x > 600000 and x <= 800000:
                return 5
            else:
                return 6

        for target in targets_profit:
            func = categorize_modellife if target == 'ModelLife' else categorize_grossprofit
            df[target+'_category' + '_pred'] = df[target+'_pred'].apply(lambda x : func(x))
            df[target+'_category'] = df[target].apply(lambda x : func(x))
        return df

    def generate(self, df_output, models, features, setting='スコア予測モデル', suffix='テスト'):

        if setting == 'スコア予測モデル':
            df_all_kinds, df_slot, df_pachinko = self.evaluate_all(df_output, targets_eval, eval_types=['r2', 'rmse'])
            fig_importance = self.plot_feature_importance(models, targets_eval, features, N=8)
            fig_heatmap = self.make_multiple_heatmaps(df_output, 0, 4, 9, targets_eval)
            
            df_pachinko.to_csv(self.folder_directory + '/精度評価_パチンコ_スコア予測モデル_'+suffix+'.csv', index=False, encoding='utf-8_sig')
            df_slot.to_csv(self.folder_directory + '/精度評価_スロット__スコア予測モデル_'+suffix+'.csv', index=False, encoding='utf-8_sig')
            df_all_kinds.to_csv(self.folder_directory + '/精度評価_全体__スコア予測モデル_'+suffix+'.csv', index=False, encoding='utf-8_sig')

            fig_importance.savefig(self.folder_directory + '/寄与度_スコア予測モデル.png')
            fig_heatmap.savefig(self.folder_directory + '/ヒートマップ_スコア予測モデル.png')


        elif setting == '貢献週・粗利予測':
            # targetsが'ModelLife' と 'GrossProfit'の時
            df_all_kinds_regr, df_slot_regr, df_pachinko_regr = self.evaluate_all(df_output,
                                                                                  targets_profit,
                                                                                  eval_types=['r2', 'rmse'])
            
            df_output = self.categorize(df_output)
            df_all_kinds_category, df_slot_category, df_pachinko_category = self.evaluate_all(df_output,
                                                                        [x + '_category' for x in targets_profit],
                                                                        eval_types=['accuracy', 'rmse'])

            tick_labels = [['0-6週', '7-9週', '9-13週', '14-17週', '18週-'],
               ['-20万', '20-30万', '30-40万', '40-60万','60-80万', '80万-']]
            
            #tick_labels = [['-20万', '20-30万', '30-40万', '40-60万','60-80万', '80万-']]

            fig_heatmap = self.make_multiple_heatmaps(df_output, [0, 0], [5, 6], N=[6, 7],
                                          targets=[x + '_category' for x in targets_profit],
                                          fig_N_rows=1, fig_N_cols=2, figsize=(18, 7), label_decimals=0, tick_labels=tick_labels)

            #fig_heatmap = self.make_multiple_heatmaps(df_output, 0, 6, N=7,
            #                              targets=[x + '_category' for x in targets_profit],
            #                              fig_N_rows=1, fig_N_cols=2, figsize=(18, 7), label_decimals=0, tick_labels=tick_labels)

            fig_importance = self.plot_feature_importance(models,
                                                          targets=targets_profit,
                                                          features=features, N=8, fig_N_rows=1, fig_N_cols=2, figsize=(22, 8))

            df_pachinko_regr.to_csv(self.folder_directory + '/精度評価_パチンコ_貢献週・粗利予測_'+suffix+'.csv', index=False, encoding='utf-8_sig')
            df_slot_regr.to_csv(self.folder_directory + '/精度評価_スロット_貢献週・粗利予測_'+suffix+'.csv', index=False, encoding='utf-8_sig')
            df_all_kinds_regr.to_csv(self.folder_directory + '/精度評価_全体_貢献週・粗利予測_'+suffix+'.csv', index=False, encoding='utf-8_sig')
            #df_pachinko_category.to_csv(self.folder_directory + '/精度評価_パチンコ_貢献週・粗利予測_'+suffix+'.csv', index=False)
            #df_slot_category.to_csv(self.folder_directory + '/精度評価_スロット_貢献週・粗利予測_'+suffix+'.csv', index=False)
            #df_all_kinds_category.to_csv(self.folder_directory + '/精度評価_全体_貢献週・粗利予測_'+suffix+'.csv', index=False)

            fig_importance.savefig(self.folder_directory + '/寄与度_貢献週・粗利予測_'+suffix+'.png')
            fig_heatmap.savefig(self.folder_directory + '/ヒートマップ_貢献週・粗利予測_'+suffix+'.png')