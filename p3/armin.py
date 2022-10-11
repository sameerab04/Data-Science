from collections import defaultdict
from pandas import Series, DataFrame
import itertools as it
import pandas as pd
import math
import csv
import sys
import argparse
import collections
import glob
import os
import re
import requests
import string
import sys

class Armin():

    def check_support(self, dict, item, num_items):
        support = 0
        if num_items == 1:
            for i in dict:
                if item in dict[i]:
                    support += 1
        else:
            for i in dict:
                both = True
                for j in item:
                    both = both and (j in dict[i])
                if both:
                    support += 1
        return support

    def combine(self,i1, i2, num_items):
        if(num_items == 1):
            return(i1,i2)
        else:
            comb = []
            for item in i1:
                if item not in comb:
                    comb.append(item)
            for item in i2:
                if item not in comb:
                    comb.append(item)
            comb.sort()
            return tuple(comb)

    def apriori(self, input_filename, output_filename, min_support_percentage, min_confidence):
        """
        Implement the Apriori algorithm, and write the result to an output file
        PARAMS
        ------
        input_filename: String, the name of the input file
        output_filename: String, the name of the output file
        min_support_percentage: float, minimum support percentage for an itemset
        min_confidence: float, minimum confidence for an association rule to be significant
        """
        dict = {}
        valid_sets = {}
        confidence = {}
        candidateSets = []
        num_items = 0
        num_transactions = 0
        with open(input_filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter= ',' )
            for row in csv_reader:
                dict[row[0]] = row[1:]
                num_transactions += 1
        for i in dict:
            for j in dict[i]:
                if j not in candidateSets:
                    candidateSets.append(j)
        num_items = len(candidateSets)
        candidateSets.sort()
        valid_sets[1] = {}

        for i in range(num_items):
            support = self.check_support(dict, candidateSets[i], 1)
            if support / num_transactions >= min_support_percentage:
                valid_sets[1][candidateSets[i]] = support

        for i in range(num_items):
            if i <= 1 : continue
            valid_sets[i] = {}
            j = 0
            for v1 in valid_sets[i-1]:
                k = 0
                for v2 in valid_sets[i-1]:
                    if k <= j:
                        k += 1
                        continue
                    prev = self.combine(v1, v2, i-1)
                    if len(prev) != i : continue
                    support = self.check_support(dict, prev, i)
                    if support / num_transactions >= min_support_percentage:
                        valid_sets[i][prev] = support
                    k += 1
                j += 1

        for i in range(num_items):
            if i <= 1: continue
            for v in valid_sets[i]:
                for comb in it.permutations(v):
                    for j in range(1, len(comb), 1):
                        if (j == 1):
                            s1 = comb[0]
                            s2 = comb[j:]
                        else:
                            s1 = tuple(comb[:j])
                            s2 = tuple(comb[j:])

                        if s1 not in valid_sets[j] : continue
                        if valid_sets[i][v] / valid_sets[j][s1] >= min_confidence:
                            if len(s2) == 1:
                                s2 = s2[0]
                            else:
                                s2 = tuple(sorted(s2))
                            confidence[(v,s1,s2)] = valid_sets[i][v] / valid_sets[j][s1]
        with open(output_filename, 'w', newline = '') as csv_out:
            writer = csv.writer(csv_out, delimiter = ',')

            for i in range(num_items):
                if i == 0 : continue
                for j in valid_sets[i]:
                    output = []
                    output.append("S")
                    output.append("{0:.4f}".format(valid_sets[i][j] / num_transactions))
                    if i == 1:
                        output.append(str(j))
                    else:
                        for k in range(len(j)):
                            output.append(str(j[k]))
                    writer.writerow(output)

            for i in confidence:
                output = []
                output.append("R")
                output.append("{0:.4f}".format(valid_sets[len(i[0])][i[0]] / num_transactions))
                output.append("{0:.4f}".format(confidence[i]))

                if len(i[1]) == 1:
                    output.append(i[1])
                else:
                    for j in range(len(i[1])):
                        output.append(str(i[1][j]))
                output.append("\'=>\'")
                if len(i[2]) == 1:
                    output.append(i[2])
                else:
                    for j in range(len(i[2])):
                        output.append(str(i[2][j]))
                writer.writerow(output)







if __name__ == "__main__":
    armin = Armin()
    armin.apriori('input.csv', 'output.sup=0.5,conf=0.7.csv', 0.5, 0.7)
    armin.apriori('input.csv', 'output.sup=0.5,conf=0.8.csv', 0.5, 0.8)
    armin.apriori('input.csv', 'output.sup=0.6,conf=0.8.csv', 0.6, 0.8)
