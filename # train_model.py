import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
import pickle
from flask import Flask, request, jsonify

# Load dataset
df = pd.read_csv("/Users/sujit/Downloads/DATA SCIENCE FILES/Project/shopping_data.csv")
df.fillna(method='ffill', inplace=True)
df.drop_duplicates(inplace=True)

# Feature Engineering
df['purchase_count'] = df.groupby('customer_id')['order_value'].transform('count')
df['avg_order_value'] = df.groupby('customer_id')['order_value'].transform('mean')

# Date handling
if 'order_date' in df.columns:
    df['order_date'] = pd.to_datetime(df['order_date'])
    latest_date = df['order_date'].max()
    df['recency'] = (latest_date - df['order_date']).dt.days
else:
    df['recency'] = np.nan

# Normalize features
scaler = MinMaxScaler()
df[['product_price', 'recommendation_score']] = scaler.fit_transform(df[['product_price', 'recommendation_score']])

# Train collaborative filtering model
reader = Reader(rating_scale=(0, 1))  # Your scaled scores are in 0-1 range now
data = Dataset.load_from_df(df[['customer_id', 'product_id', 'recommendation_score']], reader)
trainset, testset = train_test_split(data, test_size=0.2)

model = SVD()
model.fit(trainset)

# Save model
with open("recommender_model.pkl", "wb") as file:
    pickle.dump(model, file)

# Flask App
app = Flask(__name__)

# Load trained model
with open("recommender_model.pkl", "rb") as file:
    loaded_model = pickle.load(file)

@app.route('/')
def index():
    return "✅ Recommender API is running!"

@app.route('/recommend', methods=['GET'])
def recommend():
    user_id = request.args.get('user_id')
    print("Received user_id:", user_id)
    print("All customer IDs:", df['customer_id'].unique())

    if not user_id:
        return jsonify({"error": "Please provide a valid user_id"}), 400

    if user_id not in df['customer_id'].unique():
        return jsonify({"error": f"User ID '{user_id}' not found in system"}), 404

    recommendations = []
    for product_id in df['product_id'].unique():
        pred = loaded_model.predict(user_id, product_id)
        recommendations.append((product_id, pred.est))

    recommendations.sort(key=lambda x: x[1], reverse=True)
    top_recommendations = recommendations[:5]

    return jsonify({
        'user_id': user_id,
        'recommendations': [
            {"product_id": pid, "estimated_score": round(score, 2)}
            for pid, score in top_recommendations
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)