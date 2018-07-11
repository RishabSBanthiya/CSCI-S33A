import csv, os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind=engine))



def main():

    f = open('zips.csv')

    reader = csv.reader(f)
    for Zip, City, State, Latitude,Longitude,Population in reader:
        db.execute('INSERT INTO \"ZIPCODE\" (Zip, City, State, Lat,Long,Pop) VALUES (:Zip, :City, :State, :Lat, :Long, :Pop)',
                   {'Zip': Zip, 'City': City, 'State': State , 'Lat': Latitude , 'Long': Longitude , 'Pop': Population })

    db.commit()

if __name__ == '__main__':
    main()
