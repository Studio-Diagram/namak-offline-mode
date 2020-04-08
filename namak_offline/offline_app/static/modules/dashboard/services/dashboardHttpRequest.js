angular.module('dashboard')
    .service('dashboardHttpRequest', function dashboardHttpRequest($q, $http, $auth, $cookies) {
        var service = {
            'API_URL': window.location.origin,
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
            'getEmployees': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getEmployees/",
                    'data': data
                });
            },
            'checkLogin': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/checkLogin/",
                    'data': data
                });
            },
            'registerEmployee': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/registerEmployee/",
                    'data': data
                });
            },
            'searchEmployee': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/searchEmployee/",
                    'data': data
                });
            },
            'getEmployee': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getEmployee/",
                    'data': data
                });
            },
            'addMenuCategory': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addMenuCategory/",
                    'data': data
                });
            },
            'searchMenuCategory': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/searchMenuCategory/",
                    'data': data
                });
            },
            'getMenuCategory': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getMenuCategory/",
                    'data': data
                });
            },
            'getMenuCategories': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getMenuCategories/",
                    'data': data
                });
            },
            'getPrinters': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getPrinters/",
                    'data': data
                });
            },
            'addMenuItem': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addMenuItem/",
                    'data': data
                });
            },
            'deleteMenuItem': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/deleteMenuItem/",
                    'data': data
                });
            },
            'searchMenuItem': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/searchMenuItem/",
                    'data': data
                });
            },
            'getMenuItem': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getMenuItem/",
                    'data': data
                });
            },
            'getMenuItems': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getMenuItems/",
                    'data': data
                });
            },
            'addMember': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addMember/",
                    'data': data
                });
            },
            'getMembers': function (data) {
                return this.request({
                    'method': "GET",
                    'url': "/namak_offline/getMembers/",
                    'data': data
                });
            },
            'searchMember': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/searchMember/",
                    'data': data
                });
            },
            'getMember': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getMember/",
                    'data': data
                });
            },
            'getBranches': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getBranches/",
                    'data': data
                });
            },
            'searchBranch': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/searchBranch/",
                    'data': data
                });
            },
            'getBranch': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getBranch/",
                    'data': data
                });
            },
            'getMenuItemsWithCategories': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getMenuItemsWithCategories/",
                    'data': data
                });
            },
            'getTables': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTables/",
                    'data': data
                });
            },
            'addInvoiceSales': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addInvoiceSales/",
                    'data': data
                });
            },
            'getAllTodayInvoices': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllTodayInvoices/",
                    'data': data
                });
            },
            'getInvoice': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getInvoice/",
                    'data': data
                });
            },
            'endCurrentGame': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/endCurrentGame/",
                    'data': data
                });
            },
            'getAllInvoiceGames': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllInvoiceGames/",
                    'data': data
                });
            },
            'deleteItems': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/deleteItems/",
                    'data': data
                });
            },
            'settleInvoiceSale': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/settleInvoiceSale/",
                    'data': data
                });
            },
            'getTodayStatus': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTodayStatus/",
                    'data': data
                });
            },
            'getKitchenDetailSales': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getKitchenDetailSales/",
                    'data': data
                });
            },
            'getBarDetailSales': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getBarDetailSales/",
                    'data': data
                });
            },
            'getOtherDetailSales': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getOtherDetailSales/",
                    'data': data
                });
            },
            'timeCalc': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/timeCalc/",
                    'data': data
                });
            },
            'addReserve': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addReserve/",
                    'data': data
                });
            },
            'getAllReserves': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllReserves/",
                    'data': data
                });
            },
            'arriveReserve': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/arriveReserve/",
                    'data': data
                });
            },
            'deleteReserve': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/deleteReserve/",
                    'data': data
                });
            },
            'getReserve': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getReserve/",
                    'data': data
                });
            },
            'printAfterSave': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/printAfterSave/",
                    'data': data
                });
            },
            'printCash': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/printCash/",
                    'data': data
                });
            },
            'getTodayCash': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTodayCash/",
                    'data': data
                });
            },
            'getAllCashes': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllCashes/",
                    'data': data
                });
            },
            'closeCash': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/closeCash/",
                    'data': data
                });
            },
            'openCash': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/openCash/",
                    'data': data
                });
            },
            'checkCashExist': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/checkCashExist/",
                    'data': data
                });
            },
            'logOut': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/logOut/",
                    'data': data
                });
            },
            'addTable': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addTable/",
                    'data': data
                });
            },
            'searchTable': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/searchTable/",
                    'data': data
                });
            },
            'getTable': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTable/",
                    'data': data
                });
            },
            'getWorkingTime': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getWorkingTime/",
                    'data': data
                });
            },
            'getTodayForReserve': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTodayForReserve/",
                    'data': data
                });
            },
            'addTableCategory': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addTableCategory/",
                    'data': data
                });
            },
            'getTableCategory': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTableCategory/",
                    'data': data
                });
            },
            'getTableCategories': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getTableCategories/",
                    'data': data
                });
            },
            'readyForSettle': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/readyForSettle/",
                    'data': data
                });
            },
            'deleteInvoiceSale': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/deleteInvoiceSale/",
                    'data': data
                });
            },
            'getWaitingList': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getWaitingList/",
                    'data': data
                });
            },
            'addWaitingList': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/addWaitingList/",
                    'data': data
                });
            },
            'getAllInvoicesStateBase': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllInvoicesStateBase/",
                    'data': data
                });
            },
            'changeGameState': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/changeGameState/",
                    'data': data
                });
            },
            'doNotWantOrder': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/doNotWantOrder/",
                    'data': data
                });
            },
            'getAllLeftReserves': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllLeftReserves/",
                    'data': data
                });
            },
            'getAllNotComeReserves': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getAllNotComeReserves/",
                    'data': data
                });
            },
            'startInvoiceGame': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/startInvoiceGame/",
                    'data': data
                });
            },
            'getCategoriesBaseOnKind': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/getCategoriesBaseOnKind/",
                    'data': data
                });
            },
            'editPaymentInvoiceSale': function (data) {
                return this.request({
                    'method': "POST",
                    'url': "/namak_offline/editPaymentInvoiceSale/",
                    'data': data
                });
            },
            'sync_with_online': function () {
                return this.request({
                    'method': "GET",
                    'url': "/namak_offline/syncWithOnline/"
                });
            }


        };
        return service;

    });