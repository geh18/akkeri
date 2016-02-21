from models import *
import csv

# Locations from http://www.unece.org/cefact/locode/welcome.html (download csv)
# Tested this out but it's not really neccesary for now

# TABLES
"""

BEGIN;

create table countries (
    id serial not null primary key,
    name varchar not null
);

create table cities (
    id serial not null primary key,
    name varchar not null,
    country_id int not null references countries (id) on update cascade on delete cascade
);


COMMIT;


"""

# MODELS

"""


ass Country(db.Model):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    cities = relationship('City', backref='countries')

    def __unicode__(self):
        return u'%s' % self.name


class City(db.Model):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'))

"""


def read():
    file = open('locations/Part1.csv', 'rb')
    reader = csv.reader(file)

    country = None
    for i, row in enumerate(reader):
        try:
            unicode(row[3], 'utf-8')
        except Exception as e:
            continue
            print 'skipped = ' + row[3].title()

        if row[3].startswith('.'):
            if country:
                print 'country = '
                print country
                db.session.add(country)
            country = Country(name=row[3].title()[1:])
        else:
            city = City(name=row[3].title())
            country.cities.append(city)

    print 'COMMIT IT'
