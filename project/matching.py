import json
from google.protobuf import descriptor as _descriptor
from subscription_pb2 import Subscription
from publication_pb2 import Publication
import google.protobuf.json_format
from datetime import datetime


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
    s = Subscription()
    s.ParseFromString(sub)
    sub = google.protobuf.json_format.MessageToDict(s)
    mandatory_fields = sub.keys()

    print("sub {}".format(sub))
    for pub in list_of_pubs:
        found_sub_fields = 0
        p = Publication()
        p.ParseFromString(pub)
        pub = google.protobuf.json_format.MessageToDict(p)
        print("pub {}".format(pub))
        if not set(mandatory_fields).issubset(pub.keys()):
            print("pub {} doesn't have all the fields in the sub!".format(pub))
            continue
        for pub_k, pub_v in pub.items():
            if pub_k not in mandatory_fields:
                continue  # optional pub field
            if operator_matching(sub[pub_k]["value"], pub_v, sub[pub_k]["operator"]):
                found_sub_fields += 1
        if found_sub_fields == len(mandatory_fields):
            publication = Publication()
            publication.car_model = pub.get("car_model", "")
            publication.production_date = datetime.strftime(pub["production_date"], "%d-%m-%Y") if pub.get(
                "production_date") else ""
            publication.max_speed = pub.get("max_speed", 0)
            publication.horsepower = pub.get("horsepower", 0)
            publication.color = pub.get("color", "")
            matching_pubs.append(publication.SerializeToString())

    print("matching_pubs {}".format(matching_pubs))
    return matching_pubs


if __name__ == '__main__':
    print("Start")
