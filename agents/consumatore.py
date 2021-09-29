import random
import simpy

#TODO fare sì che in parte controllati camionisti e co no consumatoe (70%)

class Consumatore:

    def __init__(self, id, agentHandler):
        self.id = id
        self.spacciatore = None
        self.persone = []
        self.controllato = bool(random.randint(0, 1))
        self.cella = random.randint(0, 7)
        self.agentHandler=agentHandler

    def get_spacciatore(self):
        return self.spacciatore.get_id()

    def doIKnowPersonX(self, idd):
        result = list(filter(lambda x: x.get_id() == idd, self.persone))
        if self.spacciatore.get_id() == idd:
            result.append(self.spacciatore)

        return self.id if len(result) != 0 else -1

    def __str__(self) -> str:
        return f"Sono un Consumatore con ID={self.id}\n" \
               f"   Spacciatore: {self.spacciatore.get_id() if self.spacciatore is not None else -1}\n" \
               f"   Persone generiche: {[agent.get_id() for agent in self.persone]if len(self.persone) > 0 else -1}\n" \
               f"   Sono controllato: {self.controllato}\n" \
               f"   E mi trovo nella cella {self.cella}\n"

    def enter_simulation_environment(self, spacciatore, persone):
        self.spacciatore = spacciatore
        self.persone = persone
        self.min_interval_tel = 518400  # minimo intervallo fra telefonate
        self.max_interval_tel = 691200  # massimo intervallo fra telefonate

        self.min_spostamento = 7200  # minimo intervallo fra spostamenti
        self.max_spostamento = 32400  # massimo intervallo fra spostamenti


    def get_id(self):
        return self.id

    def is_controllato(self):
        return self.controllato

    def start_simulation(self, env):
        self.env = env
        self.action = env.process(self.run())

    def call_someone(self, is_chiamata, duration, receiver):
        self.agentHandler.handle_call(self, receiver, is_chiamata, duration, self.env.now)

    def run(self):
        while True:
            if self.controllato:

                call_params = self.agentHandler.get_call_param(
                    [self.persone])

                self.call_someone(call_params[0], call_params[1], call_params[2])
                yield self.env.timeout(call_params[1])


            call_params = self.agentHandler.get_call_param([[self.spacciatore]])
            self.call_someone(call_params[0], call_params[1], call_params[2])
            self.agentHandler.register_log(self.env.now, f"Consumatore con id {self.get_id()} ha acquistato da {call_params[2].get_id()}")

            try:
                yield self.env.timeout(int(random.randint(self.min_interval_tel**2, self.max_interval_tel**2)**0.5))
            except simpy.Interrupt as interrupt:
                print(CRED + "Sono stato interrotto da qualcosa che non doveva interrompermi!" + CEND)