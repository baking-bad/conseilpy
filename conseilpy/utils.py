__all__ = ['prepare_name']

def prepare_name(name):
    if name is None:
        raise ValueError(f'Invalid name: {name}')
    return name.replace(' ', '')
