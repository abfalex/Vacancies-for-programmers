import os
import requests

from pprint import pprint
from itertools import count
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    if salary_from is not None and salary_to is not None:
        return (salary_to + salary_from) / 2
    elif salary_from is not None:
        return salary_from * 1.2
    elif salary_to is not None:
        return salary_to * 0.8

    return None


def predict_rub_salary_sj(vacancy_info):
    salary_from = vacancy_info.get('payment_from')
    salary_to = vacancy_info.get('payment_to')
    vacancy_currency = vacancy_info.get('currency')

    salary = predict_salary(salary_from, salary_to)

    if vacancy_currency != "rub":
        return None

    if salary:
        return salary

    return None


def predict_rub_salary_hh(vacancy_info):
    vacancy_salary = vacancy_info['salary'] if vacancy_info['salary'] else None
    vacancy_currency = vacancy_salary['currency'] if vacancy_info['salary'] else None

    if vacancy_currency != "RUR":
        return None

    salary_from = vacancy_salary.get('from')
    salary_to = vacancy_salary.get('to')

    salary = predict_salary(salary_from, salary_to)

    return salary


def fetch_vacancies_hh():
    url = "https://api.hh.ru/vacancies"
    languages = ["Python", "Java", "Javascript", "Ruby", "Swift", "Go", "C", "C#", "C++", "PHP"]
    vacancies_statistic = {}

    for language in languages:
        params = {'text': f'Программист {language}', 'area': 1}

        total_vacancies = 0
        vacancies_processed = 0
        average_salary = 0

        for page in count(0):
            params['page'] = page

            response = requests.get(url, params=params)
            vacancies = response.json()

            if 'items' not in vacancies or not vacancies['items']:
                break

            total_vacancies += vacancies['found']

            for vacancy_index, vacancy_info in enumerate(vacancies['items']):
                full_vacancy_info = vacancies["items"][vacancy_index]
                salary = predict_rub_salary_hh(full_vacancy_info)

                if salary:
                    average_salary += salary
                    vacancies_processed += 1

            formatted_average_salary = round(average_salary / max(vacancies_processed, 1))

            vacancies_statistic[language] = {
                'vacancies_found': total_vacancies,
                'vacancies_processed': vacancies_processed,
                'average_salary': formatted_average_salary
            }

    return vacancies_statistic


def fetch_vacancies_sj():
    url = "https://api.superjob.ru/2.0/vacancies/"

    headers = {
        'X-Api-App-Id': os.environ['SECRET_KEY_SUPERJOB']
    }

    languages = ["Python", "Java", "Javascript", "Ruby", "Swift", "Go", "C", "C#", "C++", "PHP"]
    vacancies_statistic = {}

    for language in languages:
        params = {'catalogues': 48, 'town': 4, 'keyword': language}

        total_vacancies = 0
        vacancies_processed = 0
        average_salary = 0

        for page in count(0):
            params['page'] = page

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            vacancies = response.json()

            if 'objects' not in vacancies or not vacancies['objects']:
                break

            for vacancy_index, vacancy in enumerate(vacancies['objects']):
                total_vacancies += vacancy['client'].get('vacancy_count', 0)
                salary = predict_rub_salary_sj(vacancy)

                if salary is not None:
                    average_salary += salary
                    vacancies_processed += 1

            formatted_average_salary = round(average_salary / max(vacancies_processed, 1))

            vacancies_statistic[language] = {
                'vacancies_found': total_vacancies,
                'average_salary': formatted_average_salary,
                'vacancies_processed': vacancies_processed
            }

    return vacancies_statistic


def structure_table(table_title, statistic):
    table_info = [
        ['Язык программирования', 'Найденных вакансий', 'Обработанных вакансий', 'Средняя зарплата'],
    ]
    for language in statistic:
        vacancies_found = statistic[language].get('vacancies_found')
        average_salary = statistic[language].get('average_salary')
        vacancies_processed = statistic[language].get('vacancies_processed')

        table_info.append([language, vacancies_found, vacancies_processed, average_salary])

    return AsciiTable(table_info, table_title).table


def main():
    load_dotenv()

    hh_stats = fetch_vacancies_hh()
    sj_stats = fetch_vacancies_sj()

    structure_hh_table = structure_table('HeadHunter Moscow', hh_stats)
    structure_sj_table = structure_table('SuperJob Moscow', sj_stats)

    print(f'{structure_hh_table}\n{structure_sj_table}')


if __name__ == '__main__':
    main()
