import h2o
from sklearn.model_selection import train_test_split 
from h2o.automl import H2OAutoML

h2o.init()

big_gei = ['timestamp','dock','bikes_present_-1','bikes_present_-2']
train = train.drop(big_gei, axis=1)
train.to_csv("train.csv")
test = test.drop(big_gei, axis=1)
test.to_csv("train.csv")

train = h2o.import_file("train.csv")
test = h2o.import_file("test.csv")

x = train.columns
y="bikes_present"

aml = H2OAutoML(max_models=20, seed=1)
aml.train(x=x, y=y, training_frame=train)

preds = aml.leader.predict(test)