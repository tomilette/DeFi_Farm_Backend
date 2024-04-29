// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract piggyToken is ERC20 {
    constructor() public ERC20("Piggy Token", "PIGGY") {
        _mint(msg.sender, 1000000 * (10**18));
    }
}
