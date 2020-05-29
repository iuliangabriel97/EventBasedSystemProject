import json


def operator_matching(sub_field_value, pub_field_value, op):
    if op == "=":
        if pub_field_value != sub_field_value:
            return False
    if op == "!=":
        if sub_field_value == pub_field_value:
            return False
    if op == "<":
        if sub_field_value <= pub_field_value:
            return False
    if op == "<=":
        if sub_field_value < pub_field_value:
            return False
    if op == ">":
        if sub_field_value >= pub_field_value:
            return False
    if op == ">=":
        if sub_field_value > pub_field_value:
            return False
    return True


def try_match(list_of_pubs, sub):
    matching_pub = None
    sub = json.loads(sub.decode('utf8').replace("'", '"'))

    for field, values in sub.items():
        for pub in list_of_pubs:
            pub = json.loads(pub.decode('utf8').replace("'", '"'))
            if field not in pub:
                continue
            if not operator_matching(values["value"], pub[field], values["operator"]):
                continue
            matching_pub = pub
    return matching_pub

