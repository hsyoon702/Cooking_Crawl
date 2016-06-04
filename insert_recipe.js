var fs = require('fs'),
    request = require('request'),
    async = require('async'),

    apiHost = 'http://localhost:1337',

    apiRoute = {
        resource: '/resource',
        recipe: '/recipe',
        method: '/method',
    },

    auth = require('./auth');

for (var api in apiRoute) {
    apiRoute[api] = apiHost + apiRoute[api];
}

fs.readFile('recipe_only_valid.json', 'utf-8', function (error, data) {
    if (error) throw error;

    var recipes = JSON.parse(data);

    createRecipes(recipes);
});

function createRecipes(recipes) {
    async.eachSeries(recipes, function (recipe, cb) {
        var thumb = recipe.thumb,
            method = recipe.method,
            methodThumb = recipe.methodThumb;

        delete recipe.thumb;
        delete recipe.methodThumb;

        async.waterfall([
            createThumb,
            createRecipe,
            createMethodThumbs,
        ], done);

        function done(error, recipe) {
            if (error) {
                return console.error(error);
            }

            console.log("Done", recipe);

            cb();
        }

        function createThumb(cb) {
            request.post({
                url: apiRoute.resource,
                form: {
                    reference: thumb
                },
                auth: auth,
            }, response);

            function response(error, res, body) {
                if (error) {
                    return cb("createThumb: " + error);
                }

                var resThumb = JSON.parse(body);

                return cb(null, resThumb);
            }
        }

        function createRecipe(thumbnail, cb) {
            recipe.thumbnail = thumbnail.id;

            request.post({
                url: apiRoute.recipe,
                form: recipe,
                auth: auth,
            }, response);

            function response(error, res, body) {
                if (error) {
                    return cb("createRecipe: " + error);
                }

                console.log(body);

                var resRecipe = JSON.parse(body);

                cb(null, resRecipe);
            }
        }

        function createMethodThumbs(recipe, cb) {
            async.parallel([
                createMethod,
                createMethodThumb,
            ], function (error) {
                cb(error, recipe);
            });

            function createMethodThumb(cb) {
                async.each(methodThumb, function (thumb, cb) {
                    request.post({
                        url: apiRoute.resource,
                        form: {
                            recipe: recipe.id,
                            reference: thumb
                        },
                        auth: auth,
                    }, response);

                    function response(error, res, body) {
                        console.log(body);

                        var resMethodThumb = JSON.parse(body);

                        cb(error ? "createMethodThumb: " + error : null);
                    }
                }, function (error) {
                    cb(error);
                });
            }

            function createMethod(cb) {
                async.each(method, function (thumb, cb) {
                    request.post({
                        url: apiRoute.method,
                        form: {
                            recipe: recipe.id,
                            content: thumb
                        },
                        auth: auth,
                    }, response);

                    function response(error, res, body) {
                        console.log(body);

                        var resMethodThumb = JSON.parse(body);

                        cb(error ? "createMethod: " + error : null);
                    }
                }, function (error) {
                    cb(error);
                });
            }
        }
    }, function (error) {
        if (error) {
            console.error(error);
        }

        console.log("Whole tasks done");
    });
}
