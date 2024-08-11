from flask import Flask,jsonify,request
import pandas as pd

data = pd.read_csv('https://www.dropbox.com/scl/fi/1vxtcyy7majkkfy2z226r/India-Tourism-Statistics-2021-Table-5.2.4.csv?rlkey=b2n3x8344ud9dv1mtjz5nn1ek&raw=1')

data.dropna(subset=['Circle', 'Name of the Monument '], inplace=True)

data = data[['Circle', 'Name of the Monument ', 'Domestic-2019-20', 'Foreign-2019-20', 'Domestic-2020-21', 'Foreign-2020-21']]

data.fillna(0, inplace=True)

data['Avg_Domestic'] = (data['Domestic-2019-20'] + data['Domestic-2020-21']) / 2
data['Avg_Foreign'] = (data['Foreign-2019-20'] + data['Foreign-2020-21']) / 2

pivot_data = data.pivot_table(index='Name of the Monument ', columns='Circle', values=['Avg_Domestic', 'Avg_Foreign'], fill_value=0)

from sklearn.metrics.pairwise import cosine_similarity

cosine_sim = cosine_similarity(pivot_data[['Avg_Domestic', 'Avg_Foreign']])

cosine_sim_df = pd.DataFrame(cosine_sim, index=pivot_data.index, columns=pivot_data.index)

app=Flask(__name__)

@app.route("/recommend",methods=["POST"])
def recommend():
    data=request.get_json()
    num_recommendations=5
    sim_scores = cosine_sim_df[data["monument"]]
    sim_scores = sim_scores.sort_values(ascending=False)
    top_monuments = {}
    j=0
    for i in sim_scores[1:num_recommendations + 1].index:
        top_monuments.update({j:i})
        j+=1

    return jsonify(top_monuments),201

if __name__=="__main__":
    app.run(debug=True)