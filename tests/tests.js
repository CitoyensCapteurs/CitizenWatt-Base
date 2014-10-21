#!/usr/bin/node

/* You have to uncomment the latest lines of ../static/js/datetutils.js to use these tests. */

var assert = require('assert');
var dateutils = require('../static/js/dateutils');

assert(dateutils.getHourLength() == 3600   * 1000, 'Hour length');
assert(dateutils.getDayLength()  == 86400  * 1000, 'Day length' );
assert(dateutils.getWeekLength() == 604800 * 1000, 'Week length');

assert(dateutils.getMonthLength(new Date(2000,1,0)) == 31*86400*1000, 'January length' );
assert(dateutils.getMonthLength(new Date(2000,2,0)) == 29*86400*1000, 'February length');
assert(dateutils.getMonthLength(new Date(2000,3,0)) == 31*86400*1000, 'March length'   );
assert(dateutils.getMonthLength(new Date(2000,4,0)) == 30*86400*1000, 'April length'   );
assert(dateutils.getMonthLength(new Date(2000,5,0)) == 31*86400*1000, 'May length'     );

var d = new Date(2000,5,27,12,5,45,0);
assert(dateutils.getDayStart(d)   == (new Date(2000,5,27,0,0,0,0)).getTime(), '[1] Day start'  );
assert(dateutils.getDayEnd(d)     == (new Date(2000,5,28,0,0,0,0)).getTime(), '[1] Day end'    );
assert(dateutils.getWeekStart(d)  == (new Date(2000,5,26,0,0,0,0)).getTime(), '[1] Week start' );
assert(dateutils.getWeekEnd(d)    == (new Date(2000,6, 3,0,0,0,0)).getTime(), '[1] Week end'   );
assert(dateutils.getMonthStart(d) == (new Date(2000,5, 1,0,0,0,0)).getTime(), '[1] Month start');
assert(dateutils.getMonthEnd(d)   == (new Date(2000,6, 1,0,0,0,0)).getTime(), '[1] Month end'  );

var d = new Date(1999,11,30,18,12,9,0);
assert(dateutils.getDayStart(d)   == (new Date(1999,11,30,0,0,0,0)).getTime(), '[2] Day start'  );
assert(dateutils.getDayEnd(d)     == (new Date(1999,11,31,0,0,0,0)).getTime(), '[2] Day end'    );
assert(dateutils.getWeekStart(d)  == (new Date(1999,11,27,0,0,0,0)).getTime(), '[2] Week start' );
assert(dateutils.getWeekEnd(d)    == (new Date(2000, 0, 3,0,0,0,0)).getTime(), '[2] Week end'   );
assert(dateutils.getMonthStart(d) == (new Date(1999,11, 1,0,0,0,0)).getTime(), '[2] Month start');
assert(dateutils.getMonthEnd(d)   == (new Date(2000, 0, 1,0,0,0,0)).getTime(), '[2] Month end'  );

console.log(dateutils.getWeekEnd(d)   - dateutils.getWeekStart(d))
assert(dateutils.getDayEnd(d)   - dateutils.getDayStart(d)   == dateutils.getDayLength()  , 'Day length consistency  ');
assert(dateutils.getWeekEnd(d)  - dateutils.getWeekStart(d)  == dateutils.getWeekLength() , 'Week length consistency ');
assert(dateutils.getMonthEnd(d) - dateutils.getMonthStart(d) == dateutils.getMonthLength(d), 'Month length consistency');

assert(dateutils.getStringDay(3)    == 'Jeudi'   , 'String day by index'  );
assert(dateutils.getStringDay(d)    == 'Jeudi'   , 'String day by date'   );
assert(dateutils.getStringMonth(11) == 'Décembre', 'String month by index');
assert(dateutils.getStringMonth( d) == 'Décembre', 'String month by date' );

assert(dateutils.humanDay(d)   == 'le 30 décembre'                      , 'Human date' );
assert(dateutils.humanWeek(d)  == 'entre le 27 décembre et le 2 janvier', 'Human week' );
assert(dateutils.humanMonth(d) == 'en décembre'                         , 'Human month');

console.log('Everything is ok.')
