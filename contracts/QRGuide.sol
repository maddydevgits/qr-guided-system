// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract QRGuide {
  
  string[] _emails;
  string[] _passwords;

  uint[] _productids;
  string[] _filepaths;
  string[] _productcosts;
  string[] _productnames;
  string[] _productlocations;

  uint productid;

  constructor() {
    productid=0;
  }

  mapping(string=>bool) _users;

  function signup(string memory email,string memory password) public {

    require(!_users[email]);
    _emails.push(email);
    _passwords.push(password);
    _users[email]=true;
  }

  function viewUsers() public view returns(string[] memory,string[] memory){
    return (_emails,_passwords);
  }

  function addProduct(string memory filepath,string memory productcost,string memory productname,string memory productlocation) public {
    productid+=1;
    _productids.push(productid);
    _filepaths.push(filepath);
    _productcosts.push(productcost);
    _productlocations.push(productlocation);
    _productnames.push(productname);
  }

  function viewProducts() public view returns(string[] memory,string[] memory,string[] memory,string[] memory,uint[] memory){
    return (_filepaths,_productcosts,_productlocations,_productnames,_productids);
  }
}
