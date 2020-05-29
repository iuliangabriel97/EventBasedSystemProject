from tema.generator import PublicationsGenerator, SubscriptionsGenerator
from publication_pb2 import Publication
from subscription_pb2 import Subscription, FieldConfigType1, FieldConfigType2
from datetime import datetime

# pub_gen = PublicationsGenerator(publications_count=2).generate()
# for pub in pub_gen:
#     publication = Publication()
#     publication.car_model = pub.car_model
#     publication.production_date = datetime.strftime(pub.production_date, "%d-%m-%Y")
#     publication.max_speed = pub.max_speed
#     publication.horsepower = pub.horsepower
#     publication.color = pub.color
#     print(publication)
#     publication.SerializeToString()
#     publication.Clear()

sub_gen = SubscriptionsGenerator(subscriptions_count=2).generate()
for sub in sub_gen:
    subscription = Subscription()
    for key, value in sub.items():
        if key == "car_model":
            subscription.car_model.operator = value["operator"]
            subscription.car_model.value = value["value"]
        elif key == "horsepower":
            subscription.horsepower.operator = value["operator"]
            subscription.horsepower.value = value["value"]
        elif key == "production_date":
            subscription.production_date.operator = value["operator"]
            subscription.production_date.value = value["value"]
        elif key == "color":
            subscription.color.operator = value["operator"]
            subscription.color.value = value["value"]
        elif key == "max_speed":
            subscription.max_speed.operator = value["operator"]
            subscription.max_speed.value = value["value"]
        print(subscription)
    x = subscription.SerializeToString()
    subscription.Clear()
    print(x, type(x))
    S = Subscription()
    S.ParseFromString(x)
    print(S)
