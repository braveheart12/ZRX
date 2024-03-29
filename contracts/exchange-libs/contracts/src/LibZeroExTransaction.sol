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

pragma solidity ^0.5.9;
pragma experimental ABIEncoderV2;

import "./LibEIP712ExchangeDomain.sol";


contract LibZeroExTransaction is
    LibEIP712ExchangeDomain
{
    // Hash for the EIP712 0x transaction schema
    // keccak256(abi.encodePacked(
    //    "ZeroExTransaction(",
    //    "uint256 salt,",
    //    "uint256 expirationTimeSeconds,"
    //    "address signerAddress,",
    //    "bytes data",
    //    ")"
    // ));
    bytes32 constant public EIP712_ZEROEX_TRANSACTION_SCHEMA_HASH = 0x6b4c70d217b44d0ff0d3bf7aeb18eb8604c5cd06f615a4b497aeefa4f01d2775;

    struct ZeroExTransaction {
        uint256 salt;                   // Arbitrary number to ensure uniqueness of transaction hash.
        uint256 expirationTimeSeconds;  // Timestamp in seconds at which transaction expires.
        address signerAddress;          // Address of transaction signer.
        bytes data;                     // AbiV2 encoded calldata.
    }

    /// @dev Calculates the EIP712 hash of a 0x transaction using the domain separator of the Exchange contract.
    /// @param transaction 0x transaction containing salt, signerAddress, and data.
    /// @return EIP712 hash of the transaction with the domain separator of this contract.
    function getTransactionHash(ZeroExTransaction memory transaction)
        public
        view
        returns (bytes32 transactionHash)
    {
        // Hash the transaction with the domain separator of the Exchange contract.
        transactionHash = _hashEIP712ExchangeMessage(_hashZeroExTransaction(transaction));
        return transactionHash;
    }

    /// @dev Calculates EIP712 hash of the 0x transaction with no domain separator.
    /// @param transaction 0x transaction containing salt, signerAddress, and data.
    /// @return EIP712 hash of the transaction with no domain separator.
    function _hashZeroExTransaction(ZeroExTransaction memory transaction)
        internal
        pure
        returns (bytes32 result)
    {
        bytes32 schemaHash = EIP712_ZEROEX_TRANSACTION_SCHEMA_HASH;
        bytes memory data = transaction.data;
        uint256 salt = transaction.salt;
        uint256 expirationTimeSeconds = transaction.expirationTimeSeconds;
        address signerAddress = transaction.signerAddress;

        // Assembly for more efficiently computing:
        // keccak256(abi.encodePacked(
        //     EIP712_ZEROEX_TRANSACTION_SCHEMA_HASH,
        //     transaction.salt,
        //     transaction.expirationTimeSeconds,
        //     uint256(transaction.signerAddress),
        //     keccak256(transaction.data)
        // ));

        assembly {
            // Compute hash of data
            let dataHash := keccak256(add(data, 32), mload(data))

            // Load free memory pointer
            let memPtr := mload(64)

            mstore(memPtr, schemaHash)                                                               // hash of schema
            mstore(add(memPtr, 32), salt)                                                            // salt
            mstore(add(memPtr, 64), expirationTimeSeconds)                                           // expirationTimeSeconds
            mstore(add(memPtr, 96), and(signerAddress, 0xffffffffffffffffffffffffffffffffffffffff))  // signerAddress
            mstore(add(memPtr, 128), dataHash)                                                       // hash of data

            // Compute hash
            result := keccak256(memPtr, 160)
        }
        return result;
    }
}
