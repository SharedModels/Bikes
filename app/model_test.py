import pandas as pd
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.statespace.varmax import VARMAX
from sqlalchemy import create_engine
import os
import config

path = os.path.join('mysql+pymysql://' + config.MYSQL_USERNAME + ':' + config.MYSQL_PASSWORD +
                    '@bikes-db-1.cxd403f5i8vi.eu-west-2.rds.amazonaws.com:3306/bikes')
db_engine = create_engine(path)

df = pd.read_sql("""SELECT * FROM bikes.bikes_present""", db_engine)
df = df.dropna(thresh=len(df)-50, axis=1)
df = df.dropna()
print(df.shape)


test_df = df.head(8000)
x = test_df.drop(['timestamp'], axis=1)
# h = df.tail(10)
# h_y = h['1']
# h_x = h.drop(['1', 'timestamp'], axis=1)
# print(x)
# print(y.shape)
clf = VARMAX(x)
fit_model = clf.fit()
non_timestamp = df.drop('timestamp', axis=1)
print(non_timestamp.shape)
# print(pd.DataFrame(fit_model.forecast(fit_model.y, steps=1)))
print(non_timestamp.head(8001).tail(1).reset_index(drop=True).subtract(
    non_timestamp.head(8000


                       ).tail(1).reset_index(drop=True)).abs().mean(axis=1))
print(non_timestamp.head(8001).tail(1).reset_index(drop=True).subtract(
    pd.DataFrame(fit_model.forecast(x, steps=1), columns=list(non_timestamp))).abs().mean(axis=1))
# pred_df = pd.concat(
#     [df.head(8001).tail(1), df.head(8000).tail(1), pd.DataFrame(fit_model.forecast(fit_model.y, steps=1))], axis=0)
# pred_df.to_csv('pred.csv')
# print(df.head(8001).tail(1))
# a = clf.predict(h_y, h_x)

# print(a)
