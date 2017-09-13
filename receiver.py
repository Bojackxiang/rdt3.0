import socket
import sys
# receiver_ip = "localhost"
receiver_ip = sys.argv[1]
# receiver_port = 3000
receiver_port = sys.argv[2]
receiver_address = (receiver_ip, receiver_port)
receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_socket.bind(receiver_address)
file_name = sys.argv[3]
file = open(file_name, "w")
receiver_log = open("receiver_log.txt", "w")

class handshake_data:
    def __init__(self, syn = 0, seq = 0, ack = 0):
        self.syn = syn
        self.seq = seq
        self.ack = ack
        self.string_data = str(self.syn) +" "+ str(self.seq) + " " + str(self.ack)
        self.sending_data = self.string_data.encode("utf-8")

class data_transforming_segment:
    def __init__(self, syn=0, fin=0, ack=0, ack_bit=0, seq=0, seq_bit=0, data="None"):
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.ack_bit = ack_bit
        self.seq = seq
        self.seq_bit = seq_bit
        self.data = data
        self.string = str(self.syn) + " " + str(self.fin) + " " + str(self.ack) + " " +str(self.ack_bit) + " " + str(self.seq) + " " + str(self.seq_bit) + " " + self.data
        self.sending_data = self.string.encode("utf-8")

def data_transforming_data_fetch(data):
    syn = int(data.decode("utf-8").split()[0])
    fin = int(data.decode("utf-8").split()[1])
    ack = int(data.decode("utf-8").split()[2])
    ack_bit = int(data.decode("utf-8").split()[3])
    seq = int(data.decode("utf-8").split()[4])
    seq_bit = int(data.decode("utf-8").split()[5])
    incoming_data = data.decode("utf-8").split("/")[1]
    return syn, fin, ack, ack_bit, seq, seq_bit, incoming_data

def handshake_data_fetch(data):
    syn = int(data.decode("utf-8").split()[0])
    seq = int(data.decode("utf-8").split()[1])
    ack = int(data.decode("utf-8").split()[2])
    return syn, seq, ack

def handshake():
    data, addr = receiver_socket.recvfrom(1024)                     # should receive 1 0 0
    syn, seq, ack = handshake_data_fetch(data)
    if syn == 1:
        send_pkt1 = handshake_data(syn=syn, seq = seq, ack=seq+1)   # send 1 0 1
        receiver_socket.sendto(send_pkt1.sending_data, addr)
        data, addr = receiver_socket.recvfrom(1024)                 # receive 1 1 1
        print(data.decode("utf-8"))
        print("Connection has been build")

handshake()
while True:
    ack_number = 1
    sequence_number = 1
    data, addr = receiver_socket.recvfrom(1024)
    syn, fin, ack, ack_bit, seq, seq_bit, info = data_transforming_data_fetch(data)
    # Receiver 每收一个就要开始判断
    ack_number = seq + len(info)
    x = data_transforming_segment(ack = ack_number, seq = seq)
    receiver_socket.sendto(x.sending_data ,addr)
    # Programing is Terminated
    if fin == 1:
        print("we want to close connection")
        receiver_socket.sendto(data_transforming_segment(ack_bit=1, ack=seq+1).sending_data,addr)
        receiver_socket.sendto(data_transforming_segment(fin=1, seq=201).sending_data, addr)
        data, addr = receiver_socket.recvfrom(1024)               # seq = 202
        break
    else:
        file.writelines(info)

    # A received Sequence number is what I want
    # if ack_number == seq:                                       # if the number is what i want
    #     print("I received What I want")
    #     ack_number = ack_number + len(info)                     # renew ack number
    #     file.writelines(info)
    #     print("I want following data")
    #     i_want = data_transforming_segment(ack=ack_number, seq=sequence_number)
    #     receiver_socket.sendto(i_want.sending_data, addr)
    # if ack_number != seq:
    #     print("this is not what i want, send original ack, and the right sequence that i want to you")
    #     not_i_want = data_transforming_segment(ack=ack_number, seq=sequence_number)
    #
    #     while True:
    #         data, address = receiver_socket.recvfrom(1024)
    #         syn, fin, ack, ack_bit, seq, seq_bit, info = data_transforming_data_fetch(data)
    #         if ack_number == seq:
    #             print(info)
    #             print("I want this, cool, and i just send you the next that i want")
    #             next_i_want = data_transforming_segment(ack=ack_number+len(info), seq=sequence_number)
    #             receiver_socket.sendto(i_want.sending_data, addr)
    #             break
    #         else:
    #             continue


    # receiver_socket.sendto(data_transforming_segment(ack=ack_number, seq=sequence_number).sending_data, addr)

receiver_socket.close()

