import os
import requests

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

        average_salary = predict_salary(salary_from, salary_to)

        return average_salary

    return None


def fetch_vacancies_hh():
    url = "https://api.hh.ru/vacancies"
    languages = ["Python", "Java", "C++", "PHP", "Javascript", "Ruby", "Swift", "Go", "C", "C#"],
    vacancies_statistic = {}

    for language in languages:
        MOSCOW_ID = 1
        vacancy_salary = []

        for page in count(0):
            params = {'text': f'Программист {language}', 'area': MOSCOW_ID, 'page': page}

            response = requests.get(url, params=params)
            vacancies = response.json()

            if page >= vacancies["pages"] - 1:
                break

            for vacancy in vacancies.get('items', []):
                average_salary = predict_rub_salary_for_hh(vacancy)

                if average_salary:
                    vacancy_salary.append(average_salary)

        average_salary = None
        total_vacancies = vacancies['found']

        if vacancy_salary:
            average_salary = int(sum(vacancy_salary) / len(vacancy_salary))

        vacancies_statistic[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': len(vacancy_salary),
            'average_salary': average_salary
        }

    return vacancies_statistic


def fetch_vacancies_sj(superjob_key):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {'X-Api-App-Id': superjob_key}

    languages = ["Python", "Java", "PHP", "Javascript", "Ruby", "Swift", "Go", "C", "C#", "C++"]
    vacancies_statistic = {}

    for language in languages:
        MOSCOW_ID = 4
        PROGRAMMING_CATALOG_ID = 48

        vacancy_salary = []

        for page in count(0):
            params = {'catalogues': PROGRAMMING_CATALOG_ID, 'town': MOSCOW_ID, 'keyword': language, 'page': page}

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            vacancies = response.json()

            if not vacancies['objects']:
                break

            for vacancy in vacancies['objects']:
                predicted_salary = predict_rub_salary_for_sj(vacancy)

                if predicted_salary:
                    vacancy_salary.append(predicted_salary)

        total_vacancies = vacancies.get('total')
        average_salary = None

        if vacancy_salary:
            average_salary = int(sum(vacancy_salary) / len(vacancy_salary))

        vacancies_statistic[language] = {
            'vacancies_found': total_vacancies,
            'vacancies_processed': len(vacancy_salary),
            'average_salary': average_salary
        }

    return vacancies_statistic


def structure_table(table_title, statistic):
    table_contents = [
        ['Язык программирования', 'Найденных вакансий', 'Обработанных вакансий', 'Средняя зарплата'],
    ]
    for language, stats in statistic.items():
        vacancies_found = stats.get('vacancies_found', 0)
        vacancies_processed = stats.get('vacancies_processed', 0)
        average_salary = stats.get('average_salary', 0)

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
