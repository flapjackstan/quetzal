# -*- coding: utf-8 -*-

'''
Shopify helper functions

'''

def read_json(path, filename, ext) -> dict:
    '''
    
    Parameters
    ----------
    path : Path object
        Path object / destination.
    filename : str
        Name of file to write
    ext : str
        File type extension.

    Returns
    -------
    dict
        json converted to dictionary

    '''
    
    read_path = Path(path)
    
    with open(read_path.joinpath(filename + ext)) as json_file:
        data = json.load(json_file)
        
    return json.loads(data)