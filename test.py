import pandas as pd

df = pd.read_csv("data/2023-06-17 00:04:06.csv")

# Создание пустого словаря для хранения DataFrame'ов разных городов
dfs_by_city = {}

# Извлечение сокращенного названия города из столбца 'Поставщик'
df['Город'] = df['Поставщик'].str.split(" \(").str[0].str.split().str[-1]

# Итерация по уникальным значениям сокращенных названий городов
for city in df['Город'].unique():
    # Фильтрация DataFrame по городу
    filtered_df = df[df['Город'] == city]
    # Удаление временного столбца 'Город'
    filtered_df = filtered_df.drop('Город', axis=1)
    # Добавление DataFrame в словарь по городу
    dfs_by_city[city] = filtered_df

# Запись DataFrame'ов каждого города в отдельный лист CSV-файла
with pd.ExcelWriter('data/result.xlsx') as writer:
    for city, city_df in dfs_by_city.items():
        city_df.to_excel(writer, sheet_name=city, index=False)