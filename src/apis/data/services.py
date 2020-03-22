from models import City
from models import CasesLocation
from sqlalchemy.sql import or_
from flask import jsonify


class ReportService:

    def search_city_cases(self, query):
        cases = City.query.filter(
            or_(City.city.like('%'+query+'%'), City.state.like('%'+query+'%'))
        ).all()

        result = []

        for case in cases:
            active_cases = case.total_cases - case.suspects - \
                           case.refuses - case.deaths - case.recovered
            current_case = {
                'city': case.city,
                'state': case.state,
                'cases': {
                    'activeCases': active_cases,
                    'suspectedCases': case.suspects,
                    'recoveredCases': case.recovered,
                    'deaths': case.deaths
                }
            }
            result.append(current_case)

        return result

    def get_all_city_cases(self):
        all_cases = City.query.all()
        return compile_cases(all_cases)

    def search_city_cases_by_state(self, uf):
        city_situation = City.query.filter_by(
            state=uf).all()
        return compile_cases(city_situation)

    def get_cases_near_location(self, latitude, longitude):
        all_cases = CasesLocation.query.all()
        return compile_cases_near_location(all_cases,latitude,longitude)

def compile_cases(data):
    active_cases = sum(
        [(city.total_cases - city.suspects -
          city.refuses - city.deaths - city.recovered)
         for city in data]) or 0
    suspected_cases = sum(
        [city.suspects for city in data]) or 0
    recovered_cases = sum(
        [city.recovered for city in data]) or 0
    deaths = sum([city.deaths for city in data]) or 0

    return {
        'activeCases': active_cases,
        'suspectedCases': suspected_cases,
        'recoveredCases': recovered_cases,
        'deaths': deaths
    }

def compile_cases_near_location(data,latitude,longitude):
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
