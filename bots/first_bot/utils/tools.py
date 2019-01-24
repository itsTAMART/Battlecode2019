#


def sort_tuples(arr, bc):
    """ selection sort from:
    https://medium.com/@george.seif94/a-tour-of-the-top-5-sorting-algorithms-with-python-code-43ea9aa02889
    """
    # bc.log('before sort')
    # bc.log(arr)

    for i in range(len(arr)):
        minimum = i

        for j in range(i + 1, len(arr)):
            # Select the smallest value

            a = int(arr[j][0])
            b = int(arr[minimum][0])

            if a < b:
                minimum = j

        # Place it at the front of the
        # sorted end of the array
        arr[minimum], arr[i] = arr[i], arr[minimum]

    # bc.log('after')
    # bc.log(arr)

    return arr


def sorted_tuples(arr):
    """ selection sort from:
    https://medium.com/@george.seif94/a-tour-of-the-top-5-sorting-algorithms-with-python-code-43ea9aa02889
    """
    # bc.log('before sort')
    # bc.log(arr)

    for i in range(len(arr)):
        minimum = i

        for j in range(i + 1, len(arr)):
            # Select the smallest value

            a = int(arr[j][0])
            b = int(arr[minimum][0])

            if a < b:
                minimum = j

        # Place it at the front of the
        # sorted end of the array
        arr[minimum], arr[i] = arr[i], arr[minimum]

    # bc.log('after')
    # bc.log(arr)

    return arr



#
