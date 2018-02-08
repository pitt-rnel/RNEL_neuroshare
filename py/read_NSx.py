import struct
import numpy as np
import scipy.io as sio
import csv
import sys
import argparse
import json
import io

parser = argparse.ArgumentParser(description="Read a NSx file")
parser.add_argument('--format', type=str, nargs=1)
parser.add_argument('--input', type=str, nargs=1)
parser.add_argument('--output', type=str, nargs=1)
args = parser.parse_args()
print(args.format[0], args.input[0], args.output[0])

########## Collect input arguments ##########
save_format = args.format[0]
fname = args.input[0]
save_file = args.output[0]

########## Open NSx File ##########
datafile = open(fname, 'rb')
data_dict = {}
data_dict['NSx_File'] = fname

print("--------------------Header Info--------------------")
filetype = struct.unpack('8s', datafile.read(8))[0].decode('utf-8')
data_dict['File_Type'] = filetype
print("File Type:\t", filetype)
filespec = struct.unpack('2B', datafile.read(2))
filespec = "NEV Spec {}.{}".format(filespec[0], filespec[1])
data_dict["File_Spec"] = filespec
print("File Spec:\t", filespec)
bytes_in_headers = struct.unpack('<I', datafile.read(4))[0]
data_dict["Bytes_in_Headers"] = bytes_in_headers
print("Bytes in Headers:\t", bytes_in_headers)
label = struct.unpack('16s', datafile.read(16))[0].decode('utf-8')
data_dict["Label"] = label
print("Label:\t", label)
application = struct.unpack('52s', datafile.read(52))[0].decode('utf-8')
data_dict["Application"] = application
print("Application to Create File:\t", application)
comments = struct.unpack('200s', datafile.read(200))[0].decode('utf-8')
data_dict["Comments"] = comments
print("Comments:\t", comments)
timestamp = struct.unpack('<I', datafile.read(4))[0]
data_dict["Timestamp"] = timestamp
print("Timestamp:\t", timestamp)
period = struct.unpack('<I', datafile.read(4))[0]
data_dict["Period"] = period
print("Period:\t", period)
timestamp_res = struct.unpack('<I', datafile.read(4))[0]
data_dict["Timestamp_Resolution"] = timestamp_res
print("Timestamp Resolution of Time Stamps:\t", timestamp_res)
time_origin = struct.unpack('<8H', datafile.read(16))
data_dict["Time_Origin"] = time_origin
print("Time Origin of Samples:\t", time_origin)
channel_count = struct.unpack('<I', datafile.read(4))[0]
data_dict["Channel_Count"] = channel_count
print("Channel Count:\t", channel_count)

if save_format == "matlab":
  save_string = save_file + "_Global_Header.mat"
  channel_headers = []
  for i in range(0, channel_count):
    channel_headers.append(save_file.split("/")[-1] + "_Channel_" + str(i) + "_Header.mat")
  data_dict["Channel_Header_Files"] = channel_headers
  sio.savemat(save_string, data_dict)

if save_format == "json":
  save_string = save_file + "_Global_Header.json"
  channel_headers = []
  for i in range(0, channel_count):
    channel_headers.append(save_file.split("/")[-1] + "_Channel_" + str(i) + "_Header.json")
  data_dict["Channel_Header_Files"] = channel_headers
  with open(save_string, 'w') as outfile:
    json.dump(data_dict, outfile)


print("--------------------Ext Header Info--------------------")
EXT_HEADER_COUNT = channel_count # Num Channels as specified from channel count in header 
EXT_HEADER_SIZE = 66 # Size of each header based on NEV documentation
print(EXT_HEADER_COUNT, " extended headers")
for i in range(0, EXT_HEADER_COUNT):
  #ext_header = datafile.read(EXT_HEADER_SIZE) 
  ext_head = {}
  header_type = struct.unpack('2s', datafile.read(2))[0].decode('utf-8')
  ext_head["Header_Type"] = header_type
  electrode_id = struct.unpack('<H', datafile.read(2))[0]
  ext_head["Electrode_ID"] = electrode_id
  electrode_label = struct.unpack('16s', datafile.read(16))[0].decode('utf-8')
  ext_head["Electrode_Label"] = electrode_label
  frontend_id = struct.unpack('B', datafile.read(1))[0]
  ext_head["Frontend_ID"] = frontend_id
  frontend_connector_pin = struct.unpack('B', datafile.read(1))[0]
  ext_head["Frontend_Connector_Pin"] = frontend_connector_pin
  min_digital_value = struct.unpack('<h', datafile.read(2))[0]
  ext_head["Min_Digital_Value"] = min_digital_value
  max_digital_value = struct.unpack('<h', datafile.read(2))[0]
  ext_head["Max_Digital_Value"] = max_digital_value
  min_analog_value = struct.unpack('<h', datafile.read(2))[0]
  ext_head["Min_Analog_Value"] = min_analog_value
  max_analog_value = struct.unpack('<h', datafile.read(2))[0]
  ext_head["Max_Analog_Value"] = max_analog_value
  units = struct.unpack('16s', datafile.read(16))[0].decode('utf-8')
  ext_head["Units"] = units
  highpass_corner_freq = struct.unpack('<I', datafile.read(4))[0]
  ext_head["Highpass_Corner_Freq"] = highpass_corner_freq 
  highpass_filter_order = struct.unpack('<I', datafile.read(4))[0]
  ext_head["Highpass_Filter_Order"] = highpass_filter_order
  highpass_filter_type = struct.unpack('<H', datafile.read(2))[0]
  ext_head["Highpass_Filter_Type"] = highpass_filter_type
  lowpass_corner_freq = struct.unpack('<I', datafile.read(4))[0]
  ext_head["Lowpass_Corner_Freq"] = lowpass_corner_freq
  lowpass_filter_order = struct.unpack('<I', datafile.read(4))[0]
  ext_head["Lowpass_Filter_Order"] = lowpass_filter_order
  lowpass_filter_type = struct.unpack('<H', datafile.read(2))[0]
  ext_head["Lowpass_Filter_Type"] = lowpass_filter_type
  
  if save_format == "matlab":
    ext_head["Data_File"] = save_file.split("/")[-1] + "_Channel_" + str(i) + "_Data.csv" 
    save_string = save_file + "_Channel_" + str(i) + "_Header.mat"
    sio.savemat(save_string, ext_head)
  
  if save_format == "json":
    ext_head["Data_File"] = save_file.split("/")[-1] + "_Channel_" + str(i) + "_Data.csv"
    save_string = save_file + "_Channel_" + str(i) + "_Header.mat"
    with open(save_string, 'w') as outfile:
      json.dump(ext_head, outfile)


print("--------------------Data Packets--------------------")
packet_no = 0
print("Reading Data Packets...")

save_string = save_file + "_Packet_Metadata.csv"
with open(save_string, 'w') as f:
  row = ["Packet_No,", "Header", "Timestamp", "Num_Data_Points"]
  csvwriter = csv.writer(f, delimiter=',')
  csvwriter.writerow(row)
f.close()

while True: 
  try:
    header = struct.unpack('B', datafile.read(1))[0]
  except:
    print("Done")
    break
  if header != 1:
    break
  packet_no = packet_no + 1
  timestamp_packet = struct.unpack('<I', datafile.read(4))[0]
  num_data_points = struct.unpack('<I', datafile.read(4))[0]

  print("Packet Number\t" + str(packet_no) + ":\t" + str(num_data_points) + "\tDatapoints") 

  save_string = save_file + "_Packet_Metadata.csv"
  with open(save_string, 'w') as f:
    row = [packet_no, header, timestamp_packet, num_data_points]
    csvwriter = csv.writer(f, delimiter=',')
    csvwriter.writerow(row)
  f.close()

  num_points_processed = 0
  buffer_size = 50000
  while num_points_processed < num_data_points:
    format_string = '<' + str(channel_count) + 'h'
    read_size = min(buffer_size, num_data_points - num_points_processed)
    point_set = np.array([struct.unpack(format_string, datafile.read(channel_count * 2)) for i in
      range(0, read_size)])
    
    for x in range(0, channel_count):
      save_string = save_file + "_Channel_" + str(x) + "_Data.csv"
      with open(save_string, 'a') as f:
        rows = point_set[:, x]
        csvwriter = csv.writer(f, delimiter='\n')
        csvwriter.writerow(rows)
    num_points_processed = num_points_processed + read_size
    print("Processed:\t" + str(num_points_processed) + " points.\tRemaining:\t" +
        str(num_data_points-num_points_processed) + " points.")
  
