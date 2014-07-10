__author__ = 'raulcd'
def solution(A):
    """
    I will use recursivity so just check if the IndexError is raised when trying to access out of the array.
    >>> A = [2, 3, -1, 1, 3]
    >>> solution(A)
    4
    >>> A = [1, 1, -1, 1]
    >>> solution(A)
    -1
    >>> A = [1, -2, -1, 1]
    >>> solution(A)
    1
    """
    count = 0
    max_count = len(A)
    def next_step(count, position):
        if count > max_count:
            #Check if we have already done all the array loop
            return -1
        else:
            try:
                if position < 0:
                    # In this case we are already out of the range, so previous step
                    return count - 1
                return next_step(count+1, position + A[position])
            except IndexError:
                return count
    return next_step(count, 0)



if __name__ == "__main__":
    import doctest
    doctest.testmod()