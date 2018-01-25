
myApp.factory('queueFactory', ['$http', function ($http) {
    var _getQueue = function () {
        return $http.get("/api/getQueue").then(function successCallback(response) {
            return response.data;
        }, function errorCallback(response) {
            Materialize.toast('Error fetching queue!', 4000)
        });
    }

    var _getStopped = function () {
        return $http.get("/api/getStopped").then(function (response) {
            return response.data;
        });
    }
    var _getActive = function () {
        return $http.get("/api/getActive").then(function (response) {
            return response.data;
        });
    }
    var _getWaiting = function () {
        return $http.get("/api/getWaiting").then(function (response) {
            return response.data;
        });
    }

    var _pauseGid = function (gid) {
        return $http.put("/api/pause/" + gid)
            .then(function successCallback(response) {

                return response.data;
            }, function errorCallback(response) {
                Materialize.toast('Error pausing item!', 4000)
            });
    }
    var _pauseAll = function () {
        return $http.put("/api/pauseAll")
            .then(function successCallback(response) {
                return response.data;
            }, function errorCallback(response) {
                Materialize.toast('Error pausing items!', 4000)
            });
    }
    var _unpauseGid = function (gid) {
        return $http.put("/api/unpause/" + gid).then(function successCallback(response) {
            return response.data;
        }, function errorCallback(response) {
            Materialize.toast('Error on unpause item!', 4000)
        });
    }
    var _unpauseAll = function () {
        return $http.put("/api/unpauseAll").then(function successCallback(response) {
            return response.data;
        }, function errorCallback(response) {
            Materialize.toast('Error on unpause items!', 4000)
        });
    }
    var _removeGid = function (gid) {
        return $http.delete("/api/remove/" + gid).then(function successCallback(response) {
            return response.data;
        }, function errorCallback(response) {
            Materialize.toast('Error on remove item!', 4000)
        });
    }
    var _purgeResultsGid = function (gid) {
        return $http.delete("/api/purgeResults/" + gid).then(function successCallback(response) {
            return response.data;
        }, function errorCallback(response) {
            Materialize.toast('Error on purging results!', 4000)
        });
    }
    var _purgeResultsAll = function (gid) {
        return $http.delete("/api/purgeResults").then(function successCallback(response) {
            return response.data;
        }, function errorCallback(response) {
            Materialize.toast('Error on purging results!', 4000)
        });
    }

    var _getStatus = function (gid) {
        return $http.get("/api/getStatus/" + gid).then(
            function successCallback(response) {
                return response.data;
            },
            function errorCallback(response) {
                Materialize.toast('Error fetching data!', 4000) // 4000 is the duration of the toast
            });
    }


    return {
        getQueue: _getQueue,
        getActive: _getActive,
        getWaiting: _getWaiting,
        getStopped: _getStopped,
        pauseGid: _pauseGid,
        pauseAll: _pauseAll,
        unpauseGid: _unpauseGid,
        unpauseAll: _unpauseAll,
        removeGid: _removeGid,
        purgeResultsGid: _purgeResultsGid,
        purgeResultsAll: _purgeResultsAll,
        getStatus: _getStatus,
    };
}]);