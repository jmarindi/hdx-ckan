'''
Created on Jan 14, 2015

@author: alexandru-m-g
'''

import pylons.config as config

import ckan.logic as logic
import ckan.lib.dictization.model_dictize as model_dictize
import ckan.lib.dictization as d
import ckan.model as model

get_action = logic.get_action
check_access = logic.check_access
_get_or_bust = logic.get_or_bust

NotFound = logic.NotFound


def sort_results_case_insensitive(results, sort_by):
    if results:
        if sort_by == 'title asc':
            return sorted(results, key=lambda x: x.get('title', '').lower())
        elif sort_by == 'title desc':
            return sorted(results, key=lambda x: x.get('title', '').lower(), reverse=True)
    return results


def hdx_get_group_activity_list(context, data_dict):
    from ckanext.hdx_package.helpers import helpers as hdx_package_helpers

    group_uuid = data_dict.get('group_uuid', None)
    if group_uuid:
        check_access('group_show', context, data_dict)

        model = context['model']
        offset = data_dict.get('offset', 0)
        limit = int(
            data_dict.get('limit', config.get('ckan.activity_list_limit', 31)))

        activity_objects = model.activity.group_activity_list(group_uuid,
                                                              limit=limit, offset=offset)
        activity_stream = model_dictize.activity_list_dictize(
            activity_objects, context)
    else:
        if 'group_type' in data_dict and data_dict['group_type'] == 'organization':
            activity_stream = get_action(
                'organization_activity_list')(context, data_dict)
        else:
            activity_stream = get_action(
                'group_activity_list')(context, data_dict)
    offset = int(data_dict.get('offset', 0))
    extra_vars = {
        'controller': 'group',
        'action': 'activity',
        'id': data_dict['id'],
        'offset': offset,
    }
    return hdx_package_helpers._activity_list(context, activity_stream, extra_vars)


def hdx_light_group_show(context, data_dict):
    id = _get_or_bust(data_dict, "id")
    group_dict = {}
    group = model.Group.get(id)
    if not group:
        raise NotFound
    group_dict['group'] = group
    group_dict['id'] = group.id
    group_dict['name'] = group.name
    group_dict['display_name'] = group_dict['title'] = group.title

    result_list = []
    for name, extra in group._extras.iteritems():
        dictized = d.table_dictize(extra, context)
        if not extra.state == 'active':
            continue
        value = dictized["value"]
        result_list.append(dictized)

    group_dict['extras'] = sorted(result_list, key=lambda x: x["key"])
    return group_dict