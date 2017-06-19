def remove_dashes_inner(item):
    return item.replace('-', '_')


def remove_dashes(goals):
    return [map(remove_dashes_inner, goal) for goal in goals]


def parse_group(group, types, existing_types):
    index_of_dash = group.index('-')
    obj_type = group[index_of_dash+1]
    if obj_type not in existing_types:
        raise Exception('Type "' + str(obj_type) + '" is not recognised in domain.')
    objects = group[:index_of_dash]
    for obj in objects:
        types[obj] = obj_type
    group = group[index_of_dash+2:]
    return group, objects
