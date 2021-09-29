import random
import simpy
CRED = '\033[91m'
CEND = '\033[0m'
from agents import States

class Magazziniere:

    def __init__(self, id, agentHandler):
        self.id = id
        self.importatori = []
        self.spacciatori = []
        self.persone = []
        self.qtadroga = random.randint(0, 3)
        self.celladroga = random.randint(0, 7)
        self.cella = random.randint(0, 7)
        self.agentHandler = agentHandler

        self.last_moved = 0
        self.waiting_time_to_move = 0

    def doIKnowPersonX(self, id):
        found = false
        result = list(filter(lambda x: x.get_id() == id, self.importatori))
        if len(result) != 0:
            return self.id
        result = list(filter(lambda x: x.get_id() == id, self.spacciatori))
        if len(result) != 0:
            return self.id
        result = list(filter(lambda x: x.get_id() == id, self.persone))
        if len(result) != 0:
            return self.id

        return -1

    def __str__(self) -> str:
        return f"Sono un Magazziniere con ID={self.id}\n" \
               f"   Importatori: {[agent.get_id() for agent in self.importatori] if len(self.importatori) > 0 else -1}\n" \
               f"   Spacciatori: {[agent.get_id() for agent in self.spacciatori] if len(self.spacciatori) > 0 else -1}\n" \
               f"   Persone Generiche: {[agent.get_id() for agent in self.persone] if len(self.persone) > 0 else -1}\n" \
               f"   Ho {self.qtadroga} droga tenuta nella cella {self.celladroga}\n" \
               f"   E mi trovo nella cella {self.cella}\n"

    def enter_simulation_environment(self, importatori, spacciatori, persone):
        self.importatori = importatori
        self.spacciatori = spacciatori
        self.persone = persone
        self.min_interval_tel = 1200  # minimo intervallo fra telefonate
        self.max_interval_tel = 7200  # massimo intervallo fra telefonate

        self.min_spostamento = 1800  # minimo intervallo fra spostamenti
        self.max_spostamento = 3600  # massimo intervallo fra spostamenti

    def start_simulation(self, env):
        self.env = env
        self.action = env.process(self.run())

    def doIKnowPersonX(self, id):
        result = list(filter(lambda x: x.get_id() == id, self.persone))
        return self.id if len(result)!=0 else -1

    def get_id(self):
        return self.id

    def call_someone(self, is_chiamata, duration, receiver):
        self.agentHandler.handle_call(self, receiver, is_chiamata, duration, self.env.now)


    def run(self):
        while True:

            if self.qtadroga <=0:
                self.agentHandler.changeState(States.TRATTATIVA, self.env.now)

            call_params = self.agentHandler.get_call_param(
                [self.spacciatori, self.importatori, self.persone])

            self.call_someone(call_params[0], call_params[1], call_params[2])
            try:
                yield self.env.timeout(int(random.randint(self.min_interval_tel**2, self.max_interval_tel**2)**0.5) + call_params[1])
            except simpy.Interrupt as interrupt:
                cause = ''.join(x for x in str(interrupt.cause) if not x.isdigit())
                id = ''.join(x for x in str(interrupt.cause) if x.isdigit())

                causes1 = ["chiamata-camionista", "sms-camionista"]
                if cause in causes1:
                    self.cella = self.celladroga
                    camionista = self.agentHandler.get_agent_by_id(id)

                    self.call_someone("S", 0, camionista)

                else:
                    print(CRED + "Sono stato interrotto da qualcosa che non doveva interrompermi!" + CEND)

            if self.env.now > self.waiting_time_to_move + self.last_moved:
                self.change_cella()

    def get_cella_magazzino(self):
        return self.celladroga

    def change_cella(self):
        self.waiting_time_to_move = random.randint(self.min_spostamento, self.max_spostamento)
        self.last_moved = self.env.now
        self.cella = random.randint(0, 7)