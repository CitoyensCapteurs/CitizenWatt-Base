## Package needed

* sqlalchemy
* pymysql

## API

* /api/sensors
	* Returns all the available sensors with their types
* /api/types
	* Returns all the available measure types
* /api/<sensor:int>/get/watts/by_id/<nb:int>
	* Get measure with id nb
	* Get measure nth to last measure if nb < 0 (behaviour of Python lists)
* /api/<sensor:int>/get/[watts|kwatthours|euros]/by_id/<nb1:int>/<nb2:int>
	* Get all the measures with id between nb1 and nb2 (nb1 < nb2)
	* Get all the measures between nb1 and nb2 starting from the end if nb1, nb2 < 0 (behaviour of Python lists)
    * Get the energy / cost associated with these measures if kwatthours or euros is specified
* /api/<sensor:int>/get/watts/by_time/<time:int>
	* Idem as above, but with timestamps
* /api/<sensor:int>/get/[watts|kwatthours|euros]/by_time/<time1:int>/<time2:int>
	* Idem as above, but with timestamps
* /api/energy_providers
    * Returns all available energy providers
* /api/energy_providers/<current|<int>>
    * Returns the targeted energy provider
* /api/<provider:int>/watt_to_euros/<consumption:int>
    * Returns the price associated to the consumption (in kWh) for the specified provider
* /api/<sensor:int>/mean/[watts|euros]/[daily|weekly|monthly]
    * Returns the mean for the last day/month and for each hour/day for the last day/month
    * TODO
