import json
import helper.constants as constants


def newspapers():
    newspapers_json = constants.NEWSPAPERS_JSON_PATH
    with open(newspapers_json, 'r',encoding='utf-8') as file:
        data = json.load(file) 
        zeitungen = data['newspapers']
        return zeitungen
    
def homepage():
     homepage_json = constants.HOMEPAGE_JSON_PATH
     with open(homepage_json, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data
     
def themen(ZeitungName):
    themen_json = constants.TOPICS_JSON_PATH
    with open(themen_json, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data[ZeitungName]