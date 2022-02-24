from typing import Optional, Union, List


def get_mode_selector(obj : Optional[Union[int, List[int], slice]]) -> Union[slice, List]:
    ''' Create a mode selector for a given input object.

    For all possible input types (except for list) the object is returned
    as a slice. Lists are returned as lists.

    Parameters
    ----------
    obj : Optional[Union[int, List[int], slice]]
        Data type to be casted as a mode selector.


    '''
    MAX_MODE = 9999999
    if obj is None:
        return slice(MAX_MODE)
    elif isinstance(obj, int):
        return slice(obj)
    elif isinstance(obj, slice):
        # Reduce slice start by one so that "1" is the first element
        try:
            new_start = obj.start - 1
        except TypeError:
            new_start = 0
        # Slice start cannot be negative
        new_start = max(0, new_start)
        return slice(new_start, obj.stop, obj.step)
    elif isinstance(obj, list):
        # Reduce all list elements by 1 so that "1" is first element
        return [o - 1 for o in obj]
    else:
        obj_type = type(obj)
        err_msg = 'Invalid type {:}. Must be one of [int, slice, list, None].'
        err_msg = err_msg.format(obj_type)
        raise ValueError(err_msg)
