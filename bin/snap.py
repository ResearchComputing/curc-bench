#!/usr/bin/env python

import os
import pandas as pd

import snapshot
import users

users.execute()
snapshot.execute()

users = pd.read_csv('users.csv')
nodes = pd.read_csv('snapshot.csv')

data = pd.merge(users, nodes)
data.to_csv('snap.csv', index=False)

# Remove other files
os.remove('users.csv')
os.remove('snapshot.csv')
