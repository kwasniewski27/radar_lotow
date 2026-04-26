# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
from datetime import datetime

class BazaDanychPipeline:
    def __init__(self):
        self.con = sqlite3.connect('baza_lotow.db')
        self.cur = self.con.cursor()
        
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS loty (
                kierunek TEXT,
                data_lotu TEXT,
                cena REAL,
                waluta TEXT,
                data_sprawdzenia TEXT
            )
        """)
        self.dzisiaj = datetime.now().strftime("%Y-%m-%d")

    def process_item(self, item, spider):
        self.cur.execute("""
            INSERT INTO loty (kierunek, data_lotu, cena, waluta, data_sprawdzenia)
            VALUES (?, ?, ?, ?, ?)
        """, (
            item.get('kierunek'), 
            item.get('data'), 
            item.get('cena'), 
            item.get('waluta'), 
            self.dzisiaj # Automatycznie stemplujemy dzisiejszą datą
        ))
        
        # Zatwierdzamy zapis
        self.con.commit()
        return item

    def close_spider(self, spider):
        # 4. Na koniec pracy grzecznie zamykamy połączenie z bazą
        self.con.close()