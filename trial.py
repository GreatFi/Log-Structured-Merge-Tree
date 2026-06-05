import heapq

a = [30,24,85,66,45,28,29,40]
b = [30,24,85,99,45,28,67,40]
c = [30,24,85,96,45,28,29,40]
d = [30,24,78,66,45,57,29,40]


merged = list(heapq.merge(sorted(a), sorted(b), sorted(c), sorted(d)))
print(merged)

b = dict(name="Sam", age=20)
print(b)

line_pairs = "class,python"
kv = line_pairs.split(",")
print(kv)


a = [3,4,5]
d =len(a)
print(d)

strings = "class,python,teacher,student"

for word in sorted(strings, reverse=True):
    print(word)

