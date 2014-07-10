__author__ = 'raulcd'

def solution(A):
    """
    This functions calculates the extremes:
    >>> A = [9, 4, -3, -10]
    >>> solution(A)
    3
    >>> A = [1, -1]
    >>> solution(A)
    [0, 1]
    """
    # Calculate Average
    average = sum(A) / len(A)
    # Generator with a tuple with the element and the index
    element_idx_gen = ((element, index) for index, element in enumerate(A))
    # function to calculate the max deviation
    def check_max_dev(x, y):
        if abs(x[0] - average) == abs(y[0] - average):
            return (x[0], x[1], y[0], y[1])
        elif abs(x[0] - average) > abs(y[0] - average):
            return x
        else:
            return y
    # Using of reduce funtion to calculate the max
    max_dev_element = reduce(check_max_dev, element_idx_gen)
    # Only two possible max_deviation so if the element has a tuple of len 4
    if len(max_dev_element) > 2:
        return [max_dev_element[1], max_dev_element[3]]
    return max_dev_element[1]

if __name__ == "__main__":
    import doctest
    doctest.testmod()