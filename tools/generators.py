def countdown(i: int) -> int:
    while i >= 0:
        yield i
        i -= 1

def countup(i: int) -> int:
    f = 0
    while f < i:
        yield f
        f += 1

def range_countup(start: int, end: int) -> int:
    while start < end:
        yield start
        start += 1

def forward_count_loop(place: int, end: int) -> int:
    if place > end:
        place = 0
    while 1:
        yield place
        if place == end:
            place = 0
        else:
            place += 1

def reverse_count_loop(place: int, end: int) -> int:
    if place < 0:
        place = end
    while 1:
        yield place
        place -= 1
        if place == -1:
            place = end
