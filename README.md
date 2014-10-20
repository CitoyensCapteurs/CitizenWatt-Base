## Package needed

* sqlalchemy
* cherrypy
* numpy
* pycrypto
* psycopg2 for communication with the PostgreSQL database

## API

* /api/sensors
	* Returns all the available sensors with their types
* /api/sensors/<id:int>
    * Returns the infos for the specified sensor.
* /api/types
	* Returns all the available measure types
* /api/time
    * Returns the current timestamp of the server side.
* /api/energy_providers
    * Returns all available energy providers
* /api/energy_providers/<current|<int>>
    * Returns the targeted energy provider
* /api/<sensor:int>/get/watts/by_id/<nb:int>
	* Get measure with id nb
	* Get measure nth to last measure if nb < 0 (behaviour of Python lists)
* /api/<sensor:int>/get/[watts|kwatthours|euros]/by_id/<nb1:int>/<nb2:int>
	* Get all the measures with id between nb1 and nb2 (nb1 < nb2)
	* Get all the measures between nb1 and nb2 starting from the end if nb1, nb2 < 0 (behaviour of Python lists)
    * Get the energy / cost associated with these measures if kwatthours or euros is specified
* /api/<sensor:int>/get/watts/by_time/<time:int>
	* Idem as above, but with timestamps
* /api/<provider:re:current|\d>/watt_to_euros/<tarif:re:night|day>/<consumption:int>
    * Returns the price associated to the consumption (in kWh) for the specified provider
* /api/<sensor:int>/get/[watts|kwatthours|euros]/by_time/<time1:int>/<time2:int>/<timestep:int>
    * Idem as above, but with timestamps
    * idem avec id
* idem with ids

step > 0
