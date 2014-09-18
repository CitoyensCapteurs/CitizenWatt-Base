## Package needed

* sqlalchemy

## API

* /api/sensors
	* Returns all the available sensors with their types
* /api/<sensor:int>/get/by_id/<nb:int>
	* Get measure with id nb
	* Get measure starting from last one if nb < 0 (behaviour of Python lists)
* /api/<sensor:int>/get/by_id/<nb1:int>/<nb2:int>
	* Get all the measures with id between nb1 and nb2 (nb1 < nb2)
	* Get all the measures between nb1 and nb2 starting from the end if nb1, nb2 < 0 (behaviour of Python lists)
* /api/<sensor:int>/get/by_time/<time:int>
	* Idem as above, but with timestamps
* /api/<sensor:int>/get/by_time/<time1:int>/<time2:int>
	* Idem as above, but with timestamps
* /api/<sensor:int>/get/by_value/<value1:float>
	* Idem as above, but filtering by values
* /api/<sensor:int>/get/by_value/<value1:float>/<value2:float>
	* Idem as above, but filtering by values
* /api/energy_providers/
    * Returns all available energy providers
* /api/<provider:int>/watt_euros/<consumption:int>
    * Returns the price associated to the consumption for the specified provider
