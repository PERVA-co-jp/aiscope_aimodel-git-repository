import json
import pandas as pd
from datetime import datetime
import shutil

class management_model_change:
    def __init__(self, target_mode_id):

        self.target_mode_id = target_mode_id

        with open(f"output_train/{target_mode_id}/paths.json", "r") as file:
            self.paths = json.load(file)
        
        current_datetime = datetime.now()
        self.formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
        self.registered_at = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")

        self.df_history = pd.read_csv('model_version_history.csv')
        prev_model_version = self.df_history['model_version'].iloc[-1]
        with open("temp/prev_and_new_versions.txt", "w") as file:
            file.write(f"{prev_model_version},{self.target_mode_id}")

    def force_change(self):

        new_info = self.paths

        with open('newest_version_and_current_paths.json', "w") as file:
            json.dump(new_info, file, indent=4)

    def update_history_file(self):
        data = {'registered_at' : [self.registered_at], 'model_version' : [self.target_mode_id]}
        df = pd.DataFrame(data)
        df = pd.concat([self.df_history, df])

        df.to_csv('model_version_history.csv', index=False)

    def load_brand_data(self):
	# ブランドデータとカテゴリデータの保存
        shutil.copy(f"output_train/{self.target_mode_id}/brand_list.csv", "data_processing_files")
        shutil.copy(f"output_train/{self.target_mode_id}/enc_model.pickle", "data_processing_files")

    def process(self):
        self.force_change()
        self.update_history_file()
        self.load_brand_data()

if __name__ == "__main__":
    import sys
    arg1 = sys.argv[1]

    mmc = management_model_change(arg1)
    mmc.process()
