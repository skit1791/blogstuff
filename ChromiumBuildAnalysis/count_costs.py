"""
Summarize the compilation costs of a particular set of source files by scanning
a .csv report generated by analyze_chrome.py.

Sample usage:
1) Find the cost to compile everything.
  >python3 count_costs.py ChromeBuildVisualizer\windows-default.csv
  30137 files took 21.453 hours to build. 11.856 M lines, 3611.6 M dependent lines

2) Find the cost to compile all generated source files.
  >python3 count_costs.py ChromeBuildVisualizer\windows-default.csv gen\*
  5712 files took 4.093 hours to build. 3.069 M lines, 842.4 M dependent lines

3) Find the cost to compile all checked-in source and verify that the numbers add up.
  >python3 count_costs.py ChromeBuildVisualizer\windows-default.csv ..\..\*
  24425 files took 17.360 hours to build. 8.786 M lines, 2769.2 M dependent lines

The status is printed to stderr. If --verbose is specified then a reduced .csv file
is printed.
"""

from __future__ import print_function

import argparse
import fnmatch
import sys

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('csv_file', nargs=1)
  parser.add_argument('wildcard', nargs='?', default='*')
  parser.add_argument('--verbose', action='store_true')

  args = parser.parse_args()

  with open(args.csv_file[0], 'r') as f:
    lines = f.readlines()

  count = 0
  sum_t_ms = 0
  sum_num_dependent_lines = 0
  sum_num_lines = 0
  sum_num_deps = 0

  headers = 'name,t_ms,num_dependent_lines,num_lines,num_deps'
  assert(lines[0].strip() == headers)
  if args.verbose:
    print(lines[0].strip())
  times_s = []
  for line in lines[1:]:
    parts = line.split(',')
    if fnmatch.fnmatch(parts[0], args.wildcard):
      count += 1
      t_ms, num_dependent_lines, num_lines, num_deps = map(int, parts[1:])
      sum_num_dependent_lines += num_dependent_lines
      sum_num_lines += num_lines
      sum_num_deps += num_deps
      times_s.append(t_ms / 1e3)
      sum_t_ms += t_ms
      if args.verbose:
        print(line.strip())

  print('%d files took %1.3f hrs to build. %1.3f M lines, %1.1f M dependent lines, %1.3f M dependencies' % (count, sum_t_ms / 1e3 / 3600, sum_num_lines / 1e6, sum_num_dependent_lines / 1e6, sum_num_deps / 1e6), file=sys.stderr)
  if count > 0:
    print('Averages: %d lines, %1.2f seconds, %1.1f K dependent lines per file compiled' %(sum_num_lines / count, sum_t_ms / 1e3 / count, sum_num_dependent_lines / 1e3 / count))
    times_s.sort()
    print('min: %1.1f, 50%%ile: %1.1f, 90%%ile: %1.1f, 99%%ile: %1.1f, max: %1.1f (seconds)' % (times_s[0], times_s[len(times_s) * 50 / 100], times_s[len(times_s) * 90 / 100], times_s[len(times_s) * 99 / 100], times_s[-1]))


if __name__ == '__main__':
    sys.exit(main())
