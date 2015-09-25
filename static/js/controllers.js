(function () {

  'use strict';

  angular.module('phdApp', [])		
  .controller('SearchLocate', ['$scope', '$log','$http', function($scope, $log, $http) {
    $scope.searchContainer="none;";
    $scope.classifyContainer="none;";
    $scope.contactContainer = "none";
    $scope.resultsSearch = "none";
    $scope.inputSearch = '';
    $scope.uploadFinish = '';

	$scope.clean=function(){
    	$scope.searchContainer="none;";
    	$scope.classifyContainer = "none;";
    	$scope.contactContainer = "none";
    	$scope.resultsSearch = "none";
    }
    $scope.search=function(){
    	$scope.searchContainer="block;";
    	$scope.classifyContainer = "none;";
    	$scope.contactContainer = "none";
    	$scope.resultsSearch = "none";
    }
    $scope.searchAction=function(){
    	//console.log($scope.inputSearch);
    	if(($scope.inputSearch != '') && ($scope.inputSearch != 'undefined'))
    	{
    	$http({
    			method: 'POST', 
    			url: '/search',
     			data: {                  
                        searchValue: $scope.inputSearch
                    }}).
		    success(function(data, status, headers, config) {
		      $scope.resultsSearch = "block;";
		      $scope.papers = data;
		      //console.log($scope.papers[0][1]);
		    }).
		    error(function(data, status, headers, config) {
		      console.log('something went wrong');
		    });	
    	}
    	else
    	{
    		alert('missing value');
    	}
    	
    }
    $scope.uploadAction = function(){
    	var f = document.getElementById('file').files[0]; //console.log(f);
	    var formData = new FormData();
	    formData.append('file', f);
         $http({method: 'POST', url: '/upload',
                data: formData,
                headers: {'Content-Type': undefined},
                transformRequest: angular.identity})
            .success(function(data, status, headers, config) {console.log(data);
                     //console.log('import success!');
                     $scope.uploadFinish = 'import success!';
              })
            .error(function(data, status, headers, config) {
            	console.log('something went wrong');
             });
    
    }
    $scope.classify= function(){
    	$scope.uploadFinish = '';
    	$scope.classifyContainer = "block;";
    	$scope.searchContainer="none;";
    	$scope.contactContainer = "none";
    	$scope.resultsSearch = "none";
    }
    $scope.contact=function(){
    	$scope.contactContainer = "block";
    	$scope.searchContainer="none;";
    	$scope.classifyContainer = "none;";
    	$scope.resultsSearch = "none";
    }

  }

  ]);

}());