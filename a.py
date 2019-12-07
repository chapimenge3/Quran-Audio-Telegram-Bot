import json

with open('getup.json') as files:
    data = json.load(files)

l = []
for i in data["result"]:
    l.append( [int(i['message']['audio']['title']), i['message']['audio']['file_id'] ] )
l.sort()
print('{')
for i in l:
    print('    "',i[0],'": "', i[1], '" ,' ,sep='')

print('}')