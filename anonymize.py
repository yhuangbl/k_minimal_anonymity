#!/usr/bin/python2
import sys
import csv
import time


def read_CSV(datafile):
    data_set = []
    with open(datafile, 'r') as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            row[0] = int(row[0])
            data_set.append(row)
    f.close()
    return data_set

def write_CSV(datafile, input_data):
    with open(datafile, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(input_data)
    f.close()


class DataSet(object):
    def __init__(self, datafile, number):
        self.data_stirng = datafile
        self.data_set = read_CSV(datafile)
        self.factor = number  # create a 5-anonymity set
        self.anonymity_set = None

    def get_result(self):
        return self.anonymity_set

    def calculate_change(self, d=None, a=None):
        change = 0
        if d is None:
            d = self.data_set
        if a is None:
            a = self.anonymity_set
        if len(d) == len(a):
            for i in xrange(len(d)):
                change = change + abs(d[i][0] - a[i][0])
            return change
        else:
            print "calculate change error"
            return -1

    def sort_set(self):
        sorted_set = sorted(self.data_set, key=lambda l: l[0])
        sorted_reference = []
        for original_row in self.data_set:
            index = 0
            for row in sorted_set:
                if row[0] == original_row[0] and row[1] == original_row[1]:
                    sorted_reference.append(index)
                    break
                else:
                    index = index+1
        return (sorted_set, sorted_reference)

    def get_median(self, sequence):
        size = len(sequence)
        return sequence[size/2][0]

    # [[first set], [second set]] -> [first set, second set]
    def set_to_data(self, input_set):
        return_data = []
        for small_set in input_set:
            return_data.extend(small_set)
        return return_data

    def reorder(self, input_set, reference):
        result = []
        for ref in reference:
            result.append(input_set[ref])
        return result

    def anonymize(self):
        sort_set_result = self.sort_set()
        sorted_set = sort_set_result[0]
        set_length = len(sorted_set)
        sorted_reference = sort_set_result[1]

        # used to remeber DP results
        anonymity_set = []
        anonymity_data = []

        # base case (for 5-anonoymity: 1~9 i.e. index 0~8)
        base_num = 2*self.factor-1
        for i in xrange(base_num):
            base_set = sorted_set[:i+1]
            median = self.get_median(base_set)
            new_list = []
            for row in base_set:
                new_list.append([median, row[1]])
            anonymity_set.append([new_list])
            anonymity_data = self.set_to_data(anonymity_set[i])

        # using dynamic programming to add the elements one by one
        # DP policy: add to the last set or create a new one
        for i in xrange(base_num, set_length):  # 10 ~ i.e. index 9~
            anonymity_set.append(None)
            minimal = 9999
            for back_pointer in xrange(self.factor, 2 * self.factor):  # 5~9
                new_set_start = i-back_pointer+1
                if new_set_start > self.factor-1:
                    old_set_end = new_set_start-1
                    temp_set = anonymity_set[old_set_end][:]
                    new_sequence = sorted_set[new_set_start:i+1]
                    new_median = self.get_median(new_sequence)
                    new_add_list = []
                    for row in new_sequence:
                        new_add_list.append([new_median, row[1]])
                    temp_set.append(new_add_list)
                    temp_data = self.set_to_data(temp_set)
                    curr_change = self.calculate_change(sorted_set[:i+1], temp_data)

                    if (curr_change < minimal) and (curr_change != -1):
                        minimal = curr_change
                        anonymity_set[i] = temp_set

        # finalize result
        final_data = self.set_to_data(anonymity_set[set_length-1])
        # print "unsorted result:"
        # print final_data
        self.anonymity_set = self.reorder(final_data, sorted_reference)

        write_CSV(self.data_stirng, self.anonymity_set)


a = time.time()
datafile = sys.argv[1]
test = DataSet(datafile, 5)
test.anonymize()
b = time.time()
print "final change: ", test.calculate_change()
# print "final result:"
# print test.get_result()
print "need time:", b-a
