import pdb
import pickle
import pprint
import itertools
import numpy as np

#t_viajes={}
#t_average_by_line={}
#graph_weights={}

def process_trip(s, t_viajes):
	for i,o in enumerate(s):
		o_cod_var,o_freq,o_parada,o_ordinal,o_pasada,o_name=o.strip().split(',')
		for d in s[i+1:]:
			d_cod_var,d_freq,d_parada,d_ordinal,d_pasada,d_name=d.strip().split(',')
			
			#Sanity check
			assert o_cod_var==d_cod_var
			assert o_freq==d_freq
			assert int(o_ordinal)<int(d_ordinal)
			assert int(o_pasada)<=int(d_pasada)
			assert o_name==d_name

			if ((int(o_parada), int(d_parada)) not in t_viajes):
				t_viajes[(int(o_parada), int(d_parada))]={}

			if o_name not in t_viajes[(int(o_parada), int(d_parada))]:
				t_viajes[(int(o_parada), int(d_parada))][o_name]=[]

			t_viajes[(int(o_parada), int(d_parada))][o_name].append(int(d_pasada)-int(o_pasada))

def process_trips(input_path,output_path, t_viajes):
	records=open(input_path).readlines()
	chunk_start=0
	chunk_end=0
	while (chunk_end<len(records)):
		line_freq=records[chunk_start].split(',')[:2]
		while(chunk_end<len(records) and records[chunk_end].split(',')[:2]==line_freq):
			chunk_end+=1
		
		print("Processing: %d-%d"%(chunk_start,chunk_end))
		process_trip(records[chunk_start:chunk_end], t_viajes)
		chunk_start=chunk_end

	with open(output_path, 'wb') as handle:
		pickle.dump(t_viajes, handle, protocol=pickle.HIGHEST_PROTOCOL)

def average_trips():
	for pair in t_viajes:
		assert pair not in t_average_by_line
		t_average_by_line[pair]=[]
		for line in t_viajes[pair]:
			t_wait=round(7200.0/float(len(t_viajes[pair][line]))) # 2 hours from 7.00 to 9.00
			t_travel=round(sum(t_viajes[pair][line])/float(len(t_viajes[pair][line])))
			t_average_by_line[pair].append((line,t_wait,t_travel))

	with open('t_average_by_line.pickle', 'wb') as handle:
		pickle.dump(t_average_by_line, handle, protocol=pickle.HIGHEST_PROTOCOL)

def compute_weights():
	total_links=0
	removed_links=0
	for pair in t_average_by_line:
		fastest_time=min([a[1]+a[2] for a in t_average_by_line[pair]])

		#Discard really slow lines: travel time > min(waiting_time+travel_time)
		for line in t_average_by_line[pair]:
			total_links+=1
			if line[2]>fastest_time:
				t_average_by_line[pair].remove(line)
				#print("Discarded line %s for pair %s. Fastest time: %d"%(line,pair,fastest_time))
				removed_links+=1

		#Compute average travel time
		min_wait=min([a[1] for a in t_average_by_line[pair]])
		total_buses_in_window=sum([min_wait/a[1] for a in t_average_by_line[pair]])
		average_travel_time=round(sum([((min_wait/a[1])/total_buses_in_window)*a[2] for a in t_average_by_line[pair]]))


		#Compute average waiting time (https://math.stackexchange.com/questions/222674/average-bus-waiting-time)

		# Fully random passage times.
		w_times=[a[1] for a in t_average_by_line[pair]]
		m= 1/(sum([1/a for a in w_times]))
		average_waiting_time=round(m)
		graph_weights[pair]=average_waiting_time+average_travel_time


		# Old approach: Fully periodic passage times with random uniform initializations
		
		# average_waiting_time=0
		# w_times=[a[1] for a in t_average_by_line[pair]]
		# mbar=min(w_times)
		# pdb.set_trace()
		# for i, _ in enumerate(t_average_by_line[pair]):
		# 	print (i)
		# 	term=((-1)**i)*(mbar**(i+1))*(1/(i+1))
		# 	sumk=0
		# 	for c in itertools.combinations(w_times, i):
		# 		sumk += (1/np.product(c))
		# 	average_waiting_time+=term*sumk

		# average_waiting_time=round(average_waiting_time)
		# graph_weights[pair]=(average_waiting_time,average_travel_time)
		# print("Processed pair: %s"%pair)

	print ("%d removed out of %d links"%(removed_links,total_links))
	with open('graph_weights.pickle', 'wb') as handle:
		pickle.dump(graph_weights, handle, protocol=pickle.HIGHEST_PROTOCOL)

def main():
        
        t_viajes={}
        
        #Timetable
        path='horarios_7_9.csv'
        output_path='t_viajes.pickle'
        process_trips(path,output_path, t_viajes)

        t_viajes={}

        #GPS Times
        path='horarios_7_9_gps.csv'
        output_path='t_viajes_gps.pickle'
        process_trips(path,output_path, t_viajes)

#	global t_viajes
#	t_viajes=pickle.load(open('t_viajes.pickle', 'rb'))
#
#	average_trips()
#
#	global t_average_by_line
#	t_average_by_line=pickle.load(open('t_average_by_line.pickle', 'rb'))
#
#	compute_weights()

if __name__ == '__main__':
	main()
