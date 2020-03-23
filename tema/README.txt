Scriptul generator.py este un script python pentru a genera aleator seturi echilibrate de subscriptii si publicatii.
Structura campurilor publicatiilor este una fixa si anume:
    - car_model: str ( un string ales random din multimea {'Mercedes', 'Fiat', 'Renault', 'Opel', 'Dacia'} )
    - production_date: date ( o data aleasa random intre 01-01-1990 si 01-01-2020 )
    - horsepower: int ( un numar intreg ales random intre 70 si 300 )
    - color: str ( un string ales random din multimea {"red", "blue", "green", "black", "white"} )
    - max_speed: int ( un numar intreg ales random intre 50 si 140 )

Generatorul de subscriptii este configurabil cu ajutorul unei clase FieldConfig care are ca atribute un field-name,
o functie de generare a valorii unui field, frecventa de aparitie a field-ului in multimea totala a subscriptiilor si frecventa de aparitie a operatorilor in subscriptii, grupate dupa field.

Flow-ul generatorului de subscriptii:
    - validari input
    - valori default ale parametrilor in caz ca nu sunt folositi in apel
    - frecventa operatorilor nesetati in configurarea unui field este 1 - suma celorlalte frecvente ale operatorilor din cadrul aceluiasi field.
    - deoarece nu doresc sa am subscriptii goale, cele necompletate (nu au o configurare pe nici un field) o sa fie alese primele pentru configurare
    - se pastreaza frecventa aparitiei field-urilor si frecventa operatorilor

Se face dump a seturilor de publicatii si subscriptii ca stringuri in fisierele publications.txt, respectiv subscriptions.txt create de catre script in directorul curent.

* Observatii:
    sum(containing_ratio) poate fi > 1.00
