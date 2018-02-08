import struct
import numpy as np
import scipy.io as sio
import h5py
import sys
import argparse
import json
import io

parser = argparse.ArgumentParser(description="Read a NEV file")
parser.add_argument('--format', type=str, nargs=1)
parser.add_argument('--input', type=str, nargs=1)
parser.add_argument('--output', type=str, nargs=1)
args = parser.parse_args()
print(args.format[0], args.input[0], args.output[0])

########## Collect input arguments ##########
save_format = args.format[0]
fname = args.input[0]
save_file = args.output[0]

########## Open NEV File ##########
datafile = open(fname,'rb')
data_dict = {}
data_dict['NEV_File'] = fname

print("------------------------Header Info----------------------------")
filetype = struct.unpack('8s', datafile.read(8))[0].decode('utf-8') 
data_dict['File_Type'] = filetype
print("File Type:\t", filetype)
filespec = struct.unpack('2B', datafile.read(2))
filespec = "NEV Spec {}.{}".format(filespec[0], filespec[1])
data_dict['File_Spec'] = filespec
print("File Spec:\t", filespec)
add_flags = struct.unpack('<H', datafile.read(2))[0] 
data_dict['Additional_Flags'] = add_flags
print("Additional Flags:", add_flags)
bytes_in_headers = struct.unpack('<I', datafile.read(4))[0] 
data_dict["Bytes_in_Headers"] = bytes_in_headers
print("Bytes in Headers:\t", bytes_in_headers)
bytes_in_packets = struct.unpack('<I', datafile.read(4))[0]
data_dict["Bytes_in_Packets"] = bytes_in_packets
print("Bytes in Packets:\t", bytes_in_packets)
timestamp_res = struct.unpack('<I', datafile.read(4))[0]
data_dict["Timestamp_Resolution"] = timestamp_res
print("Timestamp Resolution of Time Stamps:\t", timestamp_res)
sample_res = struct.unpack('<I', datafile.read(4))[0]
data_dict["Sample_Resolution"] = sample_res
print("Time Resolution of Samples:\t", sample_res)
time_origin = struct.unpack('<8H', datafile.read(16))
data_dict['Time_Origin'] = time_origin
print("Time Origin of Samples:\t", time_origin)
application = struct.unpack('32s', datafile.read(32))[0].decode('utf-8')
data_dict["Application"] = application
print("Application to Create File:\t", application)
comment = struct.unpack('200s', datafile.read(200))[0].decode('utf-8')
data_dict["Comments"] = comment
print("Comments:\t", comment)
reserved = datafile.read(52) # Reserved bytes
processor_timestamp = struct.unpack('<I', datafile.read(4))[0] 
data_dict["Processor_Timestamp"] = processor_timestamp
print("Processor Timestamp:\t", processor_timestamp)
num_ext_header = struct.unpack('<I', datafile.read(4))[0]
data_dict["Num_Extended_Headers"] = num_ext_header
print("No. of Extended Headers:\t", num_ext_header)

##### Extended Header Information #####
print("------------------------Extended Header Info----------------------------")
ext_head = {}
nwave = {'packet_id':[], 'electrode_id':[], 'frontend_id':[], 'frontend_connector_pin':[], 'neural_amp_digitization_factor':[], 'energy_threshold':[], 'high_threshold':[], 'low_threshold':[], 'num_sorted_units':[], 'bytes_per_wf':[], 'stim_amp_digitization_factor':[]}
nflt = {'packet_id':[], 'electrode_id':[], 'highpass_cornerfreq':[], 'highpass_filtorder':[], 'highpass_filttype':[], 'lowpass_cornerfreq':[], 'lowpass_filtorder':[], 'lowpass_filttype':[]}
nlbl = {'packet_id':[], 'electrode_id':[], 'label':[]}
dlbl = {'packet_id':[], 'label':[], 'mode':[]}
for i in range(0, num_ext_header):   
    print("Processing ", i+1, " of ", num_ext_header, " extended headers.")
    packet_id = struct.unpack('8s', datafile.read(8))[0].decode('utf-8')
    if packet_id == "NEUEVWAV":
        nwave['packet_id'].append(packet_id)
        electrode_id = struct.unpack('<H', datafile.read(2))[0] 
        nwave['electrode_id'].append(electrode_id)
        frontend_id = struct.unpack('B', datafile.read(1))[0]
        nwave['frontend_id'].append(frontend_id)
        frontend_conn_pin = struct.unpack('B', datafile.read(1))[0]
        nwave['frontend_connector_pin'].append(frontend_conn_pin)
        neural_amp_digit = struct.unpack('<H', datafile.read(2))[0]
        nwave['neural_amp_digitization_factor'].append(neural_amp_digit) 
        energy_thresh = struct.unpack('<H', datafile.read(2))[0]
        nwave['energy_threshold'].append(energy_thresh)
        high_thresh = struct.unpack("<h", datafile.read(2))[0]
        nwave['high_threshold'].append(high_thresh)
        low_thresh = struct.unpack("<h", datafile.read(2))[0]
        nwave['low_threshold'].append(low_thresh)
        num_sorted_units = struct.unpack('B', datafile.read(1))[0]
        nwave['num_sorted_units'].append(num_sorted_units)
        bytes_per_wf = struct.unpack('B', datafile.read(1))[0]
        nwave['bytes_per_wf'].append(bytes_per_wf)
        stim_amp_digit = struct.unpack('<f', datafile.read(4))[0]
        nwave['stim_amp_digitization_factor'].append(stim_amp_digit)
        datafile.read(6)
    elif packet_id == "NEUEVFLT":
        nflt['packet_id'].append(packet_id)
        electrode_id = struct.unpack('<H', datafile.read(2))[0] 
        nflt['electrode_id'].append(electrode_id)
        highpass_corner_freq = struct.unpack('<I', datafile.read(4))[0]
        nflt['highpass_cornerfreq'].append(highpass_corner_freq)
        highpass_filt_order = struct.unpack('<I', datafile.read(4))[0]
        nflt['highpass_filtorder'].append(highpass_filt_order)
        highpass_filt_type = struct.unpack('<H', datafile.read(2))[0]
        nflt['highpass_filttype'].append(highpass_filt_type)
        lowpass_corner_freq = struct.unpack('<I', datafile.read(4))[0]
        nflt['lowpass_cornerfreq'].append(lowpass_corner_freq)
        lowpass_filt_order = struct.unpack('<I', datafile.read(4))[0]
        nflt['lowpass_filtorder'].append(lowpass_filt_order)
        lowpass_filt_type = struct.unpack('<H', datafile.read(2))[0]
        nflt['lowpass_filttype'].append(lowpass_filt_type)
        datafile.read(2)
    elif packet_id == "NEUEVLBL":
        nlbl['packet_id'].append(packet_id)
        electrode_id = struct.unpack('<H', datafile.read(2))[0] 
        nlbl['electrode_id'].append(electrode_id)
        label = struct.unpack('16s', datafile.read(16))[0].decode('utf-8')
        nlbl['label'].append(label)
        datafile.read(6)
    elif packet_id == "DIGLABEL":
        dlbl['packet_id'].append(packet_id)
        label = struct.unpack('16s', datafile.read(16))[0].decode('utf-8')
        dlbl['label'].append(label)
        mode = struct.unpack('B', datafile.read(1))[0]
        dlbl['mode'].append(mode)
        datafile.read(7)
    
ext_head['NEUEVWAV'] = nwave
ext_head['NEUEVFLT'] = nflt
ext_head['NEUEVLBL'] = nlbl
ext_head['DIGLABEL'] = dlbl

########### Data Packets ##########
print("------------------------Data Packets----------------------------")
packet_data = {}
num_packets = 0
dig_in = {'timestamp':[], 'packet_id':[], 'packet_insertion_reason':[], 'parallel_input':{'timestamp':[], 'value':[]}, 'sma1':{'timestamp':[], 'value':[]}, 'sma2':{'timestamp':[], 'value':[]}, 'sma3':{'timestamp':[], 'value':[]}, 'sma4':{'timestamp':[], 'value':[]}}
spike_events = {'timestamp':[], 'electrode_id':[], 'unit_classification_num':[], 'waveform':[]}
stim_events = {'timestamp':[], 'electrode_id':[], 'waveform':[]}
timestamp_old = 0
while True:    
  try:
    packet = datafile.read(bytes_in_packets)
    timestamp = struct.unpack('<I', packet[0:4])[0]/timestamp_res
  except:
    print("Done reading packets.")
    break
  
  if timestamp == 0:
    continue
  
  num_packets = num_packets + 1

  packetid = struct.unpack('<H', packet[4:6])[0]
  
  if packetid == 0:
    dig_in['timestamp'].append(timestamp)
    dig_in['packet_id'].append(packet_id)
    packet_insertion_reason = struct.unpack('B', packet[6:7])[0]
    dig_in['packet_insertion_reason'].append("{0:b}".format(packet_insertion_reason))
  #  datafile.read(1) # Reserved Bytes
  #  dio = datafile.read(10)
    if packet_insertion_reason & 1:
      pinput = struct.unpack('<H', packet[8:10])[0]
      dig_in['parallel_input']['timestamp'].append(timestamp)
      dig_in['parallel_input']['value'].append(pinput)
    if packet_insertion_reason & 2:
      sma1 = struct.unpack('<h', packet[10:12])[0]
      dig_in['sma1']['timestamp'].append(timestamp)
      dig_in['sma1']['value'].append(sma1)
    if packet_insertion_reason & 4:
      sma2 = struct.unpack('<h', packet[12:14])[0]
      dig_in['sma2']['timestamp'].append(timestamp)
      dig_in['sma2']['value'].append(sma2)
    if packet_insertion_reason & 8:
      sma3 = struct.unpack('<h', packet[14:16])[0]
      dig_in['sma3']['timestamp'].append(timestamp)
      dig_in['sma3']['value'].append(sma3)
    if packet_insertion_reason & 16:
      sma4 = struct.unpack('<h', packet[16:18])[0]
      dig_in['sma4']['timestamp'].append(timestamp)
      dig_in['sma4']['value'].append(sma4)
    if packet_insertion_reason & 64:
      event = "Periodic Sampling Event"
      dig_in['packet_insertion_reason'].append(event)
    if packet_insertion_reason & 128:
      event = "Serial Channel Changed"
      dig_in['packet_insertion_reason'].append(event)
#    datafile.read(2) # Reserved Bytes
  elif packetid >= 1 and packetid <= 512:
    spike_events['timestamp'].append(timestamp)
    spike_events['electrode_id'].append(packetid)
    unit_classification = struct.unpack('B', packet[6:7])[0] 
    spike_events['unit_classification_num'].append(unit_classification)
  #  datafile.read(1) # Reserved bytes
    waveform = struct.unpack('{0:d}h'.format(int((bytes_in_packets-8)/bytes_per_wf)), packet[8:])
    spike_events['waveform'].append(waveform)
  elif packetid >= 5121 and packetid <= 5632:
    stim_events['timestamp'].append(timestamp)
    stim_electrode = packetid - 5120
    stim_events['electrode_id'].append(stim_electrode)
    #datafile.read(2) # Reserved bytes
    stim_waveform = struct.unpack('{0:d}h'.format(int((bytes_in_packets-8)/bytes_per_wf)),
        packet[8:])
    stim_events['waveform'].append(stim_waveform)
  
spike_events['waveform'] = np.transpose(np.array(spike_events['waveform']))
stim_events['waveform'] = np.transpose(np.array(stim_events['waveform']))
packet_data['Digital_Input_Data'] = dig_in
packet_data['Spike_Events'] = spike_events
packet_data['Stim_Events'] = stim_events
packet_data['NUM_PACKETS'] = num_packets

########## Create Trial Data Structure ##########
print("Saving NEV File Data Structure...")
if save_format == "matlab":
  data_dict['Extended_Headers'] = ext_head
  data_dict['Data'] = packet_data
  sio.savemat(save_file, data_dict)

if save_format == "json":
  json_spikes = spike_events['waveform']
  json_stim = stim_events['waveform']
  spike_dicts = []
  stim_dicts = []
  if len(json_spikes) > 0:
    for i in range(0, json_spikes.shape[1]):
      spike_dicts.append({'wf'+str(i):json_spikes[:,i].tolist()} )
  spike_events.update({'waveform':spike_dicts})
  if len(json_stim) > 0:
    for i in range(0, json_stim.shape[1]):
      stim_dicts.append({'wf' + str(i):json_stim[:,i].tolist()})
  stim_events.update({'waveform': stim_dicts})

  packet_data.update({'Spike_Events': spike_events})
  packet_data.update({'Stim_Events': stim_events})
  data_dict.update({'Extended_Headers': ext_head})
  data_dict.update({'Data':packet_data})
  with open(save_file, 'w') as outfile:
    json.dump(data_dict, outfile)

print("Done. File saved at:\t", save_file)
