import os
from sqlite3 import Connection
from database.video import init_video
from database.video_logs import init_video_logs


def init_database():
    init_video()
    init_video_logs()

    with Connection(database=os.path.join(os.getcwd(), "var/ywke_database")) as conn:
    #Users
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            permissions INTEGER NOT NULL,
            priority INTEGER NOT NULL);""")

    #Keys
        conn.execute("""CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            key TEXT NOT NULL,
            source TEXT NOT NULL,
            creator TEXT NOT NULL references users(id));""")

        conn.execute("""CREATE TABLE IF NOT EXISTS key_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            key_id INTEGER NOT NULL REFERENCES keys(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            type TEXT NOT NULL,
            old_value TEXT NOT NULL);""")

    #Recipes
        conn.execute("""CREATE TABLE IF NOT EXISTS recipes (
            recipe_id INTEGER NOT NULL,
            step_index INTEGER NOT NULL,
            method_id INTEGER NOT NULL,
            settings TEXT NOT NULL,
            PRIMARY KEY (recipe_id, step_index));""")

        conn.execute("""CREATE TABLE IF NOT EXISTS recipes_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id),
            index_id INTEGER NOT NULL REFERENCES recipes(step_index),
            user_id INTEGER NOT NULL REFERENCES users(id),
            type TEXT NOT NULL,
            old_value TEXT NOT NULL);""")

    #Dictionnary
        conn.execute("""CREATE TABLE IF NOT EXISTS dictionnary (
            word TEXT NOT NULL PRIMARY KEY NOT NULL);""")

        conn.execute("""CREATE TABLE IF NOT EXISTS dictionnary_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            word INTEGER NOT NULL REFERENCES dictionnary(word),
            user_id INTEGER NOT NULL REFERENCES users(id),
            type TEXT NOT NULL);""")

    #Bruteforce
        conn.execute("""CREATE TABLE IF NOT EXISTS bruteforces_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            recipe_id NOT NULL REFERENCES recipes(recipe_id),
            step_index INTEGER NOT NULL REFERENCES recipes(step_index),
            input TEXT NOT NULL,
            output TEXT NOT NULL,
            score FLOAT NOT NULL);""")
