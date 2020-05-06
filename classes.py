class Drugs(object):
    """getter, setter for person"""

    def __init__(self):
        self._value = []

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        assert isinstance(value, list)
        self._value = value


class Person:
    """Class person
    Supports name, add_drgs, list"""

    band_size: int=0
    drugs = Drugs()

    def __init__(self, name):
        self.name = name
        self.drgs = []
        Person.band_size += 1

    def add_drgs(self, drgs):
        if not isinstance(drgs, list):
            return
        for d in drgs:
            self.drgs.append(d)

    def list(self):
        print("size %s" % Person.band_size)
        print("name %s" % self.name)
        for d in self.drgs:
            print('\t', d)
        for d in self.drugs:
                print('\t', d)

    def die(self):
        Person.band_size -= 1

    @classmethod
    def get_band(cls):
        return Person.band_size

