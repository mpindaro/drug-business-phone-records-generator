import itertools
import random
from Simulation import *
import pandas as pd

from agents import (Consumatore, Camionista, Esportatore, Importatore, Magazziniere, Persona, Spacciatore, States)


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class AgentHandler:
    progressive_id = itertools.count()
    events = []

    def __init__(self):
        self.camionisti = []
        self.consumatori = []
        self.esportatori = []
        self.magazzinieri = []
        self.spacciatori = []
        self.importatori = []
        self.persone = []
        self.min_tel = 3  # minima durata telefonata voce
        self.max_tel = 900  # massima durata telefonata voce
        self.sms_prob_risposta = 7  # 7 volte su 10
        self.state = States.NULLO
        self.timestamp_last_state_change = 0
        self.dataset = []
        self.log = []

    def get_timestamp_last_state_change(self):
        return self.timestamp_last_state_change

    def changeState(self, state, timestamp):
        if self.state != state:
            self.log.append((timestamp, f"Cambio di stato: da {self.state} a {state}"))
            self.state = state
        self.timestamp_last_state_change = timestamp

    def register_log(self, timestamp, event):
        self.log.append((timestamp,  event))

    def get_sms_probability(self):
        return self.sms_prob_risposta

    def get_random_tel_duration(self):
        return random.randint(self.min_tel, self.max_tel)

    def create_environment(self, n_camionisti=6, n_importatori=9, n_magazzinieri=6, n_esportatori=3, n_spacciatori=6,
                           n_consumatori=12, n_persone=6):

        self.camionisti = [Camionista(next(self.progressive_id), self) for _ in range(n_camionisti)]
        self.consumatori = [Consumatore(next(self.progressive_id), self) for _ in range(n_consumatori)]
        self.importatori = [Importatore(next(self.progressive_id), self) for _ in range(n_importatori)]
        self.magazzinieri = [Magazziniere(next(self.progressive_id), self) for _ in range(n_magazzinieri)]
        self.esportatori = [Esportatore(next(self.progressive_id), self) for _ in range(n_esportatori)]
        self.spacciatori = [Spacciatore(next(self.progressive_id), self) for _ in range(n_spacciatori)]
        self.persone = [Persona(next(self.progressive_id), self) for _ in range(n_persone)]

        self.bind()

    def bind(self):
        for camionista in self.camionisti:
            camionista.enter_simulation_environment(random.sample(self.importatori, k=4),
                                                    random.sample(self.esportatori, k=2),
                                                    self.magazzinieri)

        for consumatore in self.consumatori:
            consumatore.enter_simulation_environment(random.choice(self.spacciatori), random.sample(self.persone, k=4))

        for esportatore in self.esportatori:
            esportatore_id = esportatore.get_id()
            camionisti_per = list(filter(lambda x: x != -1,
                                         [agent.doIKnowPersonX(esportatore_id) for agent in
                                          self.camionisti]))
            camionisti = list(filter(lambda agent: agent.get_id() in camionisti_per, self.camionisti))
            esportatore.enter_simulation_environment(camionisti, self.importatori)

        for importatore in self.importatori:
            importatore_id = importatore.get_id()
            esportatori_per = list(filter(lambda x: x != -1,
                                          [agent.doIKnowPersonX(importatore_id) for agent in
                                           self.esportatori]))
            esportatori = list(filter(lambda agent: agent.get_id() in esportatori_per, self.esportatori))

            importatore.enter_simulation_environment(self.importatori, esportatori, self.spacciatori,
                                                     self.magazzinieri, random.sample(self.persone, k=4))

        for magazziniere in self.magazzinieri:
            magazziniere_id = magazziniere.get_id()

            importatori_per = list(filter(lambda x: x != -1,
                                          [agent.doIKnowPersonX(magazziniere_id) for agent in
                                           self.importatori]))
            importatori = list(filter(lambda agent: agent.get_id() in importatori_per, self.importatori))

            magazziniere.enter_simulation_environment(importatori, random.sample(self.spacciatori, k=2),
                                                      random.sample(self.persone, k=4))

        for spacciatore in self.spacciatori:
            spacciatore_id = spacciatore.get_id()


            magazzinieri = list(filter(lambda agent: agent.get_id() in magazzinieri_per, list(filter(lambda x: x != -1, [agent.doIKnowPersonX(spacciatore_id) for agent in self.magazzinieri]))))

            consumatori = [self.get_agent_by_id(tupla[0]) for tupla in list(filter(lambda x: x[1] == spacciatore_id , [ (agent.get_id(), agent.get_spacciatore()) for agent in self.consumatori]))]

            spacciatore.enter_simulation_environment(magazzinieri[0] if len(magazzinieri)>0 else None,
                                                     consumatori,
                                                     random.sample(self.persone, k=4))

        for persona in self.persone:
            id = persona.get_id()
            magazzinieri_per = list(filter(lambda x: x != -1,
                                           [agent.doIKnowPersonX(id) for agent in
                                            self.magazzinieri]))
            spacciatori_per = list(filter(lambda x: x != -1,
                                          [agent.doIKnowPersonX(id) for agent in
                                           self.spacciatori]))
            consumatori_per = list(filter(lambda x: x != -1,
                                          [agent.doIKnowPersonX(id) for agent in
                                           self.consumatori]))
            importatori_per = list(filter(lambda x: x != -1,
                                          [agent.doIKnowPersonX(id) for agent in
                                           self.importatori]))

            magazzinieri = list(filter(lambda agent: agent.get_id() in magazzinieri_per, self.magazzinieri))
            spacciatori = list(filter(lambda agent: agent.get_id() in spacciatori_per, self.spacciatori))
            consumatori = list(
                filter(lambda agent: (agent.get_id() in consumatori_per and agent.is_controllato()), self.consumatori))

            importatori = list(filter(lambda agent: agent.get_id() in importatori_per, self.importatori))
            persona.enter_simulation_environment(importatori, spacciatori, magazzinieri, consumatori)

    def __str__(self) -> str:
        return f"{''.join(str(agent) for agent in self.camionisti)}" \
               f"\n{''.join(str(agent) for agent in self.consumatori)}" \
               f"\n{''.join(str(agent) for agent in self.esportatori)}" \
               f"\n{''.join(str(agent) for agent in self.importatori)}" \
               f"\n{''.join(str(agent) for agent in self.magazzinieri)}" \
               f"\n{''.join(str(agent) for agent in self.persone)}" \
               f"\n{''.join(str(agent) for agent in self.spacciatori)}"

    def start_simulation(self, env, duration):
        for importatore in self.importatori:
            importatore.start_simulation(env)

        for camionista in self.camionisti:
            camionista.start_simulation(env)

        for magazziniere in self.magazzinieri:
            magazziniere.start_simulation(env)

        for consumatore in self.consumatori:
            consumatore.start_simulation(env)

        for esportatore in self.esportatori:
            esportatore.start_simulation(env)

        for persona in self.persone:
            persona.start_simulation(env)

        for spacciatore in self.spacciatori:
            spacciatore.start_simulation(env)

        env.run(until=duration)

        df = pd.DataFrame(self.dataset, columns=["timestamp", "mittente", "is_mittente_intercettato", "destinatario",
                                                 "is_destinatario_intercettato", "durata", "tipo"])
        df["esito_chiamata"]=1
        df.sort_values(by=["timestamp"], inplace=True)
        df.to_csv("tabulato.csv", index=False)

        df = pd.DataFrame(self.log, columns=["timestamp", "evento"])
        df.sort_values(by=["timestamp"], inplace=True)
        df.to_csv("log.csv", index=False)

        ids = [ (type(agent).__name__, agent.get_id()) for agent in self.camionisti + self.consumatori + self.esportatori + self.importatori + self.magazzinieri + self.persone + self.spacciatori]

        df = pd.DataFrame(ids, columns=["tipo", "id"])
        df.sort_values(by=["id"], inplace=True)
        df.to_csv("agents_id.csv", index=False)

        text_file = open("agents.txt", "w")
        n = text_file.write(str(self))
        text_file.close()

    def register_event(self, sender, sender_interc, receiver, receiver_interc, timestamp, voice_or_sms, duration):
        print(timestamp, sender, sender_interc, receiver, receiver_interc, duration, voice_or_sms)
        self.dataset.append((timestamp, sender, sender_interc, receiver, receiver_interc, duration, voice_or_sms))

    def generate_sms_cascade(self, sender, sender_interc, receiver, receiver_interc, timestamp):
        sms_number = random.randint(2, 6)
        start_timestamp = timestamp
        for i in range(sms_number):
            response_time = random.randint(0, 900)
            if i % 2 == 0:
                self.register_event(sender, sender_interc, receiver, receiver_interc, start_timestamp + response_time,
                                    "S", 0)
            else:
                self.register_event(receiver, receiver_interc, sender, sender_interc, start_timestamp + response_time,
                                    "S", 0)
            start_timestamp += response_time

    def get_agent_by_id(self, id):
        agents_list = [self.camionisti, self.consumatori, self.esportatori, self.importatori, self.magazzinieri,
                       self.persone, self.spacciatori]
        for agent_list in agents_list:
            res = list(filter(lambda agent: agent.get_id() == id, agent_list))
            if not len(res) == 0:
                return res[0]
        return -1

    def handle_call(self, sender, receiver, is_chiamata, duration, timestamp):
        receiver_inter = "N" if (
                (isinstance(receiver, Consumatore) and not(receiver.is_controllato())) or
                (isinstance(receiver, Camionista) and not (receiver.is_controllato())) or
                (isinstance(receiver, Esportatore) and not (receiver.is_controllato())) or
                isinstance(receiver, Persona)) else "S"

        sender_inter = "N" if ((isinstance(sender, Consumatore) and not(sender.is_controllato())) or
                               (isinstance(sender, Camionista) and not(sender.is_controllato())) or
                               (isinstance(sender, Esportatore) and not(sender.is_controllato())) or
                               isinstance(sender, Persona)) else "S"

        if sender_inter == "N" and receiver_inter == "N":
            return
        # print(receiver)
        #if isinstance(receiver, list):  # TODO: CAPIRE L'ERRORE
        #    return
        if sender.get_id() == receiver.get_id():
            return

        if is_chiamata:
            self.register_event(sender.get_id(), sender_inter, receiver.get_id(), receiver_inter, timestamp, "V",
                                duration)
        else:
            self.generate_sms_cascade(sender.get_id(), sender_inter, receiver.get_id(), receiver_inter, timestamp)
        self.innest_events(sender, receiver, is_chiamata)

    def innest_events(self, sender, receiver, is_chiamata):
        if isinstance(receiver, Esportatore):
            if isinstance(receiver, Importatore):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-importatore" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-importatore" + str(sender.get_id()))
        elif isinstance(receiver, Importatore):
            if isinstance(receiver, Spacciatore):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-spacciatore" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-spacciatore" + str(sender.get_id()))
            if isinstance(receiver, Importatore):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-importatore" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-importatore" + str(sender.get_id()))
            if isinstance(receiver, Magazziniere):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-magazziniere" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-magazziniere" + str(sender.get_id()))
            if isinstance(receiver, Camionista):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-camionista" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-camionista" + str(sender.get_id()))
        elif isinstance(receiver, Magazziniere):
            if isinstance(receiver, Camionista):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-camionista" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-camionista" + str(sender.get_id()))
        elif isinstance(receiver, Spacciatore):
            if isinstance(receiver, Consumatore):
                if is_chiamata:
                    receiver.action.interrupt("chiamata-consumatore" + str(sender.get_id()))
                else:
                    receiver.action.interrupt("sms-consumatore" + str(sender.get_id()))

    def get_state(self):
        return self.state

    def get_call_param(self, list_of_receivers):
        is_chiamata = bool(random.randint(0, self.get_sms_probability()))
        if len(list_of_receivers) > 0:
            random_receiver_type = random.randint(0, len(list_of_receivers) - 1)
            while len(list_of_receivers[random_receiver_type]) == 0:
                random_receiver_type = random.randint(0, len(list_of_receivers) - 1)

            receiver = random.choice(list_of_receivers[random_receiver_type])
            if isinstance(receiver, list):
                print( list_of_receivers,"\n" , receiver)
        else:
            receiver = None
        return is_chiamata, self.get_random_tel_duration() if is_chiamata else 0, receiver
