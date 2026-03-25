import pandas as pd


def read_excel_file(path: str) -> list[str]:
    df = pd.read_excel(path)

    # Берём первую колонку
    first_column = df.iloc[:, 0]

    # Удаляем пустые значения и приводим к строке
    values = (
        first_column
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return values