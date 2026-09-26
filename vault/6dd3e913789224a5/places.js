/* ---- the one list of places. used by the map (markers), the index (grid) and each place page (title, date, mini-map).
   id     : file name of the place page → places/<id>.html
   floor  : lower | ground | 2 | 3 | 4 | 5 | 6
   x, y   : where it is on that floor's plan, as fractions 0–1 of the image (floors/<floor>.png, 1660×1040)
   thumb  : image for the index grid
*/
var FLOORS = [
  ['lower',  'L', 'Lower Level'],
  ['ground', 'G', 'Ground Level'],
  ['2',      '2', 'Second Level'],
  ['3',      '3', 'Third Level'],
  ['4',      '4', 'Fourth Level'],
  ['5',      '5', 'Fifth Level'],
  ['6',      '6', 'Sixth Level']
];

var PLACES = [
  { id:'e15-540', floor:'5', x:0.240, y:0.520,   /* E15 side of the 5th floor is only an outline on the map — move x,y to taste */
    name:'E15-540', date:'2026.09.25', thumb:'img/e15-540/0177.jpg' }
];

function floorOf(key){ return FLOORS.find(function(f){ return f[0] === key; }) || FLOORS[1]; }
function placeOf(id){ return PLACES.find(function(p){ return p.id === id; }); }
