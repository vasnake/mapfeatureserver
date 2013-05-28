Статья на ГИС-Лаб
http://wiki.gis-lab.info/w/Mapfeatureserver_как_замена_ArcGIS_Server
http://gis-lab.info/forum/viewtopic.php?f=3&t=13731

{{Статья|Черновик}}
{{Аннотация|Описание веб-сервиса Mapfeatureserver как замены ArcGIS Server}}

[https://github.com/vasnake/mapfeatureserver Mapfeatureserver] (далее MFS) - это веб-сервис, написанный на Python (WSGI, Flask) и реализующий
[http://resources.arcgis.com/en/help/rest/apiref/index.html?overview.html ArcGIS Server REST API] для слоев типа
[http://resources.arcgis.com/en/help/rest/apiref/fslayer.html Feature Layer].
MFS был задуман как средство, позволяющее избавиться от дорогостоящего ArcGIS Server при работе с веб-картами, использующими
[http://resources.arcgis.com/content/web/web-apis ArcGIS API],
равно как и получить дополнительные возможности, отсутствующие в ArcGIS Server.

Mapfeatureserver будет полезен разработчикам ГИС решений для веб и интранет,
поскольку позволяет получить веб-карты красивые и функциональные как в ArcGIS, но без затрат на приобретение ArcGIS Server.
Как open source продукт, MFS может принести дополнительную пользу разработчикам знающим Python.

== Введение в тему ==

Чтобы было понятнее, что такое MFS, нужно иметь представление о стеке технологий, поверх которых он работает.

Как известно, есть такой подкласс ГИС решений как клиент-серверные ГИС. В случае, когда клиент использует для работы с картами
веб-браузер или мобильный терминал вроде смартфона или планшета, применяется название «веб-ГИС». Вероятно потому, что
для общения клиент-сервер используются веб технологии. Основные отличающие черты таких решений
заключаются в применении некоего картографического сервера и использовании HTTP/HTTPS для передачи данных между клиентом и сервером.
Самый распространенный вариант - это отрисовка клиентом растровых картинок, присылаемых с сервера по запросу. Из этих растровых картинок (тайлов),
как из мозаики, складывается изображение карты.

На текущий момент известно не так много веб-ГИС решений, которые позволяют не только получать растровые тайлы, но и дают клиенту возможность
полноценно работать со слоями данных, используя геометрию объектов (features) в слоях карты,
передавая между клиентом и сервером координаты точек, составляющих фигуры, их атрибуты и сопутствующие метаданные.
Естественно, передача таких данных, назовем их условно «геометрия», осуществляется согласно определенным протоколам.
Тут я говорю о форматах передачи данных поверх HTTP/HTTPS. В мире свободного ПО самое большое распространение получили протоколы
[http://en.wikipedia.org/wiki/Web_Map_Service WMS/WFS] а если точнее, согласно теме данной статьи,
[http://en.wikipedia.org/wiki/Web_Feature_Service  WFS (Web Feature Service)].

У компании Esri есть свое решение. Продукт под названием
[http://www.esri.com/software/arcgis/arcgisserver/features ArcGIS for Server] содержит подсистему, которая публикует веб карты,
слои данных из которых сделаны эти карты, и много чего еще, в данном случае не существенного. В процессе публикации карты или слоя,
на сервере АркГИС создаются так называемые [http://resources.arcgis.com/content/enterprisegis/10.0/services_webservices «веб сервисы»].
Нас, согласно теме, интересуют опубликованные слои, из которых собираются карты. В терминологии АркГИС такие слои называются
[http://gis.stackexchange.com/questions/26336/whats-the-difference-between-feature-class-and-feature-layer Feature Layer]
а сервисы, создаваемые АркГИС-ом для них называются
[http://help.arcgis.com/en/arcgisserver/10.0/help/arcgis_server_dotnet_help/index.html#//009300000022000000 Feature Service].
Протокол доступа к таким слоям несет название
[http://resources.arcgis.com/en/help/rest/apiref/index.html?featureserver.html ArcGIS Server REST API]
и позволяет через HTTP/HTTPS получать геометрию и атрибуты объектов слоя.
Сами передаваемые данные упаковываются в текст формата JSON. Примеры данных я приведу чуть позже.
Если при создании Feature Service выполнить некоторые условия (например, разместить данные в специальной БД),
то при использовании такого сервиса можно будет использовать все операции спектра
[http://en.wikipedia.org/wiki/Create,_read,_update_and_delete CRUD], а не только чтение.

Следует упомянуть, что АркГИС Сервер умеет создавать разные типы сервисов, не только Feature Sevice. К примеру,
вполне можно опубликовать слой геоданных, доступ к которому будет открыт по протоколу WFS. Но в данной статье нас
интересует только ArcGIS Server REST API, подраздел Feature Service.

Предпринимаются попытки создать на основе ArcGIS Server REST API всеобщий стандарт на геосервисы.
Этот стандарт именуется
[http://wiki.osgeo.org/wiki/Geoservices_REST_API GeoServices REST API] (http://www.opengeospatial.org/standards/requests/89)
и на данный момент сообщество очень неоднозначно реагирует на его продвижение.
Насколько мне известно, еще нет ни одной реализации GeoServices REST API.

Существуют и друге протоколы работы с геоданными, несущие модную аббревиатуру
[http://en.wikipedia.org/wiki/Representational_state_transfer REST]
в своем названии или описании, например
[http://trac.mapfish.org/trac/mapfish/wiki/MapFishProtocol MapFish Protocol] или
[http://geoserver.org/display/GEOS/REST+Overview+Page GeoServer REST API].
Эти решения тоже заслуживают внимания, но не имеют никакого касательства к Mapfeatureserver.

Что же касается Mapfeatureserver, то это продукт того же семейства, что
[http://papyrus.readthedocs.org/en/latest/ Papyrus] или
[http://featureserver.org/ FeatureServer],
только нацелен на реализацию протокола ArcGIS Server REST API, в отличие от.

К созданию MFS меня подтолкнули следующие соображения и обстоятельства.
Нашим клиентам очень нравится клиентская часть для веб-ГИС, называемая
[http://resources.arcgis.com/en/communities/silverlight-viewer/ ArcGIS Viewer for Silverlight], на базе которой
мы создали специальную сборку
[http://www.allgis.org/cartobonus/help/ «Картобонус»].
Разумеется, как детище Esri, такой вьювер лучше всего работает с серверной частью этого же вендора и не очень
способствует попыткам подружить его с слоями, загружаемыми через сторонние сервисы, в частности WFS.
Это был первый звоночек - решение задачи «подключение к Картобонусу слоев из WFS». Можно либо во вьювер добавить код,
транслирующий примитивы WFS в обьекты вьювера
([https://code.google.com/p/wfst-arcgis-viewer/ как-то так]);
либо написать некий сервис-прокси, для превращения WFS в ArcGIS Feature Service,
понимаемый вьювером «из коробки».

Другим пожеланием клиентов была функция «загрузки шейпов» во вьювер. Довольно трудно обьяснить неспециалисту,
что парсинг и отрисовка данных из шейпа в браузере - весьма не тривиальная задача. Да и зачем? Ведь можно дать пользователю
кнопку «загрузка шейпа», нажав которую, пользователь сможет создать на некоем сервере таблицу в БД и записать в нее копию шейп-файла.
После чего подключить к карте во вьювере слой, сформированный из этой таблицы.
Второй звоночек - нужен сервис, в который мы сможем грузить шейпы и потом выводить их клиентам веб-ГИС.

Кстати, о клиентских вьюверах. Очевидно, лучше всех с геоданными из Feature Service, эмуляцией которого и занимается Mapfeatureserver,
умеют работать программы от Esri (упоминать приложения типа ArcMap я тут не буду, только веб)
* [http://resources.arcgis.com/en/tutorials/ ArcGIS Online] - яркий пример картографического вьювера, сделанного на JavaScript и продвигаемого как SaaS.
* [http://resources.arcgis.com/en/communities/flex-viewer/ ArcGIS Viewer for Flex] - кроссплатформенное приложение типа RIA на технологии Flash/Flex, расширяемое, с открытым кодом.
* Уже упомянутый [http://resources.arcgis.com/en/communities/silverlight-viewer/ ArcGIS Viewer for Silverlight] - тоже RIA, но работает только под MS Windows. Зато, используя MS Visual Studio, процесс разработки плагинов и расширений заметно ускоряется и упрощается.
Замечу, что эти вьюверы активно эксплуатируют очень приличный [http://resources.arcgis.com/content/web/web-apis набор API],
предоставляемый Esri безвозмездно, то есть даром.

И, конечно, всеми любимый [http://openlayers.org/dev/examples/arcgis93rest.html OpenLayers]
тоже умеет работать со слоями по протоколу ArcGIS Server REST API.

== Mapfeatureserver - что это такое? ==

Как я уже упомянул, MFS это open source программа на Python, которая после запуска создает веб-сервис, отвечающий спецификации
[http://resources.arcgis.com/en/help/rest/apiref/index.html?overview.html ArcGIS Server REST API] для картографических слоев типа
[http://resources.arcgis.com/en/help/rest/apiref/fslayer.html Feature Layer].
Веб модуль MFS написан с использованием фреймворка Flask и отвечает спецификации WSGI, что позволяет использовать MFS в качестве
части более крупных веб-решений.

Геоданные MFS считывает из PostGIS DB, что означает необходимость
а) загрузить данные предполагаемого решения в БД PostGIS;
б) обеспечить доступ к этой БД сервису MFS.
На текущий момент, кроме PostGIS, другие БД не поддерживаются, но есть планы добавить поддержку MySQL и MongoDB.
Также, есть планы по использованию служб WFS в качестве источников данных.

Общая картина использования Mapfeatureserver выглядит примерно так.
* Геоданные (шейп-файлы, к примеру) загружаем в PostGIS.
* Для каждого слоя данных вписываем сведения в конфигурационные файлы MFS.
* Запускаем веб-сервис.
* В клиентской программе, к примеру [http://www.allgis.org/cartobonus/help/ Картобонус], добавляем к карте слои точно так же, как обычные FeatureLayer из ArcGIS Server.

Теперь о недостатках и ограничениях MFS.

На текущий момент программа находится в стадии «Proof of Concept», то есть обладает функциональностью минимально достаточной для
демонстрации работоспособности подхода.
Из всего многообразия запросов декларированных в API, наш сервис пока реализует два:
* [http://resources.arcgis.com/en/help/rest/apiref/fslayer.html layer metadata] <pre>http://<featureservice-url>/<layerId></pre>
* [http://resources.arcgis.com/en/help/rest/apiref/fsquery.html layer data query] by box <pre>http://<featurelayer-url>/query</pre>
причем запрос данных может быть только одного типа - запрос на выборку по ограничивающему боксу (box).
Этого достаточно, чтобы загрузить слой в карту и делать zoom, pan, просмотр атрибутов для features, но и только.

Пример ответа сервера на запрос метаданных слоя
<pre>
"currentVersion": 10.11,
 "id": 0,
 "name": "Ямочный ремонт",
 "type": "Feature Layer",
 "description": "Места установки заплаток на дорогах",
...
 "supportsAdvancedQueries": true,
 "geometryType": "esriGeometryPoint",
 "minScale": 0,
 "maxScale": 0,
 "extent": {
  "xmin": 27.765770083999996,
  "ymin": 52.86936644999997,
  "xmax": 36.71166105100002,
  "ymax": 62.012733638999975,
  "spatialReference": {
   "wkid": 4326,
   "latestWkid": 4326
  }
 },
 "drawingInfo": {
  "renderer": {
   "type": "uniqueValue",
   "field1": "roadcarpet",
   "field2": null,
   "field3": null,
   "fieldDelimiter": ", ",
   "defaultSymbol": null,
   "defaultLabel": null,
   "uniqueValueInfos": [
	{
	 "symbol": {
	  "type": "esriPMS",
	  "url": "http://localhost:5000/static/asfalt.png",
	  "imageData": "",
	  "contentType": "image/png",
	  "width": 24,
	  "height": 24,
	  "angle": 0,
	  "xoffset": 0,
	  "yoffset": 0
	 },
	 "value": "Асфальт",
	 "label": "Асфальт",
	 "description": ""
	},
	{
	 "symbol": {
	  "type": "esriPMS",
...
 },
 "hasM": false,
 "hasZ": false,
 "allowGeometryUpdates": true,
...
 "fields": [
  {
   "name": "objectid",
   "type": "esriFieldTypeOID",
   "alias": "OBJECTID",
   "domain": null,
   "editable": false,
   "nullable": false
  },
  {
   "name": "ptchlenght",
   "type": "esriFieldTypeSmallInteger",
   "alias": "ДлинаУчастка, м",
   "domain": null,
   "editable": true,
   "nullable": true
  },
  {
   "name": "pthcdeptht",
   "type": "esriFieldTypeSmallInteger",
   "alias": "ГлубинаУчастка, см",
   "domain": null,
   "editable": true,
   "nullable": true
  },
...
 "maxRecordCount": 1000,
 "supportedQueryFormats": "JSON, AMF",
 "capabilities": "Create,Delete,Query,Update,Uploads,Editing"
}
</pre>

Пример ответа сервера на запрос данных слоя
<pre>
{
  "features": [
    {
      "attributes": {
        "descr": "werwre",
        "gid": 8,
        "ptchlenght": 500,
        "pthcdeptht": 8,
        "regdaterec": "2012/08/02",
        "regdaterep": "2012/09/15",
        "roadcarpet": "Асфальт"
      },
      "geometry": {
        "x": 3980475.9450405277,
        "y": 6976079.279805333
      }
    }
  ],
  "fields": [
    {
      "alias": "OBJECTID",
      "name": "gid",
      "type": "esriFieldTypeOID"
    },...
    {
      "alias": "REGDATEREP",
      "length": 50,
      "name": "regdaterep",
      "type": "esriFieldTypeString"
    },
    {
      "alias": "ROADCARPET",
      "length": 50,
      "name": "roadcarpet",
      "type": "esriFieldTypeString"
    }
  ],
  "geometryType": "esriGeometryPoint",
  "globalIdFieldName": "",
  "objectIdFieldName": "gid",
  "spatialReference": {
    "latestWkid": 3857,
    "wkid": 102100
  }
}
</pre>

Остальная часть API будет реализована несколько позже. Хорошая новость заключается в том, что проект - open source и любой,
кто обладает соответствующими навыками, может ускорить реализацию недостающих функций.

== Инструкция по использованию Mapfeatureserver ==

Изложенная здесь информация может устареть к тому времени как вы читаете этот текст.
Наиболее свежую информацию о проекте вы всегда можете найти на странице проекта в GitHub
https://github.com/vasnake/mapfeatureserver

Чтобы запустить сервис MFS вам понадобится выполнить следующие шаги (в планах есть пункт: сделать нормальный Python distribution):
* Скачать [https://github.com/vasnake/mapfeatureserver MFS с GitHub].
* Поправить настройки в файле <pre>mapfeatureserver\wsgi\default_settings.py</pre>
* Установить Python 2.7 и необходимые библиотки, к примеру для MS Windows
<pre>set path=%path%;c:\d\Python27;c:\d\Python27\Scripts
pip install Flask flask-login blinker psycopg2 simplejson</pre>
[http://www.stickpeople.com/projects/python/win-psycopg/ psycopg2 for Windows]
* Запустить приложение Flask
<pre>pushd mapfeatureserver\wsgi
python mapfs_controller.py</pre>
URL веб-службы будет таким http://localhost:5000/
Если вы откроете эту страницу в браузере вы увидите служебную страницу со ссылками на тестовые слои.
Эти ссылки работать не будут, так как у вас нет таких слоев. Удалить лишнее и добавить свое вы можете поправив файл
<pre>mapfeatureserver\wsgi\templates\servlets.html</pre>

Чтобы создать новый слой, вам нужно выполнить следующие шаги:
* Получить доступ к БД PostGIS, к примеру, установив БД на свой хост.
* Загрузить шейп-файл с нужными данными в БД, к примеру так (описания опций и ключей к командам доступны во встроенной в команды справке):
<pre>set path=%path%;c:\Program Files\PostgreSQL\9.0\bin
pushd c:\t\shpdir
shp2pgsql.exe -d -I -s 4326 -W cp1251 flyzone.shp mfsdata.flyzone > flyzone.dump.sql
psql -f flyzone.dump.sql postgisdb mfs</pre>
Здесь shpdir это папка, где расположены шейп-файлы; flyzone.shp - загружаемый шейп-файл; mfsdata.flyzone - схема данных и таблица,
в которую будет загружен шейп; postgisdb - имя БД; mfs - учетная запись в БД.

* Записать сведения о слое в конфигурационный файл
<pre>mapfeatureserver\config\layers.config.ini</pre>
Идентификатор слоя (любое положительное целое число) надо вписать в список (в примере указаны три слоя)
<pre>layer.ID.list: 0,1,2</pre>
Вписать данные подключения к БД PostGIS, пример:
<pre>PG.DSN: host=vags101 port=5432 dbname=postgisdb user=mfs password=12345678 connect_timeout=10 client_encoding=utf8</pre>
Создать секцию, именованную по идентификатору слоя, скажем «2»
<pre>
[2]
layer.table = flyzone
layer.geomfield = geom
layer.oidfield = gid
layer.name = Зоны полетов с ограничениями
</pre>
Находящиеся в конфиге примеры и комментарии помогут не ошибиться.

* Создать файл метаданных для слоя. Это самая трудная часть.
<pre>mapfeatureserver\config\layer.<layer id>.config.json</pre>
Чтобы было легче, можно скопировать метаданные из аналогичного существующего слоя Feature Layer ArcGIS и внести в него правки.
Метаданные слоя из ArcGIS Server доступны по URL типа <pre>http://testags/arcgis/rest/services/flyzone/FeatureServer/2?f=pjson</pre>
если на сервере опубликована служба «flyzone» соответствующего типа.
Также, в MFS есть специальные страницы, типа <pre>http://localhost:5000/admin/dsn/flyzone?oidfield=gid&geomfield=geom</pre>
для помощи в составлении файла метаданных.

После выполнения этих шагов, можно использовать слои MFS как обычные слои ArcGIS FeatureLayer в веб-картах
построенных на [http://resources.arcgis.com/content/web/web-apis ArcGIS web API].
К примеру, есть вьювер
[http://www.allgis.org/cartobonus/help/ Картобонус], построенный на
[http://resources.arcgis.com/en/help/silverlight-viewer/concepts/ ArcGIS API for Silverlight],
именно он использовался для тестирования MFS. Чтобы добавить слой в карту, используйте URL вида
<pre>http://hostname:5000/<layer id></pre>
[[Файл:Слои Mapfeatureserver в веб-картах Картобонус.png|center|700px|Рабочий скриншот слоев из MFS во вьювере Картобонус]]

Как видите, за исключением файла метаданных, всё достаточно просто.
Теперь у нас есть свободный и бесплатный сервер Feature Layer-ов для обеспечения работы любого картографического софта,
использующего спецификации ArcGIS REST API.

== Ссылки ==
* [http://resources.arcgis.com/en/help/rest/apiref/fslayer.html Спецификации REST API]
* [http://vasnake.blogspot.ru/2013/05/mapfeatureserver-poc.html Статья в блоге автора]
* [https://github.com/vasnake/mapfeatureserver MFS на GitHub]
* [http://www.allgis.org/cartobonus/help/ web map viewer Cartobonus]

E-mail: [mailto:vasnake@gmail.com vasnake@gmail.com]
