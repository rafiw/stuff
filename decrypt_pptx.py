import msoffcrypto
import io, sys
import itertools
import multiprocessing
from multiprocessing import Pool, Event, Manager

class Data:
    def __init__(self, p, e):
        self.p = p
        self.e = e

class Worker:
    def __init__(self, path):
        with open(path, "rb") as f:
            file_data = f.read()
        self.decrypted = io.BytesIO()
        self.file = msoffcrypto.OfficeFile(io.BytesIO(file_data))
    
    def decrypt(self, data):
        if data.e.is_set():
            return
        self.file.load_key(password=data.p)
        self.decrypted.seek(0)
        self.decrypted.truncate()
        try:
            print(f"trying {data.p}")
            self.file.decrypt(self.decrypted)
        except:
            return False
        print("password is: " + data.p)
        data.e.set()
        return True

def generate_combinations(length, event):
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_+="
    for combo in itertools.product(charset, repeat=length):
        yield Data(''.join(combo), event)

cores = multiprocessing.cpu_count()
worker = Worker(sys.argv[1])

event = Manager().Event()
event.clear()
with Pool(10) as p:
    for length in range(1,20):
        result = p.map(worker.decrypt, generate_combinations(length, event))
        if event.is_set():
            sys.exit(0)
