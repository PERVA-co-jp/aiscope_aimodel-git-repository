"""
各テーブルから分析対象となるカラムを指定する。
"""

"""
それぞれのテーブルのすべてのカラム一覧

re_m_katashiki
 ['KatashikiId', 'Name', 'Kind', 'MakerId', 'NairanFlag', 'NairanDate', 'NairanInfo', 
 'TenjiFlag', 'TenjiDate', 'TenjiInfo', 'ImagePath', 'ReleaseDate', 'ReleaseDateOther', 
 'SaleUnit', 'SaleUnitOther', 'Price', 'PriceDetail', 'HyoukaKatashikiId', 'NoDataFlag', 
 'OpenFlag', 'Regist_Date', 'Regist_User', 'Update_Date', 'Update_User', 'InspectDate', 
 'Note', 'MainFlag', 'InspectFlag', 'HyoukaOpenFlag', 'SimulationOpenFlag', 
 'SimulationDataFlag', 'NewModelNews_Flag', 'NewModelNews_Date', 'HyoukaOpenDate']


re_m_katashikidetailpachinko
 ['KatashikiId', 'BigRate', 'SmallRateLabel', 'SmallRate', 'WinBallCount', 'PayCount', 
 'KakuhenRate1_1', 'KakuhenRate1_2', 'KakuhenRate1_3', 'KakuhenRate2', 'KakuhenRate3', 
 'Jitan', 'TypeId1', 'TypeDetailId1', 'TypeId2', 'TypeDetailId2', 'MovieUlr1', 'MovieUlr2',
'SiteUlr', 'EquivalentBranch', 'ModelLife', 'GrossProfit', 'Regist_Date', 'Regist_User', 
'Update_Date', 'Update_User', 'Hold', 'ContinueCountAve', 'PayCountAve', 'TamaUnitPrice']

re_m_katashikidetailslot
 ['KatashikiId', 'SpecId', 'SpecDetail1', 'SpecDetail2', 'BonusLabel1', 'BonusLabel2', 
 'BonusLabel3', 'BonusLabel4', 'BonusLabel5', 'BonusFlag1_1', 'BonusValue1_1', 'BonusFlag1_2',
 'BonusValue1_2', 'BonusFlag1_3', 'BonusValue1_3', 'BonusFlag1_4', 'BonusValue1_4', 'BonusFlag1_5',
 'BonusValue1_5', 'BonusFlag2_1', 'BonusValue2_1', 'BonusFlag2_2', 'BonusValue2_2', 'BonusFlag2_3',
 'BonusValue2_3', 'BonusFlag2_4', 'BonusValue2_4', 'BonusFlag2_5', 'BonusValue2_5', 'BonusFlag3_1',
 'BonusValue3_1', 'BonusFlag3_2', 'BonusValue3_2', 'BonusFlag3_3', 'BonusValue3_3', 'BonusFlag3_4',
 'BonusValue3_4', 'BonusFlag3_5', 'BonusValue3_5', 'BonusFlag4_1', 'BonusValue4_1', 'BonusFlag4_2',
 'BonusValue4_2', 'BonusFlag4_3', 'BonusValue4_3', 'BonusFlag4_4', 'BonusValue4_4', 'BonusFlag4_5',
 'BonusValue4_5', 'BonusFlag5_1', 'BonusValue5_1', 'BonusFlag5_2', 'BonusValue5_2', 'BonusFlag5_3',
 'BonusValue5_3', 'BonusFlag5_4', 'BonusValue5_4', 'BonusFlag5_5', 'BonusValue5_5', 'BonusFlag6_1',
 'BonusValue6_1', 'BonusFlag6_2', 'BonusValue6_2', 'BonusFlag6_3', 'BonusValue6_3', 'BonusFlag6_4',
 'BonusValue6_4', 'BonusFlag6_5', 'BonusValue6_5', 'BonusDetail', 'CoinUnit', 'GameUnit', 'MovieUlr1',
 'MovieUlr2', 'SiteUlr', 'EquivalentBranch', 'ModelLife', 'GrossProfit', 'Regist_Date', 'Regist_User',
 'Update_Date', 'Update_User', 'SpecDetail3']

re_m_katashikiframerelation
['KatashikiId', 'FrameId', 'Regist_Date', 'Regist_User', 'Update_Date', 'Update_User']

re_m_modelevaluation
['KatashikiId', 'Kind', 'Performance', 'PerformanceCoefficient', 'Spec', 'SpecCoefficient',
'Content', 'ContentCoefficient', 'News', 'NewsCoefficient', 'Concept', 'ConceptCoefficient',
'Period', 'PeriodCoefficient', 'SaleUnit', 'SaleUnitCoefficient', 'Running', 'RunningCoefficient',
'Returns', 'ReturnsCoefficient', 'Price', 'PriceCoefficient', 'Comment', 'ContributionExpected',
'Target', 'Sell', 'Catch', 'Minus', 'RecommendedNumberBig', 'RecommendedNumberMiddle',
'RecommendedNumberSmall', 'Regist_Date', 'Regist_User', 'Update_Date', 'Update_User']

re_m_pachinkotype 
['TypeId', 'TypeName', 'SortNo', 'Regist_Date', 'Regist_User', 'Update_Date', 'Update_User']

re_m_pachinkotypedetail
['TypeDetailId', 'TypeName', 'SortNo', 'Regist_Date', 'Regist_User', 'Update_Date', 'Update_User']

re_m_frame
['FrameId', 'Name', 'Color', 'MakerId', 'ImagePath', 'Regist_Date', 'Regist_User', 'Update_Date', 'Update_User', 'SortNo', 'Kind']

"""

cols_katashiki =  [
    'KatashikiId', 'MakerId', 
    'Kind', 'Name',
    #'SaleUnit',
    'SaleUnitOther', 
    'Price', 
    #'PriceDetail',
    'Regist_Date', #'Update_Date',  
    'NairanFlag', 'TenjiFlag','InspectFlag']

cols_katashikidetailpachinko = [
    'KatashikiId', 
    'BigRate', 'SmallRate', 
    #'WinBallCount',
    #'PayCount', 
    'KakuhenRate1_1', 'KakuhenRate1_2', 'KakuhenRate1_3',
    #'KakuhenRate2', 'KakuhenRate3',
    #'Jitan',
    'TypeId1', 
    'EquivalentBranch',#'Hold',
    "MovieUlr1",        
    "MovieUlr2",        
    "SiteUlr",
    'ContinueCountAve', 'PayCountAve', 'TamaUnitPrice',
    'ModelLife', 'GrossProfit']

cols_katashikidetailslot =  [
    'KatashikiId', 'SpecId', #'SpecDetail1', 'SpecDetail2'
    #'BonusLabel1', 'BonusLabel2', 'BonusLabel3', 'BonusLabel4', 'BonusLabel5',
    'BonusFlag1_1',
    'BonusValue1_1', 'BonusFlag1_2','BonusValue1_2', 'BonusFlag1_3', 'BonusValue1_3', 'BonusFlag1_4', 'BonusValue1_4', 'BonusFlag1_5',
    'BonusValue1_5', 'BonusFlag2_1', 'BonusValue2_1', 'BonusFlag2_2', 'BonusValue2_2', 'BonusFlag2_3',
    'BonusValue2_3', 'BonusFlag2_4', 'BonusValue2_4', 'BonusFlag2_5', 'BonusValue2_5', 'BonusFlag3_1',
    'BonusValue3_1', 'BonusFlag3_2', 'BonusValue3_2', 'BonusFlag3_3', 'BonusValue3_3', 'BonusFlag3_4',
    'BonusValue3_4', 'BonusFlag3_5', 'BonusValue3_5', 'BonusFlag4_1', 'BonusValue4_1', 'BonusFlag4_2',
    'BonusValue4_2', 'BonusFlag4_3', 'BonusValue4_3', 'BonusFlag4_4', 'BonusValue4_4', 'BonusFlag4_5',
    'BonusValue4_5', 'BonusFlag5_1', 'BonusValue5_1', 'BonusFlag5_2', 'BonusValue5_2', 'BonusFlag5_3',
    'BonusValue5_3', 'BonusFlag5_4', 'BonusValue5_4', 'BonusFlag5_5', 'BonusValue5_5', 'BonusFlag6_1',
    'BonusValue6_1', 'BonusFlag6_2', 'BonusValue6_2', 'BonusFlag6_3', 'BonusValue6_3', 'BonusFlag6_4',
    'BonusValue6_4', 'BonusFlag6_5', 'BonusValue6_5',
    'CoinUnit', 'GameUnit', 'ModelLife', 'GrossProfit',
    "MovieUlr1", "MovieUlr2", "SiteUlr"]

cols_Katashikiframerelation = [
    'KatashikiId', 'FrameId']

cols_pachinkotype = [
    'TypeId', 'TypeName']

cols_pachinkotypedetail = [
    'TypeDetailId', 'TypeName']

cols_frame = [
    'FrameId', 'Color']

cols_modelevaluation = [
    'KatashikiId', 
    'Performance', 'Spec', 'Content', 'News', 'Concept','Period', 
    'SaleUnit', 'Running', 'Returns', 'Price', 
    'Regist_Date'
    ]