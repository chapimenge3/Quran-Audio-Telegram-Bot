import json

with open('Surah.json') as s:
    surah = json.load(s)
print("{")
for i,j in surah.items():
    print('    "',j,'" : "',i,'" ,' , sep="")
print("}")