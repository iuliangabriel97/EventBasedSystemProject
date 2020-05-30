# EventBasedSystemProject
Implementati o arhitectura de sistem publish/subscribe, content-based, structurata in felul urmator:  Generati un flux de publicatii care sa fie emis de 1-3 noduri publisher. (10 puncte) Implementati o retea (overlay) de brokeri (maxim 3) care sa disemineze publicatiile, in functie de o filtrare bazata pe continutul acestora. (10 puncte) Simulati 3 noduri subscriber care se conecteaza aleatoriu la reteaua de brokeri si inregistreaza 10000 de suscriptii. (10 puncte) Generati setul de mesaje aleator cu ponderi echilbrate pe campuri folosind generatorul din tema practica. (5 puncte) Folositi un mecanism de serializare al mesajelor (Google Protocol Buffers sau Thrift) pentru transmiterea intre nodurile publisher/subscriber si brokers. (5 puncte) Masurati cate publicatii se livreaza cu succes prin sistemul distribuit intr-un interval continuu de feed de 3 minute, si latenta medie de livrare a unei publicatii (timpul de la emitere pana la primire) si redactati un scurt raport de evaluare a solutiei. (10 puncte) Punctaj aditional:  Rulati arhitectura pe masini virtuale diferite (nodurile subscriber pe o masina, nodurile publisher pe o masina, nodurile broker pe o masina). (3 puncte) Implementati un mecanism avansat de rutare pentru a obtine scalabilitate orizontala (publicatiile vor trece prin mai multi brokeri pana la destinatie, fiecare ocupandu-se partial de rutare, si nu doar unul care contine toate subscriptiile si face un simplu match). (5-10 puncte) Simulati si tratati (prin asigurare de suport in implementare) cazuri de caderi pe nodurile broker. (5 puncte) Implementati o modalitate de filtrare a mesajelor care sa nu permita accesul la continutul acestora (match pe subscriptii/publicatii criptate). (5-10 puncte) Implementati o modalitate de anonimizare a nodurilor subscriber si publisher. (3-7 puncte) (Nota: anonimizarea prin intermediul unui singur proxy intermediar intre subscribers/publishers si brokers se va puncta cu maxim 3 puncte)


Scrieti un program care sa genereze aleator seturi echilibrate de subscriptii si publicatii cu posibilitatea de fixare a: numarului total de mesaje, ponderii pe frecventa campurilor din subscriptii si ponderii operatorilor de egalitate din subscriptii pentru cel putin un camp. Publicatiile vor avea o structura fixa de campuri la alegere.

Exemplu:
Publicatie: {(company,"Google");(value,90.0);(drop,10.0);(variation,0.73);(date,2.02.2022)} - Structura fixa a campurilor publicatiei e: company-string, value-double, drop-double, variation-double, date-data; pentru anumite campuri (company, date), se pot folosi seturi de valori prestabilite de unde se va alege una la intamplare; pentru alte campuri (drop, variation, date) se pot stabili limite inferioare si superioare intre care se va alege una la intamplare.

Subscriptie:{(company,=,"Google");(value,>=,90);(variation,<,0.8)} - Unele campuri pot lipsi; frecventa campurilor prezente trebuie sa fie configurabila (ex. 90% company - 90% din subscriptiile generate trebuie sa includa campul "company"); pentru campul cu domeniul cel mai mic (ex. company e definit ca avand valori intr-o multime de doar 5 companii) se poate configura un minim de frecventa pentru operatorul "=" (ex. macar 90% din subscriptiile generate sa aiba ca operator pe acest camp egalitatea). Nota: cazul in care suma procentelor configurate pentru campuri e mai mica decat 100 reprezinta o situatie de exceptie care nu e necesar sa fie tratata. (pentru testare se vor folosi intotdeauna valori de procentaj ce sunt egale sau depasesc 100 ca suma)

Setul generat va fi memorat in fisiere text.

Graf latenta medie de livrare a publicatilor:
https://docs.google.com/spreadsheets/d/1HkdJMrNBsnAiTA2lLxUAy0P_Yh5Jb-aeADU5frC0LH4/edit#gid=1587825126

Proiect:
Limbaj de programare: Python
Tehnologie folosita: RabbitMQ

Desrierea solutiei:
Proiectul simuleaza o retea overlay de brokeri prin intermediul clasei BrokeOverlay care actioneaza pe post de routing manager. Acesta inregistreaza atat brokerii activi cat si vecinii acestora.  Instantele de Brokeri active primesc un id unic si sunt adaugate la reteaua overlay.
Clasa PublicationSender genereaza un numar dat de publicatii si le trimite catre BrokerOverlay folosing un exchange de tip fanout, urmand ca Overlay sa trimita publicatiile catre toti brokerii inregistrati.
Clasa SubscriptionSender genereaza un numar dat de subscriptii care sunt trimise catre BrokerOverlay. BrokerOverlay trimite subscriptiile catre brokeri (fanout exchange). Prin intermediul clasei Matching apelata din Broker, sunt filtrate publicatiile care mai apoi sunt trimise catre subscriber (in cazul in care exista match-uri).



