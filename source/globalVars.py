from collections import OrderedDict

def init():
    global pairs
    global Spheres
    global nonuniquecount
    global functionalChart
    pairs = {}
    Spheres = OrderedDict()  # key is word, value is list containing frequency plus linked status
    nonuniquecount = 0
    functionalChart = {}
def reset():
    global pairs
    global Spheres
    global nonuniquecount
    pairs = {}
    Spheres = OrderedDict()  # key is word, value is list containing frequency plus linked status
    nonuniquecount = 0