from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse

from datetime import datetime
import pickle

from app.models import PredictionInput
from app.utils import transform_into_success_response_format, transform_into_unsuccessful_format

from src.data_extraction_operator import DataExtractionOperator
#from src.data_dev_extraction_operator import DevDataExtractionOperator

from src.data_processing_operator import DataProcessingOperator
from src.data_brand_operator import BrandDataProcessing
from src.data_insert_update import DataInsertUpdate
from src.modeling import modeling

from data_columns.features_and_targets import features, targets_eval, targets_profit
from data_columns.dictionary_of_columns import cols_map # TODO 応急処置。

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

import json
with open('newest_version_and_current_paths.json', 'r') as file:
    dict_paths = json.load(file)

with open(dict_paths['model_eval_in_use'], 'rb') as handle:
    models_gbm = pickle.load(handle)
with open(dict_paths['model_profit_in_use'], 'rb') as handle:
    models_profit_gbm = pickle.load(handle)

app = FastAPI()

API_KEY = config['app']['api_key']

def get_api_key(x_api_key: str = Header(None)):
    if x_api_key is None:
        raise HTTPException(status_code=400, detail="APIキーが必要です。")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="APIキーが正しくありません。")
    return x_api_key

@app.post("/get-data-ai")
def predict(input_data: PredictionInput, api_key: str = Depends(get_api_key)):
    
    today_date = datetime.today().strftime('%Y-%m-%d')
    ymdHMS = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    # データの抽 
    df, df_katashiki_frame_relation, df_frame = DataExtractionOperator(end_date=today_date, start_date='2015-01-01', training=False).extract_and_process()
    #df, df_katashiki_frame_relation, df_frame = DevDataExtractionOperator(end_date=today_date, start_date='2015-01-01', training=False).extract_and_process()

    # ブランドマスターの更新
    df_brand_list = BrandDataProcessing(api_key=config['openai']['api_key']).create_if_nan(df, 'data_processing_files/brand_list.csv')
    df_brand_list.to_csv('data_processing_files/brand_list.csv', index=False) 
    
    # 推論用データ作成
    df = DataProcessingOperator(today_date, training=False).process(
                                                                    df,
                                                                    df_katashiki_frame_relation,
                                                                    df_frame,
                                                                    df_brand_list)
    
    # 対象IDに絞る
    target_ids = input_data.KatashikiIds
    df = df[df['KatashikiId'].isin(target_ids)]
    target_existing_ids = df['KatashikiId'].tolist()
    target_non_existing_ids = [x for x in target_ids if x not in target_existing_ids]

    if len(df) > 0:
        df_output = modeling(features,
                            targets=targets_eval).predict_all(models_gbm, df, contain_target=False)

        df_output_profit = modeling(features,
                                    targets=targets_profit).predict_all(models_profit_gbm, df, contain_target=False)

        dict_evals = df_output.rename(columns=cols_map).drop(columns='Kind').set_index('KatashikiId').to_dict('index')
        dict_profits = df_output_profit.rename(columns=cols_map).drop(columns='Kind').set_index('KatashikiId').to_dict('index')

        merged_dict = dict_evals.copy()
        for key in merged_dict:
            merged_dict[key].update(dict_profits[key])

        # データテーブルに挿入または更新
        DataInsertUpdate().process(target_existing_ids, merged_dict)

        list_response_data = transform_into_success_response_format(merged_dict, ymdHMS)

        if len(target_non_existing_ids) > 0:
            list_unsuccess_response = transform_into_unsuccessful_format(target_non_existing_ids)
            list_response_data.extend(list_unsuccess_response)

        return {'status' : 200,
                'data' : list_response_data}
    
    else:
        return {'status': 404,
                'message': 'Not found',
                'data': None}

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "message": exc.detail,
            "data": None
        },
    )

@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "message": "例外処理が行われていない箇所で何らかのエラーが起きました。",
            "data": None
        },
    )