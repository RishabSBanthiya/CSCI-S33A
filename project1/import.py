import csv, os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))



def main():
    #opening csv file
    f = open('zips.csv')

    reader = csv.reader(f)
    for Zip in reader:
        db.execute('INSERT INTO CHECKING (Zip) VALUES (:Zip)',
                   {'Zip': Zip})


    db.commit()

if __name__ == '__main__':
    main()
