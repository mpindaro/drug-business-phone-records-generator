import random

CRED = '\033[91m'
CEND = '\033[0m'
import simpy


class Spacciatore:

    def __init__(self, idd, agentHandler):
        self.idd = idd
        self.magazziniere = None
        self.consumatori = []
        self.persone = []
        self.qtadroga = random.randint(1, 3)
        self.cella = random.randint(0, 7)
        self.agentHandler = agentHandler
        self.min_droga = 1

    def __str__(self) -> str:
            return f"Sono uno Spacciatore con ID={self.get_id()}\n" \
               f"   Magazziniere: {self.magazziniere.get_id() if self.magazziniere is not None else -1 }\n" \
               f"   Consumatori: {[agent.get_id() for agent in self.consumatori] if len(self.consumatori) > 0 else -1}\n" \
               f"   Persone: {[agent.get_id() for agent in self.persone] if len(self.persone) > 0 else -1}\n" \
               f"   Ho {self.qtadroga} di droga\n" \
               f"   E mi trovo nella cella {self.cella}\n"



    def enter_simulation_environment(self, magazziniere, consumatori, persone):
        self.magazziniere = magazziniere
        self.consumatori = consumatori
        self.persone = persone
        self.min_interval_tel = 120  # minimo intervallo fra telefonate
        self.max_interval_tel = 1800  # massimo intervallo fra telefonate

        self.min_spostamento = 1800  # minimo intervallo fra spostamenti
        self.max_spostamento = 3600  # massimo intervallo fra spostamenti

    def doIKnowPersonX(self, idd):
        result = list(filter(lambda x: x.get_id() == idd, self.persone))
        return self.idd if len(result) != 0 else -1

    def get_id(self):
        return self.idd

    def start_simulation(self, env):
        self.env = env
        self.action = env.process(self.run())

    def call_someone(self, is_chiamata, duration, receiver):
        #print(type(self), type(receiver))

        self.agentHandler.handle_call(self, receiver, is_chiamata, duration, self.env.now)

    def run(self):
        while True:
            state = self.agentHandler.get_state()
            if self.magazziniere != None:
                call_params = self.agentHandler.get_call_param(
                    [[self.magazziniere], self.consumatori, self.persone])
            else: call_params = self.agentHandler.get_call_param([self.consumatori, self.persone])
            self.call_someone(call_params[0], call_params[1], call_params[2])

            try:
                yield self.env.timeout(int(random.randint(self.min_interval_tel**2, self.max_interval_tel**2)**0.5) + call_params[1])
            except simpy.Interrupt as interrupt:
                cause = ''.join(x for x in str(interrupt.cause) if not x.isdigit())
                id = ''.join(x for x in str(interrupt.cause) if x.isdigit())

                causes1 = ["chiamata-consumatore", "sms-consumatore"]
                if cause in causes1:
                    prob_spostamento = bool(random.randint(0, 4))
                    if prob_spostamento:
                        consumatore = self.agentHandler.get_agent_by_id(id)
                        self.call_someone("S", 0, consumatore)
                        self.qtadroga -= 1
                        if self.qtadroga < self.min_droga:
                            self.cella = self.magazziniere.celladroga
                            self.magazziniere.cella = self.magazziniere.celladroga
                            droga = random.randint(1, 5)
                            self.qtadroga += droga
                            self.magazziniere.qtadroga -= droga
                            self.call_someone("S", 0, self.magazziniere)
                else:
                    print(CRED + "Sono stato interrotto da qualcosa che non doveva interrompermi!" + CEND)
