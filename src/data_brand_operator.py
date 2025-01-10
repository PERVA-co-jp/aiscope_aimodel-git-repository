import openai
from openai import OpenAI
import pandas as pd

class BrandDataProcessing:
    def __init__(self, api_key):

        self.client = OpenAI(api_key = api_key)
    def remove_first_last_alphabets(self, x):
        """
        明らかなパターンを処理
        例えば、

        Lパチスロ乃木坂46 UD -> パチスロ乃木坂46

        ・頭文字のアルファベットの除去
        ・語尾のアルファベットの除去（存在する場合）
        """
        list_text = x[1:].split(' ')
        if list_text[0] == '':
            list_text = list_text[1:]
        
        if len(list_text) > 1:
            list_text = list_text[:-1]
            text = ''.join(list_text)
        else:
            text = list_text[0]
        return text

    def prompt_template(self, input_name):
        """
        GPTに入力するテンプレート
        ・出力の形式をできるだけ一貫性のあるように工夫
        """
        #input_cleaned = self.remove_first_last_alphabets(input_name)
        
        print(input_name)

        template = f"""
    以下のテキストはパチンコもしくはスロット台の名称である。
    「{input_name}」

    上記の名称からブランド名を抽出してください。
    
    マンガ、ゲーム、アイドルの名前が使われたりします。
    例えば、名称が「真北斗無双第2章」だとすると、
    必ず以下の形で出力してください。
    ブランド名：真北斗無双

    他の例だと、
    「Pカイジ鉄骨渡り勝負編 V1B」の場合
    ブランド名：カイジ

    「P FAIRY TAIL2 JQD」の場合
    ブランド名：FAIRY TAIL
        """
        return template

    def get_completion(self, prompt):
        #response = openai.completions.create(
            #model = "gpt-3.5-turbo-instruct",
            #prompt = prompt,
            #max_tokens = 1000,
            #temperature = 0
        #)
        #result = response.choices[0].text.strip()

        response = self.client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt}
                ]}
            ],
            temperature=0.0)

        print(response.choices[0].message.content)

        return response.choices[0].message.content

    def remove_label(self, text):
        """
        GPT出力から「ブランド名：」を取り除く。
        """
        
        if 'ブランド名：' in text:
            text = text.replace('ブランド名：', '')
        return text

    def search_same_brand(self, list_brand_names):
        """
        表記揺れ（入れ子状態の場合）を統一する
        例えば、
        ゲゲゲの鬼太郎 獅子奮迅
        ゲゲゲの鬼太郎
        の2つがある場合、前者が後者を含むので、後者に統一する。

        TODO: 
        ちらほら統一できていないところがある
        例えば
        コードギアス反逆のルルーシュ
        コードギアス復活のルルーシュ
        少し高度化をすれば対処可能。
        """
        
        for i in range(len(list_brand_names)-1):
            for j in range(i+1, len(list_brand_names)):
                
                name_i = list_brand_names[i]
                name_j = list_brand_names[j]
        
                if name_i in name_j:
                    list_brand_names[j] = name_i
                    break
                if name_j in name_i:
                    list_brand_names[i] = name_j
                    break
        return list_brand_names
    
    def create(self, df):
        df['brand_name'] = df['Name'].apply(
            lambda x:self.get_completion(self.prompt_template(x)))
        
        df['brand_name'] = df['brand_name'].apply(
            lambda x:self.remove_label(x))
        
        list_brand_names = df['brand_name'].tolist()
        list_brand_names = self.search_same_brand(list_brand_names)
        df['brand_name'] = list_brand_names

        # ブランドリストを保存
        df_brand_list = df[['Name', 'brand_name']].sort_values(by='brand_name')
        #df_brand_list.to_csv(brand_output_path, index=False)

        return df_brand_list
    
    def create_if_nan(self, df, existing_brand_path):
        """
        ブランドテーブルと結合して、
        NaNにブランド名を埋める。

        dfの形式は
        Name | brand_name
        name1, NaN
        name2, NaN
        name3, brand_name1
        name4, brand_name2
        のようにbrand_nameがNanになっているところにブランド名を追加する。
        """
        df_brand_list = pd.read_csv(existing_brand_path)
        df_name = df[['Name']].copy()

        df_name = df_name.drop_duplicates(keep='first')
        df_brand_list = df_brand_list.drop_duplicates(keep='first')

        df_name = pd.merge(df_name, df_brand_list, on='Name', how='left')
        
        df_brand_name_null = df_name[df_name['brand_name'].isnull()]
        df_brand_name_null['brand_name'] = df_brand_name_null['Name'].apply(
            lambda x:self.get_completion(self.prompt_template(x)))
        df_brand_name_null['brand_name'] = df_brand_name_null['brand_name'].apply(
            lambda x: self.remove_label(x))
        
        df_name = pd.concat([df_name[~df_name['brand_name'].isnull()], df_brand_name_null])

        # 既存のリストと合わせてブランドリストを作り直す
        df_brand_list = pd.concat([df_brand_list, df_name])
        df_brand_list = df_brand_list.drop_duplicates(keep='first')
        list_brand_names = df_brand_list['brand_name'].tolist()
        list_brand_names = self.search_same_brand(list_brand_names)
        df_brand_list['brand_name'] = list_brand_names

        df_brand_list = df_brand_list.sort_values(by='brand_name')
        
        return df_brand_list