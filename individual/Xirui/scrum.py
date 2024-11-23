from river import preprocessing
from sklearn import datasets

X = [
    {"country": "France", "place": "Taco Bell"},
    
    {"country": "Sweden", "place": "Burger King"},
    {"country": "France", "place": "Burger King"},
    {"country": "Russia", "place": "Starbucks"},
    {"country": "Russia", "place": "Starbucks"},
    {"country": "Sweden", "place": "Taco Bell"},
    
]

Y = [
    10, 7, 9, 4, 8, 13,
]

encoder = preprocessing.OneHotEncoder()
print('Hello')
for i in range(6):
    print(encoder.transform_one(X[i]))
    encoder.learn_one(X[i])

print(encoder.predict({"country": "France", "place": "Taco Bell"}, {7}))
