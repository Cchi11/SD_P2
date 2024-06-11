import pickle

class StoreService (object):

    def __init__(self):
        self.store = dict()
        try:
            self.restore()
        except FileNotFoundError:
            pass

    def put(self, key, value):
        try:
            self.store[key] = value
            self.save()
            success = True
        except:
            success = False

        return success

    def get(self, key):
        try:
            value = self.store[key]
            found = True
        except:
            data = None
            found = False
        
        return found, value
    
    def save(self):
        with open('binary_dict.pickle', 'wb') as f:
            pickle.dump(self.store, f)
    
    def restore(self):
        with open('binary_dict.pickle', 'rb') as f:
            self.store = pickle.load(f)
        

