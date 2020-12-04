import random

def simplebootstrap(datalist,n):
    '''
    Inputs a sample data and returns a list of 'n' bootstrapped means.
    '''
    l=len(datalist)
    samplemeans=[]
    for i in range(n):
        newsample = []
        for j in range(l):
            newsample.append(datalist[random.randint(0,l-1)])
        samplemeans.append(sum(newsample)/l)
    return samplemeans
