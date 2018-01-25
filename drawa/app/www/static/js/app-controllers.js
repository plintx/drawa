myApp.controller('AriaController', ['$scope', '$http', '$location', 'queueFactory', function ($scope, $http, $location, queueFactory) {
    $scope.showLoader = true
    $http.get("/api/getAriaVersion").then(function (response) {
        $scope.aria_info = response.data
        $scope.ariaVersion = response.data.version;
    });

    $http.get("/api/get_available_uris").then(function (response) {
        $scope.available_uris = response.data
    });
    $scope.showLoader = false
    $scope.addUri = function () {
        $scope.showLoader = true
        var dataObj = {
            uris: $scope.addUri.uri
        }
        $http({
            method: 'POST',
            url: '/api/addUri',
            data: {
                uris: $scope.addUri.uri
            }
        }).then(function successCallback(response) {
            Materialize.toast('File added', 4000)
            $scope.showLoader = false
        }, function errorCallback(response) {
            Materialize.toast('Error adding file!', 4000)
            $scope.showLoader = false
        });

        setTimeout(function () {
            $location.path("/");
        }, 200)

    };
    $scope.pauseAll = function () {
        $scope.showLoader = true
        queueFactory.pauseAll().then(function (response) {
            $scope.showLoader = false
            return response;
        });
    }
    $scope.unpauseAll = function () {
        $scope.showLoader = true
        queueFactory.unpauseAll().then(function (response) {
            $scope.showLoader = false
            return response;
        });
    }
    $scope.purgeResultsAll = function () {
        $scope.showLoader = true
        queueFactory.purgeResultsAll().then(function (response) {
            $scope.showLoader = false
            return response;
        });
    }

    $scope.formatBytes = function (bytes, decimals) {
        if (bytes == 0) return '0 Bytes';
        var k = 1024,
            dm = decimals || 2,
            sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
    $scope.getDownloadName = function (item) {
        objJson = angular.fromJson(item);
        if (typeof (item) == 'undefined') {
            return false;
        }
        //if (data.bittorrent.info.name){     
        if (item.hasOwnProperty('bittorrent')) {
            try {
                return objJson.bittorrent.info.name;
            } catch (err) {
                console.log("Bittorrent name not found, waiting...")
            }
        }
        if (item.hasOwnProperty('files')) {
            try {
                return $scope.getFileName(item.files[0].path);
            } catch (err) {
                console.log("Name not found, waiting...")
            }
        }
    }
    $scope.getFileName = function (path, isExtension) {
        var fullFileName, fileNameWithoutExtension;
        while (path.indexOf("\\") !== -1) {
            path = path.replace("\\", "/");
        }

        fullFileName = path.split("/").pop();
        return (isExtension) ? fullFileName : fullFileName.slice(0, fullFileName.lastIndexOf("."));
    }
    $scope.isArray = angular.isArray;
}]);

myApp.controller('DetailsController', ['$scope', '$location', 'queueFactory', function ($scope, $location,
    queueFactory) {
    $scope.getGidStatus = function () {
        $scope.showLoader = true
        var url = $location.path().split('/');
        var gid = url[2];
        queueFactory.getStatus(gid).then(function (response) {
            $scope.item_data = response;
            $scope.item_files = response.files;
            $scope.showLoader = false
        });
    }
    $scope.getGidStatus()

}]);

myApp.controller('QueueController', ['$scope', '$http', '$timeout', 'queueFactory', function ($scope, $http,
    $timeout, queueFactory) {
    $scope.queue = [];

    $scope.refreshData = function () {
        $scope.showLoader = true
        queueFactory.getQueue().then(function (response) {
            $scope.queue = response
            $scope.showLoader = false
        }).then(function () {
            $timeout($scope.refreshData, 1000);
        });
    }


    $scope.getFileNameOld = function (dir, path) {
        return path.slice(dir.length + 1);
    }


    $scope.pauseGid = function (gid) {
        $scope.showLoader = true;
        queueFactory.pauseGid(gid).then(function () {
            $scope.showLoader = false;
        });
    }
    $scope.unpauseGid = function (gid) {
        console.log("GID: " + gid)
        queueFactory.unpauseGid(gid)
    }
    $scope.removeGid = function (gid) {
        console.log("GID: " + gid)
        queueFactory.removeGid(gid)
    }
    $scope.purgeResultsGid = function (gid) {
        console.log("GID: " + gid)
        queueFactory.purgeResultsGid(gid)
    }
    $scope.refreshData()
}]);