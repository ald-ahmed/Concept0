var $ = require('jquery')(require("jsdom").jsdom().defaultView);
var wordsSoFar = [];
var linkedSoFar = [];

var master = [];

var published = [];

var vt;


var onemorepublished = [];
var jsonz = {};
jsonz.nodes = [];
jsonz.edges = [];

//makeConnections("iraq");
var express = require('express');
var app = express();
app.use(function(req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});



app.get('/:id', function(req, res) {

    //res.header("Content-Type", "text/cache-manifest");
    res.setHeader('Content-Type', 'application/json');

    //res.write(req.params.id);

    makeConnections(req.params.id);

    var addedAlready = [];



    $.each(wordsSoFar, function(index, val1) {

        if (addedAlready.indexOf(val1) == -1) {
            jsonz.nodes.push({
                id: val1,
                label: val1,
                x: 0,
                y: 0,
                size: 1
            });
            addedAlready.push(val1);
        }

    });

    $.each(linkedSoFar, function(index, val) {
        if (addedAlready.indexOf(val) == -1) {
            addedAlready.push(val);
            jsonz.nodes.push({
                id: val,
                label: val,
                x: 0,
                y: 0,
                size: 1
            });
        }
    });

    $.each(onemorepublished, function(index, val) {
        jsonz.edges.push(val);
    });


    res.json(jsonz);
    jsonz = {};
    jsonz.nodes = [];
    jsonz.edges = [];
    addedAlready = [];
});

app.listen(process.env.PORT || 8080);


var request = require('request');

var url = 'http://hackschedule.com/api/schedule?courses[]=MATH-125';

request.get({
    url: url,
    json: true,
    headers: {'User-Agent': 'request'}
  }, (err, res, data) => {
    if (err) {
      console.log('Error:', err);
    } else if (res.statusCode !== 200) {
      console.log('Status:', res.statusCode);
    } else {
      // data is already parsed as JSON:
      console.log(data.html_url);
    }
});


while (true){
  kalsjdas();

}

function kalsjdas(){

  $.ajax({
             url: "http://hackschedule.com/api/schedule?courses[]=MATH-125",
             type: 'GET',
             success: function(res) {
                 console.log("good" + res);
             },
             error: function (xhr, ajaxOptions, thrownError) {
  console.log(xhr.status);
  console.log(thrownError);
            }
         });

         $.ajax({
                    url: "http://hackschedule.com/api/schedule?courses[]=MATH-125",
                    type: 'GET',
                    success: function(res) {
                        console.log("good" + res);
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
         console.log(xhr.status);
         console.log(thrownError);
                   }
                });

                $.ajax({
                           url: "http://hackschedule.com/api/schedule?courses[]=MATH-125",
                           type: 'GET',
                           success: function(res) {
                               console.log("good" + res);
                           },
                           error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.status);
                console.log(thrownError);
                          }
                       });


                       $.ajax({
                                  url: "http://hackschedule.com/api/schedule?courses[]=MATH-125",
                                  type: 'GET',
                                  success: function(res) {
                                      console.log("good" + res);
                                  },
                                  error: function (xhr, ajaxOptions, thrownError) {
                       console.log(xhr.status);
                       console.log(thrownError);
                                 }
                              });
}



function requestWord(word) {
    word = word.trim().toUpperCase();

    if (uniqueWord(word) && word.length > 1) {

        var item = [];
        var data = [];

        $.ajax({
            url: "http://api.pearson.com/v2/dictionaries/wordwise/entries?headword=" + word,
            dataType: 'JSON',
            success: function(json) {

                $.each(json.results, function(index, value) {
                    var partofspeech = json.results[index].part_of_speech;
                    var definition = json.results[index].senses[0].definition;
                    var headword = json.results[index].headword;

                    if (typeof(definition) == 'object') {
                        definition = json.results[index].senses[0].definition[0];
                    }

                    if (definition && headword.toUpperCase() == word) {
                        var def = [];
                        def.push({
                            Definition: definition,
                            POS: partofspeech
                        });
                        data.push(def);

                        $.each((definition.split(" ")), function(index, val) {
                            val = val.replace(/[^A-Za-z]/g, '');

                            if (val.toUpperCase() !== word && val !== "" && val.length > 1 && trash.indexOf(val.toLowerCase()) == -1) {
                                console.log(word.toLowerCase() + ";" + val.toLowerCase());


                                requestWord(val);
                            }


                        });
                    }

                });

                item.push(data);
                master.push({
                    word: word,
                    data: item
                });

            }
        });

    }
}

function uniqueWord(query) {

    if (wordsSoFar.indexOf(query) != -1) {
        return false;
    } else if (query !== "") {
        wordsSoFar.push(query);
        return true;
    }

}
var trash = ["are", "something", "your", "etc", "its", "do", "can", "to", "of", "if", "is", "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over", "after", "beneath", "under", "above", "the", "and", "a", "that", "I", "it", "not", "he", "as", "you", "this", "but", "his", "they", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their"];


function makeConnections(word) {

word=word.toLowerCase();
    //console.log("     search: "+word);

    if (uniqueWord(word) && word.length > 1) {

        $.ajax({
            url: "http://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=" + word + "&redirects=1",
            data: {
                format: 'json'
            },
            dataType: 'jsonp',
            success: function(json) {
                var pages = json.query.pages;

                //console.log(JSON.stringify(json,null, 4));

                $.each(pages, function(index, val) {
                    //console.log(val.extract);

                    var ex = val.extract;
                    //onsole.log("     ex: "+ex);

                    $.each(val.extract.split(" "), function(index, val) {
                        val = val.replace(/[^A-Za-z]/g, '').toLowerCase();
                        if (val !== word.toLowerCase() && val !== "" && val.length > 1 && trash.indexOf(val) == -1) {

                            $.when(verifyWord(val).done(function(a1) {
                                if (vt) {
                                    published.push(word.toLowerCase() + ";" + val);
                                    console.log(word.toLowerCase() + ";" + val);
                                    linkedSoFar.push(val);
                                    onemorepublished.push({
                                        id: Math.random(),
                                        source: word.toLowerCase(),
                                        target: val
                                    });
                                  //  console.log(onemorepublished);

                                    //makeConnections(val);

                                }

                            }));


                        }

                    });


                });

            }

        });
    }

}

function verifyWord(word) {

    if (linkedSoFar.indexOf(word) != -1) {
        vt = true;
    } else if (word !== "") {

        return $.ajax({
            url: "http://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=" + word + "&redirects=1",
            data: {
                format: 'json'
            },
            dataType: 'jsonp',
            success: function(json) {
                var pages = json.query.pages;
                $.each(pages, function(index, val) {
                    var ex = val.extract;

                    if ((ex.indexOf(" refer to") >= 0) || (ex.indexOf("may stand for") >= 0)) {
                        //console.log("\ncontains may refer\n");
                        vt = false;
                        //console.log(vt);
                    } else {
                        //console.log("\n good to go \n");
                        vt = true;
                        //console.log(vt);
                    }
                });
            }
        });
    }


}
