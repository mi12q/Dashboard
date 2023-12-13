import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
from scipy.stats import shapiro, levene


def extract_data(file_name):
    data = pd.read_csv(file_name, encoding="cp1251", sep=";|,", engine="python")
    col1 = data.iloc[:, 0].to_numpy();
    col2 = data.iloc[:, 1].to_numpy();
    col3 = data.iloc[:, 2].to_numpy()
    work_days = [];
    age = [];
    gender = []
    for i in range(len(col1)):
        work_days.append(int(col1[i].split('"')[1]))
        age.append(int(col2[i]))
        gender.append(col3[i].split('""')[1])
    work_days = np.array(work_days);
    age = np.array(age);
    gender = np.array(gender)
    return work_days, age, gender


def percent(a, b):
    try:
        return (a / b) * 100
    except ZeroDivisionError:
        print("Ошибка: деление нулем")


def analyze_data(work_days, age, gender):
    female_workers = np.count_nonzero(gender == 'Ж');
    male_workers = np.count_nonzero(gender == 'М')
    workers_over_35 = np.count_nonzero(age > 35);
    young_workers = np.count_nonzero(age <= 35)
    risk_by_gender = [];
    risk_by_age = []
    for i in range(len(work_days)):
        if work_days[i] > 2:
            risk_by_gender.append(gender[i])
            risk_by_age.append(age[i])
    risk_by_gender = np.array(risk_by_gender);
    risk_by_age = np.array(risk_by_age)
    females_risk_group = np.count_nonzero(risk_by_gender == 'Ж');
    male_risk_group = np.count_nonzero(risk_by_gender == 'М')
    over_35_risk_group = np.count_nonzero(risk_by_age > 35);
    young_risk_group = np.count_nonzero(risk_by_age <= 35)
    females_percent = percent(females_risk_group, female_workers);
    male_percent = percent(male_risk_group, male_workers)
    over_35_percent = percent(over_35_risk_group, workers_over_35);
    young_workers_percent = percent(young_risk_group, young_workers)
    risk_group = np.array([male_risk_group, females_risk_group, over_35_risk_group, young_risk_group])
    all_workers = np.array([male_workers, female_workers, workers_over_35, young_workers])
    percentage = np.array([male_percent, females_percent, over_35_percent, young_workers_percent])
    return percentage, risk_group, all_workers


def table_of_values(percentage, risk_group):
    percentage = ["%.2f" % i + "%" for i in percentage]
    people_number = risk_group[0] + risk_group[1]
    males = percent(risk_group[0], people_number);
    females = percent(risk_group[1], people_number)
    over_35 = percent(risk_group[2], people_number);
    young = percent(risk_group[3], people_number)
    by_all = np.around([males, females, over_35, young], decimals=2, out=None)
    by_all = ["%.2f" % i + "%" for i in by_all]

    data_dict = {'Категория персонала': ['Мужчины', 'Женщины', 'Старше 35 лет', 'Младше 35 лет'],
                 'Процент пропускающих работу из данной категории': percentage,
                 'Доля которую составляет категория в группе из всех пропускающих': by_all}
    return pd.DataFrame(data_dict)


def get_distribution(work_days, age, gender):
    days = np.unique(work_days)
    female = [];
    male = [];
    over_35 = [];
    young_workers = []
    for i in range(len(work_days)):
        if gender[i] == 'М':
            male.append(work_days[i])
        if gender[i] == 'Ж':
            female.append(work_days[i])
        if age[i] > 35:
            over_35.append(work_days[i])
        if age[i] <= 35:
            young_workers.append(work_days[i])
    data = {'Мужчины': male, 'Женщины': female,
            'Старше 35 лет': over_35, 'Младше 35 лет': young_workers}
    return data


def shapiro_test(data):
    t, p = shapiro(data);
    alpha = 0.05
    if p > alpha:
        print("Нормальное распределение")
    else:
        print("Распределение не является нормальним")
    return t, p


def levene_test(group1, group2):
    t, p = levene(group1, group2);
    alpha = 0.05
    if p > alpha:
        print("Дисперсии в двух выборках не имеют значимых различий")
        flag = True
    else:
        print("Дисперсии отличаютcя")
        flag = False
    return t, p, flag


def t_test(group1, group2, flag):
    t, p = ttest_ind(group1, group2, equal_var=flag);
    alpha = 0.05
    if (p < alpha):
        print("Отвергаем нулевую гипотезу - грурры отличаются")
    else:
        print("Нулевую гипотезу не получилось отвергнут - раздичие между группамы незначимо")
    return t, p
