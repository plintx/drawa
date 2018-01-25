var myApp = angular.module('drawa', ['ngRoute', 'ui.materialize']);

myApp.config(function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: 'pages/main.html',
        })
        .when('/add', {
            templateUrl: 'pages/add.html',
        })
        .when('/aria', {
            templateUrl: 'pages/aria.html',
        })
        .when('/details/:param1', {
            templateUrl: 'pages/details.html',
        })
});
