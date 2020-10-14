import copy
import sys
import logging
from pathlib import Path
#sys.path.append(str(Path(__file__).resolve().parents[1]))
import csv


def select_keys(dictionary, keys):
    """Selects dictionary keys."""

    dictionary_copy = copy.deepcopy(dictionary)

    # Select keys
    #dictionary_copy = {k: dictionary_copy[k] for k in (keys)}

    dictionary_copy_select = {}

    for k in keys:
        try:
            dictionary_copy_select[k] = dictionary_copy[k]
        except KeyError as err:
            #print(f'{err}: "{k}"')
            continue

    return dictionary_copy_select


# Add prefix to keys
def rename_keys(dictionary, prefix):
    """Renames dictionary keys based on matching list."""

    dictionary = copy.deepcopy(dictionary)

    new_keys = [prefix + '_' + key for key in dictionary.keys()]

    for new_key, old_key in zip(new_keys, list(dictionary.keys())):
        dictionary[new_key] = dictionary.pop(old_key)

    return dictionary

def clean_dict(dirty_dictionary, chars=['\n']):
    
    dictionary = copy.deepcopy(dirty_dictionary)
    
    for char in chars:
        for key, val in dictionary.items():
            if isinstance(val, str) and char in val:
                dictionary[key] = val.replace(char, ' ')
                
    return dictionary

def flatten_lists(nested_lists, delimiter='|'):
    """Recursively joins nested lists using a delimiter."""

    dictionary = copy.deepcopy(nested_lists)

    def flatten_list(dictionary):
        # Base case: test for lists with dictionaries (these cannot be flattened)
        list_keys = [key for key, value in dictionary.items()
                     if isinstance(value, list)]

        for key in dictionary.keys():
            try:
                if isinstance(dictionary[key][0], dict):
                    list_keys.remove(key)
            except:
                continue

        if len(list_keys) == 0:
            return dictionary

        # Recursive case: flatten list
        else:
            for key in list_keys:
                dictionary[key] = f'{delimiter}'.join(dictionary[key])
                list_keys.remove(key)

            return flatten_list(dictionary)

    return flatten_list(dictionary)


# Recursive function to flatten all keys with dictionaries
def nested_dict_buster(nested_dict):
    """
    Recursively appends the top level key's name to the nested dict's key names. 
    Moves the renamed nested dict's keys to the top level then deletes the empty top level key.
    """

    dictionary = copy.deepcopy(nested_dict)

    def flatten(dictionary):
        # Base case
        has_dict = sum([isinstance(value, dict)
                        for key, value in dictionary.items()])

        if has_dict == 0:
            return dictionary

        # Recursive case
        else:
            for key in list(dictionary.keys()):
                if isinstance(dictionary[key], dict):
                    for k in list(dictionary[key].keys()):
                        new_key = '_'.join([key, k])
                        dictionary[new_key] = dictionary[key].pop(k)

                    dictionary.pop(key)

            return flatten(dictionary)

    return flatten_lists(flatten(dictionary))


def listed_dict_buster(dictionary, master_key):
    """Flattens list of dicts by appending the top level key name
    to the lower level key name and separating values with delimiter."""
    
    dictionary = copy.deepcopy(dictionary)
    listed_dicts = dictionary[master_key]
        
    key_set = set()

    for dict_item in listed_dicts:
        for k, v in dict_item.items():
            key_set.add(k)

    new_keys = ['_'.join([master_key, label]) for label in key_set]
    
    dictionary.update({k:[] for k in new_keys})
    
    for d in listed_dicts:
        for k, v in d.items():
            label = '_'.join([master_key, k])
            #if isinstance(v, list) and len(v) == 1:
                #v = v[0]
            if isinstance(v, list) and len(v) > 0:
                v = '|'.join(v)
                
            dictionary[label].append(str(v))
            
    dictionary.pop(master_key)
    
    return flatten_lists(dictionary)


def dict_smasher(dictionary):
    """
    Flattens a dictionary using recursive functions.
    """
    
    dictionary = copy.deepcopy(dictionary)
    
    for key, value in dictionary.items():
        if isinstance(value, dict):
            dictionary = nested_dict_buster(dictionary)
        elif isinstance(value, list):
            dictionary = listed_dict_buster(dictionary, key)
        else:
            continue
        
    return clean_dict(dictionary)

def dict_write(data, header, file_path):
    
    if not Path(file_path).is_file() and data:
        print("No file present, writing new csv...")
        try: 
        # Write a new csv
            with open(file_path, "w") as f:
                dict_writer = csv.DictWriter(f, header)
                dict_writer.writeheader()
                dict_writer.writerows(data)
        except Exception as e:
            print(f"Error writing dictionary: ", {e})
            return

    if Path(file_path).is_file() and data:
        try:
            # Append to csv
            with open(file_path, "a") as f:
                dict_writer = csv.DictWriter(f, header)
                print("Opening file...")
                dict_writer.writerows(data)            
                print(f"Appended {len(data)} rows to data.")
        except Exception as e:
            print(f"Error writing dictionary: ", {e})
            return


def remove_listed_dict_keys(list_of_dicts, keys):

    list_of_dicts_cp = copy.deepcopy(list_of_dicts)
    
    for entry in list_of_dicts_cp:
        for key in keys:
            popped = entry.pop(key)
            
    return list_of_dicts_cp