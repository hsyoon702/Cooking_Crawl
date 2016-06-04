var fs = require('fs'),
    request = require('request');

var auth = require('./auth');

fs.readFile('categories2.json', 'utf-8', function (err, data) {
    if (err) throw err;

    data = JSON.parse(data);

    console.log(data);

    data.forEach(function (category, index) {
        request.post({
            url: 'http://localhost:1337/category',
            form: category,
            auth: auth,
        }, function (error, res, body) {
            console.log(body);
        });
    });
});
