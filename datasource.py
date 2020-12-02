import pandas as pd
import os
import datetime

SOURCE = "https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/nakazeni-vyleceni-umrti-testy.csv"
DATADIR = "data"

def get_today_data() -> pd.DataFrame:
    try:
        offset = 1 if datetime.datetime.now().hour < 1 else 0
        return pd.read_csv(f"./{DATADIR}/{datetime.date.today()}.csv")
    except:
        try:
            print("[INFO] Downloading updated dataset...")
            data = pd.read_csv(SOURCE)
            if not os.path.exists(DATADIR):
                os.makedirs(DATADIR)
            data.to_csv(f"./{DATADIR}/{datetime.date.today()}.csv")
            return data
        except:
            print("[FATAL] Today data not downloaded and remote datasource is not available. Terminating...")
            exit(1)

def get_time_series(data: pd.DataFrame) -> pd.Series:
    return pd.Series(pd.date_range(data["datum"][0], periods=365, freq="D"))
