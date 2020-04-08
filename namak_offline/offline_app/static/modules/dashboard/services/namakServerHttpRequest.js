angular.module('dashboard')
    .service('namakServerHttpRequest', function namakServerHttpRequest($q, $http, $auth, $cookies) {
        return {
            'API_URL': "http://127.0.0.1:9001/",
            'use_session': false,
            'authenticated': null,
            'authPromise': null,
            'request': function (args) {
                if ($auth.getToken()) {
                    $http.defaults.headers.common.Authorization = 'Token ' + $auth.getToken();
                }
                // Continue
                params = args.params || {};
                args = args || {};
                var deferred = $q.defer(),
                    url = this.API_URL + args.url,
                    method = args.method || "GET",
                    params = params,
                    data = args.data || {};
                // Fire the request, as configured.
                $http({
                    url: url,
                    withCredentials: this.use_session,
                    method: method.toUpperCase(),
                    headers: {'X-CSRFToken': $cookies.get("csrftoken")},
                    params: params,
                    data: data
                }).then(angular.bind(this, function (data, status, headers, config) {
                        deferred.resolve(data['data'], status);
                    }), angular.bind(this, function (data, status, headers, config) {
                        console.log("error syncing with: " + url);

                        // Set request status
                        if (data) {
                            data.status = status;
                        }

                        if (status === 0) {
                            if (data === "") {
                                data = {};
                                data['status'] = 0;
                                data['non_field_errors'] = ["Could not connect. Please try again."];
                            }
                            // or if the data is null, then there was a timeout.
                            if (data === null) {
                                // Inject a non field error alerting the user
                                // that there's been a timeout error.
                                data = {};
                                data['status'] = 0;
                                data['non_field_errors'] = ["Server timed out. Please try again."];
                            }
                        }
                        deferred.reject(data, status, headers, config);
                    }));
                return deferred.promise;
            },
            'status': function () {
                return this.request({
                    'method': "GET",
                    'url': "api/offline/status/"
                });
            }


        };
    });