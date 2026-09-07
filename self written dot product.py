

w=[2,1,4]
x= [1,3,5]
h=0


for b,i in enumerate (x):
    for c,j in enumerate(w):
        if  c==b:
            h=h+i*j
        
print(h)