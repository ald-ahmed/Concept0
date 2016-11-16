var trash = ["are", "something", "your", "etc", "its", "do", "can", "to", "of", "if", "is", "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over", "after", "beneath", "under", "above", "the", "and", "a", "that", "I", "it", "not", "he", "as", "you", "this", "but", "his", "they", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their"];


var $ = require('jquery')(require("jsdom").jsdom().defaultView);
var express = require('express');
var app = express();

var S = require('string');
var execall = require('execall');


var content;
var spheres = [];
var links = [];
var current;


getContent('iraq', mainOperations);

var i=0;

function mainOperations (origin) {
  createSpheresFromText(content);
  createLinks(spheres, origin);
  //getContent(spheres[i], mainOperations);
  i++;
}


function printMe(anything,callback) {
  console.log(anything);
}

setTimeout(function() {
  printMe(spheres);
}, 5000);


//get an array of words from space or period seperated list of words (text)
function createSpheresFromText(input) {

    //replace extended hyphens with spaces so they can become 2 words when split
    input = input.replace(/—/g, " ");
    //replace lines with spaces
    input = input.replace(/\n/g, " ");

    //lets examine the input on a word by word base
    $.each(input.split(" "), function(index, val) {

        //remove artifacts
        val = S(val).strip(',', '.', ')', '(', ':', ';', '"').s;
        val = val.toLowerCase();

        //if word is origin, ignore it and move on to the next
        if (val === current) {
          return true;
        }

        //if after deletion of artifacts, we have empty string, go on to the next word
        if (val.length === 0) {
            return true;
        }

        //return an array of objects showing anything not alphanumeric
        var punctuation = execall((/[^a-z^A-Z0-9]/g), val);

        var goodToGo = true;

        //more than one alphanumeric character, probably not a word
        if (punctuation.length > 1) {
            goodToGo = false;
        }

        //if one artifact is found, push it to spheres array
        if (goodToGo) {
            spheres.push(val);
        } else {
            //console.log("     NOT SELECTED: " +val);
        }

    });

}


function createLinks(list, origin) {

    //for every word in list, link it to origin
    $(list).each(function(index, val) {

        //check entry is already created, assume is true
        var newEntry = true;

        //search the result array for the entry, increase its strength if found
        //warning that this is not the most effiecent approach
        $(links).each(function(innerIndex, innerVal) {
            if (innerVal.node == origin && innerVal.target == val) {
                innerVal.strength++;
                newEntry = false;
                return;
            }
        });

        //if new entry, create it and push it
        if (newEntry) {
            links.push({
                node: origin,
                target: val,
                strength: 1
            });
        }

    });

}



function connectChildtoChild(index) {
    if (index + 1 > spheres.length) {
        return;
    }
    for (var i = index; i < spheres.length; i++) {
        if (index != i) {
            console.log(spheres[index] + " ---- " + spheres[i] + "--------" + 1 / (Math.abs(index - i)));
        }
    }

    connectChildtoChild(index + 1);
}


function getContent(query,callback) {
  //console.log("get content called! " +query);
  $.ajax({
      url: "http://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles=" + query + "&redirects=1",
      data: {
          format: 'json'
      },
      dataType: 'jsonp',
      success: function(json) {
          var pages = json.query.pages;

          $.each(pages, function(index, val) {
              var ex = val.extract;
              content= ex;
              console.log('done loading content');
              current=query;
              callback(query);
          });

      }

  });

}


/*

function uniqueWord(query) {

    if (wordsSoFar.indexOf(query) != -1) {
        return false;
    } else if (query !== "") {
        wordsSoFar.push(query);
        return true;
    }

}


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

*/
