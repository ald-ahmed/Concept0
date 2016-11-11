var $ = require('jquery')(require("jsdom").jsdom().defaultView);



var express = require('express');
var app = express();


app.get('', function(req, res) {

    res.setHeader('Content-Type', 'application/json');
var i=1;
    setInterval(function(){
    res.write('{"an":{"'+i+'":{"label":"SN'+i+'","size":20}}} ');
i++;
  }, 2000);

//    res.end();
});

app.listen(process.env.PORT || 8000);
