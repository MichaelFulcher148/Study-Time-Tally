"""
Based on Bubble Sort, uses a list of timestamps as the comparison to base the sorting of items in the 'file_list'.
"""
def sort_list_by_date(file_list: list, timestamp_list: list) -> None:
    length: int = len(file_list)
    if length != len(timestamp_list):
        raise ValueError('Lists are not the same length.')
    for x in range(length - 1, -1, -1):
        swap_happened: bool = False
        for y in range(x):
            y2: int = y + 1
            if timestamp_list[y] > timestamp_list[y2]:
                swap_happened = True
                timestamp_list[y], timestamp_list[y2] = timestamp_list[y2], timestamp_list[y]
                file_list[y], file_list[y2] = file_list[y2], file_list[y]
        if not swap_happened:
            return

# if __name__ =='__main__':
#     list1, list2 = ['had', 'mat', 'cat'], [3, 0, 4]
#     sort_list_by_date(list1, list2)
#     assert list1 == ['mat', 'had', 'cat']
#     assert list2 == [0, 3, 4]
#
#     list1, list2 = ['t', 'u', 'g', 'h'], [5, 2, 3, 1]
#     expected1, expected2 = ['h', 'u', 'g', 't'], [1, 2, 3, 5]
#     sort_list_by_date(list1, list2)
#     assert list1 == expected1, f"Expected: {expected1}, Got:{list1}"
#     assert list2 == expected2, f"Expected: {expected2}, Got:{list2}"
#
#     list1, list2 = ['t', 'u', 'g', 'h', 'i'], [5, 0, 2, 3, 1]
#     expected1, expected2 = ['u', 'i', 'g', 'h', 't'], [0, 1, 2, 3, 5]
#     sort_list_by_date(list1, list2)
#     assert list1 == expected1, f"Expected: {expected1}, Got:{list1}"
#     assert list2 == expected2, f"Expected: {expected2}, Got:{list2}"
#
#     list1, list2 = ['t', 'u', 'g', 'h', 'i'], [1, 0, 3, 6, 7]
#     expected1, expected2 = ['u', 't', 'g', 'h', 'i'], [0, 1, 3, 6, 7]
#     sort_list_by_date(list1, list2)
#     assert list1 == expected1, f"Expected: {expected1}, Got:{list1}"
#     assert list2 == expected2, f"Expected: {expected2}, Got:{list2}"