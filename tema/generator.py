import random
import datetime


class Publication:
    def __init__(self, car_model: str,
                 production_date: datetime.datetime,
                 horsepower: int,
                 color: str,
                 max_speed: int):
        # verific tipurile de date
        assert isinstance(car_model, str)
        assert isinstance(production_date, datetime.datetime)
        assert isinstance(horsepower, int) and horsepower > 0
        assert isinstance(color, str) and color in {"red", "blue", "green", "black", "white"}
        assert isinstance(max_speed, int) and max_speed > 0

        self.car_model = car_model
        self.production_date = production_date
        self.horsepower = horsepower
        self.color = color
        self.max_speed = max_speed

    # pentru afisare
    def __repr__(self):
        return 'Publication(model={}, production_date={}, horsepower={}, color={}, max_speed={})'.format(
            self.car_model, self.production_date, self.horsepower, self.color, self.max_speed
        )

    # pentru afisare
    def __str__(self):
        return '{{(car_model,"{}");(production_date,"{}");(horsepower,{});(color,"{}");(max_speed,{})}}'.format(
            self.car_model,
            self.production_date.strftime('%d-%m-%Y'),
            self.horsepower,
            self.color,
            self.max_speed
        )


class PublicationsGenerator:
    def __init__(
            self,
            publications_count=100,
            production_date_minimum=datetime.datetime(1990, 1, 1),
            production_date_maximum=datetime.datetime(2020, 1, 1),
            horsepower_minimum=70,
            horsepower_maximum=300,
            max_speed_minimum=50,
            max_speed_maximum=140,
            allowed_colors=None,
            allowed_models=None
    ):
        if not allowed_colors:
            allowed_colors = {"red", "blue", "green", "black", "white"}

        if not allowed_models:
            allowed_models = {'Mercedes', 'Fiat', 'Renault', 'Opel', 'Dacia'}

        self.publications_count = publications_count
        self. production_date_minimum = production_date_minimum
        self.production_date_maximum = production_date_maximum
        self.horsepower_minimum = horsepower_minimum
        self.horsepower_maximum = horsepower_maximum
        self.max_speed_minimum = max_speed_minimum
        self.max_speed_maximum = max_speed_maximum
        self.allowed_models = list(allowed_models)
        self.allowed_colors = list(allowed_colors)

    def generate(self):
        for _ in range(self.publications_count):
            # numarul de zile dintre min_date si max_date
            difference = int((self.production_date_minimum - self.production_date_minimum).total_seconds() / 3600 / 24)

            # zi random din intervalul ales
            production_date = self.production_date_minimum + datetime.timedelta(days=random.randint(0, difference))

            # creaza publicatie
            yield Publication(
                random.choice(self.allowed_models),
                production_date,
                random.randint(self.horsepower_minimum, self.horsepower_maximum),
                random.choice(self.allowed_colors),
                random.randint(self.max_speed_minimum, self.max_speed_minimum)
            )


# valori default ale parametrilor
class FieldConfig:
    def __init__(
            self,
            field_name='CAR',
            value_generator_function=lambda: 0,
            containing_ratio=0.25,
            operators_frequencies=None
    ):

        # frecvente default pentru operatori
        if not operators_frequencies:
            operators_frequencies = {
                '==': 0.5,
                '!=': 0,
                '>=': 0,
                '>': 0,
                '<=': 0,
                '<': 0
            }

        assert isinstance(operators_frequencies, dict)
        # doar anumiti operatori sunt permisi
        assert set(operators_frequencies.keys()).issubset({'==', '!=', '<=', '<', '>=', '>'})
        # suma frecventelor operatorilor trebuie sa fie <= 1
        assert sum(operators_frequencies.values()) <= 1.0

        # setez frecventa operatorilor nesetati la 0
        for operator in {'==', '!=', '<=', '<', '>=', '>'}:
            if operator not in operators_frequencies:
                operators_frequencies[operator] = 0

        # redistribui frecventele operatorilor nesetati in mod egal
        operators_with_zero_frequency = list(operators_frequencies.values()).count(0)
        rest = 1.0 - sum(value for value in operators_frequencies.values())
        for operator, frequency in operators_frequencies.items():
            if not frequency:
                operators_frequencies[operator] = rest / operators_with_zero_frequency

        self.field_name = field_name
        self.generate_value = value_generator_function
        self.containing_ratio = containing_ratio

        self.operators_frequencies = operators_frequencies


# valori default ale parametrilor
class SubscriptionsGenerator:
    def __init__(
            self,
            subscriptions_count=100,
            configs=None
    ):
        # configurari default ale field-urilor subscriptiilor
        if not configs:
            configs = [
                FieldConfig(
                    field_name='car_model',
                    value_generator_function=lambda: random.choice(["Mercedes", "Fiat"]),
                    containing_ratio=0.75,
                    operators_frequencies={
                        '==': 0.5,
                        '!=': 0.5
                    }
                ),
                FieldConfig(
                    field_name='horsepower',
                    value_generator_function=lambda: random.randint(150, 220),
                    containing_ratio=0.50,
                    operators_frequencies={
                        '==': 0.5,
                        '!=': 0.5
                    }
                )
            ]

        self.subscriptions_count = subscriptions_count
        self.configs = configs

    def generate(self):
        subscriptions = [dict() for _ in range(self.subscriptions_count)]

        # pentru fiecare configurare de field
            # calculez cate subscriptii trebuie sa contina acest config
            # incerc sa configurez toate subscriptiile "empty", apoi pe cele "non-empty"
            # "empty" = subscriptii care nu au nici o configurare de field
        for config in self.configs:
            empty_subscriptions = [i for i in range(self.subscriptions_count) if not subscriptions[i]]
            non_empty_subscriptions = [i for i in range(self.subscriptions_count) if subscriptions[i]]

            to_pick = int(self.subscriptions_count * config.containing_ratio)
            to_pick_from_empty = min(len(empty_subscriptions), to_pick)
            to_pick_from_non_empty = to_pick - to_pick_from_empty

            subscriptions_to_edit = random.sample(empty_subscriptions, to_pick_from_empty) + \
                                    random.sample(non_empty_subscriptions, to_pick_from_non_empty)



            # pt fiecare chunk de subscriptii pe care vrem sa-l configuram pastram frecventa operatorilor
            operators_to_pick = {
                operator: int(len(subscriptions_to_edit) * frequency)
                for operator, frequency in config.operators_frequencies.items()
            }


            for i in subscriptions_to_edit:
                operator = random.choice([op for op, frequency in config.operators_frequencies.items() if frequency])
                for op, to_pick in operators_to_pick.items():
                    if to_pick:
                        operator = op
                        operators_to_pick[op] -= 1
                        break

                subscriptions[i][config.field_name] = {
                    'operator': operator,
                    'value': config.generate_value()
                }

        for s in subscriptions:
            if not s:
                config = random.choice(self.configs)
                operator = random.choice([op for op, frequency in config.operators_frequencies.items() if frequency])
                s[config.field_name] = {
                    'operator': operator,
                    'value': config.generate_value()
                }

        return subscriptions


def dump_publications():
    generator = PublicationsGenerator().generate()

    with open('publications.txt', 'w') as handle:
        for i in generator:
            handle.write('{}\n'.format(i))


def dump_subscriptions():
    subscriptions = SubscriptionsGenerator(100, [
        FieldConfig(
            field_name='car_model',
            value_generator_function=lambda: random.choice(["Mercedes", "Fiat"]),
            containing_ratio=0.70,
            operators_frequencies={
                '==': 0.5,
                '!=': 0.5
            }
        ),
        FieldConfig(
            field_name='horsepower',
            value_generator_function=lambda: random.randint(100, 200),
            containing_ratio=0.50,
            operators_frequencies={
                '<=': 0.5,
                '!=': 0.5
            }
        ),
        FieldConfig(
            field_name='max_speed',
            value_generator_function=lambda: random.randint(150, 250),
            containing_ratio=0.30,
            operators_frequencies={
                '>=': 0.5,
                '<': 0.5
            }
        ),
    ]).generate()

    with open('subscriptions.txt', 'w') as handle:
        for subscription in subscriptions:
            res = ''
            for attribute in subscription:
                val = subscription[attribute]['value']
                if isinstance(val, datetime.datetime):
                    val = val.strftime('%d.%m.%Y')
                else:
                    val = str(val)

                res = res + '(' \
                      + attribute \
                      + ',' + subscription[attribute]['operator'] \
                      + ',' + val \
                      + ');'

            res = '{' + res.strip(';') + '}'
            handle.write('{}\n'.format(res))


if __name__ == '__main__':
    dump_publications()
    dump_subscriptions()