from .Fsm import Fsm
from .Dfa import Dfa

class Nfa(Fsm):
    '''
        Represents a Non-deterministic Finite Automata
    '''
    EPSILON = chr(949)
    def __init__(self, States, Alphabets, Transitions, StartState, FinalStates):
        super().__init__(States, Alphabets, Transitions, StartState, FinalStates, False)

    def HasEpsilonMoves(self):
        '''
            Returns True if the NFA has epsilon-moves.
        '''
        return Nfa.EPSILON in self._Alphabets

    def EpsilonClosure(self, State):
        '''
            Returns the epsilon closure of a state.
        '''
        StateSet = {State}
        if self.HasEpsilonMoves():
            self.RecursiveClosure(State, StateSet)
        return StateSet

    def RecursiveClosure(self, State, StateSet):
        StateSet.add(State)
        for S in self.StateTransition(State, Nfa.EPSILON):
            self.RecursiveClosure(S, StateSet)

    def ToDfa(self):
        '''
        Returns the DFA corresponding to the NFA.
        It uses the powerset construction.
        '''
        Alphabets = set(self._Alphabets)
        if self.HasEpsilonMoves():
            Alphabets.remove(Nfa.EPSILON)
        States = set()
        Transitions = dict()
        FinalState = set()
        NewStates = [self.EpsilonClosure(self._StartState)]
        StartState = Fsm.SetToState(NewStates[0])
        while NewStates:
            State = NewStates.pop()
            NewState = Fsm.SetToState(State)
            States.add(NewState)
            if self._FinalStates.intersection(State):
                FinalState.add(NewState)
            Transitions[NewState] = dict()
            for Alphabet in Alphabets:
                T = set()
                for s in State:
                    for i in self.StateTransition(s, Alphabet):
                        T.update(self.EpsilonClosure(i))
                if T:
                    ns = Fsm.SetToState(T)
                    Transitions[NewState][Alphabet] = ns
                    if ns not in States and T not in NewStates:
                        NewStates.append(T)
        return Dfa(States, Alphabets, Transitions, StartState, FinalState)