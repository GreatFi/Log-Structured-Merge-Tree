"""
A simple implementation of a write-ahead-log used for reconcilation after network outages or crashes during operations.
"""
import os
import csv


class Singleton:
    
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self, filename):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated(filename)
            return self._instance

    def __call__(self):
        raise TypeError("Singletons must be accessed through 'instance()'")
    
    def __instancecheck__(self, instance):
        return isinstance(self._decorated, instance)
    
@Singleton
class WAL:
    
    def __init__(self, filename):
        
        self.filename = filename
        self.stream = open(filename, 'a')

    def write(self, val):
        try:
            self.stream.write(val)
            self.stream.flush()
            os.fsync(self.stream.fileno())
        except IOError:
            print("The filestream isn't currently open")

    def replay(self, filename):
        
        rows = []
        with open(filename, mode="r") as f:
            csv_reader = csv.reader(f)

            for row in csv_reader:
                rows.append(row)
        return rows
        

