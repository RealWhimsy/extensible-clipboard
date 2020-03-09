import sqlite3
import os

def wipe():
    path = os.path.expanduser('~/clip_collection.db')
    conn = sqlite3.connect(path)
    conn.execute('DELETE FROM clips')
    conn.execute('DELETE FROM clipboards')
    conn.commit()