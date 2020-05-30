# EventBasedSystemProject
Implementati o arhitectura de sistem publish/subscribe, content-based, structurata in felul urmator:  Generati un flux de publicatii care sa fie emis de 1-3 noduri publisher. (10 puncte) Implementati o retea (overlay) de brokeri (maxim 3) care sa disemineze publicatiile, in functie de o filtrare bazata pe continutul acestora. (10 puncte) Simulati 3 noduri subscriber care se conecteaza aleatoriu la reteaua de brokeri si inregistreaza 10000 de suscriptii. (10 puncte) Generati setul de mesaje aleator cu ponderi echilbrate pe campuri folosind generatorul din tema practica. (5 puncte) Folositi un mecanism de serializare al mesajelor (Google Protocol Buffers sau Thrift) pentru transmiterea intre nodurile publisher/subscriber si brokers. (5 puncte) Masurati cate publicatii se livreaza cu succes prin sistemul distribuit intr-un interval continuu de feed de 3 minute, si latenta medie de livrare a unei publicatii (timpul de la emitere pana la primire) si redactati un scurt raport de evaluare a solutiei. (10 puncte) Punctaj aditional:  Rulati arhitectura pe masini virtuale diferite (nodurile subscriber pe o masina, nodurile publisher pe o masina, nodurile broker pe o masina). (3 puncte) Implementati un mecanism avansat de rutare pentru a obtine scalabilitate orizontala (publicatiile vor trece prin mai multi brokeri pana la destinatie, fiecare ocupandu-se partial de rutare, si nu doar unul care contine toate subscriptiile si face un simplu match). (5-10 puncte) Simulati si tratati (prin asigurare de suport in implementare) cazuri de caderi pe nodurile broker. (5 puncte) Implementati o modalitate de filtrare a mesajelor care sa nu permita accesul la continutul acestora (match pe subscriptii/publicatii criptate). (5-10 puncte) Implementati o modalitate de anonimizare a nodurilor subscriber si publisher. (3-7 puncte) (Nota: anonimizarea prin intermediul unui singur proxy intermediar intre subscribers/publishers si brokers se va puncta cu maxim 3 puncte)

Graf latenta medie de livrare a publicatilor:
https://docs.google.com/spreadsheets/d/1HkdJMrNBsnAiTA2lLxUAy0P_Yh5Jb-aeADU5frC0LH4/edit#gid=1587825126

Proiect:
Limbaj de programare: Python
Tehnologie folosita: RabbitMQ

Desrierea solutiei:
Proiectul simuleaza o retea overlay de brokeri prin intermediul clasei BrokeOverlay care actioneaza pe post de routing manager. Acesta inregistreaza atat brokerii activi cat si vecinii acestora.  Instantele de Brokeri active primesc un id unic si sunt adaugate la reteaua overlay.
Clasa PublicationSender genereaza un numar dat de publicatii si le trimite catre BrokerOverlay folosing un exchange de tip fanout, urmand ca Overlay sa trimita publicatiile catre toti brokerii inregistrati.
Clasa SubscriptionSender genereaza un numar dat de subscriptii care sunt trimise catre BrokerOverlay. BrokerOverlay trimite subscriptiile catre brokeri (fanout exchange). Prin intermediul clasei Matching apelata din Broker, sunt filtrate publicatiile care mai apoi sunt trimise catre subscriber (in cazul in care exista match-uri).



