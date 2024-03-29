import { assert } from '@0x/assert';
import { schemas } from '@0x/json-schemas';
import {
    AbiEncoder,
    abiUtils,
    BigNumber,
    decodeBytesAsRevertError,
    decodeThrownErrorAsRevertError,
    providerUtils,
    RevertError,
    StringRevertError,
} from '@0x/utils';
import { Web3Wrapper } from '@0x/web3-wrapper';
import {
    AbiDefinition,
    AbiType,
    CallData,
    ConstructorAbi,
    ContractAbi,
    DataItem,
    MethodAbi,
    SupportedProvider,
    TxData,
    TxDataPayable,
} from 'ethereum-types';
import * as _ from 'lodash';

import { formatABIDataItem } from './utils';

export interface AbiEncoderByFunctionSignature {
    [key: string]: AbiEncoder.Method;
}

// tslint:disable: max-classes-per-file
/**
 * @dev A promise-compatible type that exposes a `txHash` field.
 *      Not used by BaseContract, but generated contracts will return it in
 *      `awaitTransactionSuccessAsync()`.
 *      Maybe there's a better place for this.
 */
export class PromiseWithTransactionHash<T> implements Promise<T> {
    public readonly txHashPromise: Promise<string>;
    private readonly _promise: Promise<T>;
    constructor(txHashPromise: Promise<string>, promise: Promise<T>) {
        this.txHashPromise = txHashPromise;
        this._promise = promise;
    }
    // tslint:disable:promise-function-async
    // tslint:disable:async-suffix
    public then<TResult>(
        onFulfilled?: (v: T) => TResult | Promise<TResult>,
        onRejected?: (reason: any) => Promise<never>,
    ): Promise<TResult> {
        return this._promise.then<TResult>(onFulfilled, onRejected);
    }
    public catch<TResult>(onRejected?: (reason: any) => Promise<TResult>): Promise<TResult | T> {
        return this._promise.catch(onRejected);
    }
    // tslint:enable:promise-function-async
    // tslint:enable:async-suffix
    get [Symbol.toStringTag](): 'Promise' {
        return this._promise[Symbol.toStringTag];
    }
}

export class BaseContract {
    protected _abiEncoderByFunctionSignature: AbiEncoderByFunctionSignature;
    protected _web3Wrapper: Web3Wrapper;
    public abi: ContractAbi;
    public address: string;
    public contractName: string;
    public constructorArgs: any[] = [];
    protected static _formatABIDataItemList(
        abis: DataItem[],
        values: any[],
        formatter: (type: string, value: any) => any,
    ): any {
        return _.map(values, (value: any, i: number) => formatABIDataItem(abis[i], value, formatter));
    }
    protected static _lowercaseAddress(type: string, value: string): string {
        return type === 'address' ? value.toLowerCase() : value;
    }
    protected static _bigNumberToString(_type: string, value: any): any {
        return BigNumber.isBigNumber(value) ? value.toString() : value;
    }
    protected static _lookupConstructorAbi(abi: ContractAbi): ConstructorAbi {
        const constructorAbiIfExists = _.find(
            abi,
            (abiDefinition: AbiDefinition) => abiDefinition.type === AbiType.Constructor,
            // tslint:disable-next-line:no-unnecessary-type-assertion
        ) as ConstructorAbi | undefined;
        if (constructorAbiIfExists !== undefined) {
            return constructorAbiIfExists;
        } else {
            // If the constructor is not explicitly defined, it won't be included in the ABI. It is
            // still callable however, so we construct what the ABI would look like were it to exist.
            const defaultConstructorAbi: ConstructorAbi = {
                type: AbiType.Constructor,
                stateMutability: 'nonpayable',
                payable: false,
                inputs: [],
            };
            return defaultConstructorAbi;
        }
    }
    protected static async _applyDefaultsToTxDataAsync<T extends Partial<TxData | TxDataPayable>>(
        txData: T,
        txDefaults: Partial<TxData> | undefined,
        estimateGasAsync?: (txData: T) => Promise<number>,
    ): Promise<TxData> {
        // Gas amount sourced with the following priorities:
        // 1. Optional param passed in to public method call
        // 2. Global config passed in at library instantiation
        // 3. Gas estimate calculation + safety margin
        const removeUndefinedProperties = _.pickBy.bind(_);
        const finalTxDefaults: Partial<TxData> = txDefaults || {};
        const txDataWithDefaults = {
            ...removeUndefinedProperties(finalTxDefaults),
            ...removeUndefinedProperties(txData),
        };
        if (txDataWithDefaults.gas === undefined && estimateGasAsync !== undefined) {
            txDataWithDefaults.gas = await estimateGasAsync(txDataWithDefaults);
        }
        return txDataWithDefaults;
    }
    protected static _throwIfCallResultIsRevertError(rawCallResult: string): void {
        // Try to decode the call result as a revert error.
        let revert: RevertError;
        try {
            revert = decodeBytesAsRevertError(rawCallResult);
        } catch (err) {
            // Can't decode it as a revert error, so assume it didn't revert.
            return;
        }
        throw revert;
    }
    protected static _throwIfThrownErrorIsRevertError(error: Error): void {
        // Try to decode a thrown error.
        let revertError: RevertError;
        try {
            revertError = decodeThrownErrorAsRevertError(error);
            // Re-cast StringRevertErrors as plain Errors for backwards-compatibility.
            if (revertError instanceof StringRevertError) {
                throw new Error(revertError.values.message as string);
            }
        } catch (err) {
            // Can't decode it.
            return;
        }
        throw revertError;
    }
    // Throws if the given arguments cannot be safely/correctly encoded based on
    // the given inputAbi. An argument may not be considered safely encodeable
    // if it overflows the corresponding Solidity type, there is a bug in the
    // encoder, or the encoder performs unsafe type coercion.
    public static strictArgumentEncodingCheck(inputAbi: DataItem[], args: any[]): string {
        const abiEncoder = AbiEncoder.create(inputAbi);
        const params = abiUtils.parseEthersParams(inputAbi);
        const rawEncoded = abiEncoder.encode(args);
        const rawDecoded = abiEncoder.decodeAsArray(rawEncoded);
        for (let i = 0; i < rawDecoded.length; i++) {
            const original = args[i];
            const decoded = rawDecoded[i];
            if (!abiUtils.isAbiDataEqual(params.names[i], params.types[i], original, decoded)) {
                throw new Error(
                    `Cannot safely encode argument: ${params.names[i]} (${original}) of type ${
                        params.types[i]
                    }. (Possible type overflow or other encoding error)`,
                );
            }
        }
        return rawEncoded;
    }
    protected _lookupAbiEncoder(functionSignature: string): AbiEncoder.Method {
        const abiEncoder = this._abiEncoderByFunctionSignature[functionSignature];
        if (abiEncoder === undefined) {
            throw new Error(`Failed to lookup method with function signature '${functionSignature}'`);
        }
        return abiEncoder;
    }
    protected _lookupAbi(functionSignature: string): MethodAbi {
        const methodAbi = _.find(this.abi, (abiDefinition: AbiDefinition) => {
            if (abiDefinition.type !== AbiType.Function) {
                return false;
            }
            // tslint:disable-next-line:no-unnecessary-type-assertion
            const abiFunctionSignature = new AbiEncoder.Method(abiDefinition as MethodAbi).getSignature();
            if (abiFunctionSignature === functionSignature) {
                return true;
            }
            return false;
        }) as MethodAbi;
        return methodAbi;
    }
    protected _strictEncodeArguments(functionSignature: string, functionArguments: any): string {
        const abiEncoder = this._lookupAbiEncoder(functionSignature);
        const inputAbi = abiEncoder.getDataItem().components;
        if (inputAbi === undefined) {
            throw new Error(`Undefined Method Input ABI`);
        }
        const abiEncodedArguments = abiEncoder.encode(functionArguments);
        return abiEncodedArguments;
    }
    constructor(
        contractName: string,
        abi: ContractAbi,
        address: string,
        supportedProvider: SupportedProvider,
        callAndTxnDefaults?: Partial<CallData>,
    ) {
        assert.isString('contractName', contractName);
        assert.isETHAddressHex('address', address);
        const provider = providerUtils.standardizeOrThrow(supportedProvider);
        if (callAndTxnDefaults !== undefined) {
            assert.doesConformToSchema('callAndTxnDefaults', callAndTxnDefaults, schemas.callDataSchema, [
                schemas.addressSchema,
                schemas.numberSchema,
                schemas.jsNumber,
            ]);
        }
        this.contractName = contractName;
        this._web3Wrapper = new Web3Wrapper(provider, callAndTxnDefaults);
        this.abi = abi;
        this.address = address;
        const methodAbis = this.abi.filter(
            (abiDefinition: AbiDefinition) => abiDefinition.type === AbiType.Function,
        ) as MethodAbi[];
        this._abiEncoderByFunctionSignature = {};
        _.each(methodAbis, methodAbi => {
            const abiEncoder = new AbiEncoder.Method(methodAbi);
            const functionSignature = abiEncoder.getSignature();
            this._abiEncoderByFunctionSignature[functionSignature] = abiEncoder;
        });
    }
}
