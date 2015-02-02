#!/usr/bin/env python

"""
This class implements a session concept.  The basic API is:

bench session --create='name of session' 
bench session --rename='name of session'
bench session --session='name'
bench list
bench avail

bench cd
bench ls
"""

import os
import datetime
import pickle
import pprint

def get_directory_name(directory, name):

    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    
    if name is not None:
        return name
        # folder_name = os.path.join(directory,str(name))
        # if not os.path.exists(folder_name):
        #     os.makedirs(folder_name)
        # return folder_name, folder_name + ".pickle"

    folder = str(datetime.date.today())
    index = 1
    while index < 100:
        folder_name = folder + "-" + str(index)
        if not os.path.exists(folder_name):
            break
        index+=1
    return folder_name


class Session:

    def __init__(self, name=None):
        print '__init__'
        self.directory = '/home/molu8455/bench/junk'
        self.name = get_directory_name(self.directory, name)
        
        # self.name, self.pickle_name = get_directory_name(self.directory, name)

    def __del__(self):
        print '__del__'
        tmp = os.path.join(self.directory, self.name + str(".pickle"))
        with open(tmp, 'wb') as output:
            pickle.dump(self, output)

    def __exit__(self, type, value, traceback):
        print '__exit__'
        
    def __enter__(self):
        print '__enter__'
        return self          

    def list(self):
        print self.name, 'list'

    def load(self):
        print self.name, 'load'

    def avail(self):
        print self.name, 'avail'

with Session('lustre_test') as session:
    session.list()

with Session() as session:
    session.list()

# What are the current sessions




# with open('data.pkl', 'rb') as infile:
#     session = pickle.load(infile)
#     session.load()
#     session.list()





# session = json.loads(dump, object_hook=as_session)

# print session
# session.list()
# session.load()

# print '===='

# with Session('test') as session:

    
#     print dump



