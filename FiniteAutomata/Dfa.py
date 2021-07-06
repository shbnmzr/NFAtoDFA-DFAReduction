from .Fsm import Fsm
import pandas as pd
import json
import copy


class Dfa(Fsm):
    '''
        Represents a Deterministic Finite Automata
    '''

    def __init__(self, States, Alphabets, Transitions, StartState, FinalStates):
        super().__init__(States, Alphabets, Transitions, StartState, FinalStates, True)
        self._MinimalStates = None
        self._MinimalFinalStates = None
        self._MinimalTransitions = None
        self._ReducedTransitions = None
        self._MinimalStartState = None

    @property
    def GetMinimalStates(self):
        return self._MinimalStates

    @property
    def GetMinimalFinalStates(self):
        return self._MinimalFinalStates

    @property
    def GetMinimalStartState(self):
        return self._MinimalStartState

    @property
    def GetReducedTransitions(self):
        return self._ReducedTransitions

    def CleanTransitions(self):
        '''
            Checks the trasitions dictionary and adjusts it to the acceptable format
        '''
        for State in self._States:
            if State in self._Transitions:
                continue
            self._Transitions[State] = dict()
            for Alphabet in self._Alphabets:
                self._Transitions[State][Alphabet] = []

    def AddTrap(self):
        '''
            Adds Trap transitions
        '''
        self.CleanTransitions()
        self._States.add('z')
        for State in self._Transitions:
            for Alphabet in self._Transitions[State]:
                if self._Transitions[State][Alphabet] == []:
                    self._Transitions[State][Alphabet].append('z')
        self._Transitions['z'] = dict()
        for Alphabet in self._Alphabets:
            self._Transitions['z'][Alphabet] = ['z']

    def RemoveTrap(self):
        '''
            Removes Trap from the final transitions
        '''
        for State in self._ReducedTransitions:
            for Alphabet in self._ReducedTransitions[State]:
                if 'z' in self._ReducedTransitions[State][Alphabet]:
                    self._ReducedTransitions[State][Alphabet] = ''
        if '{z}' in self._ReducedTransitions:
            self._ReducedTransitions.pop('{z}')
            self._MinimalStates.remove('{z}')

    def UnreachableStates(self, State, ReachableStates):
        '''
           Returns the set of reachable states.
        '''
        TransitionsCopy = copy.deepcopy(self._Transitions)
        CurrentState = str()
        if ReachableStates is None:
            ReachableStates = list()
        if not State in ReachableStates:
            ReachableStates.append(State)
            for Alphabet in TransitionsCopy[State]:
                if not TransitionsCopy[State][Alphabet] == []:
                    CurrentState = TransitionsCopy[State][Alphabet].pop()
                    self.UnreachableStates(CurrentState, ReachableStates)
        return set(ReachableStates)

    def RemoveUnreachableStates(self):
        '''
            Removes unreachable states from States and final states and transitions
        '''
        self.AddTrap()
        ReachableStates = self.UnreachableStates(self._StartState, None)
        TransitionsCopy = copy.deepcopy(self._Transitions)
        self._MinimalStates = copy.deepcopy(ReachableStates)
        self._MinimalFinalStates = {
            State for State in ReachableStates if State in self._FinalStates}
        self._MinimalTransitions = {State: Transitions for State,
                                    Transitions in TransitionsCopy.items() if State in self._MinimalStates}

    def InitialDataFrame(self):
        '''
            Determines whether the state is final
            Returns the Transition table with P0 as a DataFrame
        '''
        self.RemoveUnreachableStates()
        for State in self._MinimalTransitions:
            for Alphabet in self._MinimalTransitions[State]:
                if not self._MinimalTransitions[State][Alphabet] == []:
                    self._MinimalTransitions[State][Alphabet] = self._MinimalTransitions[State][Alphabet].pop(
                    )
                else:
                    self._MinimalTransitions[State][Alphabet] = 'z'
        IsFinal = []
        for State in sorted(self._MinimalStates):
            if State in self._MinimalFinalStates:
                IsFinal.append('1')
            else:
                IsFinal.append('0')
        TransitionTable = pd.DataFrame(self._MinimalTransitions).transpose()
        TransitionTable['eq'] = IsFinal
        return TransitionTable

    def CreateEqColumn(self, EqValues):
        '''
            Forms eq column to be inserted into the transition table
        '''
        NewEq = []
        for State in sorted(list(self._MinimalStates)):
            for Class in EqValues:
                if State in Class:
                    NewEq.append(EqValues.index(Class))
        return NewEq

    def FindPartitions(self, TransitionTable):
        '''
            Seperates equivalent states into classes
        '''
        EqClasses = pd.DataFrame()
        EqClasses = TransitionTable[TransitionTable.duplicated(keep=False)]
        EqClasses = TransitionTable.groupby(list(TransitionTable)).apply(
            lambda x: list(tuple(x.index)))
        EqValues = []
        for Class in EqClasses:
            Alph = []
            for Item in Class:
                if not sorted(list(self._MinimalStates))[Item] == 'z':
                    Alph.append(sorted(list(self._MinimalStates))[Item])
            EqValues.append(tuple(Alph))
        if tuple('z') not in EqValues:
            EqValues.append(tuple('z'))
        return EqValues

    def InitialTransitionTable(self, InitialTT):
        '''
            Forms the initial transition table and eq1
        '''
        CurrentTT = pd.DataFrame()
        for Alphabet in InitialTT.columns[:-1]:
            ColumnValues = []
            for Index, Row in InitialTT.iterrows():
                ColumnValues.append(InitialTT.at[Row[Alphabet], 'eq'])
            CurrentTT[Alphabet] = ColumnValues
        Eq0Column = list(InitialTT['eq'].copy(deep=True))
        CurrentTT.insert(loc=0, column='eq0', value=Eq0Column)
        EqValues = self.FindPartitions(CurrentTT)
        NewEq = self.CreateEqColumn(EqValues)
        CurrentTT['eq'] = NewEq
        return CurrentTT

    def FindIndistiguishableStates(self, PreviousTT, InitialTT):
        '''
            Finds equivalent states and combines them together
            Returns the new transition table
        '''
        CurrentTT = pd.DataFrame()
        Eq0Column = list(PreviousTT['eq'].copy(deep=True))
        CurrentTT.insert(loc=0, column='eq0', value=Eq0Column)
        StatesAsSortedList = list(sorted(self._MinimalStates))
        for Alphabet in InitialTT.columns[:-1]:
            ColumnValues = []
            for Index, Row in InitialTT.iterrows():
                CellContent = next(iter(self.StateTransition(Index, Alphabet)))
                ColumnValues.append(
                    CurrentTT.at[StatesAsSortedList.index(CellContent), 'eq0'])
            CurrentTT[Alphabet] = ColumnValues
        EqValues = self.FindPartitions(CurrentTT)
        NewEq = self.CreateEqColumn(EqValues)
        CurrentTT['eq'] = NewEq
        if not PreviousTT.equals(CurrentTT):
            self.FindIndistiguishableStates(CurrentTT, InitialTT)
            return
        else:
            self._ReducedTransitions = self.RemoveEquivalentStates(CurrentTT)

    def CombineEquivalentStates(self, FinalTransitionTable, NewStates):
        '''
            Combines equivalent states 
            Retruns the new transition table
        '''
        for Alphabet in FinalTransitionTable.columns:
            ColumnValues = []
            for Index, Row in FinalTransitionTable.iterrows():
                StateIndex = FinalTransitionTable.at[Index, Alphabet]
                ColumnValues.append(NewStates[StateIndex])
            FinalTransitionTable[Alphabet] = ColumnValues
        return FinalTransitionTable.copy()

    def RemoveEquivalentStates(self, FinalTransitionTable):
        '''
            Removes equivalent states 
            Converts the transition table into a JSON object 
            Returns the JSON object
        '''
        EqValues = self.FindPartitions(FinalTransitionTable)
        Classes = []
        for Class in EqValues:
            Classes.append(Fsm.SetToState(Class))
        NewClasses = []
        InitialTransitionTable = self.InitialDataFrame()
        for State in InitialTransitionTable.index:
            for Class in Classes:
                if State in Class:
                    NewClasses.append(Class)
        CleanClasses = []
        for Class in NewClasses:
            if ', z' in Class:
                Class = Class.replace(', z', '')
            if 'z' in Class:
                Class = Class.replace('z', '')
            CleanClasses.append(Class)

        NewClasses = copy.deepcopy(CleanClasses)
        self._MinimalStates = set(NewClasses.copy())
        FinalTransitionTable = FinalTransitionTable.drop('eq0', axis=1)
        FinalTransitionTable = FinalTransitionTable.drop('eq', axis=1)
        FinalTransitionTable = self.CombineEquivalentStates(
            FinalTransitionTable.copy(), Classes)
        FinalTransitionTable['states'] = NewClasses
        FinalTransitionTable = FinalTransitionTable.drop_duplicates()
        FinalTransitionTable.set_index('states', drop=True, inplace=True)
        FinalTransitionTable = FinalTransitionTable.transpose()
        TransitionTableAsJSON = FinalTransitionTable.to_json()
        TransitionTableAsJSON = json.loads(TransitionTableAsJSON)
        for State in TransitionTableAsJSON:
            for Alphabet in TransitionTableAsJSON[State]:
                if 'z' in TransitionTableAsJSON[State][Alphabet]:
                    TransitionTableAsJSON[State][Alphabet] = TransitionTableAsJSON[State][Alphabet].replace(
                        ', z', '')
        return TransitionTableAsJSON

    def CombineFinalStates(self):
        '''
            Determines the new final states
        '''
        NewFinalStates = set()
        for State in self._MinimalStates:
            for FinalState in self._MinimalFinalStates:
                if FinalState in State:
                    NewFinalStates.add(State)
        return NewFinalStates.copy()

    def CombineStartState(self):
        '''
            Replaces states that are equivalent to the start state 
        '''
        NewStartState = str()
        for State in self._MinimalStates:
            if self._StartState in State:
                NewStartState = State
        return NewStartState

    def MinimizeDfa(self):
        '''
            Performs reduction algorithm 
            Returns a new Dfa Object
        '''
        InitialTransitionTable = self.InitialDataFrame()
        self.FindIndistiguishableStates(self.InitialTransitionTable(
            InitialTransitionTable), InitialTransitionTable)
        self._MinimalFinalStates = self.CombineFinalStates()
        self._MinimalStartState = self.CombineStartState()
        self.RemoveTrap()
        return Dfa(self._MinimalStates, self._Alphabets, self._ReducedTransitions, self._MinimalStartState, self._MinimalFinalStates)

    def Display(self):
        print(' States: ', self._States)
        print(' Start: ', self._StartState)
        print(' Final States: ', self._FinalStates)
        print(' Transitions: ', self._Transitions)
