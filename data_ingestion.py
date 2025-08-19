import pandas as pd
import numpy as np
from textblob import TextBlob
from bertopic import BERTopic

# Step 1: Data Ingestion
# Define the file paths with the correct file name.
try:
    structured_file = 'data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    unstructured_file = 'data/raw/customer_interactions.csv'
    
    structured_df = pd.read_csv(structured_file).set_index('customerID')
    unstructured_df = pd.read_csv(unstructured_file).set_index('customerID')
    
except KeyError as e:
    print(f"Error: A 'customerID' column was not found. Please check your CSV files for typos. The exact error was: {e}")
    exit() # Exit the script if the key is not found

print("Structured Data Loaded Successfully.")
print("Unstructured Data Loaded Successfully.")

# Step 2: Structured Data Preprocessing
print("\n'TotalCharges' column data type BEFORE cleaning:")
print(structured_df['TotalCharges'].dtype)
structured_df['TotalCharges'] = structured_df['TotalCharges'].replace(' ', '0')
structured_df['TotalCharges'] = pd.to_numeric(structured_df['TotalCharges'])
print("\n'TotalCharges' column data type AFTER cleaning:")
print(structured_df['TotalCharges'].dtype)
print("\nNumber of missing values in 'TotalCharges' after cleaning:")
print(structured_df['TotalCharges'].isnull().sum())

structured_df['Churn'] = structured_df['Churn'].map({'Yes': 1, 'No': 0})
categorical_cols = structured_df.select_dtypes(include=['object']).columns.tolist()
structured_df = pd.get_dummies(structured_df, columns=categorical_cols, drop_first=True)

# Step 3: Data Merging
merged_df = structured_df.merge(unstructured_df, left_index=True, right_index=True, how='left')
merged_df.reset_index(inplace=True)

print("\nFirst 5 rows of the final merged DataFrame:")
print(merged_df.head())
print("\nShape of the final merged DataFrame (rows, columns):")
print(merged_df.shape)

# Step 4: Sentiment Analysis (Module 2, Part 1)
merged_df['interaction_text'] = merged_df['interaction_text'].fillna('')
def get_sentiment_polarity(text):
    return TextBlob(text).sentiment.polarity
merged_df['sentiment_score'] = merged_df['interaction_text'].apply(get_sentiment_polarity)
def get_sentiment_label(score):
    if score > 0.05:
        return 'Positive'
    elif score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'
merged_df['sentiment_label'] = merged_df['sentiment_score'].apply(get_sentiment_label)
print("\nFirst 10 customers with sentiment analysis results:")
print(merged_df[['customerID', 'interaction_text', 'sentiment_score', 'sentiment_label']].head(10))
print("\nDistribution of Sentiment Labels:")
print(merged_df['sentiment_label'].value_counts())

# Step 5: Topic Analysis (Module 2, Part 2)
documents = merged_df[merged_df['interaction_text'].str.strip() != '']['interaction_text'].tolist()

# Defensive programming: Check if the list of documents is empty before proceeding
if not documents:
    print("\nError: The list of documents is empty. Please ensure your 'customer_interactions.csv' file has content and is saved correctly.")
    merged_df['topic_id'] = -1
    merged_df['topic_name'] = 'N/A'

else:
    print(f"\nNumber of documents found for topic modeling: {len(documents)}")
    print("First few documents to be analyzed:")
    print(documents[:5])
    
    topic_model = BERTopic(language="english")
    topics, probabilities = topic_model.fit_transform(documents)
    
    topic_summary = topic_model.get_topic_info()
    print("\nIdentified Topics:")
    print(topic_summary)
    
    document_to_topic = dict(zip(documents, topics))
    merged_df['topic_id'] = merged_df['interaction_text'].apply(lambda x: document_to_topic.get(x, -1))
    
    topic_id_to_name = topic_model.get_topic_info().set_index('Topic').to_dict()['Name']
    merged_df['topic_name'] = merged_df['topic_id'].map(topic_id_to_name)
    
    print("\nFirst 10 customers with sentiment and topic analysis results:")
    print(merged_df[['customerID', 'interaction_text', 'sentiment_label', 'topic_name']].head(10))