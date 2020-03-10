const fs = require('fs')
const path = require('path');

var public_assets = path.join(process.cwd(), 'public', 'assets', 'html');


// Credit: https://github.com/typicode/json-server/issues/453
module.exports = function (req, res, next) {
  if (req.method === 'POST') {
    // Converts POST to GET and move payload to query params
    // This way it will make JSON Server think that it's a GET request
    req.method = 'GET';
    req.query = req.body;
  }

  // For the 'stop_build' POST request, the API returns 302
  if (req.url.indexOf("stop_build") === 1) {
    res.status(302);
  }

  // Use this for static content
  if (req.url.indexOf("assets/html") === 1) {
    html_file = fs.readFileSync(path.join(public_assets, 'artifacts.html')).toString();
    // console.log(html_file);

    // Send the HTML file as a response to the client
    res.send(html_file);
  }

  // Continue to JSON Server router
  next();
}
