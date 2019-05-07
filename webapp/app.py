#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Change directory to VSCode workspace root so that relative path loads work correctly. Turn this addition off with the DataScience.changeDirOnImportExport setting
import os
try:
	os.chdir(os.path.join(os.getcwd(), '..'))
	print(os.getcwd())
except:
	pass


# In[4]:


from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import sklearn
import json
import requests
import random
import string
from sklearn.neighbors import NearestNeighbors
from IPython.display import display

distance_threshold = 0.1
url = 'https://csci4140langex.herokuapp.com/v1alpha1/graphql'


# In[5]:
def genUsers(n):
    def randomString(stringLength=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    inserts = ""
    for i in range(n):
        temp_name = '\"%s\"' % randomString(9)
        inserts += '{name: %s}' % (temp_name)
        if i != n-1:
            inserts += ','
    gen_query = '''
    mutation {
        insert_users(objects: [%s]) {
            returning {
                id
            }
        } 
    }

    ''' % (inserts)
    r = requests.post(url, json={'query': gen_query})
    result = r.json()
    print(result)
    stm = ''
    users = result['data']['insert_users']['returning']
    for user in users:
        n = random.choice(range(1,10))
        j = random.choices(range(4,26), k=n)
        rand_interest = list(dict.fromkeys(j))
        for key in range(len(rand_interest)):
            stm += '{interest_id: %d, user_id: %d, score: %d}' % (rand_interest[key], user['id'], int(random.choice(range(1,6))))
            stm += ','
    stm = stm[:-1] 

    gen_query = '''
    mutation {
      insert_users_interests(objects: [%s]) {
        returning {
          id
        }
      }
    }
    ''' % stm

    r = requests.post(url, json={'query': gen_query})
    # print(r.json())
# genUsers(50)


# In[9]:


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
        score
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
    users_interests = [[d['user_id'], d['interest_id'], d['score']] for d in json['data']['users_interests']]
    users = [[d['id'], d['name'], ] for d in json['data']['users']]
    print('done fetching')
    return interests, users_interests, users

interests, users_interests, users = fetch_data()


# In[10]:


interests_df = pd.DataFrame(interests, columns=['id','name'])
interests_df.set_index('id', inplace=True)
interests_df


# In[12]:

display(users_interests)
users_interests_df = pd.DataFrame(users_interests, columns=['user_id', 'interest_id', 'score'])
#users_interests_df.set_index('user_id', inplace=True)
users_interests_df = users_interests_df.pivot_table(index='user_id', columns='interest_id', values='score', fill_value=0, aggfunc={'score': lambda a: a})
users_interests_df


# In[13]:


users_df = pd.DataFrame(users, columns=['id', 'name'])
users_df.set_index('id', inplace=True)
# users_df


# In[15]:


pd.options.display.max_columns = None
def matching(user_id):  
    model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
    model_knn.fit(users_interests_df)

    distances, indices = model_knn.kneighbors(users_interests_df.loc[user_id].values.reshape(1,-1), n_neighbors = 20)
    distances = np.delete(distances.flatten(), 0)
    # indices = indices.flatten()
    indices = np.delete(indices.flatten(), 0)
    result = users_interests_df.iloc[indices].index
    display(users_interests_df.iloc[indices])
    return distances, result
    # return {'distances': distances.tolist(), 'result': result.tolist(), 'indices': indices}

# In[ ]:
def create_chat(users_id):
    query = '''
    mutation {
        insert_chats(objects: {}) {
            returning {
                id
            }
        }
    }
    ''' 
    r = requests.post(url, json={'query': query})
    if(r.status_code == 200):
        chat_id = r.json()['data']['insert_chats']['returning'][0]['id']
        print('created chat ', chat_id)

        inserts = ""
        for user_id in users_id:
            inserts += '{user_id: %s, chat_id: %s},' % (user_id, chat_id)
        inserts = inserts[:-1]

        query = '''
        mutation {
            insert_chats_members(objects: [%s]) {
                returning {
                    id
                }
            }
        }
        ''' % (inserts)
        r = requests.post(url, json={'query': query})

        if(r.status_code == 200):
            print('create chat member')
            return chat_id 
    return -1
# In[ ]:
from flask_cors import *

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route("/matching")
def res_matching():
    user_id = request.args.get('user_id')
    distances, result = matching(int(user_id))
    print(result)
    chat_id = create_chat([user_id, result[0]])
    if(chat_id == -1):
        print('error on communicating with db')
    else:
        return json.dumps({'chat_id': chat_id})

@app.route('/')
def hello():
    return 'works' 

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

