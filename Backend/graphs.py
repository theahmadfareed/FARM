from database import session13,session14, SessionLocal

from model import newsBrands, newsCompetitor, newsHashtag, redditBrands, redditCompetitor, redditHashtag
from datetime import datetime, timedelta
from sqlalchemy import  func
from collections import defaultdict
from typing import Any

from sentiment import sia

def getSingleLineChart(input: dict[str,Any]):
    pos = input['positive']
    neg = input['negative']
    neutral = input['neutral']
    finalDict= {}
    for keys in pos.keys():
        finalDict[keys] = pos[keys] + neg[keys] + neutral[keys]
    return {"result": finalDict}



def joinDict(first: dict[str, Any],second: dict[str, Any]):
    result = {}
    for key,val in first.items():
        if key in second.keys():
            l1,l2,l3 = second[key]
            result[key] = [val[0]+l1, val[1]+l2, val[2]+l3]
        else:
            result[key] = val
    for key,val in second.items():
        if key not in result.keys():
            result[key] = val
    return result

def graph(result):
    pos = {}
    neg = {}
    neutral = {}
    for key in result.keys():
        p,n,neu = result[key]
        pos[key] = p
        neg[key] = n
        neutral[key] = neu
    return pos,neg,neutral
def getGraphs(brand: str, competitor: str, hashtag: str, day: int ):
    now = datetime.now()
    # # Calculate the date one month ago
    days = now - timedelta(days=day)
    # days = 1000
    n_brands = getNewsGraph(brand, days, newsBrands)
    n_competitors = getNewsGraph(competitor, days, newsCompetitor)
    n_hashtag = getNewsGraph(hashtag, days, newsHashtag)

    r_brands = getNewsGraph(brand, days, redditBrands)
    r_competitors = getNewsGraph(competitor, days, redditCompetitor)
    r_hashtags = getNewsGraph(hashtag, days, redditHashtag)
    
    result = joinDict(n_competitors,n_brands)

    result = joinDict(result, n_hashtag)
    result = joinDict(result, r_brands)
    result = joinDict(result, r_competitors)
    result = joinDict(result, r_hashtags)
    pos,neg,neutral = graph(result)
    
    return {"positive": pos, "negative": neg, "neutral": neutral}
    

def getNewsGraph(name: str, one_month_ago : int, table: str): 
    session18 = SessionLocal()
    rows = session18.query(table.content, func.date(table.published_at).label('published_at')).filter(table.published_at >= one_month_ago, table.name == name).all()
    


    content_dict = defaultdict(list)
    for row in rows:
        content_dict[row.published_at].append(row.content)
    sentiment_dict = {}
    for key in content_dict.keys():
        sentiment = getSentiment(content_dict[key])
        sentiment_dict[key] = sentiment
    session18.close()
    return sentiment_dict

def getNewsGraph2(name: str, one_month_ago : int, table: str): 
    rows = session13.query(table.content, func.date(table.published_at).label('published_at')).filter(table.published_at >= one_month_ago, table.name == name).all()

    content_dict = defaultdict(list)
    for row in rows:
        content_dict[row.published_at].append(row.content)
    sentiment_dict = {}
    for key in content_dict.keys():
        sentiment = getSentiment(content_dict[key])
        sentiment_dict[key] = sentiment
    return sentiment_dict

def getNewsGraph3(name: str, one_month_ago : int, table: str): 
    rows = session14.query(table.content, func.date(table.published_at).label('published_at')).filter(table.published_at >= one_month_ago, table.name == name).all()
    

    content_dict = defaultdict(list)
    for row in rows:
        content_dict[row.published_at].append(row.content)
    sentiment_dict = {}
    for key in content_dict.keys():
        sentiment = getSentiment(content_dict[key])
        sentiment_dict[key] = sentiment
    return sentiment_dict

def getSentiment(content: list):
    # contents = []
    positive = 0
    negative = 0
    neutral = 0
    # print(content)
    for data in content:
        # contents.append(data)
        
        
        result = sia.polarity_scores(data)
        # print(result)
        if result['compound'] >= 0.05 :
                positive += 1
                # content.append(positive)
        elif result['compound'] <= - 0.05 :
            negative += 1
            # content.append(negative)
        else :
            neutral += 1

    return positive,negative,neutral

