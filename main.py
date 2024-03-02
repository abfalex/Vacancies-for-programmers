import os
import requests

from pprint import pprint
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_to + salary_from) / 2

    elif salary_from:
        return salary_from * 1.2

    elif salary_to:
        return salary_to * 0.8

    return None


def predict_rub_salary_for_sj(vacancy_info):
    salary_from = vacancy_info.get('payment_from')
    salary_to = vacancy_info.get('payment_to')
    vacancy_currency = vacancy_info.get('currency')

    salary = predict_salary(salary_from, salary_to)

    if vacancy_currency != "rub":
        return None

    if salary:
        return salary

    return None


def predict_rub_salary_for_hh(vacancy_info):
    vacancy_salary = vacancy_info.get('salary', None)

    if vacancy_salary and vacancy_salary['currency']:
        if vacancy_salary['currency'] != "RUR":
            return None

        salary_from = vacancy_salary.get('from')
        salary_to = vacancy_salary.get('to')

        salary = predict_salary(salary_from, salary_to)

        if salary:
            return salary

    return None


def fetch_vacancies_hh():
    url = "https://api.hh.ru/vacancies"
    languages = ["Python", "Java", "Javascript", "Ruby", "Swift", "Go", "C", "C#", "C++", "PHP"]
    vacancies_statistic = {}

    for language in languages:
        MOSCOW_ID = 1

        params = {'text': f'Программист {language}', 'area': MOSCOW_ID}

        vacancies_processed = 0
        total_vacancies = 0
        salary = 0

        for page in count(0):
            params['page'] = page

            response = requests.get(url, params=params)
            vacancies = response.json()

            if 'items' not in vacancies or not vacancies['items']:
                break

            total_vacancies = vacancies['found']

            for vacancy_index, vacancy_info in enumerate(vacancies['items']):
                current_vacancy = vacancies["items"][vacancy_index]
                vacancy_average_salary = predict_rub_salary_for_hh(current_vacancy)

                if vacancy_average_salary:
                    salary += 0
                    vacancies_processed += 1

        average_salary = round(salary / max(vacancies_processed, 1)) if salary > 0 else 0

        vacancies_statistic[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary
        }

    return vacancies_statistic


def fetch_vacancies_sj(superjob_key):
    url = "https://api.superjob.ru/2.0/vacancies/"

    headers = {
        'X-Api-App-Id': superjob_key
    }

    languages = ["Python", "Java", "Javascript", "Ruby", "Swift", "Go", "C", "C#", "C++", "PHP"]
    vacancies_statistic = {}

    for language in languages:
        MOSCOW_ID = 4
        PROGRAMMING_CATALOG_ID = 48

        params = {'catalogues': PROGRAMMING_CATALOG_ID, 'town': MOSCOW_ID, 'keyword': language}

        total_vacancies = 0
        vacancies_processed = 0
        salary = 0

        for page in count(0):
            params['page'] = page

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            vacancies = response.json()

            if 'objects' not in vacancies or not vacancies['objects']:
                break

            for vacancy in vacancies['objects']:
                total_vacancies = vacancy['client'].get('vacancy_count', 0)
                vacancy_average_salary = predict_rub_salary_for_sj(vacancy)

                if vacancy_average_salary:
                    salary += vacancy_average_salary
                    vacancies_processed += 1

        average_salary = round(salary / max(vacancies_processed, 1)) if salary > 0 else 0

        vacancies_statistic[language] = {
            'vacancies_found': total_vacancies,
            'average_salary': average_salary,
            'vacancies_processed': vacancies_processed
        }

    return vacancies_statistic


def structure_table(table_title, statistic):
    table_contents = [
        ['Язык программирования', 'Найденных вакансий', 'Обработанных вакансий', 'Средняя зарплата'],
    ]
    for language in statistic:
        vacancies_found = statistic[language].get('vacancies_found')
        average_salary = statistic[language].get('average_salary')
        vacancies_processed = statistic[language].get('vacancies_processed')

        table_contents.append([language, vacancies_found, vacancies_processed, average_salary])

    return AsciiTable(table_contents, table_title).table


def main():
    load_dotenv()

    superjob_key = os.environ['SECRET_KEY_SUPERJOB']

    hh_stats = fetch_vacancies_hh()
    sj_stats = fetch_vacancies_sj(superjob_key)

    structure_hh_table = structure_table('HeadHunter Moscow', hh_stats)
    structure_sj_table = structure_table('SuperJob Moscow', sj_stats)

    print(f'{structure_hh_table}\n{structure_sj_table}')


if __name__ == '__main__':
    main()
