import random
import json

nums = [x for x in range(20,200)]
opts = []
for x in range(200):
    a, b = [random.choice(nums) for _ in range(2)]
    print(f'{a} + {b} = ?')
    opts.append([f'{a} + {b} = ?', a+b])

json.dump(opts, open(f'numbers.json', 'w'), indent=4)
