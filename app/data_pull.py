import pandas as pd

from sqlalchemy import create_engine
import os
import config


def pull_all(db='bikes_present'):
    path = os.path.join('mysql+pymysql://' + config.MYSQL_USERNAME + ':' + config.MYSQL_PASSWORD +
                        '@bikes-db-1.cxd403f5i8vi.eu-west-2.rds.amazonaws.com:3306/bikes')
    db_engine = create_engine(path)

    df = pd.read_sql(f"""SELECT * FROM bikes.{db}""", db_engine)
    return df


def pull_remove_na(db='bikes_present', na_thresh=50):
    df = pull_all(db)
    df = df.dropna(thresh=len(df) - na_thresh, axis=1)
    df = df.dropna()
    return df
