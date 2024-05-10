import sys

import requests
import uuid
import re
import json

from threading import Thread


class Player:
    def __init__(self, name):
        self.username = name
        self.uuid = uuid.uuid4().hex
        self.is_owner = False
        self.cards = []
        self.users = []
        self.last_card = ''

    def create_game(self, players, mod):
        self.game = GameOwner(players, mod, self.username, self.uuid)
        if self.game.game_code is not None:
            self.is_owner = True
            try:
                self.users = [user for user in (self.game.get_users())['players']]
            except KeyError:
                return False
            else:
                self.game.max_users = players
                Thread(target=self._verify_starting).start()
            return self.game.game_code
        else:
            del self.game
            return False

    def end_game(self):
        if self.is_owner:
            try:
                self.game.end_game()
            except AttributeError:
                return False
            else:
                del self.game
                self.is_owner = False
                return True
        else:
            return False

    def join_game(self, game_code):
        if not self.is_owner:
            self.game = Game(game_code, self.uuid, self.username)
            result = self.game.join()
            if result != 'JOINED':
                del self.game
                return False
            else:
                result = self.game.get_users()
                self.users = [user for user in result['players']]
                self.game.max_users = result['max_players']
                Thread(target=self._verify_starting).start()
                return True
        else:
            return False

    def leave_game(self):
        try:
            result = self.game.leave()
        except AttributeError:
            return False
        else:
            if result != 'LEAVED' and result != 'GAME FINISHED':
                if re.findall("SQL", result):
                    return False
                else:
                    return False
            else:
                self.thread_continue = False
                del self.game
                return True

    def start_game(self):
        if self.is_owner:
            try:
                _ = self.game.start_game()
            except AttributeError:
                return False
            else:
                self.has_started = True
                Thread(target=self._get_last_card).start()
                self.winner = ''
                return True
        else:
            return False

    def get_cards(self):
        try:
            cards = self.game.update_cards()
        except AttributeError:
            return False
        else:
            if cards['status'] != 'ok':
                return False
            else:
                self.player_number_of_cards = cards['data']['players_number_of_cards']
                if cards['data']['cards'] != self.cards:
                    cards['data']['cards'] = [carte.replace("\'", "\"") for carte in cards['data']['cards']]
                    self.cards = [json.loads(card) for card in cards['data']['cards']]
                if cards['data']['turn']:
                    return True

    def _get_last_card(self):
        self.can_play_var = False
        self.actual_player = ""
        self.stack_verificator = ""
        while True:
            try:
                rep = self.game.get_last_card()
                info = json.loads(rep['card'].replace("\'", "\""))
                if rep['winner']:
                    self.winner = rep['winner']
                    if self.is_owner:
                        self.game.end_game()
                    break
                self.stack_verificator, self.actual_player = info, rep['actual_player']
                if self.last_card != info:
                    self.last_card = info
                if self.get_cards() is not None:
                    info = json.loads(self.game.get_last_card()['card'].replace("\'", "\""))
                    if self.last_card != info:
                        self.last_card = info
                    self.can_play_var = True
                    break
            except AttributeError:
                break

    def play(self, card):
        try:
            is_ok = self.game.play_card(card)
        except AttributeError:
            return False
        else:
            if is_ok['status'] == 'ok':
                Thread(target=self._get_last_card).start()
                return True
            else:
                return False

    def _verify_starting(self):
        self.new_users = ""
        self.gone_user = ""
        self.has_started = False
        self.thread_continue = True
        while True:
            if not self.thread_continue:
                sys.exit(0)
            try:
                users = self.game.get_users()
            except AttributeError:
                sys.exit(0)
            else:
                if users['status'] == 'ok' and users['players'] != self.users:
                    for user in self.users:
                        if user not in users['players']:
                            self.gone_user = user
                    for user in users['players']:
                        if user not in self.users:
                            self.new_users = user
                    self.users = [user for user in users['players']]
                try:
                    if not self.is_owner and self._has_started():
                        self.winner = ''
                        break
                    elif self.is_owner and len(self.users) == self.game.players:
                        self.start_game()
                        break
                except AttributeError:
                    sys.exit(0)

    def _has_started(self):
        try:
            has_started = self.game.has_started()
        except AttributeError:
            return False
        else:
            if has_started['status'] != "ok":
                return False
            else:
                try:
                    start = has_started['started']
                except UnboundLocalError:
                    return False
                else:
                    if start:
                        self.has_started = True
                        Thread(target=self._get_last_card).start()
                    return True if start else False

    def pick(self):
        try:
            card = self.game.pick()
        except AttributeError:
            return False
        else:
            if card['status'] != 'ok':
                return False
            else:
                Thread(target=self._get_last_card).start()
                return True


class Game:
    def __init__(self, game_code, uuid_p, username):
        self.uuid = uuid_p
        self.game_code = game_code
        self.username = username

    def join(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/join_game'
            data = {
                'username': self.username,
                'game': self.game_code,
                'uuid': self.uuid
            }
            reponse = (requests.post(url, data)).json()['status']
        except:
            reponse = 'CONNECTION ERROR'
        return reponse

    def leave(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/leave_game'
            data = {
                'game': self.game_code,
                'uuid': self.uuid
            }
            reponse = (requests.post(url, data)).json()['status']
        except:
            reponse = 'CONNECTION ERROR'
        return reponse

    def update_cards(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/get_cards'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid
            }
            reponse = (requests.post(url, data)).json()
        except:
            reponse = {'status': 'CONNECTION ERROR'}
        return reponse

    def play_card(self, card):
        try:
            url = f'http://{ip}:5000/api/v1/uno/play_card'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid,
                'card': str(card),
                'username': self.username
            }
            reponse = (requests.post(url, data)).json()
        except:
            reponse = {'status': 'CONNECTION ERROR'}
        return reponse

    def get_users(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/get_users'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid,
            }
            reponse = (requests.post(url, data)).json()
        except:
            reponse = {'status': 'CONNECTION ERROR'}
        return reponse

    def has_started(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/has_started'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid,
            }
            reponse = (requests.post(url, data)).json()
        except:
            reponse = {'status': 'CONNECTION ERROR'}
        return reponse

    def get_last_card(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/get_last_card'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid,
            }
            reponse = (requests.post(url, data)).json()
        except:
            reponse = {'status': 'CONNECTION ERROR'}
        return reponse

    def pick(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/pick'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid,
                'username': self.username
            }
            reponse = (requests.post(url, data)).json()
        except:
            reponse = {'status': 'CONNECTION ERROR'}
        return reponse


class GameOwner(Game):
    def __init__(self, players, mod, username, uuid_p):
        self.mod = mod
        self.players = players
        try:
            url = f'http://{ip}:5000/api/v1/uno/create_game'
            data = {
                'username': username,
                'number_of_players': self.players,
                'mod': self.mod,
                'uuid': uuid_p
            }
            reponse = (requests.post(url, data)).json()
            if reponse['status'] != "ok":
                self.game_code = None
            else:
                super().__init__(reponse['game'], uuid_p, username)
        except requests.exceptions.ConnectionError:
            self.game_code = None

    def end_game(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/end_game'
            data = {
                'username': self.username,
                'uuid': self.uuid,
                'game': self.game_code
            }
            reponse = (requests.post(url, data)).json()
            return reponse['status'] if reponse['status'] != 'ERROR' else 'ERROR'
        except:
            return 'CONNECTION ERROR'

    def join(self):
        pass

    def leave(self):
        return self.end_game()

    def start_game(self):
        try:
            url = f'http://{ip}:5000/api/v1/uno/start_game'
            data = {
                'game_code': self.game_code,
                'uuid': self.uuid
            }
            cards = requests.post(url, data).json()
            return cards['status']
        except:
            return 'CONNECTION ERROR'


mods = ["all"]
ip = '95.157.165.95'
