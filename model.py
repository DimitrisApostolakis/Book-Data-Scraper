from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd

df = pd.read_csv("bookshelf.csv")

df['Category'] = df['Category'].replace({"Add a comment": "Default"})
# print(df.isna().sum().sum())
df = df.dropna()
# print(df.isna().sum().sum())

labeled_data = df[(df['Category'] != "Default")]
unlabeled_data = df[~df.index.isin(labeled_data.index)]
# print(labeled_data['Category'].value_counts())

model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression(max_iter=1000))
])

text = [title + " " + desc for title, desc in zip(labeled_data['Title'].values, labeled_data['Description'].values)]

model.fit(text, labeled_data['Category'].values)

predicted = model.predict([title + " " + desc for title, desc in zip(unlabeled_data['Title'].values, unlabeled_data['Description'].values)])

unlabeled_data.loc[:, 'Predicted_Category'] = predicted

print(unlabeled_data['Predicted_Category'].value_counts())