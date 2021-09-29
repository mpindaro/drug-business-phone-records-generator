from AgentHandler import *
import simpy

if __name__ == "__main__":
    agentHandler = AgentHandler()
    agentHandler.create_environment()
    #print(agentHandler)



    env = simpy.Environment()
    agentHandler.start_simulation(env, 15778800)

