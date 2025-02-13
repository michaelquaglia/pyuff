import numpy as np
import math

from ..tools import _opt_fields, _parse_header_line, check_dict_for_none

def _write2429(fh, dset):
    try:
        dict = {'active_constraint_set_no_for_group': 0,
                'active_restraint_set_no_for_group': 0,
                'active_load_set_no_for_group': 0,
                'active_dof_set_no_for_group': 0,
                'active_temperature_set_no_for_group': 0,
                'active_contact_set_no_for_group': 0 }

        dset = _opt_fields(dset, dict)
        fh.write('%6i\n%6i\n' % (-1, 2429))

        # Record 1
        # Field 8 (last field) contains the number or entities in the group
        fh.write('%10i%10i%10i%10i%10i%10i%10i%10i\n' % (dset['group_number'], 
                                                            dset['active_constraint_set_no_for_group'],
                                                            dset['active_restraint_set_no_for_group'],
                                                            dset['active_load_set_no_for_group'],
                                                            dset['active_dof_set_no_for_group'],
                                                            dset['active_temperature_set_no_for_group'],
                                                            dset['active_contact_set_no_for_group'],
                                                            len(dset['entity_type_code'])))
        # Record 2
        fh.write('%-40s\n' % (dset['group_name']))

        # Record 3-N
        # Write the full lines (which have 4 pairs)
        for i in range(len(dset['entity_type_code']) // 4):
            fh.write('%10i%10i%10i%10i%10i%10i%10i%10i\n' % (dset['entity_type_code'][i * 4], dset['entity_tag'][i * 4],
                                                                dset['entity_type_code'][i * 4 + 1], dset['entity_tag'][i * 4 + 1],
                                                                dset['entity_type_code'][i * 4 + 2], dset['entity_tag'][i * 4 + 2],
                                                                dset['entity_type_code'][i * 4 + 3], dset['entity_tag'][i * 4 + 3]))
        # Write the last line
        for i in range(len(dset['entity_type_code']) % 4):
            # don't write the line break just yet
            fh.write('%10i%10i' % (dset['entity_type_code'][i * 4], dset['entity_tag'][i * 4]))
        # Write the missing line break, but only if a non full last line has been written
        if (len(dset['entity_type_code']) % 4 != 0):
            fh.write('\n')

        fh.write('%6i\n' % -1)

    except:
        raise Exception('Error writing data-set #2429')


def _extract2429(block_data):
    """Extract  permanent groups data - data-set 2429."""
    dset = {'type': 2429, 'groups': []}
    try:
        split_data = block_data.splitlines()
        
        # there can be multiple groups in the data-set, therefore need to loop.
        lineIndex = 2
        while lineIndex < len(split_data) - 2:
            group = {}
            group.update(_parse_header_line(split_data[lineIndex], 8, [10, 10, 10, 10, 10, 10, 10, 10], [2, 2, 2, 2, 2, 2, 2, 2],
                                            ['group_number', 'active_constraint_set_no_for_group', 'active_restraint_set_no_for_group', 'active_load_set_no_for_group',
                                                'active_dof_set_no_for_group', 'active_temperature_set_no_for_group', 'active_contact_set_no_for_group', 'number_of_entities_in_group']))
            group.update(_parse_header_line(split_data[lineIndex + 1], 1, [40], [1], ['group_name']))
            # Record 1 field 8 (last field) contains the number or entities in the group
            # max 4 items per line, last line in group doesn't necessarily contain 4 elements
            indexLastLineForGroup = math.ceil(group['number_of_entities_in_group'] / 4) + lineIndex + 2
            # split all lines and then each line in separate integers. Put this in a ndarray
            values = [[int(elem) for elem in line.split()] for line in split_data[lineIndex + 2: indexLastLineForGroup]]
            # flatten the list and put in ndarray
            values = np.array([item for sublist in values for item in sublist], dtype=int)
            group['entity_type_code'] = np.array(values[::2].copy(), dtype=int)
            group['entity_tag'] = np.array(values[1::2].copy(), dtype=int)
            dset['groups'].append(group) # dset is a dictionary, but 'groups' is a list

            lineIndex = indexLastLineForGroup

    except:
        raise Exception('Error reading data-set #2429')
    return dset


def prepare_group(
        group_number,
        group_name,
        entity_type_code,
        entity_tag,
        active_constraint_set_no_for_group = 0,
        active_restraint_set_no_for_group = 0,
        active_load_set_no_for_group = 0,
        active_dof_set_no_for_group = 0,
        active_temperature_set_no_for_group = 0,
        active_contact_set_no_for_group = 0,
        return_full_dict = False):
    """Name: Permanent Groups

    R-Record, F-Field
    
    :param group_number: R1 F1, group number
    :param group_name: R2 F1, group name
    :param entity_type_code: R3-N, entity type code
    :param entity_tag: R3-N, entity tag
    :param active_constraint_set_no_for_group: R1 F2, active constraint set no. for group
    :param active_restraint_set_no_for_group: R1 F3, active restraint set no. for group
    :param active_load_set_no_for_group: R1 F3, active restraint set no. for group
    :param active_dof_set_no_for_group: R1 F3, active restraint set no. for group
    :param active_temperature_set_no_for_group: R1 F3, active restraint set no. for group
    :param active_contact_set_no_for_group: R1 F3, active restraint set no. for group
    :param return_full_dict: If True full dict with all keys is returned, else only specified arguments are included 

    Records 1 and 2 are repeated for each permanent group in the model.
    Record 3 is repeated multiple times for each group
    """

    if type(group_number) != int:
         raise TypeError('group_number must be integer')
    if type(group_name) != str:
         raise TypeError('group_name must be string')
    if np.array(entity_type_code).dtype != int:
        raise TypeError('entity_type_code must all be positive integers')
    if np.array(entity_tag).dtype != int:
        raise TypeError('entity_tag must all be positive integers')
    if type(active_constraint_set_no_for_group) != int:
         raise TypeError('active_constraint_set_no_for_group must be integer')
    if type(active_restraint_set_no_for_group) != int:
         raise TypeError('active_restraint_set_no_for_group must be integer')
    if type(active_load_set_no_for_group) != int:
         raise TypeError('active_load_set_no_for_group must be integer')
    if type(active_dof_set_no_for_group) != int:
         raise TypeError('active_dof_set_no_for_group must be integer')
    if type(active_temperature_set_no_for_group) != int:
         raise TypeError('active_temperature_set_no_for_group must be integer')
    if type(active_contact_set_no_for_group) != int:
         raise TypeError('active_contact_set_no_for_group must be integer')

    if group_number < 0:
        raise ValueError('group_number needs to be a positive integer')
    if group_name == '':
        raise ValueError('group_name needs to be a non emtpy string')
    if active_constraint_set_no_for_group < 0:
        raise ValueError('active_constraint_set_no_for_group needs to be a positive integer')
    if active_restraint_set_no_for_group < 0:
        raise ValueError('active_restraint_set_no_for_group needs to be a positive integer')
    if active_load_set_no_for_group < 0:
        raise ValueError('active_load_set_no_for_group needs to be a positive integer')
    if active_dof_set_no_for_group < 0:
        raise ValueError('active_dof_set_no_for_group needs to be a positive integer')
    if active_temperature_set_no_for_group < 0:
        raise ValueError('active_temperature_set_no_for_group needs to be a positive integer')
    if active_contact_set_no_for_group < 0:
        raise ValueError('active_contact_set_no_for_group needs to be a positive integer')

    group={
        'group_number': group_number,
        'group_name': group_name,
        'entity_type_code': entity_type_code,
        'entity_tag': entity_tag,
        'active_constraint_set_no_for_group': active_constraint_set_no_for_group,
        'active_restraint_set_no_for_group':  active_restraint_set_no_for_group,
        'active_load_set_no_for_group': active_load_set_no_for_group,
        'active_dof_set_no_for_group': active_dof_set_no_for_group,
        'active_temperature_set_no_for_group': active_dof_set_no_for_group,
        'active_contact_set_no_for_group': active_dof_set_no_for_group,
        }
    
    if return_full_dict is False:
        group = check_dict_for_none(group)

    return group


def prepare_2429(
        groups,
        return_full_dict = False):
    """Name: Permanent Groups
    
    :param groups: a list of permanent groups
    :param return_full_dict: If True full dict with all keys is returned, else only specified arguments are included 
    """
    # **Test prepare_2429**
    #>>> save_to_file = 'test_pyuff'
    #>>> myGroup1 = pyuff.prepare_group(
    #>>>     group_number = 1,
    #>>>     group_name = 'myGroup',
    #>>>     entity_type_code = np.array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10]),
    #>>>     entity_tag = np.array([ 1,  2,  3,  4,  5,  6,  7,  8,  9, 10]),
    #>>>     active_constraint_set_no_for_group = 0)
    #>>> dataset = pyuff.prepare_2429(
    #>>>     groups = [myGroup1])
    #>>> if save_to_file:
    #>>>     if os.path.exists(save_to_file):
    #>>>         os.remove(save_to_file)
    #>>>     uffwrite = pyuff.UFF(save_to_file)
    #>>>     uffwrite.write_sets(dataset, mode='add')
    #>>> dataset

    if type(groups) != list:
         raise TypeError('groups must be in a list, also a single group')
    for item in groups:
        prepare_group(
            item['group_number'],
            item['group_name'],
            item['entity_type_code'],
            item['entity_tag'],
            item['active_constraint_set_no_for_group'],
            item['active_restraint_set_no_for_group'],
            item['active_load_set_no_for_group'],
            item['active_dof_set_no_for_group'],
            item['active_temperature_set_no_for_group'],
            item['active_contact_set_no_for_group'])

    dataset={
        'type': 2429,
        'groups': groups,
        }
    
    if return_full_dict is False:
        dataset = check_dict_for_none(dataset)

    return dataset
