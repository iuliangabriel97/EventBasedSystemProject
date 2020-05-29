import json


def operator_matching(sub_field_value, pub_field_value, op):
    if op == "==":
        if pub_field_value != sub_field_value:
            return False
    if op == "!=":
        if sub_field_value == pub_field_value:
            return False
    if op == "<":
        if sub_field_value >= pub_field_value:
            return False
    if op == "<=":
        if sub_field_value > pub_field_value:
            return False
    if op == ">":
        if sub_field_value <= pub_field_value:
            return False
    if op == ">=":
        if sub_field_value < pub_field_value:
            return False
    return True


def try_match(list_of_pubs, sub):
    matching_pubs = []
    sub = json.loads(sub.decode('utf8').replace("'", '"'))
    mandatory_fields = sub.keys()

    for pub in list_of_pubs:
        found_sub_fields = 0
        pub = json.loads(pub.decode('utf8').replace("'", '"'))

        if not set(mandatory_fields).issubset(pub.keys()):
            # print("pub {} doesn't have all the fields in the sub!".format(pub))
            continue
        for pub_k, pub_v in pub.items():
            if pub_k not in mandatory_fields:
                continue  # optional pub field
            if operator_matching(sub[pub_k]["value"], pub_v, sub[pub_k]["operator"]):
                found_sub_fields += 1
        if found_sub_fields == len(mandatory_fields):
            matching_pubs.append(pub)

    return matching_pubs
