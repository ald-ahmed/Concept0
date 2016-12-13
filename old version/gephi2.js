
var express = require('express');

var app = express();
      // Gephi Streaming Master should be launch in your computer
      var websocket = new WebSocket("ws://localhost:80000/workspace0?action=updateGraph")
      websocket.onopen = function (event) {

              // Sending event following the API and message structure defined
              websocket.send('{"an":{"a":{"label":"a"}}}')
              websocket.send('{"an":{"b":{"label":"b"}}}')
              websocket.send('{"ae":{"ab":{"source":"a","target":"b"}}}')

              randomGenerate()

      };

      // A Quick & Dirty example to see the "real-time" graph
      function randomGenerate(){
            setTimeout(function(){
               var test = (Math.floor( Math.random() * 50 ) + 1)%2 ;
                for (i = 0; i < 10; i++) {
                      var id = Math.floor( Math.random() * 50 ) + 1 ;
                      websocket.send('{"an":{"'+id+'":{"label":"'+id+'"}}}')
                  }
                  for (i = 0; i < 10; i++) {
                      var source = Math.floor( Math.random() * 50 ) + 1 ;
                      var target = Math.floor( Math.random() * 50 ) + 1 ;


                      if(test===0) {
                          websocket.send('{"ae":{"'+source+'-'+target+'":{"source":"'+source+'","target":"'+target+'"}}}')
                      } else {
                          websocket.send('{"de":{"'+source+'-'+target+'":{"source":"'+source+'","target":"'+target+'"}}}')
                      }

                  }
                  randomGenerate()
              }, 2000)
      }
      // Triggered when we received a message
      // Here Gephi is actually propagating any changes to all the client (including yourself)
      // It can be usefull but can also be ignored

      /*
      websocket.onmessage = function(message){
          console.log(message)
      }
      */
