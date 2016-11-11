

var trash = ["are", "something", "your", "etc", "its", "do", "can", "to", "of", "if", "is", "in", "for", "on", "with", "at", "by", "from", "up", "about", "into", "over", "after", "beneath", "under", "above", "the", "and", "a", "that", "I", "it", "not", "he", "as", "you", "this", "but", "his", "they", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there", "their"];

var spheres=[];
var uniqueSpheres;

var $ = require('jquery')(require("jsdom").jsdom().defaultView);
var express = require('express');
var app = express();


app.get('', function(req, res) {
    res.setHeader('Content-Type', 'application/json');
});

app.listen(process.env.PORT || 8090);



//var content= "Iraq (/\u026a\u02c8r\u00e6k/, /\u026a\u02c8r\u0251\u02d0k/, or /a\u026a\u02c8r\u00e6k/; Arabic: \u0627\u0644\u0639\u0631\u0627\u0642\u200e\u200e al-\u2018Ir\u0101q), officially the Republic of Iraq (Arabic:  \u062c\u0645\u0647\u0648\u0631\u064a\u0629 \u0627\u0644\u0639\u0631\u0627\u0642  ) is a country in Western Asia, bordered by Turkey to the north, Iran to the east, Kuwait to the southeast, Saudi Arabia to the south, Jordan to the southwest, and Syria to the west. The capital, and largest city, is Baghdad. The main ethnic groups are Arabs and Kurds; others include Assyrians, Turkmen, Shabakis, Yazidis, Armenians, Mandeans, Circassians, and Kawliya. Around 95% of the country's 36 million citizens are Shia or Sunni Muslims, with Christianity, Yarsan, Yezidism, and Mandeanism also present.\nIraq has a coastline measuring 58 km (36 miles) on the northern Persian Gulf and encompasses the Mesopotamian Alluvial Plain, the northwestern end of the Zagros mountain range, and the eastern part of the Syrian Desert. Two major rivers, the Tigris and Euphrates, run south through Iraq and into the Shatt al-Arab near the Persian Gulf. These rivers provide Iraq with significant amounts of fertile land.\nThe region between the Tigris and Euphrates rivers, historically known as Mesopotamia, is often referred to as the cradle of civilisation. It was here that mankind first began to read, write, create laws, and live in cities under an organised government\u2014notably Uruk, from which \"Iraq\" is derived. The area has been home to successive civilisations since the 6th millennium BC. Iraq was the centre of the Akkadian, Sumerian, Assyrian, and Babylonian empires. It was also part of the Median, Achaemenid, Hellenistic, Parthian, Sassanid, Roman, Rashidun, Umayyad, Abbasid, Ayyubid, Mongol, Safavid, Afsharid, and Ottoman empires.\nIraq's modern borders were mostly demarcated in 1920 by the League of Nations when the Ottoman Empire was divided by the Treaty of S\u00e8vres. Iraq was placed under the authority of the United Kingdom as the British Mandate of Mesopotamia. A monarchy was established in 1921 and the Kingdom of Iraq gained independence from Britain in 1932. In 1958, the monarchy was overthrown and the Iraqi Republic created. Iraq was controlled by the Arab Socialist Ba'ath Party from 1968 until 2003. After an invasion by the United States and its allies in 2003, Saddam Hussein's Ba'ath Party was removed from power and multi-party parliamentary elections were held in 2005. The American presence in Iraq ended in 2011, but the Iraqi insurgency continued and intensified as fighters from the Syrian Civil War spilled into the country.";
content = "Situated in Southern California, Los Angeles is known for its mediterranean climate, ethnic diversity, sprawling metropolis, and as a major center of the American entertainment industry.";

byWord(content);

setTimeout(function () {
  console.log(spheres);
  connectChildtoChild(0);
//  console.log(uniqueSpheres);
}, 1000);


function byWord (content) {
  var text = normalizeText(content);
  breakText(text);
}

//put text in, break it into words
function breakText (text) {

  //make spheres
  $.each(text.split(" "), function(index, val) {
      val = normalizeWord(val);
      if(val!==undefined){createSpheres(val.toLowerCase());}
  });
  //make spheres
  uniqueify(spheres);
}

// remove line breaks and extended hyphens
function normalizeText(text) {
    text = text.replace(/\n/g, " ");
    text = text.replace("—", " ");
    return text;
}

//remove any thing other than words and words with punctuation
function normalizeWord(word) {
    var match = word.match(/((\w)|(?=\S*['-])([a-zA-Z'-]))+/g);

    if (match) {
        if (match.length == 1) {
            return word.match(/((\w)|(?=\S*['-])([a-zA-Z'-]))+/g)[0];
        }
    }
}


//get word and turn it into a spheres (node)
function createSpheres(word) {
spheres.push(word);
}


//make an array consisting of non-duplicate spheres
function uniqueify (spheres) {
  uniqueSpheres=spheres.filter(function(itm,i,a){
      return i==spheres.indexOf(itm);
  });
}

function connectMothertoChild () {

}



function connectChildtoChild (index) {
if (index+1>spheres.length){
  return;
}
for (var i=index;i<spheres.length;i++){
  if (index!=i){
  console.log(spheres[index]+" ---- "+spheres[i]+"--------"+1/(Math.abs(index-i)));
   }
}

connectChildtoChild(index+1);
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
