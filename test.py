from tensorflow import keras
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

dataset = pd.read_csv('./ai_feature/Dataset_v1.0.csv')
origin = dataset
dataset = dataset.drop(columns = ['id', 'lp_avg'])
dataset = dataset.dropna(how='any',axis = 0)

scaler = MinMaxScaler()
dataset[ : ] = scaler.fit_transform(dataset[ : ])

model = keras.models.load_model('./ann96.h5')
model.summary()

result = model.predict(dataset)
origin['predict'] = result

origin.to_csv('./dataset_AIscore.csv')