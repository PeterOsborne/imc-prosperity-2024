import math

num = [24, 70, 41, 21, 60, 47, 82, 87, 80, 35, 73, 89, 100, 90, 17, 77, 83, 85, 79, 55, 12, 27, 52, 15, 30]
hunters = [2, 4, 3, 2, 4, 3, 5, 5, 5, 3, 4, 5, 8, 7, 2, 5, 5, 5, 5, 4, 2, 3, 4, 2, 3]

letters = ['G', 'H', 'I', 'J', 'K']
numbers = ['26', '27', '28', '29', '30']

print(len(num), len(hunters))

best_one = -1
tile = -1
for i in range(len(num)):
    price = (num[i] * 7500)/hunters[i]
    if price > best_one:
        best_one = price
        tile = i

best_two = 0
tiles_two = [-1, -1]
for i in range(len(num)):
    for j in range(len(num)):
        if i == j:
            continue
        price = (num[i] * 7500)/hunters[i] + (num[j]*7500)/hunters[j] - 25
        if price > best_two:
            best_two = price
            tiles_two[0] = i
            tiles_two[1] = j


best_three = 0
tiles_three = [-1, -1, -1]
for i in range(len(num)):
    for j in range(len(num)):
        for k in range(len(num)):
            if i == j or j == k or k == i:
                continue
            price = (num[i] * 7500)/hunters[i] + (num[j]*7500)/hunters[j] + (num[k]*7500/hunters[k]) - 100
            if price > best_three:
                best_three = price
                tiles_three[0] = i
                tiles_three[1] = j
                tiles_three[2] = k


def make_coord(tiles):
    cords = []
    for tile in tiles:
        cords.append(letters[math.floor(tile/5)] + numbers[tile % 5])
    return cords

print(best_one, make_coord([tile]), tile)
print(best_two, make_coord(tiles_two), tiles_two[0], tiles_two[1])
print(best_three, make_coord(tiles_three), tiles_three[0], tiles_three[1], tiles_three[2])