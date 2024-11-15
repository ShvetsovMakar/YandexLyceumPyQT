def is_forward(array, first_button=''):
    if not first_button:
        if len(array) > 6:
            return True
        return False
    
    for i in range(len(array)):
        if array[i].name == first_button:
            return i + 6 < len(array)

def is_backward(array, first_button):
    return array[0].name != first_button
