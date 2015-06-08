import os, sys, math, random, time
import numpy as np

def get_entry_names_in_folder(path):
  return [f for f in os.listdir(path)]

def get_entry_paths_in_folder(path):
  entry_names = get_entry_names_in_folder(path)
  for index, entry_name in enumerate(entry_names):
    entry_names[index] = path + '/' + entry_name
  return entry_names

def get_file_paths_in_folder(path):
  return [entry_path for entry_path in get_entry_paths_in_folder(path) if os.path.isfile(entry_path)]

def get_sorted_file_paths_in_folder(path):
  return sorted(get_file_paths_in_folder(path))

def get_file_name_from_folder(folder_name):
  return get_sorted_file_paths_in_folder(folder_name)

def create_folder(path):
  if not os.path.exists(path):
    os.makedirs(path)

def get_dimension():
  with open('config/dimension' , 'r') as config:
    dimension = int(config.readline().strip())
  return dimension
  
def create_line_numbers(data_type, line_numbers):
  with open('config/' + data_type + '_line_numbers_for_labels' , 'wb') as line_numbers_for_labels:
    line_numbers = [str(int(s)) for s in line_numbers]
    line_numbers_for_labels.write('\t'.join(line_numbers))
  
def get_line_numbers(data_type):
  with open('config/' + data_type + '_line_numbers_for_labels' , 'r') as config:
    line_numbers = config.readline().strip().split('\t')
    line_numbers = [int(s) for s in line_numbers]
  return line_numbers
  
def get_balance_line_number(data_type, split_number, label_number):
  line_numbers = get_line_numbers(data_type)
  balance_line_number = 0
  for line_number in line_numbers:
    balance_line_number += line_number
  return int(balance_line_number/(split_number*label_number))
  
def get_original_file_names(folder_name):
  file_names = get_file_name_from_folder(folder_name)
  file_names = [s for s in file_names if not s.split('/')[-1].isdigit()]
  return file_names
  
def get_label_free_file_names(folder_name):
  file_names = get_file_name_from_folder(folder_name)
  file_names = [s for s in file_names if s.split('/')[-1].isdigit()]
  return file_names
  
def get_file_path_by_file_name(file_name):
  file_path = file_name.split('/')
  file_path.pop(-1)
  file_path = '/'.join(file_path)
  return file_path
  
def get_label(line):
  label_end_index = line.find(' ')
  label = line[:label_end_index]
  instance = line[label_end_index+1:].strip()
  return label, instance
  
def collect_sorted_labels(file_names):
  labels = []
  for file_name in file_names:
    with open(file_name, 'r') as file:
      for line in file:
        label, _ = get_label(line)
        if not label in labels:
          labels.append(label)
  labels.sort()
  return labels
  
def create_split_files(file_names, labels, data_type):
  split_number = len(labels)
  line_counters = np.zeros(split_number)
  
  file_path = get_file_path_by_file_name(file_names[0])
  split_datas = [open(file_path + '/' + str(idx), 'wb') for idx in range(split_number)]
  for file_name in file_names:
    with open(file_name, 'r') as file:
      for line in file:
        label, instance = get_label(line)
        label_idx = labels.index(label)
        split_datas[label_idx].write(instance+'\n')
        line_counters[label_idx] += 1
  [split_datas[idx].close() for idx in range(split_number)]
  
  create_line_numbers(data_type, line_counters)
  
def label_split(file_names, data_type):
  labels = collect_sorted_labels(file_names)
  create_split_files(file_names, labels, data_type)
  
def create_folder_base_on_split_number(folder_name, split_number):
  create_folder(folder_name + '/' + str(split_number))
  [create_folder(folder_name + '/' + str(split_number) + '/' + str(idx)) for idx in range(split_number)]
  
def split_label_free_file(file_name, folder_name, split_number, label_idx, ratio, label_number):
  data_type = folder_name
  line_number = int(get_line_numbers(data_type)[label_idx] / split_number)
  
  #sample_number = get_balance_line_number(data_type, split_number, label_number) * ratio 
  sample_number = int(line_number * ratio)
  with open(file_name, 'r') as input:
    sample_out_file_name = '/'.join([folder_name, str(split_number), str(label_idx)+'.sample'])
    sample_output = open(sample_out_file_name, 'wb')
    for folder_idx in xrange(split_number):
      write_out_file_name = '/'.join([folder_name, str(split_number), str(folder_idx), str(label_idx)])
      inst_output = open(write_out_file_name, 'wb')
      #sample_output = open(write_out_file_name + '.sample', 'wb')
      line_count = 0
      while line_count < line_number:
        line = input.readline()
        inst_output.write(line)
        if line_count < sample_number:
          sample_output.write(line)
        line_count += 1
      inst_output.close()
    sample_output.close()
  
def split(folder_name, split_number, ratio):
  original_file_names = get_original_file_names(folder_name)
  data_type = folder_name
  label_split(original_file_names, data_type)
  
  label_free_file_names = get_label_free_file_names(folder_name)
  label_number = len(label_free_file_names)
  create_folder_base_on_split_number(folder_name, split_number)
  for label_idx, file_name in enumerate(label_free_file_names):
    split_label_free_file(file_name, folder_name, split_number, label_idx, ratio, label_number)
  
if __name__ == '__main__':
  
  start = time.time()
  train_folder_name = 'train'
  train_split_number = 20
  train_ratio = 0.1
  split(train_folder_name, train_split_number, train_ratio)
  print 'train elapsed time: ', time.time() - start