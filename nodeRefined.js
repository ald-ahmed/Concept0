var trash = ["are", "something", "your", "etc", "its", "do", "can", "to", "of", "if", "is", "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over", "after", "beneath", "under", "above", "the", "and", "a", "that", "I", "it", "not", "he", "as", "you", "this", "but", "his", "they", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their"];

var spheres = [];
var uniqueSpheres;

var $ = require('jquery')(require("jsdom").jsdom().defaultView);
var express = require('express');
var app = express();
var S = require('string');
var execall = require('execall');
var async = require('async');

app.get('', function(req, res) {
    res.setHeader('Content-Type', 'application/json');
});

app.listen(process.env.PORT || 8090);


//var content = "Iraq (/\u026a\u02c8r\u00e6k/, /\u026a\u02c8r\u0251\u02d0k/, or /a\u026a\u02c8r\u00e6k/; Arabic: \u0627\u0644\u0639\u0631\u0627\u0642\u200e\u200e al-\u2018Ir\u0101q), officially the Republic of Iraq (Arabic:  \u062c\u0645\u0647\u0648\u0631\u064a\u0629 \u0627\u0644\u0639\u0631\u0627\u0642  ) is a country in Western Asia, bordered by Turkey to the north, Iran to the east, Kuwait to the southeast, Saudi Arabia to the south, Jordan to the southwest, and Syria to the west. The capital, and largest city, is Baghdad. The main ethnic groups are Arabs and Kurds; others include Assyrians, Turkmen, Shabakis, Yazidis, Armenians, Mandeans, Circassians, and Kawliya. Around 95% of the country's 36 million citizens are Shia or Sunni Muslims, with Christianity, Yarsan, Yezidism, and Mandeanism also present.\nIraq has a coastline measuring 58 km (36 miles) on the northern Persian Gulf and encompasses the Mesopotamian Alluvial Plain, the northwestern end of the Zagros mountain range, and the eastern part of the Syrian Desert. Two major rivers, the Tigris and Euphrates, run south through Iraq and into the Shatt al-Arab near the Persian Gulf. These rivers provide Iraq with significant amounts of fertile land.\nThe region between the Tigris and Euphrates rivers, historically known as Mesopotamia, is often referred to as the cradle of civilisation. It was here that mankind first began to read, write, create laws, and live in cities under an organised government\u2014notably Uruk, from which \"Iraq\" is derived. The area has been home to successive civilisations since the 6th millennium BC. Iraq was the centre of the Akkadian, Sumerian, Assyrian, and Babylonian empires. It was also part of the Median, Achaemenid, Hellenistic, Parthian, Sassanid, Roman, Rashidun, Umayyad, Abbasid, Ayyubid, Mongol, Safavid, Afsharid, and Ottoman empires.\nIraq's modern borders were mostly demarcated in 1920 by the League of Nations when the Ottoman Empire was divided by the Treaty of S\u00e8vres. Iraq was placed under the authority of the United Kingdom as the British Mandate of Mesopotamia. A monarchy was established in 1921 and the Kingdom of Iraq gained independence from Britain in 1932. In 1958, the monarchy was overthrown and the Iraqi Republic created. Iraq was controlled by the Arab Socialist Ba'ath Party from 1968 until 2003. After an invasion by the United States and its allies in 2003, Saddam Hussein's Ba'ath Party was removed from power and multi-party parliamentary elections were held in 2005. The American presence in Iraq ended in 2011, but the Iraqi insurgency continued and intensified as fighters from the Syrian Civil War spilled into the country.";
//content = "Situated in Southern California, Los Angeles is known for its mediterranean climate, ethnic diversity, sprawling metropolis, and as a major center of the American entertainment industry.";
//content = "al-‘Irāq)";



var content;
var spheres;
var links;

async.series(
[
   function(callback) { getContent("banana",callback); },
   function(callback) { createSpheresFromText(content,callback); },
   function(callback) { createLinks(spheres, "iraq",callback); },
   function(callback) { printMe(links,callback); },

]
);


function printMe(anything,callback) {
  console.log(anything);
}


//get an array of words from space or period seperated list of words (text)
function createSpheresFromText(input,callback) {

    var result = [];
    //replace extended hyphens with spaces so they can become 2 words when split
    input = input.replace(/—/g, " ");
    //replace lines with spaces
    input = input.replace(/\n/g, " ");

    //lets examine the input on a word by word base
    $.each(input.split(" "), function(index, val) {
        //remove artifacts
        val = S(val).strip(',', '.', ')', '(', ':', ';', '"').s;
        val = val.toLowerCase();
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

        //if one artifact is found, push it to result array
        if (goodToGo) {
            result.push(val);
        } else {
            //console.log("     NOT SELECTED: " +val);
        }

    });

    spheres=result;
    callback();
}


function createLinks(list, origin,callback) {

    //main array for collecting the entries
    var result = [];

    //for every word in list, link it to origin
    $(list).each(function(index, val) {

        //check entry is already created, assume is true
        var newEntry = true;

        //search the result array for the entry, increase its strength if found
        //warning that this is not the most effiecent approach
        $(result).each(function(innerIndex, innerVal) {
            if (innerVal.node == origin && innerVal.target == val) {
                innerVal.strength++;
                newEntry = false;
                return;
            }
        });

        //if new entry, create it and push it
        if (newEntry) {
            result.push({
                node: origin,
                target: val,
                strength: 1
            });
        }

    });
    links= result;
    callback();
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
              callback();
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
