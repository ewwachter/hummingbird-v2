from models import City
from models import CasesLocation
from sqlalchemy.sql import or_
from flask import jsonify


class ReportService:

    def search_on_location_by_term(self, query):
        cases = City.query.filter(
            or_(City.city.like(query), City.state.like(query))
        ).all()

        result = []

        for case in cases:
            current_case = {
                'city': case.city,
                'state': case.state,
                'cases': {
                    'activeCases': case.active_cases,
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

    def search_city_cases_by_state(self, state_code):
        city_situation = City.query.filter_by(
            state=state_code).all()
        return compile_cases(city_situation)

    def get_cases_near_location(self, latitude, longitude):
        # FIX: Why those variables has not been used?
        all_cases = CasesLocation.query.all()
        return compile_cases_near_location(all_cases, latitude, longitude)


def compile_cases(data):
    active_cases = sum(
        [city.active_cases
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


def compile_cases_near_location(data, latitude, longitude):
    radius = 0.001

    # search for cases within radius
    cases_nearby = []
    for case in data:
        if (
                case.latitude < float(latitude)+radius and
                case.latitude > float(latitude)-radius and
                case.longitude < float(longitude)+radius and
                case.longitude > float(longitude)-radius):
            cases_nearby.append(case)

    all_cases = [{
                'status': case.status,
                'location': {
                    'latitude': case.latitude,
                    'longitude': case.longitude
                    }
                }
                    for case in cases_nearby]

    return jsonify(all_cases)
