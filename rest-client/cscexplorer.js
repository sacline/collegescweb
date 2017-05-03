var collegeScorecardExplorer = angular.module('collegeScorecardExplorer',
  ['ngResource']);

collegeScorecardExplorer.controller('CategoryListController',
function CategoryListController($scope, $http) {

  $scope.method = 'GET';
  $scope.url = 'http://localhost:5000/cscvis/api/v2.0/data/data_types';

  $http({method: $scope.method, url: $scope.url}).
    then(function(response) {
      $scope.status = response.status;
      var data = response.data.data_type;
      var college_id_indices = []
      data.forEach(function(value, index, array) {
        if (value.name == "college_id") {
          college_id_indices.push(index);
        }
      });
      college_id_indices.forEach(function(value, index, array) {
        data.splice(value-index, 1);
      });
      $scope.dts = data;
    }, function(response) {
      $scope.status = response.status;
  });
});
