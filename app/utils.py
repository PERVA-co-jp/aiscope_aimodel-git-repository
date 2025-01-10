def transform_into_success_response_format(dict_data, date):
    
    list_data = []
    for key in list(dict_data.keys()):
        data = {
            'KatashikiId' : key,
            'message' : 'データの取得に成功しました。',
            'data' : {
                    'KatashikiId' : key,
                    'GrossProfit' : int(dict_data[key]['GrossProfit']),
                    'Concept' : truncate_decimals(dict_data[key]['Concept']),
                    'Performance' : truncate_decimals(dict_data[key]['Performance']),
                    'Content' : truncate_decimals(dict_data[key]['Content']),
                    'SaleUnit' : truncate_decimals(dict_data[key]['SaleUnit']),
                    'Spec' : truncate_decimals(dict_data[key]['Spec']),
                    'Period' : truncate_decimals(dict_data[key]['Period']),
                    'News' : truncate_decimals(dict_data[key]['News']),
                    'Running' : truncate_decimals(dict_data[key]['Running']),
                    'Returns' : truncate_decimals(dict_data[key]['Returns']),
                    'Price' : truncate_decimals(dict_data[key]['Price']),
                    'ModelLife' : truncate_decimals(dict_data[key]['ModelLife']),
                    'RegistDate' : date}
        }
    
        list_data.append(data)
    return list_data

def transform_into_unsuccessful_format(katashikiIds):
    list_unsuccess_response = []
    for x in katashikiIds:
        list_unsuccess_response.append(
            {'katashikiId' : x,
                'message' : '該当するデータが見つかりませんでした。',
                'data' : None})
    return list_unsuccess_response

def truncate_decimals(x):
    return int(x * 100) / 100