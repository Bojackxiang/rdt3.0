import socket
import time
import random

sender_ip = "localhost"
sender_port = 3001
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender_socket.bind((sender_ip, sender_port))

receiver_ip = "localhost"
receiver_port = 3000
receiver_address = (receiver_ip, receiver_port)

path = "/Users/keiichi/Desktop/9331official/9331txt2.txt"
file = open(path, "r")
sender_log = open("Sender_log.txt", "w")

mss = 12
mws = 4
time_out = 100
random_seed = 788
pdrop = 0.5


class handshake_data:
    def __init__(self, syn = 0, seq = 0, ack = 0):
        self.syn = syn
        self.seq = seq
        self.ack = ack
        self.string_data = str(self.syn) +" "+ str(self.seq) + " " + str(self.ack)
        self.sending_data = self.string_data.encode("utf-8")

def handshake_data_fetch(data):
    syn = int(data.decode("utf-8").split()[0])
    seq = int(data.decode("utf-8").split()[1])
    ack = int(data.decode("utf-8").split()[2])
    return syn, seq, ack

def handshake(sendto_address):
    syn = 1
    sequence = 0
    hand_pkt1 = handshake_data(syn=syn, seq=sequence)                   # send 1 0 0
    sender_socket.sendto(hand_pkt1.sending_data, sendto_address)
    received_pkt_1, address = sender_socket.recvfrom(1024)              # receive 1 0 1
    syn, seq, ack = handshake_data_fetch(received_pkt_1)
    if syn == 1 and ack == 1:
        hand_pkt2 = handshake_data(syn=1, seq=seq+1, ack = ack)
        sender_socket.sendto(hand_pkt2.sending_data, sendto_address)    # send 1 1 1
        print("connection has been built")
    else:
        print("connection lost")

class data_transforming_segment:
    def __init__(self, syn=0, fin=0, ack=0, ack_bit=0, seq=0, seq_bit=0, data="None"):
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.ack_bit = ack_bit
        self.seq = seq
        self.seq_bit = seq_bit
        self.data = data
        self.string = str(self.syn) + " " + str(self.fin) + " " + str(self.ack) + " " +str(self.ack_bit)+ " " + str(self.seq_bit) + " " + str(self.seq_bit) + " /" + self.data
        self.sending_data = self.string.encode("utf-8")
        self.time = None

def data_transforming_data_fetch(data):
    syn = int(data.decode("utf-8").split()[0])
    fin = int(data.decode("utf-8").split()[1])
    ack = int(data.decode("utf-8").split()[2])
    ack_bit = int(data.decode("utf-8").split()[3])
    seq = int(data.decode("utf-8").split()[4])
    seq_bit = int(data.decode("utf-8").split()[5])
    incoming_data = data.decode("utf-8").split()[6]
    return syn, fin, ack, ack_bit, seq, seq_bit, incoming_data

def close():
    close_pkt = data_transforming_segment(fin=1, seq = 200)
    sender_socket.sendto(close_pkt.sending_data, receiver_address)      # fin = 1

    data, address = sender_socket.recvfrom(1024)                        #ack bit = 1, ack = 200 + 1
    data, address = sender_socket.recvfrom(1024)                        # fin = 1, seq = 500
    print(data)
    syn, fin, ack, ack_bit, seq, seq_bit, incoming_data = data_transforming_data_fetch(data)
    close_pkt2 = data_transforming_segment(ack_bit=1, ack = seq+1)         # 1 202
    sender_socket.sendto(close_pkt2.sending_data, receiver_address)
    print("we closed")
    sender_socket.close()

def create_window():
    global data_list
    global sequence_number
    global ack
    byte = file.read(mss)
    while byte:
    # while len(byte) < mss:
        data_list.append(data_transforming_segment(data=str(byte), seq=sequence_number, ack=1))
        byte=file.read(mss)
        sequence_number += len(byte)



def pld_send(data):
    random_number = random.random()
    if random_number+pdrop < 1:
        sender_socket.sendto(data, receiver_address)
        sender_log.writelines("snd \n")
    else:
        sender_log.write("drop \n")


def receive():
    global ack_number
    global sequence_number
    global fast
    while True:
        receive_data, addr = sender_socket.recvfrom(1024)
        syn, fin, ack, ack_bit, seq, seq_bit, info = data_transforming_data_fetch(receive_data)
        sender_log.writelines("rcv \n")
        if ack_number == ack:
            fast += 1
            if fast > 2:
                return "fast trans"
        else:
            fast = 0
            ack_number = ack
            for item in data_list:
                if item.ack_number == item.seq + len(item.data):
                    create_window()
                    return "update"




start_time = time.time()
handshake(receiver_address)
sequence_number = 1
ack_number = 1
data_list = []
create_window()
fast = 0
for item in data_list:
    print(item.sending_data.decode("utf-8"))
    pld_send(item.sending_data)
# while data_list:
    # for item in data_list:
while data_list:
    result = receive()
    for item in data_list:
        if result == "fast":
            pld_send(data_list[0])
close()
