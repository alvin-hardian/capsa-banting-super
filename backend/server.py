import sys
import socket
import pickle
import select
import random
import copy
import queue
import time

class Server:
    def __init__(self):
        self.SERVER_ADDRESS = ('localhost', 5000)
        self.BUFFER_SIZE = 4096

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.SERVER_ADDRESS)
        self.server.listen(5)

        self.clients = []
        self.card_index = list(range(52))
        # self.card_index = [0, 13, 26, 39, 1, 14, 27, 40, 2, 15, 28, 41, 3, 16, 29, 42, 4, 17, 30, 43, 5, 18, 31, 44, 6, 19, 32, 45, 7, 20, 33, 46, 8, 21, 34, 47, 9, 22, 35, 48, 10, 23, 36, 49, 11, 24, 37, 50, 12, 25, 38, 51]
        random.shuffle(self.card_index)

        self.game_data = {}
        self.game_data['card_index_before'] = []
        self.game_data['card_point_before'] = -1
        self.game_data['card_index_now'] = []
        self.game_data['card_point_now'] = -1
        self.game_data['player'] = {}
        self.game_data['player'][0] = {}
        self.game_data['player'][0]['player_sequence'] = [0,1,2,3]
        self.game_data['player'][0]['card_index'] = self.card_index[:13]
        self.game_data['player'][0]['card_count'] = 13
        self.game_data['player'][1] = {}
        self.game_data['player'][1]['player_sequence'] = [1,0,2,3]
        self.game_data['player'][1]['card_index'] = self.card_index[13:26]
        self.game_data['player'][1]['card_count'] = 13
        self.game_data['player'][2] = {}
        self.game_data['player'][2]['player_sequence'] = [2,0,1,3]
        self.game_data['player'][2]['card_index'] = self.card_index[26:39]
        self.game_data['player'][2]['card_count'] = 13
        self.game_data['player'][3] = {}
        self.game_data['player'][3]['player_sequence'] = [3,0,1,2]
        self.game_data['player'][3]['card_index'] = self.card_index[39:52]
        self.game_data['player'][3]['card_count'] = 13

        self.game_order = queue.Queue()

        index_of_three_diamond = self.card_index.index(2)
        if index_of_three_diamond < 13 : 
            self.game_data['turn_player_id'] = 0
            self.game_order.put(1),self.game_order.put(2),self.game_order.put(3),self.game_order.put(0)
        elif index_of_three_diamond < 26 : 
            self.game_data['turn_player_id'] = 1
            self.game_order.put(2),self.game_order.put(3),self.game_order.put(0),self.game_order.put(1)
        elif index_of_three_diamond < 39 : 
            self.game_data['turn_player_id'] = 2
            self.game_order.put(3),self.game_order.put(0),self.game_order.put(1),self.game_order.put(2)
        elif index_of_three_diamond < 52 : 
            self.game_data['turn_player_id'] = 3
            self.game_order.put(0),self.game_order.put(1),self.game_order.put(2),self.game_order.put(3)
        

    def run(self):
        input_list = [self.server, sys.stdin]
        RUNNING = True
        FIRST = True
        while RUNNING :
            input_ready, output_ready, except_ready = select.select(input_list, [], [])

            for files in input_ready:
                if files == self.server :
                    client_socket, client_address = self.server.accept()
                    input_list.append(client_socket)
                    self.clients.append(client_socket)
                    player_index = self.clients.index(client_socket)
                    self.reply_with_id(client_socket, player_index)
                    # client_socket.send(str.encode(str(player_index)))
                    time.sleep(0.1)
                    self.broadcast_joined({
                        'count_player' : len(self.clients),
                        'player' : player_index,
                    })
                elif files == sys.stdin :
                    to_send = sys.stdin.readline()
                    to_send = to_send.strip()
                    self.clients[0].send(str.encode(to_send))
                else :
                    message = files.recv(self.BUFFER_SIZE)
                    message = pickle.loads(message)
                    print(message)
                    if message['status'] == 'QUIT':
                        self.reply_ok(files)
                        input_list.remove(files)
                        self.clients.remove(files)

                        if len(self.clients) == 0:
                            RUNNING = False
                        
                    elif message['status'] == 'UPDATE' :
                        player_id = message['data']['id']
                        is_play = message['data']['play'] == 'PLAY'
                        if is_play :
                            player_card = self.game_data['player'][player_id]['card_index']
                            player_choosen_card = message['data']['selected_card']
                            player_choosen_card_point = message['data']['selected_card_point']
                            for card in player_choosen_card:
                                player_card.remove(card)
                            self.game_data['player'][player_id]['card_index'] = player_card
                            self.game_data['player'][player_id]['card_count'] = len(player_card)
                            self.game_data['card_index_before'] = self.game_data['card_index_now']
                            self.game_data['card_point_before'] = self.game_data['card_point_now']
                            self.game_data['card_index_now'] = player_choosen_card
                            self.game_data['card_point_now'] = player_choosen_card_point
                            
                            self.game_data['turn_player_id'] = self.game_order.get()
                            
                            self.game_order.put(self.game_data['turn_player_id'])

                            if len(player_card) == 0 :
                                winner_data = {}
                                winner_data['player_id'] = player_id
                                self.broadcast_winner(winner_data)
                                RUNNING = False

                        else :
                            game_stack = queue.LifoQueue()
                            while(self.game_order.qsize() != 0):
                                game_stack.put(self.game_order.get())

                            game_stack.get()
                            
                            game_stack2 = queue.LifoQueue()
                            while(game_stack.qsize() != 0):
                                game_stack2.put(game_stack.get())

                            self.game_order = queue.Queue()
                            while(game_stack2.qsize() != 0):
                                self.game_order.put(game_stack2.get())
                            
                            x = self.game_order.get()
                            self.game_order.put(x)

                            active_player = len(list(self.game_order.queue))
                            if active_player == 1 :
                                last_man = self.game_order.get()
                                self.game_order = queue.Queue()
                                self.game_order.put(last_man)
                                for i in range(last_man + 1, len(self.clients)):
                                    self.game_order.put(i)
                                for i in range(0, last_man):
                                    self.game_order.put(i)

                                self.game_data['card_index_before'] = []
                                self.game_data['card_point_before'] = 0
                                self.game_data['card_index_now'] = []
                                self.game_data['card_point_now'] = 0

                                self.game_data['turn_player_id'] = self.game_order.get()
                                self.game_order.put(self.game_data['turn_player_id'])
                            else :
                                self.game_data['turn_player_id'] = x

                        print(list(self.game_order.queue))

                        self.broadcast_game_data(self.game_data)

        self.server.close()

    def broadcast_joined(self, data):
        data_to_send = {}
        data_to_send['status'] = 'WELCOME'
        data_to_send['data'] = {}
        data_to_send['data'] = data
        for client_socket in self.clients :
            data_pickled = pickle.dumps(data_to_send)
            client_socket.send(data_pickled)

    def broadcast_winner(self, data):
        data_to_send = {}
        data_to_send['status'] = 'WINNER'
        data_to_send['data'] = {}
        data_to_send['data'] = data
        for client_socket in self.clients :
            data_pickled = pickle.dumps(data_to_send)
            client_socket.send(data_pickled)
            

    def reply_ok(self, client_socket):
        data_to_send = {}
        data_to_send['status'] = 'BYE'
        data_to_send['data'] = {}
        data_pickled = pickle.dumps(data_to_send)
        client_socket.send(data_pickled)
    
    def reply_with_id(self, client_socket, player_id) :
        data_to_send = {}
        data_to_send['status'] = 'GET_ID'
        data_to_send['data'] = {}
        data_to_send['data']['id'] = player_id
        data_to_send['data']['card_index'] = self.game_data['player'][player_id]['card_index']
        data_to_send['data']['turn_player_id'] = self.game_data['turn_player_id']
        data_to_send['data']['count_player'] = len(self.clients)
        data_pickled = pickle.dumps(data_to_send)
        client_socket.send(data_pickled)

    def broadcast_game_data(self, data):
        data_to_send = {}
        data_to_send['status'] = 'BROADCAST'
        data_to_send['data'] = {}
        data_to_send['data'] = data
        for client_socket in self.clients :
            player_id = self.clients.index(client_socket)
            data_to_send_p = copy.deepcopy(data_to_send)
            data_to_send_p['data']['player_id'] = player_id
            data_pickled = pickle.dumps(data_to_send_p)
            client_socket.send(data_pickled)


if __name__ == "__main__":
    server = Server()
    server.run()