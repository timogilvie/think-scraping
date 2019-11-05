// Download PhantomJS here cd http://phantomjs.org/download.html

//console.log('Initializing');
var page = require('webpage').create();
var fs = require('fs');

var system = require('system');
var url = "";
if (system.args.length === 1) {
    console.log('Usage: gplay-topgrossing feed_type output_filename');
} else {
    if (system.args[1] === 'grossing'){
        url = 'https://play.google.com/store/apps/category/GAME/collection/topgrossing';
        }
    else if (system.args[1] === 'free'){
        url = 'https://play.google.com/store/apps/category/GAME/collection/topselling_free';
    }
    else if (system.args[1] === 'paid'){
        url = 'https://play.google.com/store/apps/category/GAME/collection/topselling_paid';
    }
    else{
        console.log("Invalid feed_type");
        phantom.exit();
    }
}

var path = system.args[2];
//console.log(path);

var topPos = 0;
var scrollCount = 0;
var timeOut = 1400; // We need to wait some time after each scroll. ~1.5s is the best value.
page.viewportSize = { width: 1200, height: 1000 };
page.settings.resourceTimeout = 8000;
page.onResourceTimeout = function(e) {
  console.log(e.errorCode);   // it'll probably be 408
  console.log(e.errorString); // it'll probably be 'Network timeout on resource'
  console.log('URL: '+e.url);         // the url whose request timed out
  console.log('Destination: '+path);         // the url whose request timed out
  phantom.exit(1);
};
//console.log('Connecting to '+url);
page.open(url, function(status) {
  //console.log('Connected');
  window.setInterval(function() {

      var check = page.evaluate(function() {
            return $('#show-more-button').is(':visible');
      });
      topPos = topPos + 1000;
      scrollCount = scrollCount + 1;
      if(!check) { //If #show-more-button not visible, we still not at the end.
   		page.scrollPosition = {
		  top: topPos,
		  left: 0
		};
      }
      else if (scrollCount > 20) {
          console.log("20+ scroll attempts. Failing. ");
          phantom.exit(1)
      }
      else {
        // console.log('Saving data to '+path);
        fs.write(path, page.content, 'w');
        phantom.exit();
      }
  }, timeOut);

});

