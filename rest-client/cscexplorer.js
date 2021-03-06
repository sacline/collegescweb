/**
 * cscexplorer.js
 * Copyright (C) <2017>  <S. Cline>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/** Angular module containing code for the entire web app. */
var collegeScorecardExplorer = angular.module('collegeScorecardExplorer', []);

/*
 * Factory that produces an object with data on the visibility of the form
 * and results pages.
 */
collegeScorecardExplorer.factory('toggleViewFactory', function() {
  var service = {};
  var visibility = {form : true, results : false, validResults: false} //default

  /*
   * Function returning the visibility object to the controller.
   * @return {visibility} Object with boolean properties for form and results
   *     visibility.
   */
  service.getVisibility = function() {
    return visibility;
  }

  /*
   * Function that toggles the visibility of the form and results when called.
   * @param {string} view The view to be modified.
   * @param {boolean} show True if the view should be visible, false if
   *     it should not be visible.
   */
  service.toggleView = function(view, show) {
    visibility[view] = show;
  }

  /**Function that hides all views.*/
  service.hideAllViews = function() {
    Object.keys(visibility).forEach(function(key, index, arr) {
      visibility[key] = false;
    });
  }

  return service;
});

/*
 * Controller containing data for which views are currently visisble.
 */
collegeScorecardExplorer.controller('ViewController',
    function ViewController($scope, toggleViewFactory) {

  $scope.visibility = toggleViewFactory.getVisibility();

  //jQuery call to display intro modal upon loading the page.
  $scope.showIntroOnLoad = function(){
    $(window).on('load', function(){
      $('#intromodal').modal('show');
    });
  }

  $scope.showIntroOnLoad();
});

/*
 * Factory that produces and caches data that is used across multiple
 * controllers. This data is required and is independent of queries made by
 * the user.
 */
collegeScorecardExplorer.factory('commonScorecardDataFactory', function($http) {
  var service = {};
  var baseUrl = 'http://www.clinesa.com/cscvis/api/v2.0/data';
  var categoryData = {};
  var collegeLocationData = {};

  /** Calls each of the functions needed to load the data. */
  var loadAllData = function() {
    loadCategoryData();
    loadCollegeLocationData();
  }

  /*
   * Makes the HTTP request for the category data and stores the response data.
   */
  var loadCategoryData = function() {
    var categoryUrl = baseUrl + '/data_types';
    $http({method: 'GET', url: categoryUrl}).then(
      function(response) {
        categoryData.data = response.data.data_type;
        var college_id_indices = [];
        categoryData.data.forEach(function(value, index, array) {
          if (value.name == 'college_id') {
            college_id_indices.push(index);
          }
        });
        college_id_indices.forEach(function(value, index, array) {
          categoryData.data.splice(value-index, 1);
        });
      });
  }

  /** Loads college data that will be displayed with all search results. */
  var loadCollegeLocationData = function() {
    var collegeNameUrlAddition = '/data_types/INSTNM/global';
    var collegeNamePropertyName = 'name';
    var collegeCityUrlAddition = '/data_types/CITY/global';
    var collegeCityPropertyName = 'city';
    var collegeStateUrlAddition = '/data_types/STABBR/global';
    var collegeStatePropertyName = 'state';
    loadCollegeData(collegeNameUrlAddition, collegeNamePropertyName);
    loadCollegeData(collegeCityUrlAddition, collegeCityPropertyName);
    loadCollegeData(collegeStateUrlAddition, collegeStatePropertyName);
  }

  /*
   * Makes the HTTP request for a type of general college data.
   * @param {string} urlAddition String containing the trailing end of the url
   *     to call to get data type info.
   * @param {string} propertyName String name of the property that will contain
   *     the queried data.
   */
  var loadCollegeData = function(urlAddition, propertyName) {
    var collegeDataUrl = baseUrl + urlAddition;
    $http({method: 'GET', url: collegeDataUrl}).then(
      function(response) {
        var collegeData = response.data.global;
        collegeData.forEach(function(value, index, array) {
          if (collegeLocationData[value.college_id] == undefined) {
            collegeLocationData[value.college_id] = {};
          }
          collegeLocationData[value.college_id][propertyName] = value.value;
        });
      });
  }

  /** Function to be called by the controller to get the category data. */
  service.getCategoryData = function() {
    return categoryData;
  }

  /** Function to be called by the controller to get the location data. */
  service.getCollegeLocationData = function() {
    return collegeLocationData;
  }

  loadAllData();
  return service;
});


/** Factory that maintains the criteria model for searches. */
collegeScorecardExplorer.factory('criteriaListFactory', function() {
  var service = {};
  var criteriaList = [];

  /**
   *  Criteria object containing data used throughout the app.
   *  @param {integer} index Index of the criteria in the list.
   */
  var Criteria = function(index) {
    this.index = index;
    this.selectedCategory = null;
    this.selectedCategoryType = null; //default value
    this.selectedCategoryIndex = null;
    this.allowableComparisons = null;
    this.selectedComparison = null;
    this.inputValue = null;
  };

  /*
   * Function called by the controller to add a new criteria object to the list.
   */
  service.addCriteria = function() {
    var newCriteria = new Criteria(criteriaList.length);
    criteriaList.push(newCriteria);
  }

  /*
   * Function called by the controller to remove a specific criteria object
   * from the list.
   * @param {integer} index Index of the criteria to remove.
   */
  service.removeCriteria = function(index) {
    criteriaList.splice(index, 1);
    //update the indices for each row
    criteriaList.forEach(function(item, index, array) {
      item.index = index
    });
  }

  /*
   * Returns the criteria list within an object to support data binding between
   * the model and the view.
   * @return {data: array} criteriaList Object containing the list of criteria.
   */
  service.getCriteriaList = function() {
    return {data : criteriaList};
  }

  /*
   * Setter function for the category type of the criteria from the model.
   * @param {integer} index Index of the criteria.
   * @param {string} type Type of category selected from
   *     {'TEXT', 'INTEGER', 'REAL'}.
   */
  service.setCriteriaSelectedCategoryType = function(index, type) {
    criteriaList[index].selectedCategoryType = type;
  }

  return service;
});

/** Factory that produces search result data. */
collegeScorecardExplorer.factory('searchResultFactory', function($http, $q,
    commonScorecardDataFactory, toggleViewFactory) {
  var service = {};
  var results = {data: []};
  var hostAddress = 'http://www.clinesa.com';
  var dataYear = '2014';

  var categoryData = commonScorecardDataFactory.getCategoryData();

  /*
   * Generate the url for the API call based on whether the data type is
   * year-specific or not.
   * @param {string} dataTypeName Name of the data type (criteria).
   * @param {string} dataTypeIndex Index of the data type in the data type
   *     list.
   */
  var generateDataTypeUrl = function(dataTypeName, dataTypeIndex) {
    if (categoryData.data[dataTypeIndex].scope == 'year') {
      var url = hostAddress + '/cscvis/api/v2.0/data/data_types/' + 
        dataTypeName + '/year/' + dataYear;
    }
    else {
      var url = hostAddress + '/cscvis/api/v2.0/data/data_types/' +
        dataTypeName + '/global';
    }
    return url;
  };

/*
 * Make the HTTP call and return the result.
 * @param {string} url API URL to call.
 * @return {response.data} JSON data from the API call.
 */
  var requestData = function(url) {
    return $http({method: 'GET', url: url}).then(
      //Success response
      function(response) {
        return response.data;
      },
      //Error response
      function(response) {
        return 'Error';
      });
  }

  /*
   * Adds retrieved data to the results map if it satisfies the criteria
   * specified by the user.
   * @param {Criteria} row Criteria object containing the user specified search
   *     parameters.
   * @param {Map} resultsMap Map containing results satisfying the criteria.
   * @param {data} data Data to compare against the criteria.
   */
  var addResults = function(row, resultsMap, data) {
    var dataKey = Object.keys(data)[0];
    data[dataKey].forEach(function(dataObject, dataIndex, dataArray) {
      var id = dataObject.college_id.toString();
      if (resultsMap.get(id) == undefined) {
        resultsMap.set(id, []);
      }

      //custom defineProperty function
      function _defineProperty(obj, key, value) {
        if (key in obj) {
          Object.defineProperty(obj, key, {
            value : value,
            enumerable : true,
            configurable: true,
            writable: true
          });
        }
        else {
          obj[key] = value;
        }
        return obj;
      }

      var category = row.selectedCategory;
      switch (row.selectedComparison) {
        case 'Greater than':
          if (dataObject.value > row.inputValue) {
            resultsMap.get(id).push(_defineProperty({}, category, dataObject.value));
          }
          break;
        case 'Less than':
          if (dataObject.value < row.inputValue) {
            resultsMap.get(id).push(_defineProperty({}, category, dataObject.value));
          }
          break;
        case 'Equal to':
          if (dataObject.value ==  row.inputValue) {
            resultsMap.get(id).push(_defineProperty({}, category, dataObject.value));
          }
          break;
      }
    });
  }

  /*
   * Main search function called by the controller. Calls functions to get data
   * and store it in the search results object.
   * @param [Criteria] criteriaRows List of criteria from the form controller.
   */
  service.search = function(criteriaRows) {
    results.data = [];
    var validResultMap = new Map();
    var promises = [];
    criteriaRows.forEach(function(rowItem, rowIndex, rowArray) {
      if (rowItem.selectedCategory == undefined) {
        return;
      }
      var uri = generateDataTypeUrl(
        rowItem.selectedCategory, rowItem.selectedCategoryIndex);
      promises.push(requestData(uri).then(function(apiData) {
        addResults(rowItem, validResultMap, apiData);
      }));
    });
    $q.all(promises).then(function() {
      validResultMap.forEach(function(value, key, map) {
        if (value.length == criteriaRows.length) {
          var resultsObj = {};
          resultsObj.id = key;
          Object.keys(value).forEach(function(val, k, map) {
            var category = Object.keys(value[k])[0];
            var categoryValue = value[k][category];
            resultsObj[category] = categoryValue;
          });
          results.data.push(resultsObj);
        }
      });
      //let view know there are no results only after attempting to add results
      if (results.data.length == 0) {
        toggleViewFactory.toggleView('validResults', false);
      }
      else {
        toggleViewFactory.toggleView('validResults', true);
      }
      toggleViewFactory.toggleView('results', true);
    });
  }

  /*
   * Returns search results object to the controller for display in the view.
   * @return {data} results Data object containing an array of objects with
   *     a college id and category data that satisfy the search criteria.
   */
  service.getSearchResults = function() {
    return results;
  }

  return service;
});

/** Controller that handles the criteria form view. */
collegeScorecardExplorer.controller('CriteriaFormController',
    function CriteriaFormController($scope, $http, toggleViewFactory,
        searchResultFactory, criteriaListFactory, commonScorecardDataFactory) {

  $scope.categories = commonScorecardDataFactory.getCategoryData();

  $scope.criteriaList = criteriaListFactory.getCriteriaList().data;

  /*
   * Modifies the criteria model based on user selections on the view.
   * @param {integer} rowIndex Index of row being modified.
   * @param {string} categoryName Name of the category in the criteria.
   */
  $scope.setRowCategoryInfo = function(rowIndex, categoryName) {
    var row = $scope.criteriaList[rowIndex];
    var categoryIndex = -1;
    for (var i = 0; i < $scope.categories.data.length; i++) {
      if ($scope.categories.data[i].name == categoryName) {
        categoryIndex = i;
      }
    }

    //ensure the text input is reset upon changing criteria
    row.inputValue = null;
    row.selectedCategoryType = null;

    row.selectedCategoryIndex = categoryIndex;
    row.selectedCategoryType = $scope.categories.data[categoryIndex].type;
      if (row.selectedCategoryType == 'TEXT') {
        row.allowableComparisons = ['Equal to'];
      }
      else if (row.selectedCategoryType == 'INTEGER') {
        row.allowableComparisons = ['Equal to', 'Greater than', 'Less than'];
      }
      else if (row.selectedCategoryType == 'REAL') {
        row.allowableComparisons = ['Equal to', 'Greater than', 'Less than'];
    }
  }

  /** Adds a new criteria to the end of the criteria list model. */
  $scope.addRow = function() {
    criteriaListFactory.addCriteria();
  }

  /*
   * Removes a criteria (row) at the specified index.
   * @param {rowIndex} Index of the row being removed.
   */
  $scope.removeRow = function(rowIndex) {
    criteriaListFactory.removeCriteria(rowIndex);
  }

  /*
   * Submits the form by toggling the view from the form to the results and
   * calling the search on the list of criteria.
   */
  $scope.submitForm = function() {
    toggleViewFactory.toggleView('form', false);
    searchResultFactory.search($scope.criteriaList);
  }

  /*
   * Creates an initial criteria to be present when the site loads.
   * This is to be used when showing a demo of the site.
  */
  var setInitialSearchCriteria = function() {
    if ($scope.categories.data == undefined) {
        window.setTimeout(setInitialSearchCriteria, 50);
    }
    else {
      $scope.addRow();
      $scope.criteriaList[0].selectedCategory = "ADM_RATE";
      $scope.setRowCategoryInfo(0, "ADM_RATE");
      $scope.criteriaList[0].selectedComparison = "Less than";
      $scope.criteriaList[0].inputValue = 0.1;
    }
  }

  setInitialSearchCriteria();

});

/** Controller for displaying the search results model in the results view. */
collegeScorecardExplorer.controller('ResultViewController',
    function ResultViewController($scope, searchResultFactory,
        toggleViewFactory, criteriaListFactory, commonScorecardDataFactory) {

  $scope.criteriaList = criteriaListFactory.getCriteriaList().data;
  $scope.locationData = commonScorecardDataFactory.getCollegeLocationData();

  $scope.results = searchResultFactory.getSearchResults();

  /** Toggles the view from the results back to the search form. */
  $scope.returnToSearch = function() {
    toggleViewFactory.hideAllViews();
    toggleViewFactory.toggleView('form', true);
  }
});
