/*

  Copyright 2018 ZeroEx Intl.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

*/

// solhint-disable
pragma solidity ^0.5.9;
pragma experimental ABIEncoderV2;


// @dev Interface of the asset proxy's assetData.
// The asset proxies take an ABI encoded `bytes assetData` as argument.
// This argument is ABI encoded as one of the methods of this interface.
interface IAssetData {

    function ERC20Token(address tokenAddress)
        external;
    
    function ERC721Token(
        address tokenAddress,
        uint256 tokenId
    )
        external;

    function ERC1155Assets(
        address tokenAddress,
        uint256[] calldata tokenIds,
        uint256[] calldata tokenValues,
        bytes calldata callbackData
    )
        external;

    function MultiAsset(
        uint256[] calldata amounts,
        bytes[] calldata nestedAssetData
    )
        external;

    function StaticCall(
        address callTarget,
        bytes calldata staticCallData,
        bytes32 callResultHash
    )
        external;
}
