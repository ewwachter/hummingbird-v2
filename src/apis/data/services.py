from models import City,CasesLocation
from sqlalchemy.sql import or_
from flask import jsonify

class ReportService():

    def searchCityCases(self, query):
        cases = City.query.filter(or_(City.city.like('%'+query+'%'), City.state.like('%'+query+'%'))).all()

        result = []

        for case in cases:
            activeCases = case.total_cases - case.suspects - case.refuses - case.deaths - case.recovered
            currentCase = {
            'city': case.city,
            'state': case.state,
            'cases': {
                'activeCases': activeCases,
                'suspectedCases': case.suspects,
                'recoveredCases': case.recovered,
                'deaths': case.deaths
            }}
            result.append(currentCase)

        return result
    
    def getAllCityCases(self):
        all_cases = City.query.all()

        return compileCases(all_cases)

    def searchCityCasesByState(self, uf):
        citySituation = City.query.filter_by(
            state=uf).all()

        return compileCases(citySituation)
    
    def getCasesNearLocation(self, latitude, longitude):
        cases = CasesLocation.query.all()

        return compileCasesNearLocation(cases,latitude,longitude)

def compileCases(data):
    activeCases = sum([(city.total_cases - city.suspects - city.refuses -
                    city.deaths - city.recovered) for city in data]) or 0
    suspectedCases = sum(
        [city.suspects for city in data]) or 0
    recoveredCases = sum(
        [city.recovered for city in data]) or 0
    deaths = sum([city.deaths for city in data]) or 0

    return {
        'activeCases': activeCases,
        'suspectedCases': suspectedCases,
        'recoveredCases': recoveredCases,
        'deaths': deaths
    }

def compileCasesNearLocation(data,latitude,longitude):
    RADIUS = 0.001

    # search for cases within RADIUS
    cases_nearby = []
    for case in data:
        if ((case.latitude<float(latitude)+RADIUS and case.latitude>float(latitude)-RADIUS)
            and (case.longitude<float(longitude)+RADIUS and case.longitude>float(longitude)-RADIUS)):
            cases_nearby.append(case)

    all_cases = [   {
                    'status': case.status,
                    'location':{
                        'latitude':case.latitude,
                        'longitude':case.longitude
                        }
                    }
                    for case in cases_nearby]

    return jsonify(all_cases)
