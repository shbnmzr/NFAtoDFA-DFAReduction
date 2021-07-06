from FiniteAutomata.Nfa import Nfa
from FiniteAutomata.Dfa import Dfa


def main():

    # Dfa Minimization Example
    States = {'a', 'b', 'c', 'd'}
    Alphabets = {'0', '1'}
    Transitions = {
        'a': {
            '0': ['b'],
            '1': ['c']
        },
        'd': {
            '0': ['c'],
            '1': ['f']
        }
    }
    StartState = 'a'
    FinalStates = {'c'}
    DfaMachinine = Dfa(States, Alphabets, Transitions, StartState, FinalStates)
    MinimizedDfa = DfaMachinine.MinimizeDfa()
    MinimizedDfa.Display()

    # NFA to DFA Example #1
    StatesNfa = {'a', 'b'}
    AlphabetsNfa = {}
    TransitionsNfa = {
        'a': {
            Nfa.EPSILON: ['b']
        },
        'b': {

        }
    }
    StartStateNfa = 'a'
    FinalStatesNfa = {'a'}
    NfaMachine = Nfa(StatesNfa, AlphabetsNfa, TransitionsNfa,
                     StartStateNfa, FinalStatesNfa)
    EqDfa = NfaMachine.ToDfa()
    EqDfa.Display()

    # # NFA To DFA Example #2
    StatesNfa2 = {'a', 'b', 'c'}
    AlphabetsNfa2 = {'0', '1'}
    TransitionsNfa2 = {
        'a': {
            '0': ['a'],
            '1': ['a', 'b']
        },
        'b': {
            '1': ['c'],
            '0': []
        },
        'c': {
            '0': [],
            '1': []
        }
    }
    StartStateNfa2 = 'a'
    FinalStatesNfa2 = {'c'}
    NfaMachine2 = Nfa(StatesNfa2, AlphabetsNfa2, TransitionsNfa2,
                      StartStateNfa2, FinalStatesNfa2)
    EqDfa2 = NfaMachine2.ToDfa()
    EqDfa2.Display()


if __name__ == '__main__':
    main()
