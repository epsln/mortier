from coords import point, circle
import random

def in_bounds(x, y, d_welzl):
    if x > d_welzl and x < 1000 + d_welzl and y > d_welzl and y < 1000 + d_welzl:
        return True
    else:
        False

def dist(a, b):
    return max(abs(a.x - b.x), abs(a.y - b.y))

def isInside(c, p):
    return dist(c.c, p) <= c.r

def getCircleCenter(bx, by, cx, cy):
    b = bx * bx + by * by
    c = cx * cx + cy * cy
    d = bx * cy - by * cx
    return point((cy * b - by * c) / (2 * d), (bx * c - cx * b) / (2 * d))

def circleFrom(a, b, c):
    i = getCircleCenter(b.x - a.x, b.y - a.y, c.x - a.x, c.y - a.y)
    i.x += a.x
    i.y += a.y
    return circle(i, dist(i, a))

def circleFromTwo(a, b):
    c = point((a.x + b.x) / 2.0, (a.y + b.y) / 2.0)
    return circle(c, dist(a, b) / 2.0)

def isValidCircle(c, p):
    return all(isInside(c, point) for point in p)

def minCircleTrivial(p):
    assert len(p) <= 3
    if not p:
        return circle(point(0, 0), 0)
    elif len(p) == 1:
        return circle(p[0], 0)
    elif len(p) == 2:
        return circleFromTwo(p[0], p[1])

    for i in range(3):
        for j in range(i + 1, 3):
            c = circleFromTwo(p[i], p[j])
            if isValidCircle(c, p):
                return c
    return circleFrom(p[0], p[1], p[2])

def welzlHelper(p, r, n):
    if n == 0 or len(r) == 3:
        return minCircleTrivial(r[:]) 

    idx = random.randint(0, n - 1)
    pnt = p[idx]
    p[idx], p[n - 1] = p[n - 1], p[idx]

    d = welzlHelper(p, r, n - 1)

    if isInside(d, pnt):
        return d

    return welzlHelper(p, r + [pnt], n - 1)  

def welzl(hull):
    hull_c = list(hull)
    random.shuffle(hull_c)
    return welzlHelper(hull_c, [], len(hull_c))


