import random

from agents import States

class Camionista:

    def __init__(self, id, agentHandler):
        self.id = id
        self.importatori = []
        self.esportatori = []
        self.magazzinieri = []
        self.cella = random.randint(0, 7)
        self.agentHandler = agentHandler
        self.controllato = bool(random.randint(0, 6))
        self.last_moved = 0
        self.waiting_time_to_move = 0
        self.qtadroga = random.randint(1, 3)


    def is_controllato(self):
        return self.controllato

    def __str__(self) -> str:
        return f"Sono un Camionista con ID={self.id}\n" \
               f"   Importatori: {[agent.get_id() for agent in self.importatori] if len(self.importatori) > 0 else -1}\n" \
               f"   Esportatori: {[agent.get_id() for agent in self.esportatori] if len(self.esportatori) > 0 else -1}\n" \
               f"   Magazzinieri: {[agent.get_id() for agent in self.magazzinieri] if len(self.magazzinieri) > 0 else -1}\n" \
               f"   E mi trovo nella cella {self.cella}\n"

    def enter_simulation_environment(self, importatori, esportatori, magazzinieri):
        self.importatori = importatori
        self.esportatori = esportatori
        self.magazzinieri = magazzinieri

        self.min_interval_tel = 120  # minimo intervallo fra telefonate
        self.max_interval_tel = 7200  # massimo intervallo fra telefonate

        self.min_spostamento = 1800  # minimo intervallo fra spostamenti
        self.max_spostamento = 3600  # massimo intervallo fra spostamenti

        self.waiting_time_to_move = random.randint(self.min_spostamento, self.max_spostamento)

    def get_id(self):
        return self.id

    def start_simulation(self, env):
        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            state = self.agentHandler.get_state()


            if state == States.CARICO_IN_ARRIVO:
                call_params = self.agentHandler.get_call_param([self.importatori, self.esportatori, self.magazzinieri])
                self.call_someone(call_params[0], call_params[1], call_params[2])
                yield self.env.timeout(call_params[1])
                yield self.env.timeout(int(random.randint(self.min_interval_tel**2, self.max_interval_tel**2)**0.5))
            else:
                yield self.env.timeout(int(random.randint(self.min_interval_tel**2, self.max_interval_tel**2)**0.5))

            if self.env.now > self.waiting_time_to_move + self.last_moved:
                self.change_cella()

            if self.qtadroga <= 0:
                self.agentHandler.changeState(States.NULLO)

    def call_someone(self, is_chiamata, duration, receiver):
        self.agentHandler.handle_call(self, receiver, is_chiamata, duration, self.env.now)

    def doIKnowPersonX(self, id):
        result = list(filter(lambda x: x.get_id() == id, self.importatori))
        if len(result) != 0:
            return self.id
        result = list(filter(lambda x: x.get_id() == id, self.esportatori))
        if len(result) != 0:
            return self.id
        result = list(filter(lambda x: x.get_id() == id, self.magazzinieri))
        if len(result) != 0:
            return self.id

        return -1

    def change_cella(self):
        self.waiting_time_to_move=random.randint(self.min_spostamento, self.max_spostamento)
        self.last_moved = self.env.now
        magazziniere = random.choice(self.magazzinieri)
        self.cella = magazziniere.get_cella()

        self.agentHandler.register_log(self.env.now, f"Droga depositata dal camionista {self.get_id()} da {magazziniere.get_id()}" )

        call_params = self.agentHandler.get_call_param([])
        self.call_someone(call_params[0], call_params[1], magazziniere)
        droga_depositata = random.randint(1, self.qtadroga)
        magazziniere.qtadroga += droga_depositata
        self.qtadroga-=droga_depositata

        yield self.env.timeout(call_params[1])
