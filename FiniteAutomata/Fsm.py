from . import Error
import json


class Fsm:
    '''
        Represents Finite State Automota

        States: A set containing all the states
        Alphabets: A set containing all the symbols(alphabets)
        Transitions: A dictionary containing all the transitions
        StartState: Initial State
        FinalStates: A set of all the accepting states
    '''

    def __init__(self, States, Alphabets, Transitions, StartState, FinalStates, IsDeteministinc):
        self._States = States
        self._Alphabets = Alphabets
        self._Transitions = Transitions
        self._StartState = StartState
        self._FinalStates = FinalStates
        self._IsDeterministic = IsDeteministinc

    @property
    def GetStates(self):
        '''
            Returns the set of states
        '''
        return self._States

    @property
    def GetAlphabets(self):
        '''
            Returns the alphabets
        '''
        return self._Alphabets

    @property
    def GetTransitions(self):
        '''
            Returns the transitions
        '''
        return self._Transitions

    @property
    def GetStartState(self):
        '''
            Returns initial state
        '''
        return self._StartState

    @property
    def GetFinalStates(self):
        '''
            Returns the set of the accepting states
        '''
        return self._FinalStates

    def StateTransition(self, State, Alphabet):
        '''
            It returns the next state from a state and an alphabet
            It returns {} if there is no transition
        '''
        if State not in self._States:
            raise Exception('%s is not a State' % State)
        if Alphabet not in self._Alphabets:
            raise Exception('%s is not an Alphabet' % Alphabet)
        if State in self._Transitions and Alphabet in self._Transitions[State]:
            return self._Transitions[State][Alphabet]
        return None if self._IsDeterministic else {}

    @staticmethod
    def SetToState(S):
        '''
            Transforms a set of states to a new state.
        '''
        return '{' + ', '.join(sorted(str(i) for i in S)) + '}'

    @staticmethod
    def ConvertToJson(obj):
        return json.dumps(obj)
