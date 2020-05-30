SET python=C:\Users\gcrisnuta\AppData\Local\Programs\Python\Python37\python.exe

::start "Broker Overlay" %python% ..\BrokerOverlay.py
::start "Broker1" %python% ..\Broker.py
::start "Broker2" %python% ..\Broker.py
::start "Broker3" %python% ..\Broker.py
::start "Publisher" %python% ..\PublicationSender.py
start "Subscriber" %python% -i ..\SubscriptionSender.py