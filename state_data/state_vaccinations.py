import requests
from bs4 import BeautifulSoup
import pandas as pd
import tabula
import datetime
import pytz


def read(source: str) -> (pd.DataFrame, pd.DataFrame):
    soup = BeautifulSoup(requests.get(source).content, "html.parser")
    for img in soup.find_all("img"):
        if img.get("alt") == "Vaccination State Data":
            url = img.parent["href"]
            break

    return parse_data(url)


def parse_data(url: str) -> (pd.DataFrame, pd.DataFrame):
    kwargs = {"pandas_options": {"dtype": str, "header": None}}
    dfs_from_pdf = tabula.read_pdf(url, pages="all", **kwargs)
    state_df = dfs_from_pdf[1].drop([0, 1]).set_index(0)
    first_dose_vaccinations = (
        state_df.drop([3, 4], axis=1)
        .append(
            pd.DataFrame(
                [
                   ["date", str(
                        (
                            datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
                            - datetime.timedelta(days=1)
                        ).date()
                    )]
                ], columns=[1,2]
            ), ignore_index=True
        )
        .transpose()
    )
    second_dose_vaccinations = (
        state_df.drop([2, 4], axis=1)
        .append(
            pd.DataFrame(
                [
                    ["date", str(
                        (
                            datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
                            - datetime.timedelta(days=1)
                        ).date()
                    )]
                ], columns=[1,3]
            ), ignore_index=True
        )
        .transpose()
    )

    return (first_dose_vaccinations, second_dose_vaccinations)


def main():
    source = "https://www.mohfw.gov.in/"
    first_dose, second_dose = read(source)
    # columns = ["A & N Islands","Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chandigarh","Chhattisgarh","Dadra & Nagar Haveli","Daman & Diu","Delhi","Goa","Gujarat","Haryana","Himachal Pradesh","Jammu & Kashmir","Jharkhand","Karnataka","Kerala","Ladakh","Lakshadweep","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Miscellaneous","date"]
    first_dose.iloc[1:].to_csv("first_dose_state_wise.csv", header=None, index=False, mode='a')
    second_dose.iloc[1:].to_csv("second_dose_state_wise.csv", header=None, index=False, mode='a')


if __name__ == "__main__":
    main()
