import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder
from functions import extract_data, analyze_data, table_of_values, get_distribution, shapiro_test, \
    levene_test, t_test

st.set_page_config(
    page_title="Dashboard",
    layout="wide",
)

@st.cache_data
def get_data(uploaded_file) -> pd.DataFrame:
    work_days, age, gender = extract_data(uploaded_file)
    my_dict = {'Количество больничных дней': work_days, 'Возраст': age, 'Пол': gender}
    return pd.DataFrame(my_dict)


uploaded_file = st.file_uploader("Выберыте файл - по формату аналогичный «М.Тех_Данные_к_ТЗ_DS»")
if uploaded_file is not None:
    data1 = get_data(uploaded_file)

    st.markdown("### Таблица 1 - данные в таблице можно менять")
    gb = GridOptionsBuilder.from_dataframe(data1)
    gb.configure_column('Количество больничных дней', editable=True)
    gb.configure_column('Возраст', editable=True)
    gb.configure_column('Пол', editable=True)
    gridOptions = gb.build()

    grid_return = AgGrid(data1,
                         gridOptions=gridOptions)
    data1 = grid_return['data']
    work_days = data1['Количество больничных дней']
    age = data1["Возраст"]
    gender = data1['Пол']
    percentage, risk_group, all_workers = np.around(analyze_data(work_days, age, gender), decimals=2, out=None)

    placeholder = st.empty()
    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            fig, ax = plt.subplots(2, figsize=(10, 5))
            explode = (0, 0.1)
            ax[0].pie([risk_group[0], risk_group[1]], explode=explode, labels=['Мужчины', 'Женщины'], autopct='%1.1f%%',
                      shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90,
                      colors=['olivedrab', 'rosybrown'])
            ax[0].set_title("Персонал пропускающий более 2 рабочих дней - доля по полу")

            explode = (0, 0.1)
            ax[1].pie([risk_group[2], risk_group[3]], explode=explode, labels=['Старше 35 лет', 'Младше 35 лет'],
                      autopct='%1.1f%%',
                      shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90,
                      colors=['olivedrab', 'rosybrown'])
            ax[1].set_title("Персонал пропускающий более 2 рабочих дней - доля по возрасту")
            st.write(fig)
            plt.close()
        with col2:
            fig, ax = plt.subplots(2, figsize=(10, 5))
            explode = (0, 0.1)
            ax[0].pie([risk_group[0], all_workers[0] - risk_group[0]], explode=explode,
                      labels=['Пропускающие более 2 рабочих дней ', 'Не пропускающие'], autopct='%1.1f%%',
                      shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90,
                      colors=sns.color_palette('Set2'))
            ax[0].set_title("Мужчины - доля по больничным дням")

            explode = (0, 0.1)
            ax[1].pie([risk_group[1], all_workers[1] - risk_group[1]], explode=explode,
                      labels=['Пропускающие более 2 рабочих дней ', 'Не пропускающие'], autopct='%1.1f%%',
                      shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90,
                      colors=sns.color_palette('Set2'))
            ax[1].set_title("Женщины - доля по больничным дням")
            st.write(fig)
            plt.close()

        with col3:
            fig, ax = plt.subplots(2, figsize=(10, 5))
            explode = (0, 0.1)
            ax[0].pie([risk_group[2], all_workers[2] - risk_group[2]], explode=explode,
                      labels=['Пропускающие более 2 рабочых дней ', 'Не пропускающие'], autopct='%1.1f%%',
                      shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90,
                      colors=['cornflowerblue', 'gold'])
            ax[0].set_title("Персонал старше 35 - доля по больничным дням")

            explode = (0, 0.1)
            ax[1].pie([risk_group[3], all_workers[3] - risk_group[3]], explode=explode,
                      labels=['Пропускающие более 2 рабочых дней ', 'Не пропускающие'], autopct='%1.1f%%',
                      shadow={'ox': -0.04, 'edgecolor': 'none', 'shade': 0.9}, startangle=90,
                      colors=['cornflowerblue', 'gold'])
            ax[1].set_title("Персонал младше 35 - доля по больничным дням")
            st.write(fig)
            plt.close()

        data2 = table_of_values(percentage, risk_group)
        st.markdown("### Таблица 2")
        st.dataframe(data2)

        values = get_distribution(work_days, age, gender)
        by_gender = dict(list(values.items())[0: 2])
        by_age = dict(list(values.items())[2: 4])
        st.markdown("### Графики распределения ")
        col1, col2, = st.columns(2)
        with col1:
            sns.set_style("darkgrid")
            fig1 = sns.displot(by_gender, kde=True)
            st.pyplot(fig1)
            plt.close()
        with col2:
            sns.set_style("darkgrid")
            fig2 = sns.displot(by_age, kde=True)
            st.pyplot(fig2)
            plt.close()

        man = values['Мужчины']
        woman = values['Женщины']
        older_group = values['Старше 35 лет']
        younger_group = values['Младше 35 лет']

        st.markdown("### Статистические тесты")
        st.markdown("### Нулевая гипотеза - нет различий между группами")
        st.markdown("### 1. Группы распределены по полу")

        t1, p1 = shapiro_test(all_workers)
        t2, p2, flag2 = levene_test(man, woman)
        t3, p3 = t_test(man, woman, flag2)
        alpha = 0.05

        st.markdown("#### 1) Шапиро — Уилка тест")
        col1, col2, = st.columns(2)
        col1.metric(
            label="t-stat",
            value=round(t1, 3),
        )
        col2.metric(
            label="p-уровень значимости",
            value=round(p1, 3),
        )

        if p1 > alpha:
            st.markdown("#### Нормальное распределение: p > 0.05")
        else:
            st.markdown("#### Распределение не является нормальным: p > 0.05")

        st.markdown("#### 2) Левене тест")
        col1, col2, = st.columns(2)
        col1.metric(
            label="t-stat",
            value=round(t2, 3),
        )
        col2.metric(
            label="p-уровень значимости",
            value=round(p2, 3),
        )

        if p2 > alpha:
            st.markdown("#### Дисперсии в двух выборках не имеют значимых различий: p > 0.05")
        else:
            st.markdown("#### Дисперсии отличаютcья: p < 0.05")

        st.markdown("#### 3) t-критерий Стьюдента")
        col1, col2, = st.columns(2)
        col1.metric(
            label="t-stat",
            value=round(t3, 3),
        )
        col2.metric(
            label="p-уровень значимости",
            value=round(p3, 3),
        )

        if p2 > alpha:
            st.markdown("#### Нулевую гипотезу не получилось отвергнуть - различие между группами незначимо: p > 0.05")
        else:
            st.markdown("#### Отвергаем нулевую гипотезу - группы отличаютсья: p < 0.05")

        st.markdown("### 2. Группы распределены по возрасту")
        t2, p2, flag2 = levene_test(older_group, younger_group)
        t3, p3 = t_test(older_group, younger_group, flag2)

        st.markdown("#### 1) Шапиро — Уилка тест")
        col1, col2, = st.columns(2)

        col1.metric(
            label="t-stat",
            value=round(t1, 3),
        )
        col2.metric(
            label="p-уровень значимости",
            value=round(p1, 3),
        )

        if p1 > alpha:
            st.markdown("#### Нормальное распределение: p > 0.05")
        else:
            st.markdown("#### Распределение не является нормальным: p > 0.05")

        st.markdown("#### 2) Левене тест")
        col1, col2, = st.columns(2)
        col1.metric(
            label="t-stat",
            value=round(t2, 3),
        )
        col2.metric(
            label="p-уровень значимости",
            value=round(p2, 3),
        )

        if p2 > alpha:
            st.markdown("#### Дисперсии в двух выборках не имеют значимых различий: p > 0.05")
        else:
            st.markdown("#### Дисперсии отличаютcя: p < 0.05")

        st.markdown("#### 3) t-критерий Стьюдента")
        col1, col2, = st.columns(2)
        col1.metric(
            label="t-stat",
            value=round(t3, 3),
        )
        col2.metric(
            label="p-уровень значимости",
            value=round(p3, 3),
        )

        if p2 > alpha:
            st.markdown(
                "#### Нулевую гипотезу не получилось отвергнуть - различие между группами незначимо: p > 0.05")
        else:
            st.markdown("#### Отвергаем нулевую гипотезу - группы отличаютсья: p < 0.05")
