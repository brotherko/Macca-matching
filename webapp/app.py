from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import sklearn
import json
import requests
import random
import string
from sklearn.metrics.pairwise import euclidean_distances

url='https://csci4140langex.herokuapp.com/v1alpha1/graphql'
#%%
def fetch_data():
    query = '''
    {
      list_interests {
        id
        name
      }

      users_interests {
        id
        user_id
        interest_id
      }

      users {
        id
        name
      }
    }
    '''
    r = requests.post(url, json={'query': query})
    json = r.json()
    # print(json)
    interests = [[d['id'], d['name']] for d in json['data']['list_interests']]
    users_interests = [[d['user_id'], d['interest_id']] for d in json['data']['users_interests']]
    users = [[d['id'], d['name'], ] for d in json['data']['users']]
    return interests, users_interests, users


#%%
interests, users_interests, users = fetch_data()
interests_df = pd.DataFrame(interests, columns=['id','name'])
interests_df.set_index('id', inplace=True)
interests_df


#%%
users_interests_df = pd.DataFrame(users_interests, columns=['user_id', 'interest_id'])
#users_interests_df.set_index('user_id', inplace=True)
users_interests_df = users_interests_df.pivot_table(index='user_id', columns='interest_id', values='interest_id', fill_value=0, aggfunc={'interest_id': lambda _: 1})
# users_interests_df


#%%
users_df = pd.DataFrame(users, columns=['id', 'name'])
users_df.set_index('id', inplace=True)
# users_df


#%%
# users_with_interests_df = users_df.join(users_interests_df, how='left')
# users_with_interests_df


#%%
from sklearn.neighbors import NearestNeighbors
import numpy as np
def matching(user_id):  
    model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    model_knn.fit(users_interests_df)
    # result = users_interests_df.loc[user_id].to_frame().T

    distances, indices = model_knn.kneighbors(users_interests_df.loc[user_id].values.reshape(1,-1), n_neighbors = 20)
    distances = np.delete(distances.flatten(), 0)
    indices = np.delete(indices.flatten(), 0)
    return {'distances': distances.tolist(), 'result': indices.tolist()}
#     for idx in indices[0]:
#     #     if idx != 
#         result = result.append(users_interests_df.iloc[idx].T)

#     print(result)
app = Flask(__name__)

@app.route("/matching")
def res_matching():
  user_id = request.args.get('user_id')
  res = json.dumps(matching(int(user_id)))
  return res 

@app.route('/')
def hello():
    return 'works' 

if __name__ == '__main__':
    app.run(host='0.0.0.0')
