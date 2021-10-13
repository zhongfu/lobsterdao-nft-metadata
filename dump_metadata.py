#!/usr/bin/env python3
import csv
import json
from lobster_utils import get_owners, get_id_map

def dump():
    TOTAL_SUPPLY = 6751
    traits = dict()
    metadata = dict()

    for i in range(0, TOTAL_SUPPLY):
        with open(f'metadata/{i}', 'r') as f:
            data = json.load(f)
            attrs = data.pop('attributes')
            attr_d = dict()
            for attr in attrs:
                attr_d[attr['trait_type'].lower().replace(' ', '_')] = attr['value']
            data['attributes'] = attr_d
            metadata[i] = data

        for trait_type, val in data['attributes'].items():
            traits.setdefault(trait_type, dict()).setdefault(val, set()).add(i)

    traits = {typ: dict(sorted(d.items(), key=lambda t: len(t[1]), reverse=True)) for typ, d in traits.items()}

    trait_counts = dict()
    for trait_type, d1 in traits.items():
        counts = dict()
        total = TOTAL_SUPPLY
        for val, ids in d1.items():
            counts[val] = len(ids)
            total -= len(ids)
        counts[None] = total
        trait_counts[trait_type] = dict(sorted(counts.items(), key=lambda t: t[1], reverse=True))

    # dump owners here
    # would need to map nft id -> ipfs id
    owners, _ = get_owners()
    id_map = get_id_map()
    rev_id_map = [-1] * TOTAL_SUPPLY
    for idx, real_id in enumerate(id_map):
        rev_id_map[real_id] = idx

    with open(f'metadata.csv', 'w') as f:
        headers = ['id', 'nft_id', 'name', 'owner', 'dna', 'image']
        trait_names = list(traits.keys())
        headers.extend(trait_names)
        headers.append('n_traits')
        headers.extend(f"{trait_name}_rarity" for trait_name in trait_names)

        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for idx, meta in metadata.items():
            row = {
                'id': idx,
                'nft_id': rev_id_map[idx],
                'name': meta['name'],
                'owner': owners[rev_id_map[idx]] if rev_id_map[idx] < len(owners) else 'None',
                'dna': meta['dna'],
                'image': meta['image'],
            }
            n_traits = 0
            rarity_cols = dict()
            for trait_name in trait_names:
                val = meta['attributes'].get(trait_name)
                if val is not None:
                    n_traits += 1
                row[trait_name] = val or 'None'
                rarity_cols[f'{trait_name}_rarity'] = trait_counts[trait_name][val] / TOTAL_SUPPLY
            row['n_traits'] = n_traits
            row.update(rarity_cols)
            writer.writerow(row)

    with open(f'rarities.csv', 'w') as f:
        headers = ['trait', 'value', 'count', 'rarity']
        writer = csv.DictWriter(f, headers)
        writer.writeheader()
        for trait_name in trait_names:
            for val, cnt in trait_counts[trait_name].items():
                if cnt == 0:
                    continue
                writer.writerow({
                    'trait': trait_name,
                    'value': val or 'None',
                    'count': cnt,
                    'rarity': cnt / TOTAL_SUPPLY
                })

if __name__ == '__main__':
    dump()
