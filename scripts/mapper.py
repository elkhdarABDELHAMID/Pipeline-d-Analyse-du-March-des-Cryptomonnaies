#!/usr/bin/env python3
import json
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        record = json.loads(line)
    except ValueError:
        continue
    
    if isinstance(record, list):
        for item in record:
            if isinstance(item, dict):
                coin_id = item.get('id')
                current_price = item.get('current_price')
                volume = item.get('total_volume')
                
                if not coin_id or current_price is None or volume is None:
                    continue
                try:
                    price_float = float(current_price)
                    volume_float = float(volume)
                except ValueError:
                    continue

                price_squared = price_float * price_float
                print("{}\t{},{},{},{}".format(coin_id, price_float, price_squared, volume_float, 1))
    elif isinstance(record, dict):
        coin_id = record.get('id')
        current_price = record.get('current_price')
        volume = record.get('total_volume')

        if not coin_id or current_price is None or volume is None:
            continue
        try:
            price_float = float(current_price)
            volume_float = float(volume)
        except ValueError:
            continue

        price_squared = price_float * price_squared
        print("{}\t{},{},{},{}".format(coin_id, price_float, price_squared, volume_float, 1))