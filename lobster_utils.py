#!/usr/bin/env python3.8
import brownie
from brownie import Contract
import csv

brownie.network.connect('mainnet')
contract = Contract('0x026224a2940bfe258d0dbe947919b62fe321f042')

def get_owners():
    """
    returns (owners, count_per_address)
    """
    total_supply = contract.totalSupply()

    # hopefully faster with multicall
    with brownie.multicall:
        owners = list()
        for i in range(0, total_supply):
            owners.append(contract.ownerOf(i))
            if i % 2000 == 0:
                brownie.multicall.flush()

    # count num occurrences of each address, then sort in reverse order
    owner_addresses = set(owners)
    count_per_address = {addr: owners.count(addr) for addr in owner_addresses}
    count_per_address = dict(sorted(count_per_address.items(), key=lambda x: x[1], reverse=True))

    return (owners, count_per_address)

def get_id_map():
    """
    returns id map for lobsters
    """
    seed = contract.seed()
    if seed == 0:
        return lambda x: None
    max_tokens = contract.maxTokens()

    ids = list(range(0, max_tokens))

    for i in range(0, max_tokens - 1):
        kec = int.from_bytes(brownie.web3.keccak(brownie.web3.codec.encode_abi(('uint256', 'uint256'), (seed, i))), 'big')
        j = i + (kec % (max_tokens - i))
        (ids[i], ids[j]) = (ids[j], ids[i])

    return ids

def main():
    owners, count_per_address = get_owners()

    with open('nft_owners.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['address', 'count'])
        writer.writerows(count_per_address.items())

    print('\n'.join([f"{addr}: {count}" for addr, count in count_per_address.items()]))

if __name__ == '__main__':
    main()
