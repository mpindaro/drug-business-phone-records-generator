import random
import simpy


class Persona:

    def __init__(self, id, agentHandler):
        self.id = id
        self.importatori = []
        self.spacciatori = []
        self.magazzinieri = []
        self.consumatoreControllato = []
        self.cella = random.randint(0, 7)
        self.agentHandler = agentHandler
        self.last_moved = 0
        self.waiting_time_to_move = 0

    def __str__(self) -> str:
        return f"Sono una Persona Generica con ID={self.id}\n" \
               f"   Importatori: {[agent.get_id() for agent in self.importatori] if len(self.importatori) > 0 else -1}\n" \
               f"   Spacciatori: {[agent.get_id() for agent in self.spacciatori] if len(self.spacciatori) > 0 else -1}\n" \
               f"   Magazzinieri: {[agent.get_id() for agent in self.magazzinieri] if len(self.magazzinieri) > 0 else -1}\n" \
               f"   Consumatori Controllati: {[agent.get_id() for agent in self.consumatoreControllato] if len(self.consumatoreControllato) > 0 else -1}\n" \
               f"   E mi trovo nella cella {self.cella}\n"

    def enter_simulation_environment(self, importatori, spacciatori, magazzinieri, consumatoreControllato):
        self.importatori = importatori
        self.spacciatori = spacciatori
        self.magazzinieri = magazzinieri
        self.consumatoreControllato = consumatoreControllato

        self.min_interval_tel = 120  # minimo intervallo fra telefonate
        self.max_interval_tel = 1800  # massimo intervallo fra telefonate

        self.min_spostamento = 1800  # minimo intervallo fra spostamenti
        self.max_spostamento = 3600  # massimo intervallo fra spostamenti

        self.waiting_time_to_move = random.randint(self.min_spostamento, self.max_spostamento)

    def get_id(self):
        return self.id

    def start_simulation(self, env):
        self.env = env
        self.action = env.process(self.run())

    def call_someone(self, is_chiamata, duration, receiver):
        self.agentHandler.handle_call(self, receiver, is_chiamata, duration, self.env.now)

    def run(self):
        while True:
            not_empty_relations = []
            if len(self.importatori) > 0:
                not_empty_relations.append(self.importatori)
            if len(self.spacciatori) > 0:
                not_empty_relations.append(self.spacciatori)
            if len(self.magazzinieri) > 0:
                not_empty_relations.append(self.magazzinieri)
            if len(self.consumatoreControllato) > 0:
                not_empty_relations.append(self.consumatoreControllato)

            if len(not_empty_relations) == 0:
                break
            call_params = self.agentHandler.get_call_param(not_empty_relations)

            self.call_someone(call_params[0], call_params[1], call_params[2])
            try:
                yield self.env.timeout(int(random.randint(self.min_interval_tel**2, self.max_interval_tel**2)**0.5) + call_params[1])
            except simpy.Interrupt as interrupt:
                print(CRED + "Sono stato interrotto da qualcosa che non doveva interrompermi!" + CEND)

            if self.env.now > self.waiting_time_to_move + self.last_moved:
                self.change_cella()



    def change_cella(self):
        self.waiting_time_to_move = random.randint(self.min_spostamento, self.max_spostamento)
        self.last_moved = self.env.now
        self.cella = random.randint(0, 7)
