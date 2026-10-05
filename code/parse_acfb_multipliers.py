#!/usr/bin/env python3
"""Parse state and U.S. forestry value-added multipliers from the Arkansas Center for
Forest Business (2023) report text. Input: acfb.txt from `pdftotext -layout acfb2023.pdf acfb.txt`
(report: https://www.uamont.edu/academics/CFANR/forestbusiness/USForestryEconomicContributionbyState20230109.pdf).
Output: out/acfb2023_state_va_multipliers.csv (direct, multiplier and total GDP; total/direct ratio)."""
import re, csv
L = open('acfb.txt').read().split('\n')
rows = []
for i, l in enumerate(L):
    if 'Forestry Direct Contribution' in l:
        name = L[i-1].strip(); nums = []; j = i + 1
        while len(nums) < 3 and j < i + 20:
            m = re.findall(r'\$([\d,]+)', L[j])
            if len(m) == 2: nums.append(m[1])
            j += 1
        if len(nums) == 3:
            d, mu, t = (float(x.replace(',', '')) for x in nums)
            rows.append((name, d, mu, t, t / d))
with open('out/acfb2023_state_va_multipliers.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['area', 'direct_va', 'multiplier_va', 'total_va', 'va_multiplier']); w.writerows(rows)
print(len(rows), 'rows')
