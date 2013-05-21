mapfeatureserver
================

WSGI (Python, Flask) service for ArcGIS Feature Layer REST replacement

## Что это

Mapfeatureserver это веб-сервис, написанный на Python (WSGI, Flask) с целью имитации ArcGIS FeatureServer ([Feature Service – Layer aka FeatureLayer](http://resources.arcgis.com/en/help/rest/apiref/fslayer.html)) без привлечения закрытого и дорогого софта.

На данном этапе проект находится в состоянии Proof Of Concept, то есть черновика, позволяющего определить применимость идеи и направления развития.

Сервис умеет отвечать пока только на два вида запросов:

1. метаданные слоя [http://&lt;featureservice-url&gt;/&lt;layerId&gt;](http://resources.arcgis.com/en/help/rest/apiref/fslayer.html)
2. выборка объектов прямоугольником [http://&lt;featurelayer-url&gt;/query](http://resources.arcgis.com/en/help/rest/apiref/fsquery.html)

Для выборки имеет значение только ограниченный набор параметров.
Пример: `http://service/0/query?geometry={"xmin":3907314.1268439,"ymin":6927697.68990079,"xmax":3996369.71947852,"ymax":7001516.67745022,"spatialReference":{"wkid":102100}}&outSR=102100`

Этих два вида запросов уже позволяют использовать слои сервиса в программах типа [Картобонус](http://www.allgis.org/cartobonus/help/) основанных на ArcGIS Silverlight API. Использование ограничивается добавлением слоя в карту и просмотром обьектов и их атрибутов на карте и в формах отображения атрибутов.
Фильтрация и редактирование записей пока не реализованы.
Вероятнее всего, в других API от Esri слои тоже могут использоваться, но точно не знаю, не проверял.

## Как использовать

Для запуска сервиса нужно сделать следующее:
Установить Python 2.7 и необходимые библиотеки, например для MS Windows

```
set path=%path%;c:\d\Python27;c:\d\Python27\Scripts
pip install Flask flask-login blinker psycopg2 simplejson
```

[psycopg2 for Windows](http://www.stickpeople.com/projects/python/win-psycopg/)

запустить приложение Flask

```
pushd mapfeatureserver\wsgi
python mapfs_controller.py
```

Сервис доступен по URL
`http://localhost:5000/`
На странице вы увидите ссылки на тестовые слои, эти ссылки работать не будут. Убрать их можно отредактировав файл
`mapfeatureserver\wsgi\templates\servlets.html`

Для добавления слоя к сервису нужно сделать следующее:
* обеспечить доступ к БД PostGIS, например установив [СУБД](http://postgis.net/windows_downloads) на свой хост;
* загрузить в БД shp-файл с данными, по примеру

```
set path=%path%;c:\Program Files\PostgreSQL\9.0\bin
pushd c:\t\shpdir
shp2pgsql.exe -d -I -s 4326 -W cp1251 flyzone.shp mfsdata.flyzone > flyzone.dump.sql
psql -f flyzone.dump.sql postgisdb mfs
```

* зарегистрировать слой в сервисе отредактировав файл
`mapfeatureserver\config\layers.config.ini`
ориентируясь на приведенные в нем примеры.

* Создать файл (самая сложная и трудоемкая часть)
`mapfeatureserver\config\layer.<layer id>.config.json`
Проще всего взять за основу выдачу аналогичной службы ArcGIS Feature Layer, по примеру
`http://testags/arcgis/rest/services/flyzone/FeatureServer/2?f=pjson`
и использовать служебную страницу сервиса, по примеру
`http://localhost:5000/admin/dsn/flyzone?oidfield=gid&geomfield=geom`

Созданный слой можно использовать в картприложениях типа [Картобонус](http://www.allgis.org/cartobonus/help/), добавляя его в карту как обычный FeatureLayer ArcGIS `http://hostname:5000/<layer id>`

## Планы по развитию

* Код: упаковать модули в пакет, может быть Python egg.
* Слои: алиасы полей брать из метаданных.
* Слои: реализовать работу функции Identify (Инфо в Картобонус).
* Слои: реализовать функцию редактирования фичей — атрибутики и геометрии.
* Слои: реализовать фильтрацию записей.
* Слои: реализовать ограничение списка полей в выдаче.
* Код: покрыть код тестами и использовать mock вместо реальной БД.
* Платформа: сделать версию для MySQL.

## Лицензия и ограничения

Код предоставляется и распространяется под лицензией [GNU](http://www.gnu.org/licenses/gpl.html).

Ограничения: необходим доступ к БД PostGIS; файл метаданных слоя приходится создавать вручную; из всех видов запросов указанных в спецификации Esri, работает только один — на выборку объектов прямоугольником.

Copyright 2012-2013 Valentin Fedulov
mailto:vasnake@gmail.com
